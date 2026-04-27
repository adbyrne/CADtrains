#!/usr/bin/env python3
"""
Ceiling + eave combined test section — with integrated pendant light fixtures.

Changes from v1:
  - Eave body is uniform thickness (flat top AND bottom) — no slope.
    Slope is carried by the roof backing panels, not the eave piece.
  - 2 pendant light fixtures integrated into ceiling face — print together.
  - Print orientation changed to FACE-UP (attic face Z=CEIL_T on plate).
    Ceiling face (Z=0) prints last; pendants build narrow-to-wide as final
    layers above ceiling face — no overhangs, no supports needed.

Geometry:
  - Eave overhang (X=0..OVERHANG): soffit face + 14mm tick marks for #8147
  - Wall zone (X=OVERHANG..OVERHANG+WALL_T): 2.2×1.5mm channel on Z=0 face
  - Ceiling span (X=OVERHANG+WALL_T..total_span): 3mm pressed tin grid on Z=0 face
  - Pendants hang from Z=0 ceiling face into -Z (2mm stem + 2.5mm cone shade)

Print orientation: FACE-UP — attic face (Z=CEIL_T) on plate.
  Grid ridges, tick marks, and pendant bodies all print as final layers above Z=0.
  No supports needed.

Output:
  FCStd: CADtrains/Station/freecad/CeilingEaveTest.FCStd
  STL:   CADtrains/Station/printed_files/CeilingEaveTest.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart

SECTION_L  = 50.0    # section length (Y)
OVERHANG   = 12.0    # eave projection beyond wall outer face
WALL_T     = 2.0     # wall thickness
CEIL_T     = 2.5     # uniform body thickness (eave + ceiling)
ROOM_SPAN  = 20.0    # ceiling extension into room beyond wall inner face

# Wall channel: 2.2mm wide x 1.5mm deep, centred on wall thickness
CHAN_W   = 2.2
CHAN_D   = 1.5
CHAN_X   = OVERHANG + (WALL_T - CHAN_W) / 2

# Tin grid on ceiling face (Z=0, ridges protrude at -Z)
GRID_P   = 3.0
GRID_W   = 0.3
GRID_H   = 0.3

# Tick marks on soffit face (Z=0, protrude at -Z)
TICK_SP  = 14.0
TICK_W   = 0.3
TICK_H   = 0.3

# Wire hole through ceiling
WIRE_D   = 2.0
WIRE_X   = OVERHANG + WALL_T + 4.0
WIRE_Y   = SECTION_L / 2

# Pendant light fixture dimensions
SHADE_RIM_D = 4.0    # rim diameter (wide end, at bottom of shade)
SHADE_TOP_D = 2.5    # crown diameter (narrow end, at top of shade)
SHADE_H     = 2.5    # shade height
STEM_D      = 2.0    # stem diameter — must exceed LED_HOLE_D for solid connection
STEM_H      = 2.0    # stem length (Z=0 at ceiling face, stem goes to Z=-STEM_H)
LED_HOLE_D  = 1.2    # wire hole — smaller than STEM_D (leaves 0.4mm annular wall)

total_w    = OVERHANG + WALL_T
total_span = total_w + ROOM_SPAN
ceil_x0    = total_w           # ceiling zone start (X)
ceil_x1    = total_span        # ceiling zone end (X)

print(f"Section: {SECTION_L}mm long  overhang={OVERHANG}mm  ceil_t={CEIL_T}mm (uniform)")
print(f"Ceiling zone: X={ceil_x0:.1f}..{ceil_x1:.1f}mm  Wall channel: X={CHAN_X:.2f}..{CHAN_X+CHAN_W:.2f}")

# ---- Base body: simple uniform-thickness box --------------------------------
body = Part.makeBox(total_span, SECTION_L, CEIL_T)

# ---- Wall channel (opens at Z=0 ceiling face, cuts upward into body) --------
body = body.cut(Part.makeBox(CHAN_W, SECTION_L, CHAN_D,
                              FreeCAD.Vector(CHAN_X, 0, 0)))

# ---- Wire hole ---------------------------------------------------------------
body = body.cut(Part.makeCylinder(WIRE_D/2, CEIL_T + 1.0,
                                   FreeCAD.Vector(WIRE_X, WIRE_Y, -0.5),
                                   FreeCAD.Vector(0, 0, 1)))
print(f"Wire hole: X={WIRE_X:.1f}  Y={WIRE_Y:.1f}  dia={WIRE_D}mm")

# ---- Tin grid on ceiling face (Z=0, ridges at -Z) ---------------------------
nx = int((ceil_x1 - ceil_x0) / GRID_P) + 2
for i in range(nx):
    gx = ceil_x0 + i * GRID_P
    if gx > ceil_x1: break
    body = body.fuse(Part.makeBox(GRID_W, SECTION_L, GRID_H,
                                   FreeCAD.Vector(gx - GRID_W/2, 0, -GRID_H)))
ny = int(SECTION_L / GRID_P) + 2
for i in range(ny):
    gy = i * GRID_P
    if gy > SECTION_L: break
    body = body.fuse(Part.makeBox(ceil_x1 - ceil_x0, GRID_W, GRID_H,
                                   FreeCAD.Vector(ceil_x0, gy - GRID_W/2, -GRID_H)))
print(f"Tin grid: {nx} X-lines x {ny} Y-lines  pitch={GRID_P}mm")

# ---- Tick marks on soffit face (Z=0, protrude at -Z) ------------------------
n_ticks = int(SECTION_L / TICK_SP) + 1
for i in range(n_ticks):
    ty = i * TICK_SP
    if ty > SECTION_L: break
    body = body.fuse(Part.makeBox(OVERHANG, TICK_W, TICK_H,
                                   FreeCAD.Vector(0, ty - TICK_W/2, -TICK_H)))
print(f"Tick marks: {n_ticks}  spacing={TICK_SP}mm")

# ---- Pendant fixtures hanging from ceiling face (Z=0 into -Z) ---------------
# Stem extends 0.5mm INTO the ceiling body (Z=-STEM_H to Z=+0.5) to ensure
# volumetric overlap for fuse — touching at Z=0 face only does not connect.
STEM_EMBED = 0.5
pendant_positions = [
    (OVERHANG + WALL_T + ROOM_SPAN/2, SECTION_L/3),
    (OVERHANG + WALL_T + ROOM_SPAN/2, 2*SECTION_L/3),
]
for cx, cy in pendant_positions:
    stem  = Part.makeCylinder(STEM_D/2, STEM_H + STEM_EMBED,
                               FreeCAD.Vector(cx, cy, -STEM_H),
                               FreeCAD.Vector(0, 0, 1))
    shade = Part.makeCone(SHADE_RIM_D/2, SHADE_TOP_D/2, SHADE_H,
                           FreeCAD.Vector(cx, cy, -STEM_H - SHADE_H),
                           FreeCAD.Vector(0, 0, 1))
    hole  = Part.makeCylinder(LED_HOLE_D/2, STEM_H + SHADE_H + 0.2,
                               FreeCAD.Vector(cx, cy, -STEM_H - SHADE_H - 0.1),
                               FreeCAD.Vector(0, 0, 1))
    pendant = stem.fuse(shade).cut(hole)
    body = body.fuse(pendant)
print(f"Pendants: {len(pendant_positions)}  at Y={[round(p[1],1) for p in pendant_positions]}")
print(f"  Shade: rim={SHADE_RIM_D}mm  crown={SHADE_TOP_D}mm  H={SHADE_H}mm")
print(f"  Stem: dia={STEM_D}mm  H={STEM_H}mm  Total hang={STEM_H+SHADE_H:.1f}mm")

# ---- Export -----------------------------------------------------------------

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/CeilingEaveTest.FCStd"
try: FreeCAD.closeDocument("CeilingEaveTest")
except: pass
doc = FreeCAD.newDocument("CeilingEaveTest")
obj = doc.addObject("Part::Feature", "CeilingEave")
obj.Shape = body
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/CeilingEaveTest.stl"
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
