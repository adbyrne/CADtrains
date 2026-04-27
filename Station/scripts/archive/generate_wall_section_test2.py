#!/usr/bin/env python3
"""
Wall section test 2 — three sections: miter joint test + door fit tests.

Section A: #8028/69 window (WIN_H +0.2mm fix), miter RIGHT end
Section B: #8033 passenger door (9.55x29.70mm), miter LEFT end
           A + B held at 90° confirm the miter joint closes flush.
Section C: #8038 freight door (30.38x34.80mm), no miter — standalone fit test

All sections: WALL_T=2mm, WALL_H=10'6" (~35.9mm), face-down print orientation
(exterior face on build plate at Z=0).

Fixes from WallSectionTest v1:
  - Miter cut now extends to Z = WALL_T + CAP_T (2.8mm) so cap rail is included.
  - Clock radius increased from 1.0mm to 1.5mm.
  - WIN_H for #8028/69 increased from 19.85 to 20.05mm (+0.2mm).

Output:
  FCStd: CADtrains/Station/freecad/WallSectionTest2.FCStd
  STLs:  CADtrains/Station/printed_files/WallTest2_{A_Window,B_Door,C_FreightDoor}.stl
"""

import xmlrpc.client
import sys

proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os, math

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Global wall parameters (same for all sections) ----------------------

WALL_H     = ft(10, 6)   # working wall height ~35.9mm (10\'6" prototype)
WALL_T     = 2.0          # wall thickness
WAINSCOT_H = ft(3, 6)    # cap rail zone height ~12.3mm (3\'6" prototype)
CAP_H      = 1.5          # cap rail band height
CAP_T      = 0.8          # cap rail proud of interior face
Z_CUT      = WALL_T + CAP_T   # 2.8mm — miter extends to cover cap rail protrusion
CLOCK_R    = 1.5          # clock disc radius (increased from 1.0mm)
CLOCK_T    = 0.5
NOTICE_W   = 8.0
NOTICE_H   = 5.0
NOTICE_T   = 0.5

print(f"Wall height: {WALL_H:.2f}mm  Wall thickness: {WALL_T}mm  Z_CUT: {Z_CUT}mm")
print(f"Wainscot: {WAINSCOT_H:.2f}mm  Clock radius: {CLOCK_R}mm")

# ---- Helper: build one wall section --------------------------------------

def make_section(label, WALL_L, opening_w, opening_h, opening_sill,
                 miter_right=False, miter_left=False, add_relief=True):
    """
    Build one wall section with a centered opening.
    Miter cuts are applied after relief features so cap rail is included.
    """
    wall = Part.makeBox(WALL_L, WALL_H, WALL_T)

    # Opening centered in section, cuts full thickness
    cx = WALL_L / 2
    notch = Part.makeBox(opening_w, opening_h, WALL_T,
                         FreeCAD.Vector(cx - opening_w / 2, opening_sill, 0))
    wall = wall.cut(notch)

    if add_relief:
        # Wainscot cap rail: two segments either side of the opening
        left_w  = cx - opening_w / 2
        right_w = WALL_L - (cx + opening_w / 2)

        if left_w > 0.5:
            cap_left = Part.makeBox(
                left_w, CAP_H, CAP_T,
                FreeCAD.Vector(0, WAINSCOT_H - CAP_H, WALL_T))
            wall = wall.fuse(cap_left)

        if right_w > 0.5:
            cap_right = Part.makeBox(
                right_w, CAP_H, CAP_T,
                FreeCAD.Vector(cx + opening_w / 2, WAINSCOT_H - CAP_H, WALL_T))
            wall = wall.fuse(cap_right)

        # Notice board: left of opening, above wainscot
        nb_x = cx - opening_w / 2 - NOTICE_W - 3.0
        nb_y = WAINSCOT_H + 2.0
        if nb_x > 2.0 and nb_y + NOTICE_H < WALL_H - 1.0:
            nb = Part.makeBox(NOTICE_W, NOTICE_H, NOTICE_T,
                              FreeCAD.Vector(nb_x, nb_y, WALL_T))
            wall = wall.fuse(nb)

        # Clock disc: above opening center
        clock_y = opening_sill + opening_h + 3.0
        if clock_y + CLOCK_R + 1.0 < WALL_H:
            clock = Part.makeCylinder(
                CLOCK_R, CLOCK_T,
                FreeCAD.Vector(cx, clock_y, WALL_T),
                FreeCAD.Vector(0, 0, 1))
            wall = wall.fuse(clock)

    # Miter cuts applied AFTER relief so cap rail protrusion is included
    if miter_right:
        v1 = FreeCAD.Vector(WALL_L,          0, 0)
        v2 = FreeCAD.Vector(WALL_L,          0, Z_CUT)
        v3 = FreeCAD.Vector(WALL_L - Z_CUT,  0, Z_CUT)
        wire = Part.makePolygon([v1, v2, v3, v1])
        miter = Part.Face(wire).extrude(FreeCAD.Vector(0, WALL_H, 0))
        wall = wall.cut(miter)
        print(f"  {label}: miter right  Z_CUT={Z_CUT}mm")

    if miter_left:
        v1 = FreeCAD.Vector(0,      0, 0)
        v2 = FreeCAD.Vector(0,      0, Z_CUT)
        v3 = FreeCAD.Vector(Z_CUT,  0, Z_CUT)
        wire = Part.makePolygon([v1, v2, v3, v1])
        miter = Part.Face(wire).extrude(FreeCAD.Vector(0, WALL_H, 0))
        wall = wall.cut(miter)
        print(f"  {label}: miter left   Z_CUT={Z_CUT}mm")

    return wall


# ---- Build three sections ------------------------------------------------

print("\\nSection A: #8028/69 window, miter right")
secA = make_section("A_Window",
    WALL_L=50.0,
    opening_w=9.38, opening_h=20.05, opening_sill=ft(2, 0),
    miter_right=True, miter_left=False,
    add_relief=True)
print(f"  opening: 9.38 x 20.05mm  sill at {ft(2,0):.2f}mm")

print("\\nSection B: #8033 passenger door, miter left")
secB = make_section("B_Door",
    WALL_L=50.0,
    opening_w=9.55, opening_h=29.70, opening_sill=0.0,
    miter_right=False, miter_left=True,
    add_relief=True)
print(f"  opening: 9.55 x 29.70mm  sill at 0.0mm (floor level)")

print("\\nSection C: #8038 freight door, no miter")
secC = make_section("C_FreightDoor",
    WALL_L=50.0,
    opening_w=30.38, opening_h=34.80, opening_sill=0.0,
    miter_right=False, miter_left=False,
    add_relief=True)
print(f"  opening: 30.38 x 34.80mm  sill at 0.0mm (floor level)")
print(f"  wall material each side of door: {(50.0 - 30.38) / 2:.2f}mm")

print("\\nSection D: #8125 freight door/transom, no miter (SK half-size freight room only)")
secD = make_section("D_FreightDoor8125",
    WALL_L=50.0,
    opening_w=23.9, opening_h=32.65, opening_sill=0.0,
    miter_right=False, miter_left=False,
    add_relief=True)
print(f"  opening: 23.9 x 32.65mm  sill at 0.0mm (floor level)")
print(f"  wall material each side of door: {(50.0 - 23.9) / 2:.2f}mm")
print(f"  compare to #8038: {30.38 - 23.9:.2f}mm narrower, {34.80 - 32.65:.2f}mm shorter")

# ---- FreeCAD document with all three sections ----------------------------

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/WallSectionTest2.FCStd"
os.makedirs(os.path.dirname(fc_path), exist_ok=True)

try: FreeCAD.closeDocument("WallSectionTest2")
except: pass
doc = FreeCAD.newDocument("WallSectionTest2")

GAP = 10.0   # Y spacing between sections in document

for name, shape, y_offset in [
    ("Section_A_Window",          secA, 0),
    ("Section_B_Door",            secB, WALL_H + GAP),
    ("Section_C_FreightDoor8038", secC, (WALL_H + GAP) * 2),
    ("Section_D_FreightDoor8125", secD, (WALL_H + GAP) * 3),
]:
    obj = doc.addObject("Part::Feature", name)
    placed = shape.copy()
    placed.translate(FreeCAD.Vector(0, y_offset, 0))
    obj.Shape = placed

doc.recompute()
doc.saveAs(fc_path)
print(f"\\nSaved {fc_path}")

# ---- Export STLs ---------------------------------------------------------

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)

for tag, shape in [
    ("A_Window",          secA),
    ("B_Door",            secB),
    ("C_FreightDoor8038", secC),
    ("D_FreightDoor8125", secD),
]:
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                   AngularDeflection=0.1, Relative=False)
    out = os.path.join(stl_dir, f"WallTest2_{tag}.stl")
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
