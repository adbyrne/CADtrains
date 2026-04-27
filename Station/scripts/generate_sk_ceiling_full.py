#!/usr/bin/env python3
"""
SK station — full-building ceiling (waiting + ticket office + bay + freight).

Single lift-off piece covering all three rooms. Eaves: 24mm siding/passenger
sides, 11mm gable ends. Pressed-tin 4mm grid on underside. Bay channel on
passenger side (trapezoidal). Wall channels for all four exterior walls and
both interior partition walls. Four pendant fixtures (2 waiting, 1 ticket,
1 freight). Wire holes at WT and TF partition wall centres.

Coordinate system matches other SK scripts (building coordinates):
  X: length  (waiting → freight)
  Y: depth   (siding Y=0 → passenger Y=BLDG_D)
  Z: height  (floor Z=0 → wall top Z=WALL_H)

Piece prints face-down (grid face on build plate, Z=WALL_H on plate).
Slab footprint: ~138.6mm X × 88mm Y — fits 250×210mm build plate.

Output:
  FCStd: CADtrains/Station/freecad/SK_CeilingFull.FCStd
  STL:   CADtrains/Station/printed_files/SK_CeilingFull.stl
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
BLDG_D    = 40.0         # SK site limit
WAITING_W = ft( 7, 7)    # 26.56mm
TICKET_W  = ft(10, 2)    # 35.6mm
FREIGHT_W = ft(13, 3)    # 46.40mm
BLDG_L    = WAITING_W + TICKET_W + FREIGHT_W + 4 * WALL_T   # 116.56mm

X_WT_WALL = WALL_T + WAITING_W                              # 28.56mm
X_TF_WALL = WALL_T + WAITING_W + WALL_T + TICKET_W         # 66.16mm

W_CX = WALL_T + WAITING_W / 2                              # 15.28mm  waiting centre
T_CX = WALL_T + WAITING_W + WALL_T + TICKET_W / 2         # 48.36mm  ticket centre
F_CX = X_TF_WALL + WALL_T + FREIGHT_W / 2                 # 91.36mm  freight centre

SQ2      = math.sqrt(2)
BAY_PROJ = ft(2, 6)                    # 8.76mm
FRONT_W  = TICKET_W - 2 * BAY_PROJ    # 18.1mm
HW       = TICKET_W / 2               # 17.8mm
FHW      = FRONT_W  / 2               # 9.04mm

DADO_D   = 0.5    # partition wall tongue protrusion into exterior wall dado

# ---- Ceiling / eave parameters -----------------------------------------------
CEIL_T    = 2.5
EAVE_SIDE = 24.0   # passenger/siding eave — #8147 rafter tails
EAVE_END  = 11.0   # gable-end eave — #8147 short rafter tails
CHAN_W    = 2.2    # WALL_T + 0.2mm clearance
CHAN_D    = 1.5
chan_off  = (CHAN_W - WALL_T) / 2   # 0.1mm overhang each side of wall

# ---- Pressed tin grid --------------------------------------------------------
GRID_P    = 4.0
GRID_W    = 0.4
GRID_D    = 0.3

print(f"SK Ceiling Full  BLDG_L={BLDG_L:.2f}  BLDG_D={BLDG_D}  GRID_P={GRID_P}mm")
print(f"  W_CX={W_CX:.2f}  T_CX={T_CX:.2f}  F_CX={F_CX:.2f}")
print(f"  Bay: HW={HW:.2f}  FHW={FHW:.2f}  PROJ={BAY_PROJ:.2f}")

# =============================================================================
# 1. CEILING SLAB — full building + eaves on all four sides
# =============================================================================
x0 = -EAVE_END                   # -11.0mm
x1 = BLDG_L + EAVE_END           # 127.56mm
y0 = -EAVE_SIDE                  # -24.0mm
y1 = BLDG_D + EAVE_SIDE          #  64.0mm

slab = Part.makeBox(x1 - x0, y1 - y0, CEIL_T,
                    FreeCAD.Vector(x0, y0, WALL_H))
print(f"  Slab: {x1-x0:.2f} x {y1-y0:.0f}mm")

# =============================================================================
# 2. WALL CHANNELS (cut from ceiling bottom at Z=WALL_H)
# =============================================================================

# ---- Siding wall (exterior face Y=0, interior Y=WALL_T) — runs in X ----------
# Stop at gable walls (X=0..BLDG_L), do not cut into eave overhangs
slab = slab.cut(Part.makeBox(BLDG_L, CHAN_W, CHAN_D,
                              FreeCAD.Vector(0, WALL_T/2 - CHAN_W/2, WALL_H)))
print(f"  Channel: siding  X=0..{BLDG_L:.2f}  Y={WALL_T/2-CHAN_W/2:.1f}..{WALL_T/2+CHAN_W/2:.1f}")

# ---- WT + TF partition walls (run in Y) --------------------------------------
pw_y0 = WALL_T - DADO_D - 0.1
pw_y1 = BLDG_D - WALL_T + DADO_D + 0.1
for label, px in [("WT", X_WT_WALL), ("TF", X_TF_WALL)]:
    slab = slab.cut(Part.makeBox(CHAN_W, pw_y1 - pw_y0, CHAN_D,
                                  FreeCAD.Vector(px - chan_off, pw_y0, WALL_H)))
    print(f"  Channel: {label} partition  X={px-chan_off:.1f}..{px-chan_off+CHAN_W:.1f}  Y={pw_y0:.1f}..{pw_y1:.1f}")

# ---- Gable end walls (run in Y, exterior face at X=0 and X=BLDG_L) ----------
for label, ex in [("waiting-end", 0.0), ("freight-end", BLDG_L)]:
    cx = ex + WALL_T/2 if ex == 0.0 else ex - WALL_T/2
    slab = slab.cut(Part.makeBox(CHAN_W, BLDG_D, CHAN_D,
                                  FreeCAD.Vector(cx - CHAN_W/2, 0, WALL_H)))
    print(f"  Channel: {label}  X={cx-CHAN_W/2:.1f}..{cx+CHAN_W/2:.1f}  Y=0..{BLDG_D}")

# ---- Bay wall channels (trapezoidal, over 45° panel tops + front panel) ------
BAY_CLR = 0.1

left_ch = [
    FreeCAD.Vector(T_CX - HW  - BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                          WALL_H),
    FreeCAD.Vector(T_CX - FHW - BAY_CLR/SQ2,            BLDG_D + BAY_PROJ + BAY_CLR/SQ2,               WALL_H),
    FreeCAD.Vector(T_CX - FHW + WALL_T/SQ2 + BAY_CLR/SQ2,   BLDG_D + BAY_PROJ - WALL_T/SQ2 - BAY_CLR/SQ2, WALL_H),
    FreeCAD.Vector(T_CX - HW  + WALL_T/SQ2 + BAY_CLR/SQ2,   BLDG_D - BAY_CLR/SQ2,                         WALL_H),
    FreeCAD.Vector(T_CX - HW  - BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                          WALL_H),
]
slab = slab.cut(Part.Face(Part.makePolygon(left_ch)).extrude(FreeCAD.Vector(0, 0, CHAN_D)))

right_ch = [
    FreeCAD.Vector(T_CX + HW  + BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                          WALL_H),
    FreeCAD.Vector(T_CX + FHW + BAY_CLR/SQ2,            BLDG_D + BAY_PROJ + BAY_CLR/SQ2,               WALL_H),
    FreeCAD.Vector(T_CX + FHW - WALL_T/SQ2 - BAY_CLR/SQ2,   BLDG_D + BAY_PROJ - WALL_T/SQ2 - BAY_CLR/SQ2, WALL_H),
    FreeCAD.Vector(T_CX + HW  - WALL_T/SQ2 - BAY_CLR/SQ2,   BLDG_D - BAY_CLR/SQ2,                         WALL_H),
    FreeCAD.Vector(T_CX + HW  + BAY_CLR/SQ2,            BLDG_D + BAY_CLR/SQ2,                          WALL_H),
]
slab = slab.cut(Part.Face(Part.makePolygon(right_ch)).extrude(FreeCAD.Vector(0, 0, CHAN_D)))

slab = slab.cut(Part.makeBox(FRONT_W + 2*BAY_CLR, CHAN_W, CHAN_D,
                              FreeCAD.Vector(T_CX - FHW - BAY_CLR,
                                             BLDG_D + BAY_PROJ - WALL_T/2 - CHAN_W/2, WALL_H)))
print(f"  Channel: bay walls (L/R 45° + front)")

# ---- Passenger wall channel — split around bay opening, extended by bay_inner_w
# Stop at gable walls (X=0..BLDG_L), do not cut into eave overhangs
bay_inner_w = WALL_T / SQ2
pass_y    = BLDG_D - WALL_T/2 - CHAN_W/2
left_end  = T_CX - HW + bay_inner_w
right_sta = T_CX + HW - bay_inner_w
slab = slab.cut(Part.makeBox(left_end, CHAN_W, CHAN_D,
                              FreeCAD.Vector(0, pass_y, WALL_H)))
slab = slab.cut(Part.makeBox(BLDG_L - right_sta, CHAN_W, CHAN_D,
                              FreeCAD.Vector(right_sta, pass_y, WALL_H)))
print(f"  Channel: passenger wall  left X=0..{left_end:.1f}  right X={right_sta:.1f}..{BLDG_L:.2f}  (bay_inner_w={bay_inner_w:.2f})")

# =============================================================================
# 3. PRESSED TIN GRID on bottom face (all three rooms + bay)
# =============================================================================
gx0 = WALL_T             # waiting gable wall interior face
gx1 = BLDG_L - WALL_T   # freight gable wall interior face
bx0 = T_CX - HW
bx1 = T_CX + HW
gy0 = WALL_T
gy1 = BLDG_D
by1 = BLDG_D + BAY_PROJ

# Lines parallel to X (spaced in Y)
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

print(f"  Grid: {GRID_P}mm cells  {cnt_x} X-lines  {cnt_y} Y-lines  X={gx0:.1f}..{gx1:.1f}")

# =============================================================================
# 4. WIRE HOLES at WT and TF partition wall centres (near siding end)
# =============================================================================
WIRE_HOLE_R = 1.0
for wlabel, wpx in [("WT", X_WT_WALL), ("TF", X_TF_WALL)]:
    wcx = wpx + WALL_T / 2
    wcy = WALL_T + 1.0
    slab = slab.cut(Part.makeCylinder(WIRE_HOLE_R, CEIL_T, FreeCAD.Vector(wcx, wcy, WALL_H)))
    print(f"  Wire hole {wlabel}: X={wcx:.1f}  Y={wcy:.1f}  D={2*WIRE_HOLE_R}mm")

# =============================================================================
# 5. PENDANT LIGHT FIXTURES
#    Waiting room: 2 pendants at 1/3 and 2/3 of room length
#    Ticket office: 1 pendant at T_CX
#    Freight room:  1 pendant at F_CX
#    All at Y = BLDG_D/2 (room depth centre)
# =============================================================================
RIM_R   = 2.0
TOP_R   = 1.25
SHADE_H = 2.5
LED_R   = 0.6

p_cy = BLDG_D / 2   # Y centre for all pendants

pendants = [
    ("W1", WALL_T + WAITING_W / 3,       p_cy),
    ("W2", WALL_T + 2 * WAITING_W / 3,   p_cy),
    ("T",  T_CX,                          p_cy),
    ("F",  F_CX,                          p_cy),
]

for name, pcx, pcy in pendants:
    shade = Part.makeCone(RIM_R, TOP_R, SHADE_H,
                          FreeCAD.Vector(pcx, pcy, WALL_H - SHADE_H),
                          FreeCAD.Vector(0, 0, 1))
    slab = slab.fuse(shade)
    slab = slab.cut(Part.makeCylinder(LED_R, SHADE_H + CEIL_T,
                                       FreeCAD.Vector(pcx, pcy, WALL_H - SHADE_H)))
    print(f"  Pendant {name}: ({pcx:.2f},{pcy:.2f})")

# =============================================================================
# 6. RAFTER TAIL TICK MARKS on eave soffits (Z=WALL_H face)
#    Small cylindrical dimples at 14mm spacing, centred in each eave strip.
#    Siding/passenger faces run in X (0..BLDG_L), gable faces run in Y (0..BLDG_D).
# =============================================================================
TICK_R     = 0.5
TICK_D     = 0.3
TICK_SPACE = 14.0

tick_cnt = 0

def cut_tick_row(shape, positions, fixed_coord, axis, z):
    """Cut tick dimples along a row. axis='x' fixes Y, axis='y' fixes X."""
    for p in positions:
        if axis == 'x':
            cx, cy = p, fixed_coord
        else:
            cx, cy = fixed_coord, p
        shape = shape.cut(Part.makeCylinder(TICK_R, TICK_D, FreeCAD.Vector(cx, cy, z)))
    return shape

def tick_positions(start, end, spacing):
    pos = []
    p = start
    while p <= end + 1e-6:
        pos.append(p)
        p += spacing
    return pos

# Siding eave: Y = -EAVE_SIDE..0, ticks along X, row centred at Y = -EAVE_SIDE/2
x_ticks = tick_positions(0, BLDG_L, TICK_SPACE)
slab = cut_tick_row(slab, x_ticks, -EAVE_SIDE / 2, 'x', WALL_H)
tick_cnt += len(x_ticks)
print(f"  Ticks: siding eave  {len(x_ticks)} marks  Y={-EAVE_SIDE/2:.1f}")

# Passenger eave: Y = BLDG_D..BLDG_D+EAVE_SIDE, ticks along X, row at Y = BLDG_D+EAVE_SIDE/2
slab = cut_tick_row(slab, x_ticks, BLDG_D + EAVE_SIDE / 2, 'x', WALL_H)
tick_cnt += len(x_ticks)
print(f"  Ticks: passenger eave  {len(x_ticks)} marks  Y={BLDG_D+EAVE_SIDE/2:.1f}")

# Waiting gable eave: X = -EAVE_END..0, ticks along Y, row at X = -EAVE_END/2
y_ticks = tick_positions(0, BLDG_D, TICK_SPACE)
if y_ticks[-1] < BLDG_D - 1e-3:
    y_ticks.append(BLDG_D)
slab = cut_tick_row(slab, y_ticks, -EAVE_END / 2, 'y', WALL_H)
tick_cnt += len(y_ticks)
print(f"  Ticks: waiting gable eave  {len(y_ticks)} marks  X={-EAVE_END/2:.1f}")

# Freight gable eave: X = BLDG_L..BLDG_L+EAVE_END, ticks along Y, row at X = BLDG_L+EAVE_END/2
slab = cut_tick_row(slab, y_ticks, BLDG_L + EAVE_END / 2, 'y', WALL_H)
tick_cnt += len(y_ticks)
print(f"  Ticks: freight gable eave  {len(y_ticks)} marks  X={BLDG_L+EAVE_END/2:.1f}")

print(f"  Total tick marks: {tick_cnt}  spacing={TICK_SPACE}mm  R={TICK_R}mm  depth={TICK_D}mm")

# =============================================================================
# EXPORT
# =============================================================================
fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/SK_CeilingFull.FCStd"
try: FreeCAD.closeDocument("SK_CeilingFull")
except: pass
doc = FreeCAD.newDocument("SK_CeilingFull")
obj = doc.addObject("Part::Feature", "CeilingFull")
obj.Shape = slab
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/SK_CeilingFull.stl"
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
