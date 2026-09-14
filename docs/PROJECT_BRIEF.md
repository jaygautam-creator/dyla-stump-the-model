# Project brief: my notes

Written 2026-09-14 before starting. Facts link to sources; my own guesses are marked as such.

## The company

Thuli Studios Private Limited, Chennai. Incorporated 30 Nov 2024. Their stated aim is "next-gen AI products
with an India-first approach." Small team; the brief says every hire has to be someone the rest of the
team learns from.

Sources: [thuli.studio](https://www.thuli.studio/),
[Tracxn](https://tracxn.com/d/legal-entities/india/thuli-studios-private-limited/__9gvIpPPdp_S8H2WspY41fMH9FBo2oAW-SCfH0byEhNY),
[The Company Check](https://www.thecompanycheck.com/company/thuli-studios-private-limited/U62011TN2024PTC175141)

## The product: Dyla

[dyla.ai](https://dyla.ai/) is AI for Indian jewellery retail, which they describe as "a $100 billion category
still vastly underexplored by technology." They sell to jewellery brands and retailers. Three products on the site:

1. **E-Catalog Studio**: iPhone product photos turned into studio-quality jewellery imagery.
2. **Conversational Shopping**: styling and recommendations over WhatsApp and Instagram.
3. **Digital Styling Counter**: in-store AI to style, visualise and choose.

There is also a consumer iOS app ([App Store](https://apps.apple.com/in/app/dyla/id6749906266)) for try-on and
styling, recently opened to the UK, Europe and UAE.

## Why this problem probably matters to them (my guess)

"Someone photographs an object and wants to know exactly which catalogue item it is" is what happens when:

- a shopper sends a photo or an Instagram screenshot on WhatsApp and asks "do you have this?"
- a customer at the store counter shows a piece and wants the closest match
- a phone photo has to be matched against studio imagery, the same gap E-Catalog Studio works on

So I'm treating this as a small prototype of visual search for a jewellery retailer.

## The problem (Problem 2, Stump the Model)

**Part A, the matcher.** A photo goes in; ranked top-5 catalogue items with a confidence score come out.
Catalogue of at least 5,000 scraped images. They care about the retrieval approach, what happens when there is
no match, and single-lookup speed.

**Part B, the stumper.** At least 100 phone photos, shot by me, of items that are in the catalogue, made hard:
bad lighting, odd angles, occlusion, clutter, motion blur, reflections, hand or wrist in frame. Each labelled with
the correct item and the conditions I was trying to induce. A harness reports accuracy per condition.

**What they want to see.** The gap between clean and hard, and a diagnosis of why. My own evaluation method,
defended. Which conditions hurt most, what I tried, what didn't work.

**Optional extensions (pick one and do it properly):** refuse correctly on items not in the catalogue;
100k items under 100 ms on CPU; multiple items per photo; add 1,000 items without recomputing; automated
stumper. I'm picking refusal.

## What they're asking for

- Both halves built.
- 12 to 15 hours over 5 to 7 days.
- AI tools allowed; full session logs in `/logs` are required.
- `DECISIONS.md`, max two pages: architecture and what was rejected, trade-offs, testing, where it breaks,
  next two weeks.
- Private GitHub repo, README that runs on a clean machine in under 5 minutes.

How they assess: doing exactly what's asked, correctly, is a no. What moves it is something unasked that matters,
a weakness found and named first, an obvious approach measured and replaced with evidence, and clear ownership
of decisions. The follow-up is a 45-minute call where I change the system live under a new constraint, so I
need to understand every part of it.

Constraints I should be ready for in that call: faster lookup, adding new items, a different operating point for
refusal, a new failure condition, swapping the backbone, multiple items in one photo.
