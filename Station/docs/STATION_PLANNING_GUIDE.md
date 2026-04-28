# Station Model — Planning Guide for Full Detail Print

NY&E Layout | Prototype: New Haven standard combination station (Fig. 172)
Basis for a freelanced C&O-prototype variation, circa 1905.

This guide is a starting checklist for the session where we build the detailed,
printable station model. Work through each section before starting CAD work.

---

## Background Decisions (already made)

These are settled — record them here so we don't re-debate them.

- **Standard structure with site variations:** The NH Fig. 172 plan is the standard.
  6–7 stations on the layout; at least one will use the standard form as-is.
  Known variation types to plan for:
    - Half-size freight room (shorter building)
    - Freight room with end doors instead of side doors
  Design the CAD model parametrically so variations can be generated from the same script.

- **Single-level platform all around the building.** No height difference between
  freight and passenger platform faces. This also means the interior can be a
  single floor level — simplifies both CAD and interior detailing.

- **Multi-piece print.** Walls, roof, platform, interior structure are separate prints.

- **Exterior walls: embossed styrene sheet, not 3D printed.**
  Print walls face-down to provide a clean interior surface and structural detail.
  The exterior surface will be covered with embossed styrene (brick, board & batten, etc.).
  This means: no exterior texture needed on printed walls — just correct geometry.

- **Commercial doors and windows: Tichy.**
  Print openings to accept Tichy castings — not frames, not glazing.
  **Action required:** locate Tichy inventory and confirm exact opening dimensions
  before finalizing wall CAD. (Window and door sizes will drive opening dimensions.)

- **Platform: reuse/adapt StationPlatform FreeCAD project.**
  `CADtrains/StationPlatform/` is already parametric via spreadsheet.
  Platform surface: either 3D printed with embossed plank lines, or covered with
  embossed styrene sheet — decide at build time.

- **Interior detail:** 3D print for larger structural elements (subfloor, benches,
  wainscoting); commercial detail parts for smaller items. Further definition as work progresses.

---

## 1. Verify Planning Token Dimensions

Print the planning token first and confirm fit on the layout before committing
to the detail model dimensions.

### SK (Stans Knob) token — sent to print 2026-04-14

Token includes all confirmed openings at measured Tichy dimensions:
- Siding face: waiting door (#8033), ticket window (#8028/69), freight door (#8038)
- Passenger face: waiting door (#8033), freight door (#8038)
- Gable ends: single window (#8028/69) each
- Interior walls: waiting/ticket door + ticket wicket notch (#8032); ticket/freight door (#8032)
- Operator bay rectangular protrusion on ticket office passenger face

- [ ] Does 116.6mm building length feel right in the site envelope?
- [ ] Does 80.6mm total platform depth fit within the arc constraint at the site? (81.9mm limit)
- [ ] Does building orientation B (waiting left/JC, freight right/HC) look correct?
- [ ] Any dimension changes needed before detail model?

### Standard token — pending update

Standard token (generate_stationplantoken.py) still uses old nominal opening dimensions
and does not yet have the operator bay. Update before printing for standard stations.

- [ ] Add operator bay to Building_A and Building_B
- [ ] Update opening dimensions to measured Tichy values
- [ ] Split Platform into Platform_A / Platform_B (bay notch position differs per orientation)
- [ ] Standard checklist items (189mm length, 52.6mm depth, 28mm passenger platform, etc.)

---

## 2. Tichy Door and Window Dimensions

**Must resolve before wall CAD work begins.**

Parts are in InvenTree under **Model Railroad / Structure Detail Parts** (pks 81–88 + new entries for station-specific parts).

### Opening layout decisions (confirmed 2026-04-14)

Track-side and non-track-side faces of each room are mirror images of each other.

| Room | Face | Standard | SK |
|------|------|----------|----|
| Freight room | siding + passenger | 1 freight door (#8038) + 1 window (#8028/69, between door and office wall) | 1 freight door (#8125, 23.90×32.65mm) only |
| Ticket office | siding | 1 window (#8028/69) | same |
| Ticket office | passenger | operator bay protrusion (no wall opening) | same |
| Waiting room | siding + passenger | 1 door (#8033) + 1 window (#8028/69, beside door) | 1 door (#8033) only |
| Gable ends | left + right | double window #8070 | double window #8070 (confirmed 2026-04-17) |
| Interior: waiting/ticket | — | door (#8032) + ticket wicket notch (~5mm) | same |
| Interior: ticket/freight | — | door (#8032) | same |

### Part assignments and measured CAD opening dimensions

All parts from #8091 sampler pack. Catalog insert scanned: `CADtrains/docs/Tichy #8091 list.pdf`.
InvenTree: Model Railroad / Structure Detail Parts, pks 96–102.

| Part | Opening (W × H) | Description | Notes |
|------|----------------|-------------|-------|
| #8028 / #8069 | **9.38 × 19.85mm** | 4/4 Double-Hung Window | Interchangeable; #8069 open sash |
| #8070 | **19.00 × 19.85mm** | Double Unit Window (2×#8028/69) | Standard gable ends |
| #8032 | **10.30 × 24.45mm** | 4-Panel Interior Door | Interior room connections |
| #8033 | **9.55 × 29.70mm** | 4-Lite Door & Transom | External waiting room doors |
| #8038 | **30.38 × 34.80mm** | Baggage/Freight Sliding Door | Freight room exterior (current SK assignment — see notes) |
| #8024 | **11.70 × 19.80mm** | 6/6 Double-Hung Window, 36"W × 64"H | Bay center window only; in #8091 assortment |
| #8066 | measure on arrival | Loading Dock Door | Ordered Qty 4 — may replace/supplement freight room door |
| #8053 | measure on arrival | Baggage Door | Ordered Qty 4 — may replace/supplement freight room door |
| #8125 | **23.90 × 32.65mm** | Freight Door/Transom | 6.5mm narrower + 2.2mm shorter than #8038; SK half-size freight room candidate |

Measured: #8028/69, #8070, #8032, #8033, #8038, #8024, #8125 ✅ | Ordered, pending measurement: #8066, #8053

**Freight door note:** #8125 measured (23.90×32.65mm) — 6.5mm narrower and 2.2mm shorter than #8038.
SK half-size freight room: compare C (#8038) and D (#8125) test sections to select one.
Standard freight room: #8038 remains the assignment.
Still to measure on arrival: #8066 and #8053 — may be additional alternatives.

### Pre-wall-CAD checklist

- [x] All Tichy opening dimensions measured (incl. #8024 bay center window: 11.70 × 19.80mm)
- [x] Gable end window part confirmed (#8070 standard, #8028/69 SK)
- [x] Interior door parts confirmed (#8032 both interior walls)
- [x] Opening layout per face confirmed (table above)
- [x] **#8125 measured** (23.90×32.65mm) — SK half-size freight room candidate; test section D vs C
- [ ] **Measure #8066, #8053 on arrival** — compare to #8038/#8125; may be additional candidates
- [ ] Count pieces of each part in the physical #8091 sprue; update InvenTree stock for #8064, #8032, #8033, #8070.

---

## 3. Overall Build Strategy

### Piece breakdown (confirmed 2026-04-14)

| Piece | Count | Print orientation | Notes |
|-------|-------|------------------|-------|
| Exterior wall panels | 4 | Face-down (exterior on plate) | Siding face, passenger face (with bay gap), left gable, right gable |
| Floor + interior | 1 | Floor face-down | Integral: interior walls, bay walls, benches, wainscoting, desk, sub-floor ledge |
| Chair (operator) | 1 | — | Separate small print; placed at bay desk |
| Roof (main hip) | 1 | — | Separate; may cover with embossed styrene or paint shingles |
| Canopy (passenger platform) | 1 | — | Shed roof separate from main roof |
| Chimney | 1 | — | Small separate print |

- **45° mitered joints** on all mating edges: wall-to-wall corners, wall-to-floor, and bay side wall edges to passenger wall panel edge. Consistent miter angle parameter (`MITER = 45`) in script.
- **Glazing:** clear styrene sheet cut to window openings, applied from inside during final assembly.
- **Embossed styrene:** applied to exterior faces of the 4 main wall panels. Bay exterior below windows is small enough to paint directly.

- [x] **Parametric script:** Script generates standard + SK variants from shared parameters.
      Key parameters: FREIGHT_W, TICKET_W, WAITING_W, BLDG_D, WALL_H, WALL_T, MITER, door/window positions.

- [x] **Printing orientation:** Walls print face-down (exterior on build plate) for clean geometry and styrene adhesion.

- [ ] **Material:** PETG recommended for wall panels (durable, slight flex).
      Roof: PETG or PLA — less handling stress.

### Interior detail philosophy (confirmed)

Visible through windows at viewing distance — aim for *suggestion of objects*, not precision detail.
Correct silhouette + appropriate paint colors completes the illusion.
- Waiting room: benches along walls (printed), stove suggestion
- Ticket office: desk fitting bay footprint, lamp post shape, telegraph key block, book shapes — all integral to floor piece; separate chair
- Freight room: bare floor, sub-floor ledge, possibly a baggage cart suggestion

---

## 4. Operator Bay

The ticket office bay window is the key identifying feature of this station type.
It projects toward the track (passenger) side from the ticket office section.

- [x] Confirm bay prototype dimensions from Fig. 172 elevation.
      **Confirmed:** 6'0" wide × 2'6" projection (measured from SmallStation.png).
      HO: 21mm wide × 8.75mm projection.
      Standard platform clearance past bay: 8'0" − 2'6" = 5'6" — adequate for baggage carts.
- [x] Bay walls are part of the floor piece (Option 2 build strategy).
      Bay side wall edges and passenger wall panel edge meet at 45° miter.
      Exterior bay surfaces below windows: painted directly (too small for embossed styrene).
- [x] Three-sided polygonal profile, 45° side panels, bay opening = full ticket office width.
      **SK bay dimensions (confirmed):** opening = TICKET_W_SK = 35.6mm wide x 8.75mm projection.
      Side panel face: 12.37mm (window margin 1.5mm each side).
      Front panel face: 18.1mm (window margin 4.4mm each side).
      All three faces carry standard #8028/#8069 window opening (9.38mm).
- [ ] Bay roof: extend bay walls to full eave height — same ceiling height as office.
      No separate bay roof; main eave continues over bay.
- [x] Bay desk: integral to floor piece, spans bay interior.
      Printed-in suggestive details: telegraph key block, book shapes, lamp post. Chair: separate print.
- [ ] **Bay windows (confirmed):**
      Side panels ×2: #8028 or #8069 (9.38mm opening — same as building standard windows).
      Center/front panel ×1: **#8024, 6/6 Double-Hung, 36"W × 64"H prototype** (~10.51mm nominal HO).
        Height diff vs #8028/69: only 2 scale inches — negligible. Wider pane pattern reads as feature window.
      Measured opening: **11.70 × 19.80mm**. In #8091 assortment ✅
      Bay test print center opening is sized for #8028/69 (placeholder — update after measuring #8024).
- [ ] **Bay test print pending** — `BayTest_Connected.stl`: one connected L-center-R piece.
      Confirm side panel window fit and overall proportion before finalizing script.

---

## 5. Roof, Ceiling, and Eaves

### Strategy (confirmed 2026-04-14, updated 2026-04-17)
- **Ceiling+eave combined piece** (3): one per room, ceiling and eave soffit printed as a single piece.
  - Ceiling face: 3mm pressed tin grid, printed face-down.
  - Soffit face: flat (no printed rafter stubs) — Tichy #8147 short pieces glued on with 14mm spacing.
  - 7mm-spaced tick marks on soffit face as placement guides for #8147.
  - Wall interface: 2.2mm wide × 1.5mm deep channel on underside drops over wall top (0.2mm clearance on 2mm wall). Snug friction fit — no glue — allows lift-off.
  - 4 small triangular hip corner blocks (separate prints) fill eave miter at building corners.
- **Roof backing panels** (4 printed): replace separate scaffolding + cut styrene approach.
  - 2 trapezoidal (long sides, ~189mm) + 2 triangular (hip ends, ~52.6mm base).
  - Each panel: 1.5–2mm wedge printed at 5:12 pitch; hip edges beveled at 45° plan angle.
  - Tabs on panel bottom drop into channels on ceiling top face — same locating system.
  - #8135 strips: 5.5mm wide, installed overlapping (~3–3.5mm effective exposure); ~12–14 rows per long panel.
  - First row overhangs eave edge slightly. Strips trimmed at beveled hip edges.
- **Lift-off roof assembly**: ceiling panels + corner blocks + scaffolding + styrene panels lift off as one unit to access interior. Wire length planned to allow lift without disconnecting.
- **Roof surface**: Tichy #8135 Slate Shingles are individual rows/strips (not solid sheet). Applied row by row to printed backing panels.
  - Coverage: 36 sq in per pack; 2 packs covers full hip roof with margin.
  - **Printed backing panels** (4): trapezoid long sides × 2, triangular hip ends × 2. Printed at pitch angle — no cutting jigs needed.
  - Each panel: 1.5–2mm thick wedge; bottom edge rests on eave top; hip edges beveled at 45° plan angle.
  - Panels connect to ceiling+eave top face via tab/channel (same system as scaffolding).
  - Ridge cap and hip corner caps from plain styrene strip.
  - **Jigs cancelled:** pitch cutting jig and styrene panel templates no longer needed.
  - Hip miter guide: TBD — may be replaced by raised guide edge printed on backing panel bevels.
  - **Standard construction for all stations.** After SK, assess #8135 supply and either reorder or substitute an equivalent overlapping strip shingle product. Printed backing panels are product-agnostic.
- **Canopy** (passenger platform): separate soffit panel + brackets. Deferred.

### Confirmed from SmallStation.png (2026-04-14)
- **Roof pitch:** ~5:12 (≈22°) estimated from elevation proportions. Working value for jig/brace design; eave piece top edge is the definitive physical reference.
- **Eave overhang depth:** ~3–4 prototype feet = 10–14mm HO. Confirm precise value before scripting eave pieces.
- **Chimney:** confirmed above waiting/ticket wall, slightly toward waiting room side.
- **Bay:** angled side panels confirmed at 45°.

### Resolved (2026-04-15 — parts ordered)
- [x] **Roof surface material:** **Tichy #8135 Slate Shingles** (Qty 2 ordered). Replaces plain embossed styrene; apply sheets to eave+brace structure as planned.

### Tichy parts measured (2026-04-17)
- **#8147 Rafter Tails** ✅ — Short: 10.6mm L × 1.8mm H × 0.8mm W. Long: 23.4mm L. Short fits eave test print. **Use #8147 short for all stations.** Printed rafter stubs omitted from eave CAD; tick marks at 14mm spacing on soffit face instead.
- **#8204 Station Eave Supports** ✅ — 24.8mm at eave / 30.4mm at wall / 37.8mm corner. **Reserved for HC (fancier station).** Not used on SK or standard stations.

Note: **#8092 Turned Porch Post** (Qty 2) is reserved for the SK hotel building project, not the station.

### Confirmed (2026-04-17)
- **Ceiling surface:** 3mm pressed tin grid ✅ (larger cells read better viewed through windows)
- **Eave overhang:** 12mm working value confirmed by test print ✅
- **Rafter tail spacing:** 14mm (prototype ~4', simplified for model) ✅
- **Exterior wall attachment to floor:** rabbet/ledge on floor piece top edge, wall panel base sits into it ✅

### Still to confirm
- [ ] **Canopy post style** — 3D printed posts, brass rod, or commercial casting? (Decide at canopy detail stage.)
- [ ] **Bay roof** — small shed below main eaves, or main eaves continue over bay? (Previous guidance: extend to eave height)

### Chimney (confirmed)
- Single chimney above the waiting/ticket interior wall (confirmed from Fig. 172).
- Waiting room stove and office stove both flue to this chimney (one pipe each side of partition).
- Flue pipes: ~1.5mm dia — separate small prints or brass rod through hole in ceiling panel.
- Chimney: separate printed piece, mounts from above through roof/ceiling.

### Printed roof parts (confirmed approach 2026-04-14)

**Structural:**
| Part | Qty | Notes |
|------|-----|-------|
| Ceiling+eave combined | 3 | Per room; 3mm pressed tin grid face; flat soffit with 14mm tick marks; 2.2×1.5mm wall channel; wire holes |
| Hip corner eave blocks | 4 | Triangular; fill eave miter at building corners; glue to adjacent ceiling+eave pieces |
| Roof backing panel — long side | 2 | Trapezoidal wedge 1.5–2mm; 5:12 pitch; 189mm × ~41mm slope; hip edges beveled 45°; tabs into ceiling channel |
| Roof backing panel — hip end | 2 | Triangular wedge 1.5–2mm; 5:12 pitch; ~52.6mm base; miter edges beveled 45° |
| Ceiling light pendants | 4–5 | Kerosene-style cone; 4mm rim / 2.5mm top / 2.5mm tall; short stem; 1.5mm LED hole |

**Jigs/templates (construction aids — not visible in finished model):**
| Part | Qty | Notes |
|------|-----|-------|
| Pitch cutting jig | 1 | Block with pitch-angle face for guiding knife cuts on styrene |
| Hip miter guide | 1 | Guide for 45° hip corner cuts on styrene panels |
| Styrene panel templates | 4 | Trace-and-cut outlines: 2× trapezoid (long sides) + 2× triangle (end hips) |

**Roof surface:** Tichy **#8135 Slate Shingles** sheets, cut from templates using jigs, resting on eave top edge and glued to internal braces. Eave brackets (#8204) and rafter tails (#8147) to be evaluated on arrival for station use.

### Wire routing for lighting (updated 2026-04-17)
- **Ceiling panel holes:** 2 × ~2mm dia per panel near interior wall edges; wires exit upward into roof void
- **Wall wire channel:** 1.5×1.5mm corner notch at siding end of each interior wall, sealed by exterior wall when assembled
- **Optional wall chase:** notch top inside edge of wall panel to run wire between rooms
- **Floor feed hole:** 4–5mm hole through floor piece near building center → down into platform → layout wiring below
- **Lift-off clearance:** wire length planned to allow roof assembly to lift without disconnecting (slack loop in roof void)
- LED fixtures: pendant lights (kerosene cone style) — LED sits in 1.5mm hole in top of pendant, canopy glue secures; wire runs up through ceiling hole

### Assembly sequence (updated 2026-04-17)
**Permanent (glued):**
1. Floor piece → platform slot
2. 4 exterior wall panels → rabbet into floor ledge, miter-glue corners
3. Pendant light fixtures → glue to ceiling piece underside; thread LED wires through holes
4. Hip corner eave blocks → glue to ceiling+eave piece corners

**Lift-off assembly (no glue at wall interface):**
5. Ceiling+eave pieces (3) → drop wall channel over wall tops; route wires up through ceiling holes
6. Roof scaffolding → tabs into ceiling top channels; wire slack loop coiled in roof void
7. Ridge block + hip gussets → glue into scaffolding
8. 4 embossed styrene hip panels → cut from templates using pitch/miter jigs, glue onto scaffolding
9. Hip corner + ridge caps → plain styrene strip
10. Chimney → insert from above through roof/ceiling
11. Flue pipes → through ceiling holes into stove stubs
12. #8147 rafter tail short pieces → canopy glue at 14mm tick marks on soffit face

---

## 6. Platform and Foundation

- [ ] **Review StationPlatform project** (`CADtrains/StationPlatform/`) at session start.
      Confirm what the existing parametric model covers and whether it can be
      adapted directly or needs a new derived version for this station.
- [ ] **Single-level platform all around** — set platform height consistently on all four sides.
      Determine platform height above rail (prototype standard ~3'6" passenger platform).
      HO: ~12.5mm above tie top. Confirm against track/roadbed plan.
- [ ] **Platform surface:** printed planking texture, or smooth for embossed styrene?
- [ ] **Platform edge detail:** edge board (raised lip), or flush?
- [ ] **Canopy posts:** style TBD — 3D printed, brass rod, or commercial casting. Decide at canopy detail stage.

---

## 7. Interior Detail (confirmed approach 2026-04-14)

**Philosophy:** Suggestive shapes + paint at viewing distance. Correct silhouette and paint color = illusion complete. Not calibrated for close-up photography.

**What prints where:**
- Wall panel faces: integral raised relief for notices, timetable boards, clock discs (~2mm dia)
- Floor piece: all furniture and floor detail printed integral; items too fine printed separately

### Wood plank floor
Parallel grooves 0.3mm deep. Oriented along building length (X-axis) as typical for the period.

**Pitch confirmed (2026-04-16 tile test):**
- **Floor planks: 2.0mm pitch** (~6.9" prototype) — reads well under layout lighting
- **Wall wainscoting: 1.5mm pitch** (~5.1" prototype) — finer texture, suitable for wall boards below cap rail

### Room-by-room detail list

| Item | Room | Method | Notes |
|------|------|--------|-------|
| Wood plank floor | All | Integral grooves in floor piece | |
| Wainscot rail | All | Low raised band on wall face (integral to wall panel) | ~1/3 wall height |
| Wall clock | All | 2mm raised disc on wall panel | Prominent position — stations were time-critical |
| Wall notices / schedule boards | All | Thin raised rectangles on wall panel | Paint white, black dot "text" |
| Benches ×2 | Waiting | Integral to floor | Simple slab with leg stubs |
| Potbelly stove | Waiting | Integral to floor | Near waiting/ticket wall; flue stub rising |
| Water cooler | Waiting | Integral to floor | Small cylinder on stand near door |
| Potbelly stove | Office | Integral to floor | Corner near ticket/freight wall; flue stub |
| Bay desk | Office | Integral to floor | Telegraph key block, books, lamp post |
| Second desk + chair | Office | Integral (desk) + separate (chair) | Non-bay area, against siding wall |
| Filing cabinets ×2 | Office | Integral to floor | Against siding or end wall; ~4×3×7mm each |
| Pigeonhole rack | Office | Integral to wall panel face | ~3×4 cells, beside ticket window, wall-mounted |
| Safe | Office | Integral to floor | Corner behind bay desk |
| Freight scale | Freight | Integral to floor | Large flat-bed; ~15×8mm base |
| Hand truck | Freight | Separate small print | L-profile, leans against wall |
| Freight desk | Freight | Integral to floor | Against ticket/freight wall for waybills |
| Crates/boxes | Freight | Integral to floor | Varied rectangular blocks; stack against wall |
| Barrels ×2 | Freight | Integral to floor | Short cylinders ~4–5mm dia |
| Trunks/suitcases | Freight | Integral to floor | Low rectangles near freight door |
| Mail sacks | Freight | Integral to floor | Rounded lumps near freight door |

### Stoves and flues
- Both stoves (waiting room and office) against the waiting/ticket interior wall — one each side.
- Flue pipes (~1.5mm dia): separate small prints or brass rod, pass through ceiling panel hole.
- Single chimney mounts from above through roof/ceiling.

### Figures
- Deferred — add commercial HO figures at final detail stage as desired.

---

## 8. Reference Material

Have the following ready at session start:

- `Projects/Trains/SmallStation.png` — Fig. 172 plan and elevation (primary reference)
- `/home/abyrne/Downloads/Books/Trains/` — period PDFs (Passenger Terminals book
  may have additional NH station detail drawings)
- Planning token physical print + any dimension notes from test fit
- Tichy door/window inventory with opening dimensions
- `CADtrains/StationPlatform/freecad/` — existing parametric platform model
- FreeCAD MCP bridge running (`localhost:9875`)
- MCP reference: `/home/abyrne/Projects/.claude/GENERATED_MCP_REFERENCE.md`

---

## 9. Suggested Session Sequence

### Completed
1. ✅ Resolve Tichy opening dimensions
2. ✅ Confirm opening layout per face (standard and SK)
3. ✅ SK planning token printed with all openings and interior walls

### Completed this session (2026-04-14)
4. ✅ SK token field-tested — windows and doors fit, print confirmed good
5. ✅ Build strategy confirmed: 4 wall panels + floor piece + ceiling/eave + jigs + styrene roof
6. ✅ Full interior detail inventory confirmed (see Section 7)
7. ✅ Roof/ceiling/eave approach confirmed: printed ceilings + eaves, #8135 slate shingles
8. ✅ Bay dimensions confirmed: full office width (35.6mm SK), 45°, all three faces get windows
9. ✅ SK/HC resort context captured: hotel across tracks, staff station, siding = hotel deliveries

### Test prints generated (2026-04-15) — in print queue
10. ✅ `Bay3DTest.stl` — 3D bay with actual 45° walls; all three windows (#8028/69 sides, #8024 front); upright with base plate
11. ✅ `WallSectionTest.stl` — 50mm wall section, 10'6" working height, #8028/69 window, 45° miter end, wainscot cap rail + notice board + clock disc
12. ✅ `PlankTileTest.stl` — two-zone groove tile: 1.5mm pitch (5.1" prototype) vs 2.0mm pitch (6.9" prototype)
    - Note: `BayTest_Connected.stl` (flat) superseded by Bay3DTest for window fit evaluation

### Test prints 2 (2026-04-16) — in print queue
13b. `WallTest2_A_Window.stl` — 50mm section, #8028/69 window (WIN_H 20.05mm), miter right, wainscot/clock(r=1.5mm)/notice
13c. `WallTest2_B_Door.stl` — 50mm section, #8033 door (9.55×29.70mm), miter left; hold A+B at 90° to test joint
13d. `WallTest2_C_FreightDoor8038.stl` — 50mm section, #8038 freight door (30.38×34.80mm), no miter
13e. `WallTest2_D_FreightDoor8125.stl` — 50mm section, #8125 freight door (23.90×32.65mm), no miter; SK-only comparison
     Script: `CADtrains/Station/scripts/generate_wall_section_test2.py`

### Completed (2026-04-16 / 2026-04-17)
13. ✅ Test print results confirmed:
    - **Bay 3D** — #8024 front window fits. #8028/69 side windows fit.
    - **Wall section v1** — miter joint flush. Cap rail fix (Z_CUT=2.8mm) confirmed needed.
      WIN_H +0.2mm (19.85→20.05mm) confirmed correct. Clock disc workable at r=1.5mm.
    - **Plank tile** — both pitches read well: 2.0mm for floor, 1.5mm for wall wainscoting.
    - **Wall section v2 (A+B miter joint)** — closes flush, cap rail included. ✅
    - **Wall section v2 B (#8033 door)** — fits at floor level. ✅
    - **Wall section v2 C vs D** — **#8125 selected** for SK freight room (better proportion). ✅
    - **Clock disc r=1.5mm** — workable for tick marks. ✅
14. ✅ SK freight door confirmed: **#8125** (23.90×32.65mm). Standard stations retain #8038.
15. ✅ Gable end windows confirmed: **#8070 double window for all stations including SK.**
    Script updated; SK token STLs regenerated.
### Test prints 3 (2026-04-17) — sent to print; partial results confirmed same session
16a. `WallTest3_Window.stl` — Script: `generate_wall_section_test3.py`
16b. `OfficeInteriorTest2.stl` — Script: `generate_office_interior_test2.py`
16c. `CeilingTileTest.stl` — **3mm cells selected** ✅ Script: `generate_ceiling_tile_test.py`
16d. `EaveTest.stl` — **12mm overhang confirmed; #8147 short fits** ✅ Script: `generate_eave_test.py`

### Confirmed from test prints 3 and parts measurement (2026-04-17)
- #8032 interior door: wall opening stays at 10.30mm; add separate 11.75mm wide × CAP_H notch at cap rail zone on each face to clear door frame. DOOR_H +0.2mm tolerance (24.45→24.65mm).
- #8147 short rafter tails fit soffit; omit printed stubs, use tick marks at 14mm pitch. ✅
- #8204 eave supports reserved for HC. ✅
- Ceiling: 3mm pressed tin grid confirmed. ✅
- Eave overhang: 12mm confirmed. ✅
- Ceiling+eave as one combined piece per room. ✅
- Lift-off roof assembly (ceiling+eave+scaffolding+roof panels). ✅
- Exterior wall attachment: rabbet/ledge on floor piece top edge. ✅
- Ceiling light fixtures: kerosene-style pendant cone (4mm rim / 2.5mm top / 2.5mm H) with stem and 1.5mm LED hole. ✅

### Test prints 4 — evaluated ✅
17a. `CeilingEaveTest.stl` — **channel fits on 2mm wall ✅. Pendants look good ✅. Tin grid ✅.**
     Notes: pendants must be over wire holes in production prints. Exterior walls must be same 2mm thickness; embossed styrene fits below ceiling channel interface.
     Pendant fix: STEM_D increased to 2.0mm, LED_HOLE_D reduced to 1.2mm (hole was wider than stem, causing floating geometry).
     Eave flat-top change: uniform thickness confirmed correct — slope carried by roof backing panels.
17b. Standalone `PendantLightTest.stl` — superseded; pendants integrated into ceiling piece.

### Confirmed from test prints 4
- Ceiling+eave channel: 2.2×1.5mm on 2mm wall confirmed fit ✅
- Pendant integrated into ceiling print: confirmed good ✅
- Floor warping (previous session): caused by eave piece rocking on plate, not PLA adhesion ✅
- Interior door height: DOOR_H 24.75mm confirmed fit ✅
- Exterior wall thickness: 2.0mm (same as interior) — embossed styrene applied below ceiling channel line

### Completed (2026-04-18) — SK production scripts
18. ✅ `generate_sk_siding_wall.py` — siding face wall panel: #8033 waiting door, #8028/69 office window, #8125 freight door, partition dadoes, wire grooves at dados, cap rail with 45° miters (outer corner — corrected), wainscot grooves, rabbet, end miters. STL: `SK_SidingWall.stl`.
19. ✅ `generate_sk_passenger_wall.py` — passenger face wall panel: mirrors siding (same doors), full TICKET_W=35.6mm bay opening full height, same interior details. STL: `SK_PassengerWall.stl`.
20. ✅ `generate_sk_gable_wall.py` — both gable end panels (print ×2): #8070 19.00×19.85mm centered, miters both ends, wainscot, rabbet. STL: `SK_GableWall.stl`.
21. ✅ `generate_sk_floor_basic.py` — floor + interior (basic):
    - Floor slab 116.6×52.6×2.0mm + 4 registration tongues (fit wall rabbets)
    - Floor plank grooves 2.0mm pitch
    - Wire notches: 1.5×1.5mm on siding-face tongue at **both** WT and TF partition wall X centres; covered by siding wall when assembled
    - WT + TF partition walls full height: #8032 door (centred in depth, Z=FLOOR_T), cap rail both faces, 45° cap rail miters at door + siding + passenger ends, cap rail notch 11.75mm wide at door, wainscot grooves both faces, clock discs both faces
    - Ticket wicket: 7×7mm through-opening on WT wall, passenger side of door (Y=33.4..40.4mm), sill Z=13.1mm; counter shelf 2mm projection into waiting room
    - Partition wall passenger-end chamfers: **tongue-only** 45° chamfer on non-office face (WT left/waiting, TF right/freight); DADO_D×DADO_D = 0.5mm legs; starts at wall face (Y=py_pass=50.6mm), tapers to 0.5mm at tongue tip (py_tongue=51.1mm) — no room intrusion; office-side extension block (1.41×0.5×WALL_H mm) bridges bay inner filler to partition body
    - Bay inner corner fillers: 1.41mm wide × 1.5mm deep × WALL_H at X=T_CX±HW (within bay opening), Y=51.1..52.6mm
    - Bay integral: trapezoidal floor slab, 45° side panels, front panel; all 3 windows (#8028/69 sides, #8024 front); WIN_SILL=9.65mm
    - STL: `SK_FloorBasic.stl`

**All 5 SK wall/floor pieces sent to test print 2026-04-18.**

### Completed (2026-04-19) — Ceiling ticket office test
22. ✅ `generate_ceiling_ticket_test.py` — ticket office ceiling + eave test piece:
    - Slab: 59.6×100.6×2.5mm (X=17.6..77.2mm, Y=−24..76.6mm); eaves EAVE_SIDE=24mm (#8147 long rafter tails), EAVE_END=11mm (#8147 short)
    - Wall channels: siding wall, WT partition, TF partition, passenger wall — all 2.2mm wide × 1.5mm deep
    - Bay wall channels (corrected): 3 separate parallelogram/rectangle strips over left 45° panel, right 45° panel, front panel tops — **not** a filled trapezoid; bay ceiling interior preserved
    - Grid: **4mm cells** (test value — compare against 3mm confirmed baseline); room Y=2..52.6mm full office width; bay Y=52.6..61.3mm at bay width only (bx0..bx1)
    - Wire holes: 2.0mm dia at WT and TF partition wall X centres, Y=3.0mm (siding end)
    - Pendant light: frustum cone R=2.0→1.25mm H=2.5mm at office centre; 1.2mm dia LED hole through slab
    - STL: `SK_CeilingTicketTest.stl`
    - **Known issue (deferred):** Grid extends slightly outside the bay tapered footprint into the eave zone. X-direction lines in the bay zone (Y>BLDG_D) span full bx0..bx1 width regardless of the bay taper — should narrow at higher Y. Y-direction lines for X within bx0..bx1 extend to by1 even when outside the trapezoidal bay wall boundary (T_CX±HW at back vs T_CX±FHW at front). Fix: clip X-lines to tapered bay width per Y level; clip Y-lines to bay wall boundary per X position. Accept for test print; fix before production ceiling print.

**SK_CeilingTicketTest sent to test print 2026-04-19.** SK_FloorBasic also confirmed ready to print (no changes needed).

### Deferred items (fix before production prints)
- **Ceiling grid outside bay footprint** — see item 22 known issue above. Bay grid overruns the trapezoidal taper zone into eave area. Fix requires per-Y bay width calculation for X-lines and per-X bay boundary limit for Y-lines.
- **SK Y depth = 40mm site constraint** — SK site limits building depth to 40mm HO (vs standard BLDG_D=52.6mm). X length (116.6mm) is correct. Requires BLDG_D redesign in all SK scripts: floor slab, partition wall spans, bay geometry (BAY_PROJ may need adjustment), ceiling slab dimensions, platform depth. Do before production prints — current test prints are at 52.6mm depth. See item 32 below.

### Next session — evaluate test prints, then proceed
23. Evaluate SK_FloorBasic test print fit:
    - [ ] Wall panel miters close flush at corners
    - [ ] Floor tongues seat into wall rabbets (4 sides)
    - [ ] Bay-partition corner: chamfer + fillers provide continuous surface, no snag
    - [ ] Partition wall passenger-end chamfer: assembly lead-in works, no gap/step visible
    - [ ] Bay windows: side #8028/69 and front #8024 fit openings at WIN_SILL=9.65mm
    - [ ] Interior door #8032 fits partition wall openings
    - [ ] Ticket wicket 7×7mm opening correct; counter shelf visible
    - [ ] Wire notches accessible from siding face; siding wall covers when assembled
    - [ ] Any dimensional adjustments needed before adding extras
24. Evaluate SK_CeilingTicketTest print:
    - [ ] Wall channel drops cleanly over 2mm walls (2.2×1.5mm)
    - [ ] Bay wall channels: bay ceiling ceiling solid, channel strips only over panel tops
    - [ ] 4mm grid cells vs 3mm — compare against earlier CeilingEaveTest; select pitch for production
    - [ ] Pendant cone proportion and LED hole usable
    - [ ] Wire holes accessible (Y=3mm siding end)
    - [ ] Eave depth 24mm passenger side adequate; 11mm gable end adequate
25. Fix ceiling grid to respect bay taper (deferred item above)
26. ✅ Passenger wall + floor piece assembly chamfers (2026-04-20):
    - Floor partition walls: replaced 1mm room-body quadrilateral cut with tongue-only 45° chamfer (0.5mm DADO_D legs); no room intrusion; cap rail non-office miter unchanged (p_leg=CHAMFER_P=1mm confirmed correct)
    - Passenger wall: replaced full-depth bay-edge chamfer (was creating a notch) with 0.5mm dado-entrance chamfer inside each dado channel at non-office wall (FT left wall X=48.4, TW right wall X=88.0)
    - Both chamfers are now hidden inside the dado/tongue interface — not visible from room or exterior
    - Evaluate against test prints to confirm assembly lead-in is adequate; may need to adjust size
27. **SK Y depth = 40mm redesign** — see deferred item above. Affects all SK scripts.
28. Add floor piece extras (deferred from basic):
    - Clock + notice board relief on partition walls
    - Benches ×2 (waiting room)
    - Stove stubs (waiting + office), flue holes through ceiling
    - Ceiling pendant wire holes (one per room, over pendant positions)
    - Bay desk + telegraph key block + lamp post
29. Ceiling+eave production pieces (3 rooms): waiting, ticket (from confirmed test), freight
30. Roof backing panels: 2 trapezoidal + 2 triangular wedge; hip edges beveled 45°; tabs for ceiling channel
31. Chimney (separate small print)
32. ✅ Standard station variant — **complete 2026-04-27**. Seven new `generate_std_*.py` scripts:
    - WAITING_W ft(15,2)=53.1mm, FREIGHT_W ft(26,6)=92.8mm, BLDG_D ft(15,0)=52.6mm, BLDG_L=189.6mm
    - Freight door #8038 (30.38×34.80mm; SK was #8125)
    - Added waiting-room and freight-room windows on siding and passenger faces (W_WIN_CX=0.25×WAITING_W from gable; F_WIN_CX near TF/FT partition)
    - Side bay window frames on floor piece (ported from SK)
    - Interior window frames on all exterior walls (ported from SK)
    - Platform: A/B orientation flag — wire holes at correct partition-wall X for each orientation
    - Ceiling: slab 211.6mm × 100.6mm, all pendant/channel/grid positions scale automatically
    - All STLs generated and ISO views complete

---

*Updated: 2026-04-27 | All SK and Standard station scripts complete. All STLs and ISO views generated.*
