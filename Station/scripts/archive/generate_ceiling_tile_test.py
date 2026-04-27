#!/usr/bin/env python3
"""
Pressed tin ceiling tile test — two grid cell sizes side by side.

Zone A (left 30mm): 2mm grid cells
Zone B (right 30mm): 3mm grid cells
Raised ridge grid: 0.3mm wide x 0.3mm proud ridges between cells.
Tile body: 60 x 30 x 2mm, printed ceiling-face DOWN.

Print orientation: ceiling face on plate (Z=0). Ridges protrude from Z=TILE_T upward.
Division notch at X=30mm: 0.5mm wide x 0.5mm deep (zone boundary marker).

Output:
  STL: CADtrains/Station/printed_files/CeilingTileTest.stl
  FCStd: CADtrains/Station/freecad/CeilingTileTest.FCStd
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

TILE_L = 60.0
TILE_W = 30.0
TILE_T = 2.0

RIDGE_W = 0.3       # ridge width
RIDGE_H = 0.3       # ridge height proud of tile surface
ZONE_A_CELL = 2.0   # cell size zone A
ZONE_B_CELL = 3.0   # cell size zone B
ZONE_X = TILE_L / 2  # X=30mm boundary

print(f"Tile: {TILE_L}x{TILE_W}x{TILE_T}mm")
print(f"Zone A (0-{ZONE_X:.0f}mm): {ZONE_A_CELL}mm cells  "
      f"Zone B ({ZONE_X:.0f}-{TILE_L:.0f}mm): {ZONE_B_CELL}mm cells")
print(f"Ridge: {RIDGE_W}mm wide x {RIDGE_H}mm proud")

tile = Part.makeBox(TILE_L, TILE_W, TILE_T)

# Division notch between zones
notch = Part.makeBox(0.5, TILE_W, 0.5,
                     FreeCAD.Vector(ZONE_X - 0.25, 0, TILE_T - 0.5))
tile = tile.cut(notch)

def add_ridges(base, x_start, x_end, cell_size):
    """Add raised grid ridges to the tile surface in a given X zone."""
    ridges = []
    # X-direction ridges (run along Y, spaced in X)
    x = x_start
    while x <= x_end + 0.01:
        rx = max(x_start, x - RIDGE_W/2)
        rw = min(x + RIDGE_W/2, x_end) - rx
        if rw > 0.05:
            ridges.append(Part.makeBox(rw, TILE_W, RIDGE_H,
                                       FreeCAD.Vector(rx, 0, TILE_T)))
        x += cell_size

    # Y-direction ridges (run along X, spaced in Y)
    y = 0.0
    while y <= TILE_W + 0.01:
        ry = max(0, y - RIDGE_W/2)
        rh = min(y + RIDGE_W/2, TILE_W) - ry
        if rh > 0.05:
            ridges.append(Part.makeBox(x_end - x_start, rh, RIDGE_H,
                                       FreeCAD.Vector(x_start, ry, TILE_T)))
        y += cell_size

    result = base
    for r in ridges:
        result = result.fuse(r)
    return result

tile = add_ridges(tile, 0,      ZONE_X, ZONE_A_CELL)
tile = add_ridges(tile, ZONE_X, TILE_L, ZONE_B_CELL)
print("Ridges added")

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/CeilingTileTest.FCStd"
try: FreeCAD.closeDocument("CeilingTileTest")
except: pass
doc = FreeCAD.newDocument("CeilingTileTest")
obj = doc.addObject("Part::Feature", "CeilingTile")
obj.Shape = tile
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/CeilingTileTest.stl"
MeshPart.meshFromShape(Shape=tile, LinearDeflection=0.03,
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
