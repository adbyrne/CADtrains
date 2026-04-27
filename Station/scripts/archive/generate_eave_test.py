#!/usr/bin/env python3
"""
Eave/soffit test section — self-contained, no external parts required.

Cross-section geometry (in XZ plane, X = across eave, Z = height):
  - X=0: drip edge (outer)
  - X=OVERHANG: wall outer face
  - X=OVERHANG+WALL_T: wall inner face (locating tongue inner edge)
  - Z=0..SOFFIT_T: soffit body (constant thickness)
  - Z=SOFFIT_T at X=OVERHANG+WALL_T rises to Z=SOFFIT_T+HEIGHT_RISE at X=0
    (pitch slope on top face)

Locating tongue: thin tab at inner end (X=OVERHANG..OVERHANG+WALL_T) that sits
inside the wall top. Extends down TONGUE_H below soffit face.

Rafter tail stubs: rectangular stubs on soffit face, every RAFTER_SPACING along
section length (Y axis). 1.5mm wide x 1.0mm tall x RAFTER_T deep.

Print orientation: END-ON (one Y=0 end face on plate, section length = print height).
  - Soffit face is vertical during printing → clean surface
  - Rafter tail stubs are horizontal protrusions → no overhang issues
  - Pitch-angle top face is vertical → clean

Provisional values (adjust after measuring #8204/#8147):
  OVERHANG = 12mm, SOFFIT_T = 3mm, pitch 5:12 (~22.6 degrees)

Output:
  FCStd: CADtrains/Station/freecad/EaveTest.FCStd
  STL:   CADtrains/Station/printed_files/EaveTest.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os, math

SECTION_L  = 60.0    # length of test section (Y axis = print height when end-on)
OVERHANG   = 12.0    # horizontal projection beyond wall outer face
WALL_T     = 2.0     # wall thickness (for locating tongue width)
SOFFIT_T   = 3.0     # minimum eave thickness at drip edge

PITCH_RISE = 5.0
PITCH_RUN  = 12.0
PITCH_ANGLE = math.atan2(PITCH_RISE, PITCH_RUN)  # ~22.6 deg

# Height rise across the overhang at pitch angle
HEIGHT_RISE = OVERHANG * (PITCH_RISE / PITCH_RUN)   # = 5.0mm
# Total height at wall face = SOFFIT_T + HEIGHT_RISE
H_AT_WALL   = SOFFIT_T + HEIGHT_RISE                 # = 8.0mm
# Additional rise across wall thickness (locating tongue zone)
H_AT_INNER  = H_AT_WALL + WALL_T * (PITCH_RISE / PITCH_RUN)  # = 8.83mm

TONGUE_H   = 2.0     # tongue drops below soffit face to locate inside wall top
TONGUE_GAP = 0.2     # clearance gap so tongue fits inside wall

# Rafter tail stubs on soffit face
RAFTER_SPACING = 7.0   # ~2\' prototype spacing
RAFTER_W       = 1.5   # stub width along section length
RAFTER_T       = 1.5   # stub depth (protrudes from soffit outer face)
RAFTER_H       = 1.0   # stub height (= dimension across eave, at drip edge)

print(f"Eave section: L={SECTION_L}mm  overhang={OVERHANG}mm  soffit_t={SOFFIT_T}mm")
print(f"Pitch: {PITCH_RISE}:{PITCH_RUN} ({math.degrees(PITCH_ANGLE):.1f} deg)")
print(f"H at wall face={H_AT_WALL:.2f}mm  H at inner edge={H_AT_INNER:.2f}mm")
print(f"Total eave width (tongue+overhang): {OVERHANG+WALL_T:.1f}mm")

# Build eave body as an extruded polygon cross-section
# Cross-section in XZ plane (X = across eave, Z = height):
#   Outer bottom:  (0, 0)
#   Inner bottom:  (OVERHANG + WALL_T - TONGUE_GAP, 0)  -- soffit bottom
#   Inner top:     (OVERHANG + WALL_T - TONGUE_GAP, H_AT_INNER)
#   Outer top:     (0, SOFFIT_T)
# This gives the sloped top face and flat soffit bottom.

pts = [
    FreeCAD.Vector(0,                              0,          0),
    FreeCAD.Vector(OVERHANG + WALL_T,              0,          0),
    FreeCAD.Vector(OVERHANG + WALL_T,              0,          H_AT_INNER),
    FreeCAD.Vector(0,                              0,          SOFFIT_T),
    FreeCAD.Vector(0,                              0,          0),
]
wire  = Part.makePolygon(pts)
face  = Part.Face(wire)
eave  = face.extrude(FreeCAD.Vector(0, SECTION_L, 0))

# Locating tongue: thin tab at inner end extending below soffit face (in -Z)
# The tongue sits inside the wall top. Width = WALL_T - 2*TONGUE_GAP.
# Tongue goes from X=OVERHANG+TONGUE_GAP to X=OVERHANG+WALL_T-TONGUE_GAP,
# from Z=-TONGUE_H to Z=0 (soffit face).
tongue = Part.makeBox(WALL_T - 2*TONGUE_GAP, SECTION_L, TONGUE_H,
                      FreeCAD.Vector(OVERHANG + TONGUE_GAP, 0, -TONGUE_H))
eave = eave.fuse(tongue)

# Rafter tail stubs on soffit face (Z=0, protrude in -Z direction)
# Since printing end-on, -Z in model = toward build plate during print.
# Model stubs as protrusions at Z=0 going into -Z.
n_rafters = int(SECTION_L / RAFTER_SPACING)
for i in range(n_rafters + 1):
    ry = i * RAFTER_SPACING
    if ry > SECTION_L:
        break
    # Stub at the drip edge area (X=0..RAFTER_T, near outer edge)
    stub = Part.makeBox(RAFTER_T, RAFTER_W, RAFTER_H,
                        FreeCAD.Vector(0, ry - RAFTER_W/2, -RAFTER_H))
    eave = eave.fuse(stub)
print(f"Added {n_rafters+1} rafter tail stubs  spacing={RAFTER_SPACING}mm")

# Trim tongue at section ends if rafter stubs overlap — no issue since stubs are at Z<0
# and tongue is also at Z<0 but at X=OVERHANG region. No conflict.

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/EaveTest.FCStd"
try: FreeCAD.closeDocument("EaveTest")
except: pass
doc = FreeCAD.newDocument("EaveTest")
obj = doc.addObject("Part::Feature", "EaveSection")
obj.Shape = eave
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files/EaveTest.stl"
MeshPart.meshFromShape(Shape=eave, LinearDeflection=0.05,
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
