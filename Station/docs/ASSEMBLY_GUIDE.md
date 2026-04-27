# Station Assembly Guide

NY&E Layout | SK (Stans Knob) station | HO scale 1:87 | Circa 1905
Prototype basis: New Haven standard combination station Fig. 172

---

## Parts Inventory

### Printed parts

| Part | Qty | STL file | Status | Notes |
|------|-----|----------|--------|-------|
| Exterior wall — passenger face | 1 | `SK_PassengerWall.stl` | In test print | Bay opening full TICKET_W wide × full height; wainscot, cap rail, rabbet |
| Exterior wall — siding face | 1 | `SK_SidingWall.stl` | In test print | #8033 door, #8028/69 window, #8125 freight door; wire grooves at dados; rabbet |
| Exterior wall — freight end gable | 1 | `SK_GableWall.stl` | In test print | #8070 double window; 45° miters both sides; print ×2 (same file) |
| Exterior wall — waiting end gable | 1 | `SK_GableWall.stl` | In test print | Same file as freight gable |
| Floor piece (basic) | 1 | `SK_FloorBasic.stl` | In test print | Integral partition walls, bay, plank grooves, wire notches; interior details (benches, desks, stoves, cargo); 0.15mm layer height |
| Ceiling+eave — ticket office | 1 | `SK_CeilingTicketTest.stl` | In test print | 4mm tin grid test; 24mm side eave, 11mm gable eave; pendant; wire holes |
| Ceiling+eave — full building | 1 | `SK_CeilingFull.stl` | ✅ STL ready | Single lift-off piece: all three rooms + bay. 4mm tin grid; 4 pendants (2 waiting, 1 ticket, 1 freight); wall channels all 4 exterior + 2 partition walls; 24mm side eaves, 11mm gable eaves; wire holes at WT/TF centres |
| Roof backing panel — long side | 2 | `SK_RoofPanel_Long.stl` | ✅ Print confirmed | Trapezoidal ×2 (flip one 180° for passenger side — half-lap ridge tabs interlock). Wedge eave rib + 1 flat rib. |
| Roof backing panel — hip end | 2 | `SK_RoofPanel_Hip.stl` | ✅ Print confirmed | Triangular ×2. Wedge eave rib only. Registers against long panel rabbet ledge. |
| Kerosene pendant fixtures | 4–5 | *(integral)* | Pending | Integrated into ceiling pieces; R=2.0→1.25mm cone, H=2.5mm; 1.2mm LED hole |

### Commercial parts

| Part | # | Qty | Where used |
|------|---|-----|-----------|
| Exterior door | #8033 | 4 | Waiting passenger/siding, freight passenger/siding |
| Interior door | #8032 | 2 | Waiting/ticket, ticket/freight |
| Passenger window | #8028/69 | 6 | Freight passenger ×2, ticket passenger ×1, waiting passenger ×1, siding ×2 |
| Gable double window | #8070 | 2 | Both end gable walls |
| Freight door (SK) | #8125 | 1 | Freight siding face |
| Rafter tails (short) | #8147 | ~40 | Soffit face, 14mm spacing; canopy glue |
| Slate shingles | #8135 | 2 packs | Individual strip rows applied to printed backing panels; 2 packs confirmed sufficient coverage |
| Micro LEDs | — | 4–5 | One per pendant; canopy glue into 1.5mm hole |
| Chimney | — | 1 | Commercial casting; position over TF-wall stoves (passenger side); through roof/ceiling hole |
| Flue pipes | — | 2 | Brass rod ~1.5mm dia; waiting room + ticket office stoves; through ceiling holes |
| Operator chair | — | 1 | Commercial HO detail; placed after building in final layout position |

### Materials

- Clear styrene sheet — glazing, cut to window openings, applied from inside
- Embossed styrene — exterior wall cladding (brick or board & batten per room)
- Plain styrene strip — ridge cap, hip corner caps
- Canopy glue — LED mounting in pendants, #8147 rafter tails
- Plastic cement — all other joints

---

## Key Dimensions

| Dimension | Value |
|-----------|-------|
| Building (HO) | 116.6mm L × 40.0mm W (SK site limit; standard 52.6mm W) |
| Wall height | 36.8mm (10'6" prototype) |
| Wall thickness | 2.0mm |
| Wainscot height (cap rail) | 9.65mm |
| Window sill height | 9.65mm |
| Window top | 29.70mm (aligns with #8033 door top) |
| Eave overhang — passenger + siding faces | 24mm (#8147 long rafter tails) |
| Eave overhang — gable ends | 11mm (#8147 short rafter tails) |
| Roof pitch | 5:12 (~22°) |
| Rafter tail spacing | 14mm |
| Floor plank pitch | 2.0mm |
| Wainscot groove pitch | 1.2mm |
| Wall channel (ceiling) | 2.2mm W × 1.5mm D |
| Ceiling grid cell pitch | 4mm (test); 3mm (baseline confirmed) — select after test print evaluation |
| Pendant cone | R=2.0mm rim → R=1.25mm top, H=2.5mm; 1.2mm LED hole |
| Wire holes (ceiling) | 2.0mm dia at WT and TF partition X, Y=3mm (siding end) |
| Ticket wicket opening | 7×7mm, sill Z=13.1mm (3'9"), passenger side of door |
| Partition wall chamfer | 1mm 45° on non-office face, at passenger wall end |

---

## Assembly Sequence

### Phase 1 — Permanent base (glue all joints)

1. **Floor piece** — Place on platform slot. Route main wire lead down through floor feed hole before setting.
2. **Exterior walls** — Set each panel base into rabbet ledge on floor top edge. Miter-glue all four corners. Check square before glue sets.
3. **Interior glazing** — Cut clear styrene to each window opening. Apply from inside with small drops of plastic cement at corners.
4. **Exterior cladding** — Cut and apply embossed styrene sheets to exterior wall faces.

### Phase 2 — Pendant fixtures (before ceiling, while access is easy)

5. **Pending lights** — Glue pendant fixture to ceiling piece underside face-up on workbench. Thread micro LED into 1.5mm hole from above; secure with canopy glue. Let cure fully before handling.
   - Waiting room: 2 pendants, spaced evenly along centerline
   - Ticket office: 1 pendant, centered over desk area
   - Freight room: 1–2 pendants near center

### Phase 3 — Lift-off roof assembly (build separately, drop onto walls)

6. **Roof backing panels** — Drop panel tabs into ceiling top face channels (no glue — friction fit for lift-off). Long trapezoidal panels first, then hip-end triangular panels. Beveled edges meet at hip lines.
8. **#8135 slate shingle strips** — 5.5mm wide, overlapping (~3–3.5mm exposure per row; ~12–14 rows per long panel). Start at eave with first row overhanging edge slightly. Work upward; trim strip ends at beveled hip edges. Let each row tack before continuing.
9. **Hip corner + ridge caps** — Plain styrene strip, glue over joints at hip lines and ridge.
11. **Chimney** — Insert from above through roof hole; cement in place.
12. **Flue pipes** — Insert from above, through ceiling holes, down to stove stub positions.

### Phase 4 — Final fitting

13. **Set lift-off assembly on building** — wall channel drops over wall tops (friction fit, no glue). Thread LED wires from ceiling void down to main wire lead with enough slack for full roof lift clearance.
14. **#8147 rafter tails** — Apply short pieces to soffit face at 14mm tick marks using canopy glue. Work one face at a time; hold with tweezers until tack sets.
15. **Commercial doors and windows** — Press Tichy castings into wall openings. Cement from inside.
16. **Operator chair and fine details** — Place after building is in final layout position.

---

## Wire Routing

```
Pendant LED (each room)
  │  wire up through ceiling hole (2mm dia)
  │
Ceiling void (wire slack loop coiled here for lift clearance)
  │
Interior wall top channel notch (1.5×1.5mm, siding end)
  │
Floor wire feed hole (4–5mm dia, near building center)
  │
Platform chase → layout wiring below
```

All wires run from pendant through ceiling, along the wall channel notch (sealed by exterior wall), and down through the floor. One main connection point below floor level.

---

## Notes

- **Cap rail at interior doors (#8032):** Wall opening = 10.30mm (door leaf). Additional 11.75mm wide × 1.5mm tall notch on each wall face at cap rail height to clear door frame flanges.
- **Eave soffit:** Flat face — do not fill tick marks before #8147 installation. Tick marks are guides only.
- **Lift-off clearance:** Test lift height before cementing chimney to roof. Ensure all wire leads have adequate slack.
- **Styrene panels:** Apply #8135 shingle sheets with grain running down slope (not across). Overlap rows per sheet instructions.
- **#8204 eave supports:** Reserved for HC station only — do not use here.
- **Rafter tails:** Long (#8147, 24mm) for passenger and siding face soffits. Short (#8147, 10.6mm) for gable end soffits. Canopy glue at 14mm tick marks.
- **Passenger wall + floor assembly lead-in:** Partition wall tongues have 0.5mm 45° chamfers on non-office face tip (tongue-only, no room intrusion). Passenger wall dadoes have matching 0.5mm 45° chamfers inside the dado channel at the non-office wall (FT left wall X=48.4, TW right wall X=88.0). Both are hidden inside the dado/tongue interface when assembled.
- **Ceiling pendant wire routing:** LED wire exits through 1.2mm LED hole upward, loops in ceiling void, exits through 2mm wire hole at ceiling edge. Pendant is integral to the ceiling print — install LED before fitting ceiling to walls.

---

## Open Items (before production prints)

| Item | Script | Description |
|------|--------|-------------|
| Ceiling grid — bay taper clip | `generate_sk_ceiling_full.py` | ✅ Verified correct. X-lines narrow per-Y in bay zone; Y-lines taper to bay wall boundary. Gable eave tick marks: 4 per end (Y=0/14/28/40mm). |
| Floor piece extras | `generate_sk_floor_basic.py` | ✅ STL ready (`SK_FloorBasic.stl`). Notice board relief both faces both walls; bay counter (54"×30"); INTERIOR_DETAILS=True: waiting benches ×2 (gable wall, Y-centred), stoves back-to-back on TF wall (ticket+freight share chimney), waiting stove on WT wall; ticket office desk+clutter, filing cabs ×2, waste bucket, pigeon hole shelf; freight crates, barrels, bags, standup desk by notice board. Floor guard tiles under all stoves. OCCT fix: side bay window cutter inner-bottom vertex clipped to BAY_Y0+0.2 to avoid degenerate boolean on complex shape. |
| Roof panel — long side | `generate_sk_roof_panels.py` | ✅ STL ready (`SK_RoofPanel_Long.stl`). Trapezoidal ×2 (print ×2, flip one 180° for passenger side — ridge tabs interlock). PANEL_T=2mm; eave rib = right-triangle wedge (thin at eave, full RIB_H=4mm at ridge side, hypotenuse at 5:12 pitch — mates flush with ceiling top); 1 flat rib at ~35mm from eave (above hip interference zone); ridge half-lap joints (TAB_H=1mm tabs at 0–25%/50–75%, matching recesses at 25–50%/75–100%); 1×1mm rabbet ledge on both hip edges. Print outer face down, no supports, 0.1–0.15mm layer height. |
| Roof panel — hip end | `generate_sk_roof_panels.py` | ✅ STL ready (`SK_RoofPanel_Hip.stl`). Triangular ×2 (identical). PANEL_T=2mm; eave rib = right-triangle wedge only (no flat ribs). Outer face registers against long panel rabbet ledge; styrene strip cap finishes hip corner. Print outer face down, no supports. |
| Platform | `generate_sk_platform.py` | ✅ STL ready. Two variants — set `PLATFORM_VARIANT` at top of script. **Freight** (`SK_Platform.stl`): 126×88×17mm, 18mm finished surface (NMRA Classic E=14mm; Old-Time=10mm). **Passenger** (`SK_Platform_Passenger.stl`): 126×88×9mm, 10mm finished surface (E=6mm). Both: open-bottom shell, 2mm walls + 2mm top slab, print top face down. Exterior faces: horizontal plank grooves (12" boards + 6" footer course + plain at grade) + vertical post grooves at ~12ft spacing (long sides X=42/84mm, short ends Y=44mm). Wire holes: 2mm dia through top slab at platform X=53.1 and X=92.7, Y=29mm (aligns with partition wall siding exits). JST-XH 2P connector boss: horizontal channel 8.8×9.3×8.8mm fused to inner top slab face; body slot 5.8×5.8×7.8mm along Y, lips 1.5mm × 2 retain connector (2.8mm drop-out gap); open collar/wire entry at Y=28mm, 5.8×5.8mm mating opening at Y=35.8mm. Freight: boss fully inside void (6.2mm clearance). Passenger: boss protrudes 1.8mm below open bottom — requires layout access hole. Building positioned by styrene sheet cut to building outline. |

## Remaining Prints

All SK prints are complete. No further scripts required.

## External / Commercial Parts (not printed)

| Part | Source | Notes |
|------|--------|-------|
| Chimney | Commercial casting | Position over TF-wall stoves (passenger side); through roof and ceiling hole |
| Flue pipes | Brass rod ~1.5mm dia | 2 required; waiting room + ticket office stoves; through ceiling holes |
| Operator chair | Commercial HO figure/detail | Placed after building in final layout position |

---

*Updated: 2026-04-27 | All SK prints complete. Chimney/flues/chair: external parts. Hip corner blocks not needed — single-piece ceiling covers corners. Next: ISO views; GitHub publish*
