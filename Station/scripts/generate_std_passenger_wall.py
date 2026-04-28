#!/usr/bin/env python3
"""
Standard station — passenger face exterior wall panel.

Passenger face = track-facing/front face of building.
Building A orientation: X=0 = freight end (HC direction), X=BLDG_L = waiting end (JC direction).
(Mirrored X from siding wall so gable miters align correctly at both corners.)

Coordinate system:
  X: building length direction (freight→waiting)
  Y: wall thickness (0 = exterior/track face, WALL_T = interior face)
  Z: height (0 = floor, WALL_H = wall top)

Openings (left to right, freight→waiting):
  - Freight room door:   #8038  30.38×34.80mm  sill at floor (Z=0)
  - Freight room window: #8028/#8069  9.38×20.05mm  sill at WAINSCOT_H  near FT partition
  - Operator bay:        full TICKET_W wide (35.6mm)  full wall height  sill at floor (Z=0)
  - Waiting room window: #8028/#8069  9.38×20.05mm  sill at WAINSCOT_H  near waiting gable
  - Waiting room door:   #8033  9.55×29.70mm  sill at floor (Z=0)

Interior face (Y=WALL_T):
  - Wainscot grooves 1.2mm pitch, Z=0..WAINSCOT_H, depth 0.3mm from face
  - Cap rail continuous full width (notched at bay/door openings by cut)
  - NO clock disc or notice boards (those are on partition walls only)

Ends: 45° miter at both ends (to mate with gable walls).
Base: 1.0mm deep × 1.5mm tall rabbet on interior face (floor piece tongue locates here).

Bay opening: the operator bay (separate print) slots against the exterior face (Y=0)
  and is secured from inside. Opening = full TICKET_W wide × full wall height.

Print orientation: face-down (exterior face Y=0 on plate); wall stands up in Z.

Output:
  FCStd: CADtrains/Station/freecad/Std_PassengerWall.FCStd
  STL:   CADtrains/Station/printed_files/Std_PassengerWall.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Building dimensions (standard variant) ---------------------------------
WALL_T    = 2.0
WALL_H    = ft(10, 6)    # 36.8mm

WAITING_W = ft(15, 2)   # 53.1mm
TICKET_W  = ft(10, 2)   # 35.60mm (same as SK)
FREIGHT_W = ft(26, 6)   # 92.8mm

BLDG_L = WAITING_W + TICKET_W + FREIGHT_W + 4 * WALL_T

# Room centers in X — passenger wall is X-mirrored vs siding wall:
#   freight end at X=0, waiting end at X=BLDG_L.
F_CX = WALL_T + FREIGHT_W / 2
T_CX = WALL_T + FREIGHT_W + WALL_T + TICKET_W / 2
W_CX = WALL_T + FREIGHT_W + WALL_T + TICKET_W + WALL_T + WAITING_W / 2

# ---- Interior face details --------------------------------------------------
WAINSCOT_H = 9.65
CAP_H      = 1.5
CAP_T      = 0.8
Z_CUT      = WALL_T + CAP_T   # 2.8mm — miter and bay/door cut depth

GROOVE_P   = 1.2
GROOVE_W   = 0.3
GROOVE_D   = 0.3

# ---- Partition wall locating dadoes -----------------------------------------
X_FT_WALL = WALL_T + FREIGHT_W              # left face of freight/ticket partition
X_TW_WALL = WALL_T + FREIGHT_W + WALL_T + TICKET_W  # left face of ticket/waiting partition
DADO_D    = 0.5

# ---- Rabbet at base ---------------------------------------------------------
RABBET_D   = 1.0
RABBET_H   = 1.5

# ---- Tichy opening dimensions -----------------------------------------------
PASS_DOOR_W  =  9.55   # #8033 exterior door
PASS_DOOR_H  = 29.70
WIN_W        =  9.38   # #8028/#8069 window
WIN_H        = 20.05
WIN_SILL     = WAINSCOT_H   # 9.65mm
FREIGHT_DW   = 30.38   # #8038 standard freight door
FREIGHT_DH   = 34.80

BAY_X0 = T_CX - TICKET_W / 2   # = X_FT_WALL + WALL_T

FRAME_D = 0.6
FRAME_W = 1.45

# ---- Extra window centres (standard variant — not in SK) --------------------
# Waiting room window near waiting gable end (X=BLDG_L)
W_WIN_CX = BLDG_L - WALL_T - WAITING_W * 0.25
# Freight room window near FT partition (left/freight side)
F_WIN_CX = X_FT_WALL - WALL_T - WIN_W / 2 - 3.0

def add_int_frame(shape, x0, x1, z0, z1):
    """Raised interior frame: FRAME_W × FRAME_D legs + head."""
    shape = shape.fuse(Part.makeBox(FRAME_W, FRAME_D, z1-z0+FRAME_W, FreeCAD.Vector(x0-FRAME_W, WALL_T, z0)))
    shape = shape.fuse(Part.makeBox(FRAME_W, FRAME_D, z1-z0+FRAME_W, FreeCAD.Vector(x1,         WALL_T, z0)))
    shape = shape.fuse(Part.makeBox(x1-x0+2*FRAME_W, FRAME_D, FRAME_W, FreeCAD.Vector(x0-FRAME_W, WALL_T, z1)))
    return shape

print(f"Std Passenger Wall: {BLDG_L:.1f} x {WALL_H:.1f} x {WALL_T}mm  (freight end X=0)")
print(f"Rooms: F={FREIGHT_W:.1f}  T={TICKET_W:.1f}  W={WAITING_W:.1f}mm")
print(f"Centers: F={F_CX:.1f}  T={T_CX:.1f}  W={W_CX:.1f}mm")
print(f"Bay opening: X={BAY_X0:.1f}..{BAY_X0+TICKET_W:.1f}  (full height)")
print(f"Extra windows: W_WIN_CX={W_WIN_CX:.1f}  F_WIN_CX={F_WIN_CX:.1f}mm")

# ---- Base wall --------------------------------------------------------------
wall = Part.makeBox(BLDG_L, WALL_T, WALL_H)

# ---- Cap rail on interior face — fuse BEFORE door/bay cuts ------------------
wall = wall.fuse(Part.makeBox(BLDG_L, CAP_T, CAP_H,
                               FreeCAD.Vector(0, WALL_T, WAINSCOT_H - CAP_H)))

# ---- Freight room door: #8038 (at X=0 / freight end) ------------------------
wall = wall.cut(Part.makeBox(FREIGHT_DW, WALL_T + CAP_T, FREIGHT_DH,
                              FreeCAD.Vector(F_CX - FREIGHT_DW/2, 0, 0)))
print(f"Freight door #8038: X={F_CX-FREIGHT_DW/2:.1f}..{F_CX+FREIGHT_DW/2:.1f}  H={FREIGHT_DH}")

# ---- Operator bay opening (full TICKET_W wide, full wall height) -------------
wall = wall.cut(Part.makeBox(TICKET_W, WALL_T + CAP_T, WALL_H,
                              FreeCAD.Vector(BAY_X0, 0, 0)))
print(f"Bay opening: X={BAY_X0:.1f}..{BAY_X0+TICKET_W:.1f}  full height")

# ---- Waiting room door: #8033 (at X=BLDG_L / waiting end) ------------------
wall = wall.cut(Part.makeBox(PASS_DOOR_W, WALL_T + CAP_T, PASS_DOOR_H,
                              FreeCAD.Vector(W_CX - PASS_DOOR_W/2, 0, 0)))
print(f"Waiting door #8033: X={W_CX-PASS_DOOR_W/2:.1f}..{W_CX+PASS_DOOR_W/2:.1f}  H={PASS_DOOR_H}")

# ---- Window openings (sill at WAINSCOT_H — no cap rail overlap) -------------
# Waiting room window: near waiting gable end
wall = wall.cut(Part.makeBox(WIN_W, WALL_T, WIN_H,
                              FreeCAD.Vector(W_WIN_CX - WIN_W/2, 0, WIN_SILL)))
print(f"Waiting window #8028/69: X={W_WIN_CX-WIN_W/2:.1f}..{W_WIN_CX+WIN_W/2:.1f}  sill={WIN_SILL}")

# Freight room window: near FT partition
wall = wall.cut(Part.makeBox(WIN_W, WALL_T, WIN_H,
                              FreeCAD.Vector(F_WIN_CX - WIN_W/2, 0, WIN_SILL)))
print(f"Freight window #8028/69: X={F_WIN_CX-WIN_W/2:.1f}..{F_WIN_CX+WIN_W/2:.1f}  sill={WIN_SILL}")

# ---- Partition wall dadoes on interior face ---------------------------------
for px in [X_FT_WALL, X_TW_WALL]:
    wall = wall.cut(Part.makeBox(WALL_T, DADO_D + CAP_T, WALL_H,
                                  FreeCAD.Vector(px, WALL_T - DADO_D, 0)))
print(f"Partition dadoes at X={X_FT_WALL:.1f} (FT) and X={X_TW_WALL:.1f} (TW)  depth={DADO_D}mm + cap {CAP_T}mm")

# ---- 45° miter on cap rail ends at partition wall dadoes --------------------
CAP_Z0 = WAINSCOT_H - CAP_H

for px in [X_FT_WALL, X_TW_WALL]:
    v1 = FreeCAD.Vector(px,         WALL_T,         CAP_Z0)
    v2 = FreeCAD.Vector(px,         WALL_T + CAP_T, CAP_Z0)
    v3 = FreeCAD.Vector(px - CAP_T, WALL_T + CAP_T, CAP_Z0)
    wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
        FreeCAD.Vector(0, 0, CAP_H)))
    cx = px + WALL_T
    v1 = FreeCAD.Vector(cx,           WALL_T,         CAP_Z0)
    v2 = FreeCAD.Vector(cx,           WALL_T + CAP_T, CAP_Z0)
    v3 = FreeCAD.Vector(cx + CAP_T,   WALL_T + CAP_T, CAP_Z0)
    wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
        FreeCAD.Vector(0, 0, CAP_H)))
print(f"Cap rail 45° miters at dado edges (4 cuts)")

# ---- Wainscot grooves on interior face --------------------------------------
n_g = int(BLDG_L / GROOVE_P) + 2
for i in range(n_g):
    gx = i * GROOVE_P
    if gx > BLDG_L: break
    wall = wall.cut(Part.makeBox(GROOVE_W, GROOVE_D, WAINSCOT_H,
                                  FreeCAD.Vector(gx - GROOVE_W/2, WALL_T - GROOVE_D, 0)))
print(f"Wainscot: {n_g} grooves  pitch={GROOVE_P}mm")

# ---- Rabbet on interior face at base ----------------------------------------
wall = wall.cut(Part.makeBox(BLDG_L, RABBET_D, RABBET_H,
                              FreeCAD.Vector(0, WALL_T - RABBET_D, 0)))
print(f"Rabbet: depth={RABBET_D}mm  height={RABBET_H}mm")

# ---- Assembly-aid dado entrance chamfers ------------------------------------
# FT dado: chamfer left wall (X=X_FT_WALL) at entrance corner
v1 = FreeCAD.Vector(X_FT_WALL,          WALL_T,        0)
v2 = FreeCAD.Vector(X_FT_WALL + DADO_D, WALL_T,        0)
v3 = FreeCAD.Vector(X_FT_WALL,          WALL_T - DADO_D, 0)
wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
    FreeCAD.Vector(0, 0, WALL_H)))
# TW dado: chamfer right wall at entrance corner
tw_inner = X_TW_WALL + WALL_T
v1 = FreeCAD.Vector(tw_inner,          WALL_T,          0)
v2 = FreeCAD.Vector(tw_inner - DADO_D, WALL_T,          0)
v3 = FreeCAD.Vector(tw_inner,          WALL_T - DADO_D, 0)
wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
    FreeCAD.Vector(0, 0, WALL_H)))
print(f"Dado entrance chamfers: X={X_FT_WALL:.1f} (FT)  X={tw_inner:.1f} (TW)  {DADO_D}mm 45°")

# ---- 45° miter at both ends -------------------------------------------------
v1 = FreeCAD.Vector(0,       0,     0)
v2 = FreeCAD.Vector(0,       Z_CUT, 0)
v3 = FreeCAD.Vector(Z_CUT,   Z_CUT, 0)
wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
    FreeCAD.Vector(0, 0, WALL_H)))

v1 = FreeCAD.Vector(BLDG_L,          0,     0)
v2 = FreeCAD.Vector(BLDG_L,          Z_CUT, 0)
v3 = FreeCAD.Vector(BLDG_L - Z_CUT,  Z_CUT, 0)
wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
    FreeCAD.Vector(0, 0, WALL_H)))
print(f"Miters at both ends  Z_CUT={Z_CUT}mm")

# ---- Interior door and window frames ----------------------------------------
wall = add_int_frame(wall, F_CX - FREIGHT_DW/2, F_CX + FREIGHT_DW/2, 0, FREIGHT_DH)
wall = add_int_frame(wall, F_WIN_CX - WIN_W/2, F_WIN_CX + WIN_W/2, WIN_SILL, WIN_SILL + WIN_H)
wall = add_int_frame(wall, W_WIN_CX - WIN_W/2, W_WIN_CX + WIN_W/2, WIN_SILL, WIN_SILL + WIN_H)
wall = add_int_frame(wall, W_CX - PASS_DOOR_W/2, W_CX + PASS_DOOR_W/2, 0, PASS_DOOR_H)
print(f"Interior frames: F-door, F-window, W-window, W-door (4 total; bay has no frame)")

# ---- Export -----------------------------------------------------------------
fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/Std_PassengerWall.FCStd"
try: FreeCAD.closeDocument("Std_PassengerWall")
except: pass
doc = FreeCAD.newDocument("Std_PassengerWall")
obj = doc.addObject("Part::Feature", "PassengerWall")
obj.Shape = wall
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/Std_PassengerWall.stl"
MeshPart.meshFromShape(Shape=wall, LinearDeflection=0.05,
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
