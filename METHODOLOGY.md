# Project Greenprints: Methodology

_This file is generated automatically every time the tool runs, from the files in `config/`. Do not edit it by hand; edit the config and re-run._

## Results at a glance

Between **September 2023** and **September 2026**, Blueprints for Pangaea redistributed **85,401 lbs** (42.7 short tons) of surplus medical supplies across **46 shipments**. We estimate this avoided **131 metric tons of CO2 equivalent (MTCO2e)** (range 110 to 152) compared with the supplies being landfilled.

If the supplies would instead have been sent to combustion (incinerated), the estimate is 154 MTCO2e (range 143 to 166).

1 shipment(s) had no weight or box/pallet count and are **not** included in these totals.

## What we measured

Blueprints for Pangaea (B4P) collects surplus medical supplies from Michigan Medicine that would otherwise be thrown away, and sends them to clinics locally, nationally and internationally. This analysis estimates the greenhouse gas emissions avoided because those supplies were reused instead of discarded.

## The data

- Source: B4P's *Master Shipment Database* (Google Sheet), exported as CSV.
- Date range: shipments dated **September 2023 through September 2026** (inclusive). The sheet records month and year only, so each shipment is dated the 1st of its month.
- Weight: the *Poundage of shipments (lbs)* column, which includes the boxes and packaging the supplies were shipped in.
- Academic years run September to August (for example, 2023-24 = September 2023 to August 2024).

## Method: EPA Waste Reduction Model (WARM)

We use the U.S. EPA's **Waste Reduction Model (WARM), version 16** (December 2023). WARM gives an emission factor, in MTCO2e per short ton (1 short ton = 2,000 lbs), for each material under each way of handling it.

The emissions avoided are the difference between two scenarios:

- **Baseline (without B4P): Landfilling.** The supplies would have been thrown away and sent to a landfill. As a sensitivity check we also report a **Combustion** baseline, because hospital waste is often incinerated. The landfill figure is the headline number.
- **Alternative (what B4P does): Source reduction.** The supplies are used by a clinic, so new supplies do not need to be manufactured. WARM credits the emissions from making those new products as avoided.

```
avoided MTCO2e = short tons x (baseline factor - alternative factor)
```

Example: 2,000 lbs of mixed plastics = 1 short ton x (0.02 - (-1.87)) = **1.89 MTCO2e avoided**.

We also report a smaller **disposal-only** number: what disposing of the supplies would itself have emitted (short tons x baseline factor). For plastics in a landfill this is very small, because plastics barely break down. Comparing it with the headline shows that almost all of the benefit comes from avoided manufacturing.

### The replacement assumption

The method assumes that **every donated item replaces a new item the recipient would otherwise have bought**. If a clinic would simply have gone without, or if some donated items go unused, the true benefit is smaller than reported.

## What the supplies are made of (material profiles)

WARM factors are per material, but our records mostly give only a total weight and a short comment. Each shipment is therefore given a **material profile**: an assumed mix of WARM materials by weight. **These mixes are estimates, not measurements**; they are placeholders until B4P weighs and sorts sample boxes.

A shipment's profile is chosen by keyword rules applied to the Comments, Recipient Name and Shipping Destination columns. The first rule that matches wins:

| Order | Profile | Pattern (case-insensitive regex) |
|---|---|---|
| 1 | durable_medical_equipment | wheelchair\|walker\|crutch\|\bcanes?\b\|\bDME\b\|durable medical |
| 2 | medical_equipment | blood pressure\|microscope\|monitor\|machine |
| 3 | ppe | glove\|mask\|face shield\|N95\|gown\|\bPPE\b |
| 4 | surgical_supplies | surgical\|surgial |
| 5 | absorbent_and_textiles | diaper\|bed pad\|blanket\|hygiene\|washcloth |
| 6 | mixed_medical_supplies | (no match: default) |


Each profile has a **central** (best guess), **low** and **high** version. Low assumes less cardboard/paper packaging; high assumes more. Every total is reported as a central estimate with a low-high range.

| Profile | Material | low | central | high |
|---|---|---|---|---|
| absorbent_and_textiles | Mixed Paper (general) | 0.45 | 0.60 | 0.75 |
| absorbent_and_textiles | Mixed Plastics | 0.55 | 0.40 | 0.25 |
| durable_medical_equipment | Corrugated Containers | 0.06 | 0.10 | 0.19 |
| durable_medical_equipment | Mixed Metals | 0.73 | 0.70 | 0.63 |
| durable_medical_equipment | Mixed Plastics | 0.21 | 0.20 | 0.18 |
| medical_equipment | Corrugated Containers | 0.06 | 0.10 | 0.19 |
| medical_equipment | Mixed Metals | 0.53 | 0.50 | 0.45 |
| medical_equipment | Mixed Plastics | 0.42 | 0.40 | 0.36 |
| mixed_medical_supplies | Corrugated Containers | 0.16 | 0.30 | 0.44 |
| mixed_medical_supplies | Mixed Metals | 0.12 | 0.10 | 0.08 |
| mixed_medical_supplies | Mixed Plastics | 0.72 | 0.60 | 0.48 |
| ppe | Corrugated Containers | 0.05 | 0.15 | 0.25 |
| ppe | Mixed Plastics | 0.95 | 0.85 | 0.75 |
| surgical_supplies | Corrugated Containers | 0.10 | 0.25 | 0.40 |
| surgical_supplies | Mixed Metals | 0.12 | 0.10 | 0.08 |
| surgical_supplies | Mixed Plastics | 0.78 | 0.65 | 0.52 |


Resulting emission factor for each profile (MTCO2e avoided per short ton):

| Profile | Scenario | Avoided MTCO2e/short ton (Landfilling baseline) | Avoided MTCO2e/short ton (Combustion baseline) | Disposal-only MTCO2e/short ton (Landfilling) |
|---|---|---|---|---|
| mixed_medical_supplies | low | 2.72 | 3.38 | 0.05 |
| mixed_medical_supplies | central | 3.23 | 3.67 | 0.07 |
| mixed_medical_supplies | high | 3.74 | 3.95 | 0.09 |
| ppe | low | 2.08 | 3.23 | 0.03 |
| ppe | central | 2.47 | 3.42 | 0.04 |
| ppe | high | 2.86 | 3.62 | 0.06 |
| surgical_supplies | low | 2.49 | 3.27 | 0.04 |
| surgical_supplies | central | 3.04 | 3.57 | 0.06 |
| surgical_supplies | high | 3.58 | 3.87 | 0.08 |
| durable_medical_equipment | low | 3.41 | 2.87 | 0.03 |
| durable_medical_equipment | central | 3.52 | 2.98 | 0.04 |
| durable_medical_equipment | high | 3.75 | 3.19 | 0.05 |
| medical_equipment | low | 3.04 | 2.98 | 0.03 |
| medical_equipment | central | 3.17 | 3.08 | 0.04 |
| medical_equipment | high | 3.43 | 3.28 | 0.05 |
| absorbent_and_textiles | low | 3.80 | 4.23 | 0.04 |
| absorbent_and_textiles | central | 4.44 | 4.60 | 0.05 |
| absorbent_and_textiles | high | 5.08 | 4.97 | 0.06 |


Adult diapers, bed pads, blankets and hygiene items have no exact WARM material; they are approximated as a mix of mixed plastics and mixed paper.

### WARM factors used

| Material | Source reduction | Recycling | Combustion | Landfilling |
|---|---|---|---|---|
| Corrugated Containers | -5.58 | -3.14 | -0.49 | 0.18 |
| Mixed Paper (general) | -6.07 | -3.55 | -0.49 | 0.07 |
| Office Paper | -7.95 | -2.86 | -0.47 | 1.13 |
| HDPE | -1.42 | -0.76 | 1.29 | 0.02 |
| LDPE | -1.80 |  | 1.29 | 0.02 |
| PET | -2.17 | -1.04 | 1.24 | 0.02 |
| LLDPE | -1.58 |  | 1.29 | 0.02 |
| PP | -1.52 | -0.79 | 1.29 | 0.02 |
| PS | -2.50 |  | 1.65 | 0.02 |
| PVC | -1.93 |  | 0.66 | 0.02 |
| Mixed Plastics | -1.87 | -0.93 | 1.26 | 0.02 |
| Steel Cans | -3.03 | -1.83 | -1.59 | 0.02 |
| Aluminum Cans | -4.80 | -9.13 | 0.03 | 0.02 |
| Mixed Metals | -3.65 | -4.39 | -1.02 | 0.02 |
| Glass | -0.53 | -0.28 | 0.03 | 0.02 |
| Carpet | -3.68 | -2.38 | 1.10 | 0.02 |


Source: EPA WARM Version 16, Management Practices Chapters, Exhibit 1-1, <https://www.epa.gov/system/files/documents/2024-01/warm_management_practices_v16_dec.pdf>.

## Missing weights

1. If a weight is recorded, we use it.
2. If not, but the number of pallets and/or boxes is known, we estimate it with B4P's Estimates Calculator: pallets x 489.14 lbs + boxes x 39.4 lbs.
3. If neither is known, the shipment is left out of the totals and listed in the data quality report so it can be filled in.

## Limitations

- **Freight emissions are not counted.** Trucking and ocean/air shipping to recipients produce emissions that would reduce the net benefit, especially for international shipments. The tool is designed so this can be added later.
- **Material profiles are estimates.** The low-high range shows how much the result depends on them; sampling real boxes would narrow it.
- **Replacement assumption.** We assume each donated item displaces the purchase of a new one.
- **WARM is a U.S. model.** Manufacturing and disposal emissions are U.S. averages and may differ for the actual products and for recipient countries.
- **Shipment weight includes packaging**, which is why cardboard appears in the profiles.
- **Month-level dates.** Shipments are dated to the month, not the day.
