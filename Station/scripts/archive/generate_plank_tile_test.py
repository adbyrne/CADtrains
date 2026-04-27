#!/usr/bin/env python3
"""
Floor plank tile test print.

Two zones on one tile to compare groove readability side by side:
  Zone A (left 30mm):  1.5mm pitch planks (~5.1" prototype)
  Zone B (right 30mm): 2.0mm pitch planks (~6.9" prototype)

Both use 0.3mm wide x 0.3mm deep grooves running the full length (X axis).
Tile: 60mm (X) x 20mm (Y) x 3mm (Z).  Print flat, groove side up.

Pick whichever zone reads better after printing; use that pitch in the floor piece.

Output:
  FreeCAD: CADtrains/Station/freecad/PlankTileTest.FCStd
  STL:     CADtrains/Station/printed_files/PlankTileTest.stl
"""

import xmlrpc.client
import sys

proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

TILE_L   = 60.0   # total tile length (two 30mm zones)
TILE_W   = 20.0   # tile width
TILE_T   = 3.0    # tile thickness
ZONE_L   = TILE_L / 2   # 30mm per zone

GROOVE_W = 0.3    # groove width (mm)
GROOVE_D = 0.3    # groove depth (mm)

PITCH_A  = 1.5    # zone A plank pitch (~4.3" prototype)
PITCH_B  = 2.0    # zone B plank pitch (~5.8" prototype)

tile = Part.makeBox(TILE_L, TILE_W, TILE_T)

def cut_grooves(shape, x_start, x_end, pitch):
    """Cut parallel grooves along X direction at given Y pitch."""
    y = pitch
    while y < TILE_W:
        groove = Part.makeBox(
            x_end - x_start, GROOVE_W, GROOVE_D,
            FreeCAD.Vector(x_start, y - GROOVE_W/2, TILE_T - GROOVE_D)
        )
        shape = shape.cut(groove)
        y += pitch
    return shape

tile = cut_grooves(tile, 0,       ZONE_L, PITCH_A)
tile = cut_grooves(tile, ZONE_L,  TILE_L, PITCH_B)

# Dividing line between zones: shallow notch so zones are easy to distinguish
div = Part.makeBox(0.5, TILE_W, GROOVE_D * 2,
                   FreeCAD.Vector(ZONE_L - 0.25, 0, TILE_T - GROOVE_D * 2))
tile = tile.cut(div)

n_a = int(TILE_W / PITCH_A)
n_b = int(TILE_W / PITCH_B)
inch = chr(34)
print(f"Zone A (left):  pitch={PITCH_A}mm  ~{PITCH_A*87/25.4:.1f}{inch} prototype  {n_a} grooves")
print(f"Zone B (right): pitch={PITCH_B}mm  ~{PITCH_B*87/25.4:.1f}{inch} prototype  {n_b} grooves")

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/PlankTileTest.FCStd"
os.makedirs(os.path.dirname(fc_path), exist_ok=True)

try: FreeCAD.closeDocument("PlankTileTest")
except: pass
doc = FreeCAD.newDocument("PlankTileTest")
obj = doc.addObject("Part::Feature", "PlankTile")
obj.Shape = tile
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)
mesh = MeshPart.meshFromShape(Shape=tile, LinearDeflection=0.05,
                               AngularDeflection=0.1, Relative=False)
out = os.path.join(stl_dir, "PlankTileTest.stl")
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
