#!/usr/bin/env python3
"""
Office interior wall test 2 — WT partition with floor sections, wainscot both faces.

Tests:
  - #8032 interior door (10.30 x 24.45mm), sill at floor
  - Ticket wicket: 7.0 x 7.0mm opening (~2'0" x 2'0" prototype), sill at 3'9" = 13.1mm
      Counter shelf: 1mm thick x 2mm projection on waiting room face
  - Wainscot vertical board grooves (1.5mm pitch) on BOTH wall faces to cap rail
  - Cap rail (continuous full width) on BOTH wall faces
  - Wire channel at siding end: 2.5mm deep x full height x full thickness
  - Floor sections both sides (15mm each): 2.0mm pitch plank grooves on top face

Coordinate system:
  X: wall width (building depth direction, 0=siding end, WALL_W=passenger end)
  Y: perpendicular to wall (building length), wall at Y=0..WALL_T
     waiting room: Y=-FLOOR_L..0,  ticket office: Y=WALL_T..WALL_T+FLOOR_L
  Z: height (floor top Z=0, wall Z=0..WALL_H, floor Z=-FLOOR_T..0)

Print orientation: floor bottom face (Z=-FLOOR_T) down on plate.
  Wall stands up in Z; floor sections are the base layer; no supports needed.

Output:
  FCStd: CADtrains/Station/freecad/OfficeInteriorTest2.FCStd
  STL:   CADtrains/Station/printed_files/OfficeInteriorTest2.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

WALL_W   = 30.0        # test section width (enough for door + wicket)
WALL_H   = ft(10, 6)   # 36.8mm
WALL_T   = 2.0
FLOOR_L  = 15.0        # floor extends each side of wall
FLOOR_T  = 2.0         # floor thickness

WIN_SILL    = 29.70 - 20.05   # 9.65mm
WAINSCOT_H  = WIN_SILL        # cap rail at window sill height
CAP_H       = 1.5
CAP_T       = 0.8

GROOVE_P    = 1.2      # wainscot board pitch (finer than floor)
GROOVE_W    = 0.3
GROOVE_D    = 0.3

PLANK_P     = 2.5      # floor plank pitch (wider than wainscot)
PLANK_W     = 0.3
PLANK_D     = 0.3

DOOR_W      = 10.30    # #8032 interior door
DOOR_H      = 24.75   # 24.45 + 0.30mm print tolerance

WICKET_W    = 7.0      # ticket wicket opening
WICKET_H    = 7.0
WICKET_SILL = ft(3, 9)  # counter height ~13.1mm

SHELF_T     = 1.0      # counter shelf thickness
SHELF_PROJ  = 2.0      # shelf projection into waiting room (-Y direction)
SHELF_EXTRA = 1.0      # shelf overhangs wicket edge each side

CHAN_D = 1.5           # wire channel depth from siding end (X direction)
CHAN_Y = 1.5           # wire channel width (Y, partial thickness — leaves 0.5mm wall)

DOOR_CX   = WALL_T + 2.0 + DOOR_W/2
WICKET_CX = DOOR_CX + DOOR_W/2 + 2.0 + WICKET_W/2

print(f"Wall: {WALL_W}x{WALL_H:.1f}x{WALL_T}mm  Floor: {FLOOR_L}mm each side x {FLOOR_T}mm thick")
print(f"Door #8032 center X={DOOR_CX:.2f}mm  top={DOOR_H:.2f}mm")
print(f"Wicket center X={WICKET_CX:.2f}mm  sill={WICKET_SILL:.2f}mm  top={WICKET_SILL+WICKET_H:.2f}mm")
print(f"WAINSCOT_H={WAINSCOT_H:.2f}mm  WIN_SILL={WIN_SILL:.2f}mm")

# ---- Base geometry ----------------------------------------------------------

wall  = Part.makeBox(WALL_W, WALL_T, WALL_H)
# Single continuous floor slab spanning full width — under wall and both room sides
floor = Part.makeBox(WALL_W, FLOOR_L*2 + WALL_T, FLOOR_T,
                     FreeCAD.Vector(0, -FLOOR_L, -FLOOR_T))
body = wall.fuse(floor)

# ---- Cap rail on both faces BEFORE door cut ---------------------------------
# Fusing first then cutting openings means the door/wicket remove the cap rail
# in those zones naturally — no manual splitting needed.
body = body.fuse(Part.makeBox(WALL_W, CAP_T, CAP_H,
                               FreeCAD.Vector(0, -CAP_T, WAINSCOT_H - CAP_H)))
body = body.fuse(Part.makeBox(WALL_W, CAP_T, CAP_H,
                               FreeCAD.Vector(0, WALL_T, WAINSCOT_H - CAP_H)))

# ---- Openings (cut after cap rail so door removes cap rail in doorway) ------

# Door: extends in Y to include cap rail protrusions on both faces
body = body.cut(Part.makeBox(DOOR_W, WALL_T + 2*CAP_T, DOOR_H,
                              FreeCAD.Vector(DOOR_CX - DOOR_W/2, -CAP_T, 0)))

# Ticket wicket (full wall thickness, above counter)
body = body.cut(Part.makeBox(WICKET_W, WALL_T, WICKET_H,
                              FreeCAD.Vector(WICKET_CX - WICKET_W/2, 0, WICKET_SILL)))

# Counter shelf on waiting room face (Y=0), protrudes into waiting room (-Y)
body = body.fuse(Part.makeBox(WICKET_W + 2*SHELF_EXTRA, SHELF_PROJ, SHELF_T,
                               FreeCAD.Vector(WICKET_CX - WICKET_W/2 - SHELF_EXTRA,
                                              -SHELF_PROJ,
                                              WICKET_SILL - SHELF_T)))

# Wire channel: partial-thickness notch at siding end corner, full wall height.
# Sealed by exterior siding wall when assembled. 1.5x1.5mm — holds 2x 30ga wire easily.
body = body.cut(Part.makeBox(CHAN_D, CHAN_Y, WALL_H, FreeCAD.Vector(0, 0, 0)))

# ---- Wainscot grooves on both wall faces (Z=0..WAINSCOT_H) ------------------

n_g = int(WALL_W / GROOVE_P) + 2
for i in range(n_g):
    gx = i * GROOVE_P
    if gx > WALL_W:
        break
    x0 = gx - GROOVE_W / 2
    body = body.cut(Part.makeBox(GROOVE_W, GROOVE_D, WAINSCOT_H,
                                  FreeCAD.Vector(x0, 0, 0)))
    body = body.cut(Part.makeBox(GROOVE_W, GROOVE_D, WAINSCOT_H,
                                  FreeCAD.Vector(x0, WALL_T - GROOVE_D, 0)))
print(f"Wainscot: {n_g} groove positions x2 faces  pitch={GROOVE_P}mm")

# ---- Floor plank grooves (run in Y, spaced in X at 2.0mm pitch) -------------
# Cut from floor top surface (Z=0) downward by PLANK_D

n_p = int(WALL_W / PLANK_P) + 2
for i in range(n_p):
    gx = i * PLANK_P
    if gx > WALL_W:
        break
    x0 = gx - PLANK_W / 2
    body = body.cut(Part.makeBox(PLANK_W, FLOOR_L, PLANK_D,
                                  FreeCAD.Vector(x0, -FLOOR_L, -PLANK_D)))
    body = body.cut(Part.makeBox(PLANK_W, FLOOR_L, PLANK_D,
                                  FreeCAD.Vector(x0, WALL_T, -PLANK_D)))
print(f"Floor planks: {n_p} groove positions x2 sides  pitch={PLANK_P}mm")

# ---- Export -----------------------------------------------------------------

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/OfficeInteriorTest2.FCStd"
try: FreeCAD.closeDocument("OfficeInteriorTest2")
except: pass
doc = FreeCAD.newDocument("OfficeInteriorTest2")
obj = doc.addObject("Part::Feature", "OfficeInterior")
obj.Shape = body
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/OfficeInteriorTest2.stl"
MeshPart.meshFromShape(Shape=body, LinearDeflection=0.05,
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
