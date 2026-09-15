# Deployment

Live demo, deployed 2026-09-15 at zero recurring cost, no paid plan anywhere (constraint from the
project owner). What's actually running, and how to reproduce or redeploy it.

## Live URLs

- Frontend: https://frontend-neon-nine-bl3oyccpzz.vercel.app
- Backend API: https://140-245-24-132.sslip.io (`/health`, `/match`, `/catalogue-image`)

## Why this stack, after three rejected platforms

Every managed "free" container platform actually tried caps out around 512MB RAM — not enough to hold
CLIP + torch without OOM-crashing:

| Platform | Result |
|---|---|
| Render (free tier) | ~512MB RAM. Ruled out before trying (owner's constraint: no paid plans). |
| Koyeb (free tier) | 512MB RAM, 0.1 vCPU — confirmed via their own docs. Same problem as Render. |
| Hugging Face Spaces (free CPU) | Docker/Gradio SDKs now require a PRO subscription on the free CPU tier — confirmed directly from the API (`402 Payment Required`), not assumed. |
| **Oracle Cloud "Always Free"** | **24GB RAM available (used a 1GB instance in the end, see below) — genuinely $0 forever within the free allowance. Card required for identity verification at signup, but never charged if usage stays in the Always Free tier.** |

## What's actually running

- **Compute:** an Oracle Cloud Always Free VM (`VM.Standard.E2.1.Micro`, 1 vCPU / 1GB RAM — the ARM
  `A1.Flex` shape, which has much more headroom, was tried first but every size request failed with
  "Out of host capacity" in the ap-mumbai-1 region; a known, common Always Free ARM availability issue,
  not specific to this project). 6GB swap added to give the 1GB box real headroom.
- **Container:** `backend/Dockerfile`, built **locally** (cross-compiled for `linux/amd64` via `docker
  buildx --platform linux/amd64`) rather than on the VM itself — the VM was too weak to run the build
  (pip installing torch + embedding 7,272 catalogue images pushed it into heavy swap-thrashing;
  ~45 minutes in, it hadn't even finished downloading catalogue images). The local build finished the
  same work end-to-end in about 26 minutes, most of it CLIP embedding under x86 emulation on an M2
  Mac (natively this takes about 90 seconds — QEMU emulation overhead accounts for the rest). The
  1.4GB image was `docker save | gzip`'d, `scp`'d to the VM, and `docker load`'d there.
- **Reverse proxy + TLS:** Caddy, with a free `sslip.io` "magic domain"
  (`140-245-24-132.sslip.io` resolves to the VM's own IP automatically, no domain purchase or DNS setup
  needed) so Caddy can obtain a real Let's Encrypt certificate via the HTTP-01/TLS-ALPN-01 challenge.
  A plain HTTP backend wouldn't work here regardless — browsers block an HTTPS page (the Vercel
  frontend) from calling a plain-HTTP API (mixed content).
- **A real bug found during setup:** Oracle's own security list (the cloud-level firewall) had ports
  80/443 open, but the VM's *own* `iptables` (the OS-level firewall, separate from OCI's) only allowed
  SSH by default — a common gotcha on Oracle's stock Ubuntu images. Diagnosed via Caddy's ACME challenge
  failing with "Error getting validation data," fixed by explicitly `ACCEPT`ing 80/443 in `iptables`
  before the default `REJECT` rule, then persisted with `netfilter-persistent`.
- **Frontend:** Next.js on Vercel (free Hobby tier), `NEXT_PUBLIC_API_URL` set to the backend's HTTPS
  URL via `vercel env add ... production`.
- **CORS:** tightened after both were live — `CORS_ORIGINS` on the backend container is scoped to the
  exact Vercel domain(s), not left at the Dockerfile's development default of `*`.

## Known limitations of this setup

- **Slow.** A single match request takes ~15-18 seconds on this VM (vs ~1 second on the M2 Mac used for
  development) — no GPU, 1 shared vCPU, heavy swap usage. Acceptable for a take-home demo, not for real
  traffic.
- **Single point of failure**, no redundancy, no auto-restart beyond Docker's `--restart unless-stopped`
  (survives a container crash or VM reboot, not an Oracle-side outage).
- **The VM is genuinely resource-constrained** (1GB RAM, 6GB swap doing real work) — rebuilding the
  Docker image *on* the VM itself is not practical; use the local-build-then-transfer approach above.

## Reproducing / redeploying

```bash
# 1. Provision the VM (idempotent -- safe to re-run, skips resources that already exist)
python3 scripts/oci_provision.py VM.Standard.E2.1.Micro   # or VM.Standard.A1.Flex if ARM capacity is free

# 2. Build the backend image locally for the VM's architecture (amd64)
docker buildx build --platform linux/amd64 -t dyla-backend:amd64 -f backend/Dockerfile --load .

# 3. Transfer and load it
docker save dyla-backend:amd64 | gzip > /tmp/dyla-backend.tar.gz
scp -i ~/.oci/keys/dyla-vm /tmp/dyla-backend.tar.gz ubuntu@<VM_IP>:~/
ssh -i ~/.oci/keys/dyla-vm ubuntu@<VM_IP> "docker load -i ~/dyla-backend.tar.gz"

# 4. Run it
ssh -i ~/.oci/keys/dyla-vm ubuntu@<VM_IP> \
  "docker run -d --name dyla-backend --restart unless-stopped -p 8000:8000 \
   -e CORS_ORIGINS='https://<your-vercel-domain>' dyla-backend:amd64"

# 5. Point Caddy at it (/etc/caddy/Caddyfile on the VM):
#    <ip-with-dashes>.sslip.io { reverse_proxy localhost:8000 }
#    then: sudo systemctl restart caddy
# If TLS issuance fails with "Error getting validation data", check iptables allows 80/443
# (OCI's security list being open is not sufficient -- the VM's own firewall must allow it too).

# 6. Deploy the frontend
cd frontend && vercel env add NEXT_PUBLIC_API_URL production   # paste the backend's https:// URL
vercel --prod
```
