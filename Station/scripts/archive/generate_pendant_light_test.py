#!/usr/bin/env python3
"""
Kerosene pendant ceiling light fixture test — array of 4.

Fixture geometry (Z=0 at ceiling face, fixture hangs downward into -Z):
  - Shade: truncated cone, rim dia 4.0mm (bottom), top dia 2.5mm, height 2.5mm
  - Stem: cylinder 1.0mm dia x 2.0mm, above shade (Z=0 down to Z=-2.0mm crown)
  - Total hang: stem (2.0mm) + shade (2.5mm) = 4.5mm below ceiling
  - LED hole: 1.5mm dia through full height of stem+shade (wire enters from ceiling Z=0)

Print orientation: face-up (Z=0 on plate, fixtures point upward).
  - Rim face (widest point) is the first layer — prints clean.
  - Stem top flush with plate face.

Array: 4 fixtures in a row, 15mm spacing (easy to separate with flush cutters).

Output:
  FCStd: CADtrains/Station/freecad/PendantLightTest.FCStd
  STL:   CADtrains/Station/printed_files/PendantLightTest.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart

SHADE_RIM_D  = 4.0    # rim (bottom) diameter
SHADE_TOP_D  = 2.5    # crown (top) diameter
SHADE_H      = 2.5    # shade height
STEM_D       = 1.0    # stem diameter
STEM_H       = 2.0    # stem height above shade crown (toward ceiling)
LED_HOLE_D   = 1.5    # through-hole for LED/wire

# Print orientation: rim (Z=0) on plate, fixture hangs up (+Z)
# Z=0: rim face (wide end of cone on plate)
# Z=SHADE_H: crown of shade
# Z=SHADE_H+STEM_H: top of stem (ceiling face)

SPACING  = 15.0   # centre-to-centre in array
N        = 4      # number of fixtures

def make_fixture(cx, cy):
    # Shade: frustum (truncated cone)
    # Part.makeCone(r1, r2, height, position, direction)
    shade = Part.makeCone(SHADE_RIM_D/2, SHADE_TOP_D/2, SHADE_H,
                           FreeCAD.Vector(cx, cy, 0),
                           FreeCAD.Vector(0, 0, 1))

    # Stem: cylinder from shade crown up to ceiling face
    stem = Part.makeCylinder(STEM_D/2, STEM_H,
                              FreeCAD.Vector(cx, cy, SHADE_H),
                              FreeCAD.Vector(0, 0, 1))

    fixture = shade.fuse(stem)

    # LED/wire hole: through full height
    hole = Part.makeCylinder(LED_HOLE_D/2, SHADE_H + STEM_H + 0.2,
                              FreeCAD.Vector(cx, cy, -0.1),
                              FreeCAD.Vector(0, 0, 1))
    fixture = fixture.cut(hole)
    return fixture

print(f"Pendant fixture: rim={SHADE_RIM_D}mm  top={SHADE_TOP_D}mm  H={SHADE_H}mm")
print(f"Stem: dia={STEM_D}mm  H={STEM_H}mm  Total hang={SHADE_H+STEM_H:.1f}mm")
print(f"LED hole: {LED_HOLE_D}mm dia through full height")
print(f"Array: {N} fixtures  spacing={SPACING}mm")

# Build array
total_w = (N - 1) * SPACING
x0 = 0.0
body = make_fixture(x0, 0)
for i in range(1, N):
    body = body.fuse(make_fixture(x0 + i * SPACING, 0))

# ---- Export -----------------------------------------------------------------

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/PendantLightTest.FCStd"
try: FreeCAD.closeDocument("PendantLightTest")
except: pass
doc = FreeCAD.newDocument("PendantLightTest")
obj = doc.addObject("Part::Feature", "PendantArray")
obj.Shape = body
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/PendantLightTest.stl"
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
