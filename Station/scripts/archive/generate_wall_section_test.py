#!/usr/bin/env python3
"""
Wall section test print — short section of a detail-model wall panel.

Tests before committing to full wall CAD:
  - Wall thickness rigidity (WALL_T = 2mm face-down)
  - Tichy #8028/#8069 opening fit (9.38 x 19.85mm)
  - 45° miter end geometry — check joint closes cleanly against another mitered piece
  - Interior relief detail readability at HO scale:
      wainscot cap rail, notice board placeholder, clock disc
  - Face-down print surface quality for embossed styrene adhesion

Orientation for printing: exterior face DOWN (Z=0 on plate).
  X = wall length, Y = wall height (lying along Y), Z = wall thickness (print direction)

WALL_H = 35.9mm (working value: 10'6" prototype HO).
  *** Confirm final wall height before scripting full wall panels. ***
  Adjust WALL_H here to test a different value.

Output:
  FreeCAD: CADtrains/Station/freecad/WallSectionTest.FCStd
  STL:     CADtrains/Station/printed_files/WallSectionTest.stl
"""

import xmlrpc.client
import sys

proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os, math

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Dimensions -------------------------------------------------------

WALL_L   = 50.0          # test section length (mm)
WALL_H   = ft(10, 6)     # working wall height ~35.9mm (10'6" prototype) -- CONFIRM before full print
WALL_T   = 2.0           # wall thickness

WIN_W    = 9.38          # #8028/#8069 opening width
WIN_H    = 19.85         # #8028/#8069 opening height
WIN_SILL = ft(2, 0)      # ~2' sill height = 6.9mm HO

WAINSCOT_H = ft(3, 6)    # wainscot zone height ~12.3mm (3'6" prototype -- chair rail height)
CAP_H      = 1.5         # cap rail band height (mm)
CAP_T      = 0.8         # cap rail proud of interior face

NOTICE_W   = 8.0         # notice board placeholder width
NOTICE_H   = 5.0         # notice board placeholder height
NOTICE_T   = 0.5         # notice board relief depth

CLOCK_R    = 1.0         # clock disc radius (2mm dia = ~7" prototype)
CLOCK_T    = 0.5         # clock disc relief height

print(f"Wall section: {WALL_L:.0f}mm x {WALL_H:.1f}mm x {WALL_T:.0f}mm")
print(f"  Window:    {WIN_W:.2f} x {WIN_H:.2f}mm  sill at {WIN_SILL:.1f}mm")
print(f"  Wainscot:  {WAINSCOT_H:.1f}mm high  cap rail {CAP_H:.1f}mm x {CAP_T:.1f}mm proud")
print(f"  Clearance above window: {WALL_H - WIN_SILL - WIN_H:.1f}mm")

# ---- Build wall -------------------------------------------------------

wall = Part.makeBox(WALL_L, WALL_H, WALL_T)

# Window opening: centered in section, cuts full thickness
cx = WALL_L / 2
notch = Part.makeBox(WIN_W, WIN_H, WALL_T,
                     FreeCAD.Vector(cx - WIN_W/2, WIN_SILL, 0))
wall = wall.cut(notch)

# ---- Interior face relief (protrudes from Z=WALL_T) -------------------

# Wainscot cap rail: two segments either side of window opening
# Window spans cx-WIN_W/2 to cx+WIN_W/2 in X; cap rail stops at those edges.
cap_left = Part.makeBox(cx - WIN_W/2, CAP_H, CAP_T,
                        FreeCAD.Vector(0, WAINSCOT_H - CAP_H, WALL_T))
cap_right = Part.makeBox(WALL_L - (cx + WIN_W/2), CAP_H, CAP_T,
                         FreeCAD.Vector(cx + WIN_W/2, WAINSCOT_H - CAP_H, WALL_T))
wall = wall.fuse(cap_left).fuse(cap_right)

# Notice board placeholder: left of window, above wainscot
nb_x = cx - WIN_W/2 - NOTICE_W - 3.0   # 3mm gap from window edge
nb_y = WAINSCOT_H + 2.0
if nb_x > 2.0:   # only if there is room
    nb = Part.makeBox(NOTICE_W, NOTICE_H, NOTICE_T,
                      FreeCAD.Vector(nb_x, nb_y, WALL_T))
    wall = wall.fuse(nb)

# Clock disc: above window center
clock_y = WIN_SILL + WIN_H + 3.0
if clock_y + CLOCK_R < WALL_H - 1.0:   # only if there is room
    clock = Part.makeCylinder(
        CLOCK_R, CLOCK_T,
        FreeCAD.Vector(cx, clock_y, WALL_T),
        FreeCAD.Vector(0, 0, 1)
    )
    wall = wall.fuse(clock)

# ---- 45-degree miter at right end ------------------------------------
# Cuts triangle from interior face corner so two walls join at 45°.
# In XZ plane: removes vertices (WALL_L, WALL_T), (WALL_L-WALL_T, WALL_T), (WALL_L, 0).
# Exterior face retains sharp corner at X=WALL_L; interior face bevels back WALL_T.

v1 = FreeCAD.Vector(WALL_L,          0,      0)
v2 = FreeCAD.Vector(WALL_L,          0,      WALL_T)
v3 = FreeCAD.Vector(WALL_L - WALL_T, 0,      WALL_T)
wire = Part.makePolygon([v1, v2, v3, v1])
miter_cut = Part.Face(wire).extrude(FreeCAD.Vector(0, WALL_H, 0))
wall = wall.cut(miter_cut)

# ---- Export -----------------------------------------------------------

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/WallSectionTest.FCStd"
os.makedirs(os.path.dirname(fc_path), exist_ok=True)

try: FreeCAD.closeDocument("WallSectionTest")
except: pass
doc = FreeCAD.newDocument("WallSectionTest")
obj = doc.addObject("Part::Feature", "WallSection")
obj.Shape = wall
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)
mesh = MeshPart.meshFromShape(Shape=wall, LinearDeflection=0.05,
                               AngularDeflection=0.1, Relative=False)
out = os.path.join(stl_dir, "WallSectionTest.stl")
mesh.write(out)
print(f"Wrote {out}")

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
