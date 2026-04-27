#!/usr/bin/env python3
"""
SK station — gable end wall panel.

Both gable ends (waiting end and freight end) are identical — print two.
Building depth (exterior face to exterior face): BLDG_D = ft(15,0) ~52.6mm.

Coordinate system:
  X: building depth direction (siding face → passenger face)
  Y: wall thickness (0 = exterior face, WALL_T = interior face)
  Z: height (0 = floor, WALL_H = wall top)

Openings:
  - Gable window: #8070 double window  19.00×19.85mm  sill at WAINSCOT_H=9.65mm  centered X

Interior face (Y=WALL_T):
  - Wainscot grooves 1.2mm pitch, Z=0..WAINSCOT_H, depth 0.3mm from face
  - Cap rail continuous full width
  - NO partition wall dadoes (partition walls do not connect to gable ends)

Ends: 45° miter at both ends (X=0 and X=BLDG_D) to mate with siding and passenger walls.
Base: 1.0mm deep × 1.5mm tall rabbet on interior face.

Print orientation: face-down (exterior face Y=0 on plate); wall stands up in Z.
Print qty: 2 (one per end).

Output:
  FCStd: CADtrains/Station/freecad/SK_GableWall.FCStd
  STL:   CADtrains/Station/printed_files/SK_GableWall.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Dimensions -------------------------------------------------------------
WALL_T    = 2.0
WALL_H    = ft(10, 6)    # 36.8mm
BLDG_D    = 40.0         # SK site limit (standard would be ft(15,0)=52.6mm)

# ---- Interior face details --------------------------------------------------
WAINSCOT_H = 9.65
CAP_H      = 1.5
CAP_T      = 0.8
Z_CUT      = WALL_T + CAP_T   # 2.8mm — miter cut depth

GROOVE_P   = 1.2
GROOVE_W   = 0.3
GROOVE_D   = 0.3

# ---- Rabbet at base ---------------------------------------------------------
RABBET_D   = 1.0
RABBET_H   = 1.5

# ---- Tichy #8070 double window ----------------------------------------------
WIN_W    = 19.00   # #8070 double unit window
WIN_H    = 19.85
WIN_SILL = WAINSCOT_H   # 9.65mm  (win top = 29.30mm)
WIN_CX   = BLDG_D / 2   # centered on gable

FRAME_D = 0.6    # interior frame proud of interior face
FRAME_W = 1.45   # frame leg width

def add_int_frame(shape, x0, x1, z0, z1):
    """Raised interior frame: FRAME_W × FRAME_D legs + head."""
    shape = shape.fuse(Part.makeBox(FRAME_W, FRAME_D, z1-z0+FRAME_W, FreeCAD.Vector(x0-FRAME_W, WALL_T, z0)))
    shape = shape.fuse(Part.makeBox(FRAME_W, FRAME_D, z1-z0+FRAME_W, FreeCAD.Vector(x1,         WALL_T, z0)))
    shape = shape.fuse(Part.makeBox(x1-x0+2*FRAME_W, FRAME_D, FRAME_W, FreeCAD.Vector(x0-FRAME_W, WALL_T, z1)))
    return shape

print(f"SK Gable Wall: {BLDG_D:.1f} x {WALL_H:.1f} x {WALL_T}mm  (print qty: 2)")
print(f"Window #8070: X={WIN_CX-WIN_W/2:.1f}..{WIN_CX+WIN_W/2:.1f}  sill={WIN_SILL}  top={WIN_SILL+WIN_H:.2f}")
print(f"Z_CUT={Z_CUT}mm  WAINSCOT_H={WAINSCOT_H}mm")

# ---- Base wall --------------------------------------------------------------
wall = Part.makeBox(BLDG_D, WALL_T, WALL_H)

# ---- Cap rail on interior face — fuse BEFORE window cut ---------------------
wall = wall.fuse(Part.makeBox(BLDG_D, CAP_T, CAP_H,
                               FreeCAD.Vector(0, WALL_T, WAINSCOT_H - CAP_H)))

# ---- Window opening: #8070 --------------------------------------------------
# Window sill is at WAINSCOT_H — cap rail ends there, no cap rail overlap needed
wall = wall.cut(Part.makeBox(WIN_W, WALL_T, WIN_H,
                              FreeCAD.Vector(WIN_CX - WIN_W/2, 0, WIN_SILL)))
print(f"Window cut: Y=0..{WALL_T}  (no cap rail overlap — sill at cap rail top)")

# ---- Wainscot grooves on interior face --------------------------------------
n_g = int(BLDG_D / GROOVE_P) + 2
for i in range(n_g):
    gx = i * GROOVE_P
    if gx > BLDG_D: break
    wall = wall.cut(Part.makeBox(GROOVE_W, GROOVE_D, WAINSCOT_H,
                                  FreeCAD.Vector(gx - GROOVE_W/2, WALL_T - GROOVE_D, 0)))
print(f"Wainscot: {n_g} grooves  pitch={GROOVE_P}mm")

# ---- Rabbet on interior face at base ----------------------------------------
wall = wall.cut(Part.makeBox(BLDG_D, RABBET_D, RABBET_H,
                              FreeCAD.Vector(0, WALL_T - RABBET_D, 0)))
print(f"Rabbet: depth={RABBET_D}mm  height={RABBET_H}mm")

# ---- 45° miter at both ends (mates with siding and passenger wall miters) ---
# Waiting/siding end (X=0)
v1 = FreeCAD.Vector(0,       0,     0)
v2 = FreeCAD.Vector(0,       Z_CUT, 0)
v3 = FreeCAD.Vector(Z_CUT,   Z_CUT, 0)
wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
    FreeCAD.Vector(0, 0, WALL_H)))

# Freight/passenger end (X=BLDG_D)
v1 = FreeCAD.Vector(BLDG_D,          0,     0)
v2 = FreeCAD.Vector(BLDG_D,          Z_CUT, 0)
v3 = FreeCAD.Vector(BLDG_D - Z_CUT,  Z_CUT, 0)
wall = wall.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(
    FreeCAD.Vector(0, 0, WALL_H)))
print(f"Miters at both ends  Z_CUT={Z_CUT}mm")

# ---- Interior window frame (raised, 0.6mm × 1.45mm) -------------------------
wall = add_int_frame(wall, WIN_CX - WIN_W/2, WIN_CX + WIN_W/2, WIN_SILL, WIN_SILL + WIN_H)
print(f"Interior frame: gable #8070 window (sill={WIN_SILL})")

# ---- Export -----------------------------------------------------------------
fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/SK_GableWall.FCStd"
try: FreeCAD.closeDocument("SK_GableWall")
except: pass
doc = FreeCAD.newDocument("SK_GableWall")
obj = doc.addObject("Part::Feature", "GableWall")
obj.Shape = wall
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/SK_GableWall.stl"
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
