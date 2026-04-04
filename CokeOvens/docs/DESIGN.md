# Coke Oven Bank — Design Document

## Overview

HO scale (1:87) modular bank coke oven scenic model, circa 1900.
C&O Railway prototype, West Virginia coalfields.
Based on HABS/HAER survey drawings, Connellsville Coal & Coke Region
(Shoaf Works, pa2870 series) — identical beehive oven technology to C&O/New River operations.

## Prototype

**Type:** Bank ovens — built into a natural hillside cut, pre-machine era, fully hand-operated.

**Operation (hand method):**
1. Larry car delivers slack coal along ridge track above ovens
2. Coal dumped through larry hole (crown) into oven chamber
3. Worker levels coal through arch opening with leveling hoe
4. Oven fires ~48–72 hours (beehive, open combustion)
5. Coke quenched with water from above (larry hole) or by hand
6. Coke drawn out via arch opening using coke fork
7. Loaded into gondola (bulk) or box car (bagged) on the coke siding

**Siding:** Single track parallel to oven front face.
Mixed use: gondola cars (bulk coke) + 36-ft box cars (bagged coke/supplies).
Siding sized for 4 × 36-ft cars (~28" of siding in HO).

## Dimensional Basis (HABS pa2870 drawings)

| Feature | Real | HO (mm) |
|---|---|---|
| Oven interior diameter | 12 ft | 42.1 |
| Oven wall thickness (firebrick) | 1 ft 4½ in | 4.8 |
| Oven exterior diameter | 14 ft 9 in | 51.7 |
| Oven center-to-center spacing | 14 ft 9 in | 51.7 (domes tangent) |
| Dome interior height (floor to crown) | ~7 ft | 24.5 |
| Larry hole diameter | 2 ft 6 in | 8.8 |
| Arch opening width | 5 ft | 17.5 |
| Arch rect. lower portion | 1 ft | 3.5 |
| Arch semicircle radius | 2 ft 6 in | 8.75 |
| Front wall height | ~5 ft | 17.5 |
| Front wall thickness | 2 ft | 7.0 |
| Coke yard depth (front wall to retaining wall) | 14 ft | 49.1 |
| Retaining wall height | 3 ft 6 in | 12.2 |
| Parapet lip above yard floor | 9 in | 2.6 |

## Current Status: v8 (script generate_cokeovens.py)

### Pieces

### v8 changes vs v7
- **Alignment hole fix:** Section left-face hole was mis-positioned (started at X=−PEG_H−0.5,
  outside the part). Now cuts correctly from X=0 into the left face (3.5 mm deep).
- **End cap holes:** Alignment hole added to end cap right face (X=END_CAP_W); mirror
  transform propagates it to the mirror cap's left face automatically.
- **Print-assist fillet:** 1.5 mm fillet at the slope fill / front wall junction
  (Y=FW_THICK, Z=OW_H_TOTAL−2) eases the overhang in back-side-down print orientation.
  Retaining wall inner corner has stepped topology that prevents filleting.
- **STL export in script:** `_export_stl()` / `_facets` dict added; ISO screenshot saved
  to `images/cokeovens_iso.png`.

**CokeOvenSection** (4 ovens per section, 209.7 × 121.7 × 52.1 mm)
- Single fused solid — one printable piece
- Retaining wall with 4 complete variable-height stone courses (courses snapped to
  `CAP_YARD_H` boundary so top course is always complete)
- Parapet lip at yard edge; stone courses applied post-fuse to avoid parapet fill-back
- Front wall: 9-voussoir arch treatment on each opening
  - Radial mortar joints (8 cuts, 9 voussoirs including keystone)
  - Extrados groove tracing the outer ring boundary (voussoir tops)
  - Vertical jamb joints on rectangular reveal below spring line
  - Stone courses on front wall applied post-fuse, segmented around arch rings
    using Z-aware circular chord masking (no rectangular ghost zone)
- 4 hollow dome shells with larry holes at crowns
- Slope fill: trapezoidal wedge Y=FW_THICK→CAP_BACK_Y, top slopes OW_H_TOTAL−2
  to SHELF_H−2; dome spheres cut from fill
- Back shelf with N-scale larry track grooves (9 mm gauge)
- Alignment peg (right face) + hole (left face) on retaining wall zone
- Fits Prusa Core One 250×210 mm bed ✓

**CokeOvenSection_1** (1-oven test piece, 54.7 × 121.7 × 52.1 mm)
- Same as 4-oven section, single oven — for print verification

**EndCapStoneWall** (7 × 121.7 × 52.1 mm)
- 4-zone profile:
  - Zone A: yard block Y=−YARD_DEPTH→0, height=CAP_YARD_H (course-aligned)
  - Zone B: oven wall block Y=0→FW_THICK, height=OW_H_TOTAL
  - Zone C: 3 equal steps Y=FW_THICK→CAP_BACK_Y, heights 43.1→47.6→52.1 mm
- Stone courses on: outward face (full height), front track face (0→CAP_YARD_H),
  oven wall riser (CAP_YARD_H→OW_H_TOTAL), 3 step riser faces
- Larry track grooves on back shelf top

**EndCapStoneWall_Mirror** — X-mirror of above, for opposite bank end

### Print orientation (all pieces)
- Print upright: base (Z=0, rail level) on print bed
- Section arches face front; semicircular arches self-supporting (no bridge supports)
- End cap prints on its 7 mm face — use brim

### Modular assembly
- Sections butt-join end-to-end (alignment peg + hole at each joint face)
- One end cap at each end of the assembled bank

### Key v7 fixes
- **Post-fuse stone cuts:** Front wall and retaining wall stone courses are now applied
  after the main fuse so that parapet/base-slab material can't fill back the grooves.
  Root cause of "3.5 courses" and "original style" appearance in prior versions.
- **Parapet position:** Moved from Z_YARD+YARD_SLAB to Z_YARD; parapet_top_z =
  YARD_BASE_H+LEDGE_H. Eliminates visible ledge bump at retaining wall top.
- **CAP_YARD_H:** Global constant snapped to next MASTER_COURSES boundary above
  YARD_BASE_H (14.25 vs 12.26 mm). Used on retaining wall face, end cap front face,
  and end cap ow-face stone courses.
- **Voussoir arch detail:** 9-voussoir radial joint pattern + extrados groove +
  vertical jamb joints on rectangular reveal. Stone courses masked from arch ring
  using Z-aware circular chord exclusion (no rectangular ghost).

## Parametric Variables

```python
SCALE        = 87.0
N_OVENS      = 4            # ovens per printed section
OVEN_ID      = 42.1 mm
OVEN_WALL    = 4.8 mm
OVEN_SPACING = 51.7 mm      # = OVEN_OD (domes tangent)
ARCH_W       = 17.5 mm
ARCH_RECT_H  = 3.5 mm
ARCH_RAISE   = 8.75 mm      # ft(2.5) plinth height below arch
FW_THICK     = 7.0 mm
YARD_DEPTH   = 49.1 mm
YARD_BASE_H  = 12.2 mm
CAP_YARD_H   = 14.25 mm     # next course boundary above YARD_BASE_H
LEDGE_H      = 2.6 mm
SHELF_H      = 52.1 mm
STONE_LARGE  = 3.6 mm
STONE_SMALL  = 1.7 mm
STONE_MORTAR = 0.42 mm
STONE_GD     = 0.9 mm
END_CAP_W    = 7.0 mm
N_VOUS       = 9            # voussoirs per arch
```

## Files

| File | Description |
|---|---|
| `scripts/generate_cokeovens.py` | Parametric generation script (v8) |
| `freecad/CokeOvens.FCStd` | FreeCAD source document |
| `printed_files/CokeOven_Section_4ovens_v8.stl` | 4-oven section STL (32416 facets) |
| `printed_files/CokeOven_Section_1oven_v8.stl` | 1-oven test piece STL (9108 facets) |
| `printed_files/CokeOven_EndCap_v8.stl` | End cap STL (6414 facets) |
| `printed_files/CokeOven_EndCap_Mirror_v8.stl` | Mirrored end cap STL (6566 facets) |
| `images/cokeovens_iso.png` | CAD isometric view |
| `images/service-pnp-habshaer-pa-pa2800-pa2870-*.jpg` | HABS reference drawings |
| `images/scientific-american-...1901.jpg` | 1901 cross-section reference |

## Post-Print Checklist & Next Session Plan

### After printing the 1-oven test piece

- [ ] **Stone course readability** — can individual courses be seen at arm's length?
      Target: courses visible without magnification. If too fine, increase STONE_MORTAR
      from 0.42 → 0.5 mm and STONE_GD from 0.9 → 1.0 mm.
- [ ] **Voussoir readability** — do the 9 voussoir joints and extrados groove read
      clearly? If lost in print, widen STONE_MORTAR or deepen STONE_GD for arch ring only.
- [ ] **Arch opening** — check arch proportions against prototype photo. Plinth (ARCH_RAISE)
      should be visible as 2–3 courses below the spring line.
- [ ] **Groove depth printability** — verify 0.4 mm nozzle / 0.2 mm layer can resolve
      STONE_GD=0.9 mm grooves. May need to increase to 1.0–1.1 mm.
- [ ] **Larry track grooves** — check 9 mm gauge, 1.8 mm wide, 0.9 mm deep grooves
      accept N-scale track ties flush with surface.
- [ ] **Alignment peg** — test fit peg (Ø2 mm × 3 mm) into hole (Ø2.3 mm × 3.5 mm)
      on an adjacent section. Adjust PEG_HOLE_R if too tight/loose.
- [ ] **Overall proportions** — compare against HABS drawings and prototype photos.
      Key check: retaining wall height (~3½ ft) vs front wall height (~5 ft + arch).

### After successful test print — production items

- [ ] **Print full 4-oven section** — `CokeOven_Section_4ovens_v7.stl`
- [ ] **Print end caps** — one each of `CokeOven_EndCap_v7.stl` and
      `CokeOven_EndCap_Mirror_v7.stl`
- [ ] **Determine bank length** — how many 4-oven sections for the layout?
      Each section = 209.7 mm (~9.7 ft HO); a 6-oven bank = 1.5 sections.
- [ ] **Verify 36-ft car truck-swing clearance** — YARD_DEPTH=49 mm ≈ 14 ft prototype;
      check gondola and 36-ft box car overhang at the coke siding curve.

### Future scenic / detail work (separate sessions)

- [ ] **Painting & weathering** — stone grey base, coke dust black in yard recess,
      rust streaks on oven faces, whitewash traces on upper dome
- [ ] **Coke yard scenic fill** — pack retaining wall recess (YARD_DROP=1.5 mm)
      with fine black ballast or coke dust static grass material
- [ ] **Larry track** — lay N-scale flex track in back shelf grooves; paint rail rust
- [ ] **Iron ring detail** — consider raised bead at dome base (horizontal ring),
      could be added as a thin torus in the script
- [ ] **Companion structures** (separate CAD projects):
      - Company office / weigh house
      - Scale house
      - Water tank (for quenching)
      - Coal tipple / larry car loading ramp
