#!/usr/bin/env python3
"""
Office interior wall test — waiting/ticket (WT) partition wall.

Tests:
  - #8032 interior door (10.30 x 24.45mm), sill at floor
  - Ticket wicket: window-like opening with integral counter shelf
      Counter at 3'9" = 13.1mm; opening 3.5mm wide x 4.1mm tall above counter
      Shelf: 1mm thick x 2mm projection on waiting room face
  - Wire channel slot at siding-face end: 2.5mm deep x full height x full thickness
      Covered by siding exterior wall when assembled; holds 2x 30-32ga wires

Coordinate system (wall panel lying flat, print face-down):
  X = wall width = building depth (SK: 42mm, siding end at X=0)
  Y = wall height = WALL_H
  Z = wall thickness = WALL_T (Z=0 = ticket office face on plate; Z=WALL_T = waiting room face)

Print orientation: flat, ticket office face (Z=0) down.

Output:
  FCStd: CADtrains/Station/freecad/OfficeInteriorTest.FCStd
  STL:   CADtrains/Station/printed_files/OfficeInteriorTest.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

WALL_W   = ft(12, 0)      # SK building depth = 42mm (wall width in X)
WALL_H   = ft(10, 6)      # 36.8mm
WALL_T   = 2.0

# #8032 interior door
DOOR_W   = 10.30
DOOR_H   = 24.45

# Ticket wicket
WICKET_W     = 3.5         # opening width
WICKET_H     = 4.1         # opening height above counter
WICKET_SILL  = ft(3, 9)   # counter height ~13.1mm (~3\'9" prototype)
SHELF_T      = 1.0         # shelf thickness
SHELF_PROJ   = 2.0         # shelf projection into waiting room (from waiting face)
SHELF_EXTRA  = 1.0         # shelf extends past wicket edge each side

# Wire channel at siding end (X=0): runs full height, full thickness
CHAN_D = 2.5               # depth into wall from siding end (X direction)

# Position: door near siding end, wicket beside door (toward passenger side)
DOOR_CX  = WALL_T + 2.0 + DOOR_W / 2          # ~9.15mm from siding end
WICKET_CX = DOOR_CX + DOOR_W/2 + 2.0 + WICKET_W/2   # beside door

print(f"Wall: {WALL_W:.1f} x {WALL_H:.1f} x {WALL_T}mm")
print(f"Door #8032 center X={DOOR_CX:.2f}mm  sill=0  top={DOOR_H:.2f}mm")
print(f"Wicket center X={WICKET_CX:.2f}mm  sill={WICKET_SILL:.2f}mm  top={WICKET_SILL+WICKET_H:.2f}mm")
print(f"Wire channel: X=0..{CHAN_D}mm  full Z+Y")

wall = Part.makeBox(WALL_W, WALL_H, WALL_T)

# Interior door (full thickness cut)
door = Part.makeBox(DOOR_W, DOOR_H, WALL_T,
                    FreeCAD.Vector(DOOR_CX - DOOR_W/2, 0, 0))
wall = wall.cut(door)

# Ticket wicket opening (full thickness cut)
wicket = Part.makeBox(WICKET_W, WICKET_H, WALL_T,
                      FreeCAD.Vector(WICKET_CX - WICKET_W/2, WICKET_SILL, 0))
wall = wall.cut(wicket)

# Counter shelf on waiting room face (Z=WALL_T), protrudes in +Z
shelf = Part.makeBox(WICKET_W + 2*SHELF_EXTRA, SHELF_T, SHELF_PROJ,
                     FreeCAD.Vector(WICKET_CX - WICKET_W/2 - SHELF_EXTRA,
                                    WICKET_SILL - SHELF_T,
                                    WALL_T))
wall = wall.fuse(shelf)

# Wire channel at siding end: notch from X=0, full height, full thickness
chan = Part.makeBox(CHAN_D, WALL_H, WALL_T, FreeCAD.Vector(0, 0, 0))
wall = wall.cut(chan)
print(f"Wire channel notch: {CHAN_D}mm deep x {WALL_H:.1f}mm tall x {WALL_T}mm wide")

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/OfficeInteriorTest.FCStd"
try: FreeCAD.closeDocument("OfficeInteriorTest")
except: pass
doc = FreeCAD.newDocument("OfficeInteriorTest")
obj = doc.addObject("Part::Feature", "InteriorWall")
obj.Shape = wall
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/OfficeInteriorTest.stl"
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
