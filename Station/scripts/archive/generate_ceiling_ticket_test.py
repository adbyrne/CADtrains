#!/usr/bin/env python3
"""
Ticket office ceiling + eave test (includes bay).

Tests:
  - Ceiling channel fit over WT/TF partition wall tops
  - Bay wall channel (trapezoidal) over bay panel tops
  - Bay ceiling footprint matches bay geometry
  - 4mm pressed tin grid cells (compare against 3mm confirmed in previous test)
  - Standard 12mm eave on siding / left / right sides
  - Bay front eave

Coordinate system matches other SK scripts (building coordinates):
  X: length (waiting→freight)
  Y: depth  (siding Y=0 → passenger Y=BLDG_D)
  Z: height (floor Z=0 → wall top Z=WALL_H)

Piece prints face-down (grid face on build plate, Z=WALL_H on plate).

Output:
  FCStd: CADtrains/Station/freecad/SK_CeilingTicketTest.FCStd
  STL:   CADtrains/Station/printed_files/SK_CeilingTicketTest.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, math

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Building dimensions (matching other SK scripts) -------------------------
WALL_T    = 2.0
WALL_H    = ft(10, 6)    # 36.8mm
BLDG_D    = 40.0         # SK site limit (standard would be ft(15,0)=52.6mm)
TICKET_W  = ft(10, 2)    # 35.6mm
WAITING_W = ft( 7, 7)    # 26.56mm
BLDG_L    = WAITING_W + TICKET_W + ft(13, 3) + 4 * WALL_T

T_CX      = WALL_T + WAITING_W + WALL_T + TICKET_W / 2   # 48.4mm
X_WT_WALL = WALL_T + WAITING_W                             # 28.6mm
X_TF_WALL = WALL_T + WAITING_W + WALL_T + TICKET_W        # 66.2mm

SQ2       = math.sqrt(2)
BAY_PROJ  = ft(2, 6)                   # 8.76mm
FRONT_W   = TICKET_W - 2 * BAY_PROJ   # 18.1mm
HW        = TICKET_W / 2               # 17.8mm
FHW       = FRONT_W  / 2               # 9.04mm

DADO_D    = 0.5    # partition wall dado protrusion into exterior wall

# ---- Ceiling / eave parameters -----------------------------------------------
CEIL_T    = 2.5
EAVE_SIDE = 24.0   # passenger/siding eave depth — #8147 rafter tails 24mm
EAVE_END  = 11.0   # gable-end eave depth — #8147 short rafter tails 11mm
CHAN_W    = 2.2    # WALL_T + 0.2mm clearance
CHAN_D    = 1.5

# ---- Pressed tin grid — testing 4mm (vs 3mm confirmed) ----------------------
GRID_P    = 4.0
GRID_W    = 0.4
GRID_D    = 0.3

print(f"SK Ceiling Ticket Test  GRID_P={GRID_P}mm")
print(f"  Office: X={X_WT_WALL:.1f}..{X_TF_WALL:.1f} ({TICKET_W:.1f}mm)")
print(f"  Bay: T_CX={T_CX:.1f}  HW={HW:.1f}  FHW={FHW:.2f}  PROJ={BAY_PROJ:.2f}")

# =============================================================================
# 1. CEILING SLAB
# =============================================================================
# Rectangular slab spanning ticket office + gable-end eaves (X) and full
# siding+passenger eave depth (Y). The 24mm passenger eave covers the bay
# footprint entirely — no separate bay ceiling polygon needed.
x0 = X_WT_WALL - EAVE_END   # 17.6mm
x1 = X_TF_WALL + EAVE_END   # 77.2mm
slab = Part.makeBox(x1 - x0, BLDG_D + 2*EAVE_SIDE, CEIL_T,
                    FreeCAD.Vector(x0, -EAVE_SIDE, WALL_H))
print(f"  Slab: {x1-x0:.1f} x {BLDG_D+2*EAVE_SIDE:.1f}mm  EAVE_SIDE={EAVE_SIDE}  EAVE_END={EAVE_END}")

# =============================================================================
# 2. WALL CHANNELS (cut from ceiling bottom face at Z=WALL_H)
# =============================================================================
# Siding wall: exterior face at Y=0, interior at Y=WALL_T
# Channel centred on wall: Y = WALL_T/2 ± CHAN_W/2 = -0.1..2.1
slab = slab.cut(Part.makeBox(x1 - x0, CHAN_W, CHAN_D,
                              FreeCAD.Vector(x0, WALL_T/2 - CHAN_W/2, WALL_H)))
print(f"  Channel: siding wall  Y={WALL_T/2-CHAN_W/2:.1f}..{WALL_T/2+CHAN_W/2:.1f}")

# WT + TF partition wall channels (along Y)
# Partition wall spans Y = WALL_T-DADO_D .. BLDG_D-WALL_T+DADO_D = 1.5..51.1
pw_y0 = WALL_T - DADO_D - 0.1
pw_y1 = BLDG_D - WALL_T + DADO_D + 0.1
chan_off = (CHAN_W - WALL_T) / 2   # 0.1mm each side
for label, px in [("WT", X_WT_WALL), ("TF", X_TF_WALL)]:
    slab = slab.cut(Part.makeBox(CHAN_W, pw_y1 - pw_y0, CHAN_D,
                                  FreeCAD.Vector(px - chan_off, pw_y0, WALL_H)))
    print(f"  Channel: {label} partition  X={px-chan_off:.1f}..{px-chan_off+CHAN_W:.1f}  Y={pw_y0:.1f}..{pw_y1:.1f}")

# Bay wall channels: 3 narrow strips over left 45° panel, right 45° panel,
# and front panel tops. Back wall is covered by passenger wall channel above.
# Each strip expanded by BAY_CLR beyond the wall face for clearance.
# Left/right panels run at 45° so perpendicular offsets are ±BAY_CLR/SQ2 in both X and Y.
BAY_CLR = 0.1

# Left 45° panel: outer normal = (-1/SQ2, +1/SQ2), inner normal = (+1/SQ2, -1/SQ2)
left_ch = [
    FreeCAD.Vector(T_CX - HW  - BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                      WALL_H),
    FreeCAD.Vector(T_CX - FHW - BAY_CLR/SQ2,            BLDG_D + BAY_PROJ + BAY_CLR/SQ2,            WALL_H),
    FreeCAD.Vector(T_CX - FHW + WALL_T/SQ2 + BAY_CLR/SQ2,   BLDG_D + BAY_PROJ - WALL_T/SQ2 - BAY_CLR/SQ2,  WALL_H),
    FreeCAD.Vector(T_CX - HW  + WALL_T/SQ2 + BAY_CLR/SQ2,   BLDG_D - BAY_CLR/SQ2,                          WALL_H),
    FreeCAD.Vector(T_CX - HW  - BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                      WALL_H),
]
slab = slab.cut(Part.Face(Part.makePolygon(left_ch)).extrude(FreeCAD.Vector(0, 0, CHAN_D)))

# Right 45° panel: outer normal = (+1/SQ2, +1/SQ2), inner normal = (-1/SQ2, -1/SQ2)
right_ch = [
    FreeCAD.Vector(T_CX + HW  + BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                      WALL_H),
    FreeCAD.Vector(T_CX + FHW + BAY_CLR/SQ2,            BLDG_D + BAY_PROJ + BAY_CLR/SQ2,            WALL_H),
    FreeCAD.Vector(T_CX + FHW - WALL_T/SQ2 - BAY_CLR/SQ2,   BLDG_D + BAY_PROJ - WALL_T/SQ2 - BAY_CLR/SQ2,  WALL_H),
    FreeCAD.Vector(T_CX + HW  - WALL_T/SQ2 - BAY_CLR/SQ2,   BLDG_D - BAY_CLR/SQ2,                          WALL_H),
    FreeCAD.Vector(T_CX + HW  + BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                      WALL_H),
]
slab = slab.cut(Part.Face(Part.makePolygon(right_ch)).extrude(FreeCAD.Vector(0, 0, CHAN_D)))

# Front panel: wall centre at Y = BLDG_D+BAY_PROJ - WT/2, X = T_CX±FHW
slab = slab.cut(Part.makeBox(FRONT_W + 2*BAY_CLR, CHAN_W, CHAN_D,
                              FreeCAD.Vector(T_CX - FHW - BAY_CLR,
                                             BLDG_D + BAY_PROJ - WALL_T/2 - CHAN_W/2, WALL_H)))
print(f"  Channel: bay walls — L/R 45° strips + front strip  wall_t/SQ2={WALL_T/SQ2:.2f}mm in XY")

# =============================================================================
# 3. PRESSED TIN GRID on bottom face
# =============================================================================
# Room grid: full ticket-office width (gx0..gx1), Y = WALL_T..BLDG_D
# Bay grid:  bay width only (bx0..bx1),            Y = BLDG_D..BLDG_D+BAY_PROJ
# Grid does NOT extend into the eave (Y > BLDG_D outside bay width).
gx0 = X_WT_WALL
gx1 = X_TF_WALL
bx0 = T_CX - HW
bx1 = T_CX + HW
gy0 = WALL_T
gy1 = BLDG_D
by1 = BLDG_D + BAY_PROJ

# Lines parallel to X (spaced in Y)
# Room zone (gy <= gy1): full office width gx0..gx1.
# Bay zone (gy1 < gy <= by1): width narrows at 45° — half-width = HW-(gy-BLDG_D).
cnt_x = 0
gy = gy0
while gy <= by1 + GRID_P:
    if gy <= gy1:
        slab = slab.cut(Part.makeBox(gx1 - gx0, GRID_W, GRID_D,
                                      FreeCAD.Vector(gx0, gy - GRID_W/2, WALL_H)))
        cnt_x += 1
    elif gy <= by1:
        bay_hw = HW - (gy - BLDG_D)
        x_l = T_CX - bay_hw
        x_r = T_CX + bay_hw
        if x_r > x_l:
            slab = slab.cut(Part.makeBox(x_r - x_l, GRID_W, GRID_D,
                                          FreeCAD.Vector(x_l, gy - GRID_W/2, WALL_H)))
            cnt_x += 1
    gy += GRID_P

# Lines parallel to Y (spaced in X)
# Room zone (gx outside bx0..bx1): y_end = gy1.
# Bay centre (bx0+BAY_PROJ .. bx1-BAY_PROJ = T_CX±FHW): y_end = by1 (full bay depth).
# Bay taper (bx0..T_CX-FHW and T_CX+FHW..bx1): y_end clips to 45° bay wall boundary.
cnt_y = 0
gx = gx0
while gx <= gx1 + GRID_P:
    if bx0 <= gx <= bx1:
        if gx <= T_CX - FHW:
            y_end = min(BLDG_D + (gx - bx0), by1)   # left taper
        elif gx >= T_CX + FHW:
            y_end = min(BLDG_D + (bx1 - gx), by1)   # right taper
        else:
            y_end = by1                               # centre: full bay depth
    else:
        y_end = gy1
    slab = slab.cut(Part.makeBox(GRID_W, y_end - gy0, GRID_D,
                                  FreeCAD.Vector(gx - GRID_W/2, gy0, WALL_H)))
    gx += GRID_P
    cnt_y += 1

print(f"  Grid: {GRID_P}mm cells  {cnt_x} X-lines  {cnt_y} Y-lines  room Y={gy0:.1f}..{gy1:.1f} bay Y={gy1:.1f}..{by1:.1f}")

# =============================================================================
# 4. WALL CHANNELS — passenger wall (split around bay opening)
# =============================================================================
# Passenger wall has a full TICKET_W opening for the bay — no wall in that zone.
# Channel split around the bay opening, but extended inward by bay_inner_w each side
# to cover the floor piece bay inner filler blocks (WALL_T/SQ2 wide, sit between
# the 45° bay panel inner face and the partition wall end at the passenger wall).
bay_inner_w = WALL_T / SQ2
pass_y    = BLDG_D - WALL_T/2 - CHAN_W/2
left_end  = T_CX - HW + bay_inner_w
right_sta = T_CX + HW - bay_inner_w
slab = slab.cut(Part.makeBox(left_end - x0, CHAN_W, CHAN_D,
                              FreeCAD.Vector(x0, pass_y, WALL_H)))
slab = slab.cut(Part.makeBox(x1 - right_sta, CHAN_W, CHAN_D,
                              FreeCAD.Vector(right_sta, pass_y, WALL_H)))
print(f"  Channel: passenger wall  left X={x0:.1f}..{left_end:.1f}  right X={right_sta:.1f}..{x1:.1f}  Y={pass_y:.1f}..{pass_y+CHAN_W:.1f}  (bay_inner_w={bay_inner_w:.2f}mm)")

# Wire feed holes at WT and TF partition wall X centres, near siding end (Y = WALL_T + 1.0).
# Wires run down partition wall face on siding side, exit through floor notch.
WIRE_HOLE_R = 1.0
for wlabel, wpx in [("WT", X_WT_WALL), ("TF", X_TF_WALL)]:
    wcx = wpx + WALL_T / 2
    wcy = WALL_T + 1.0
    slab = slab.cut(Part.makeCylinder(WIRE_HOLE_R, CEIL_T, FreeCAD.Vector(wcx, wcy, WALL_H)))
    print(f"  Wire hole {wlabel}: X={wcx:.1f}  Y={wcy:.1f}  D={2*WIRE_HOLE_R}mm")

# =============================================================================
# 5. PENDANT LIGHT (kerosene-style shade frustum hanging from ceiling)
# =============================================================================
# Shade: truncated cone, wide rim at bottom (RIM_R), narrow top at ceiling face (TOP_R).
# LED hole: cylinder cut through ceiling slab for LED insertion from above.
RIM_R   = 2.0    # shade open rim radius
TOP_R   = 1.25   # shade top (ceiling) radius
SHADE_H = 2.5    # shade height (hangs below ceiling)
LED_R   = 0.6    # LED hole radius (1.2mm dia)

p_cx = T_CX
p_cy = BLDG_D / 2
shade = Part.makeCone(RIM_R, TOP_R, SHADE_H,
                       FreeCAD.Vector(p_cx, p_cy, WALL_H - SHADE_H),
                       FreeCAD.Vector(0, 0, 1))
slab = slab.fuse(shade)
# LED hole starts at bottom of pendant rim and cuts through pendant + slab.
slab = slab.cut(Part.makeCylinder(LED_R, SHADE_H + CEIL_T,
                                   FreeCAD.Vector(p_cx, p_cy, WALL_H - SHADE_H)))
print(f"  Pendant: R={RIM_R}→{TOP_R}mm H={SHADE_H}mm at ({p_cx:.1f},{p_cy:.1f})  LED hole D={2*LED_R}mm pendant+ceiling")

# =============================================================================
# EXPORT
# =============================================================================
fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/SK_CeilingTicketTest.FCStd"
try: FreeCAD.closeDocument("SK_CeilingTicketTest")
except: pass
doc = FreeCAD.newDocument("SK_CeilingTicketTest")
obj = doc.addObject("Part::Feature", "CeilingTicketTest")
obj.Shape = slab
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/SK_CeilingTicketTest.stl"
MeshPart.meshFromShape(Shape=slab, LinearDeflection=0.05,
                        AngularDeflection=0.1, Relative=False).write(stl)
print(f"Wrote {stl}")
_result_ = "Done"
'''

result = proxy.execute(CODE)
if result.get("success"):
    print(result.get("stdout", ""))
    print("OK:", result.get("result"))
else:
    print("ERROR:", result.get("error_message"))
    print(result.get("error_traceback", ""))
    sys.exit(1)
