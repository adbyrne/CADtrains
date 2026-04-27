#!/usr/bin/env python3
"""
Wall section test 3 — updated sill + wainscot vertical board paneling.

Changes from v2:
  - WIN_SILL = 9.65mm (window tops aligned to #8033 door top at 29.70mm)
  - WAINSCOT_H = WIN_SILL = 9.65mm (cap rail sits at window sill height)
  - Wainscot paneling: 1.5mm-pitch vertical board grooves on interior face, floor to cap rail

Single section, miter right end.

Output:
  FCStd: CADtrains/Station/freecad/WallSectionTest3.FCStd
  STL:   CADtrains/Station/printed_files/WallTest3_Window.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

WALL_L   = 50.0
WALL_H   = ft(10, 6)     # 36.8mm working wall height
WALL_T   = 2.0

WIN_W    = 9.38
WIN_H    = 20.05          # confirmed +0.2mm fix
WIN_SILL = 29.70 - WIN_H  # 9.65mm — tops aligned to #8033 door

WAINSCOT_H = WIN_SILL     # cap rail at window sill height = 9.65mm
CAP_H      = 1.5
CAP_T      = 0.8
Z_CUT      = WALL_T + CAP_T  # 2.8mm miter depth

GROOVE_P   = 1.5          # wainscot board pitch (mm)
GROOVE_W   = 0.3
GROOVE_D   = 0.3          # depth from interior face

CLOCK_R    = 1.5
CLOCK_T    = 0.5
NOTICE_W   = 8.0
NOTICE_H   = 5.0
NOTICE_T   = 0.5

print(f"WIN_SILL={WIN_SILL:.2f}mm  WAINSCOT_H={WAINSCOT_H:.2f}mm  (both = {WIN_SILL*87/25.4:.1f} prototype inches)")
print(f"Window top={WIN_SILL+WIN_H:.2f}mm  Door top=29.70mm  diff={(WIN_SILL+WIN_H)-29.70:.2f}mm")

wall = Part.makeBox(WALL_L, WALL_H, WALL_T)

# Window opening
cx = WALL_L / 2
notch = Part.makeBox(WIN_W, WIN_H, WALL_T, FreeCAD.Vector(cx - WIN_W/2, WIN_SILL, 0))
wall = wall.cut(notch)

# Wainscot vertical board grooves on interior face (Z = WALL_T - GROOVE_D to WALL_T)
n = int(WALL_L / GROOVE_P) + 1
for i in range(n):
    gx = i * GROOVE_P
    if gx > WALL_L:
        break
    g = Part.makeBox(GROOVE_W, WAINSCOT_H, GROOVE_D,
                     FreeCAD.Vector(gx - GROOVE_W/2, 0, WALL_T - GROOVE_D))
    wall = wall.cut(g)
print(f"Cut {n} wainscot grooves  pitch={GROOVE_P}mm")

# Cap rail: continuous full width — WIN_SILL == WAINSCOT_H so window starts
# exactly where rail ends; no overlap, no split needed.
wall = wall.fuse(Part.makeBox(WALL_L, CAP_H, CAP_T,
                               FreeCAD.Vector(0, WAINSCOT_H - CAP_H, WALL_T)))

# Notice board left of window
nb_x = cx - WIN_W/2 - NOTICE_W - 3.0
nb_y = WAINSCOT_H + 2.0
if nb_x > 2.0 and nb_y + NOTICE_H < WALL_H - 1.0:
    wall = wall.fuse(Part.makeBox(NOTICE_W, NOTICE_H, NOTICE_T,
                                   FreeCAD.Vector(nb_x, nb_y, WALL_T)))

# Clock disc above window
clock_y = WIN_SILL + WIN_H + 3.0
if clock_y + CLOCK_R + 1.0 < WALL_H:
    wall = wall.fuse(Part.makeCylinder(CLOCK_R, CLOCK_T,
                                        FreeCAD.Vector(cx, clock_y, WALL_T),
                                        FreeCAD.Vector(0, 0, 1)))

# Miter right end (includes cap rail)
v1 = FreeCAD.Vector(WALL_L,          0, 0)
v2 = FreeCAD.Vector(WALL_L,          0, Z_CUT)
v3 = FreeCAD.Vector(WALL_L - Z_CUT,  0, Z_CUT)
wall = wall.cut(Part.Face(Part.makePolygon([v1,v2,v3,v1])).extrude(FreeCAD.Vector(0,WALL_H,0)))

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/WallSectionTest3.FCStd"
try: FreeCAD.closeDocument("WallSectionTest3")
except: pass
doc = FreeCAD.newDocument("WallSectionTest3")
obj = doc.addObject("Part::Feature", "WallSection")
obj.Shape = wall
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/WallTest3_Window.stl"
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
