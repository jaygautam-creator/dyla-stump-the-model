"""One-time provisioning of the Always Free OCI VM that hosts the backend.

Not part of the matcher/eval codebase -- a deployment utility, run once interactively. Idempotent
where practical (checks for existing resources by display name before creating), but this is
infrastructure-as-a-script, not infrastructure-as-code; re-running it isn't meant to be routine.
"""
import sys
import time

import oci

DISPLAY_PREFIX = "dyla-backend"
SSH_PUBLIC_KEY_PATH = "/Users/jaygautam/.oci/keys/dyla-vm.pub"


def get_or_create(list_fn, create_fn, name_field="display_name", **filters):
    for item in list_fn():
        if getattr(item, name_field) == filters.get(name_field) and all(
            getattr(item, k, None) == v for k, v in filters.items() if k != name_field
        ):
            print(f"  found existing: {filters.get(name_field)}")
            return item
    return create_fn()


def main():
    config = oci.config.from_file()
    tenancy = config["tenancy"]
    compartment_id = tenancy  # root compartment -- fine for a personal Always Free tenancy

    identity = oci.identity.IdentityClient(config)
    net = oci.core.VirtualNetworkClient(config)
    compute = oci.core.ComputeClient(config)

    ad = identity.list_availability_domains(compartment_id).data[0].name
    print(f"Availability domain: {ad}")

    # --- VCN ---
    vcn_name = f"{DISPLAY_PREFIX}-vcn"
    vcns = net.list_vcns(compartment_id, display_name=vcn_name).data
    if vcns:
        vcn = vcns[0]
        print(f"VCN exists: {vcn.id}")
    else:
        print("Creating VCN...")
        vcn = net.create_vcn(
            oci.core.models.CreateVcnDetails(
                compartment_id=compartment_id, display_name=vcn_name, cidr_block="10.0.0.0/16"
            )
        ).data
        oci.wait_until(net, net.get_vcn(vcn.id), "lifecycle_state", "AVAILABLE")

    # --- Internet gateway ---
    igw_name = f"{DISPLAY_PREFIX}-igw"
    igws = net.list_internet_gateways(compartment_id, vcn_id=vcn.id, display_name=igw_name).data
    if igws:
        igw = igws[0]
    else:
        print("Creating internet gateway...")
        igw = net.create_internet_gateway(
            oci.core.models.CreateInternetGatewayDetails(
                compartment_id=compartment_id, vcn_id=vcn.id, display_name=igw_name, is_enabled=True
            )
        ).data
        oci.wait_until(net, net.get_internet_gateway(igw.id), "lifecycle_state", "AVAILABLE")

    # --- Route table: default route via the internet gateway ---
    route_tables = net.list_route_tables(compartment_id, vcn_id=vcn.id).data
    default_rt = next(rt for rt in route_tables if rt.display_name.startswith("Default"))
    net.update_route_table(
        default_rt.id,
        oci.core.models.UpdateRouteTableDetails(
            route_rules=[
                oci.core.models.RouteRule(
                    destination="0.0.0.0/0", destination_type="CIDR_BLOCK", network_entity_id=igw.id
                )
            ]
        ),
    )

    # --- Security list: SSH (22), HTTP (80), HTTPS (443) ingress; all egress ---
    security_lists = net.list_security_lists(compartment_id, vcn_id=vcn.id).data
    default_sl = next(sl for sl in security_lists if sl.display_name.startswith("Default"))
    ingress_ports = [22, 80, 443]
    net.update_security_list(
        default_sl.id,
        oci.core.models.UpdateSecurityListDetails(
            ingress_security_rules=[
                oci.core.models.IngressSecurityRule(
                    protocol="6",  # TCP
                    source="0.0.0.0/0",
                    tcp_options=oci.core.models.TcpOptions(
                        destination_port_range=oci.core.models.PortRange(min=p, max=p)
                    ),
                )
                for p in ingress_ports
            ],
            egress_security_rules=[
                oci.core.models.EgressSecurityRule(protocol="all", destination="0.0.0.0/0")
            ],
        ),
    )
    print(f"Security list updated: ingress {ingress_ports} open")

    # --- Subnet ---
    subnet_name = f"{DISPLAY_PREFIX}-subnet"
    subnets = net.list_subnets(compartment_id, vcn_id=vcn.id, display_name=subnet_name).data
    if subnets:
        subnet = subnets[0]
    else:
        print("Creating subnet...")
        subnet = net.create_subnet(
            oci.core.models.CreateSubnetDetails(
                compartment_id=compartment_id,
                vcn_id=vcn.id,
                display_name=subnet_name,
                cidr_block="10.0.0.0/24",
                availability_domain=None,  # regional subnet
                route_table_id=default_rt.id,
                security_list_ids=[default_sl.id],
            )
        ).data
        oci.wait_until(net, net.get_subnet(subnet.id), "lifecycle_state", "AVAILABLE")
    print(f"Subnet: {subnet.id}")

    # --- Image: latest Always-Free-eligible Ubuntu for the target shape ---
    shape = sys.argv[1] if len(sys.argv) > 1 else "VM.Standard.A1.Flex"
    images = compute.list_images(
        compartment_id, operating_system="Canonical Ubuntu", shape=shape, sort_by="TIMECREATED", sort_order="DESC"
    ).data
    image = images[0]
    print(f"Shape: {shape}, image: {image.display_name}")

    with open(SSH_PUBLIC_KEY_PATH) as f:
        ssh_key = f.read().strip()

    instance_name = f"{DISPLAY_PREFIX}-vm"
    instances = compute.list_instances(compartment_id, display_name=instance_name).data
    instances = [i for i in instances if i.lifecycle_state not in ("TERMINATED", "TERMINATING")]
    if instances:
        print(f"Instance already exists: {instances[0].id} ({instances[0].lifecycle_state})")
        instance = instances[0]
    else:
        # Always Free ARM capacity ("Out of host capacity") is frequently exhausted in busy regions --
        # a smaller request often succeeds where a larger one doesn't, since capacity fragments. Try a
        # few sizes, smallest last-resort first isn't right either -- try biggest-useful down to
        # smallest-still-viable for CLIP+torch (needs ~1-2GB comfortably).
        is_flex = shape.endswith(".Flex")
        sizes = [(2, 12), (1, 6), (1, 4)] if is_flex else [None]
        instance = None
        last_error = None
        for size in sizes:
            shape_config = None
            if size:
                ocpus, mem_gb = size
                print(f"Launching instance ({shape}, {ocpus} OCPU / {mem_gb}GB RAM)...")
                shape_config = oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=ocpus, memory_in_gbs=mem_gb)
            else:
                print(f"Launching instance ({shape}, fixed shape)...")
            try:
                instance = compute.launch_instance(
                    oci.core.models.LaunchInstanceDetails(
                        compartment_id=compartment_id,
                        availability_domain=ad,
                        display_name=instance_name,
                        shape=shape,
                        shape_config=shape_config,
                        source_details=oci.core.models.InstanceSourceViaImageDetails(image_id=image.id),
                        create_vnic_details=oci.core.models.CreateVnicDetails(
                            subnet_id=subnet.id, assign_public_ip=True
                        ),
                        metadata={"ssh_authorized_keys": ssh_key},
                    )
                ).data
                break
            except oci.exceptions.ServiceError as e:
                if "Out of host capacity" not in str(e.message):
                    raise
                print(f"  out of capacity, trying next size...")
                last_error = e
        if instance is None:
            raise last_error
        print(f"Instance launching: {instance.id}")
        print("Waiting for RUNNING state (this can take a few minutes)...")
        oci.wait_until(compute, compute.get_instance(instance.id), "lifecycle_state", "RUNNING", max_wait_seconds=600)

    vnic_attachments = compute.list_vnic_attachments(compartment_id, instance_id=instance.id).data
    vnic = net.get_vnic(vnic_attachments[0].vnic_id).data
    print(f"\nInstance IP: {vnic.public_ip}")
    print(f"SSH: ssh -i {SSH_PUBLIC_KEY_PATH.replace('.pub', '')} ubuntu@{vnic.public_ip}")


if __name__ == "__main__":
    sys.exit(main())
