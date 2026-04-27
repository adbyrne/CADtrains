#!/usr/bin/env python3
"""
Bay 3D test print — full-height bay with actual 45° angled walls.

Prints upright (bay back open, all walls vertical — no support needed).
Thin base plate ties all three walls together at the bottom.

Side windows omitted — fit already confirmed from SK planning token.
Front panel carries #8024 (11.70 x 19.80mm) opening — primary thing to test.

Evaluate:
  - Overall 3D proportions of bay projecting from building
  - #8024 center window proportion and fit
  - 45° side panel angles feel right in hand / against building wall

Output:
  FreeCAD: CADtrains/Station/freecad/Bay3DTest.FCStd
  STL:     CADtrains/Station/printed_files/Bay3DTest.stl
"""

import xmlrpc.client
import sys

proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os, math

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Dimensions -------------------------------------------------------

WALL_H   = ft(10, 6)    # working wall height ~35.9mm (10'6" prototype) -- CONFIRM before full print
WALL_T   = 2.0
BAY_PROJ = ft(2, 6)     # ~8.75mm bay projection
TICKET_W = ft(10, 2)    # ~35.6mm -- full SK office width = bay opening width
FRONT_W  = TICKET_W - 2 * BAY_PROJ    # ~18.1mm front panel face
HW       = TICKET_W / 2               # half-width of bay opening
FHW      = FRONT_W / 2                # half-width of front panel
SQ2      = math.sqrt(2)
WT       = WALL_T

WIN_SILL     = ft(2, 0)    # ~6.9mm sill height
WIN_W        = 9.38         # #8028/#8069 side panel windows
WIN_H        = 19.85        # #8028/#8069
CENTER_WIN_W = 11.70        # #8024 6/6 double-hung
CENTER_WIN_H = 19.80        # #8024

BASE_T = 1.0    # base plate thickness (holds panels together on build plate)

print(f"Bay 3D test: opening {TICKET_W:.1f}mm  proj {BAY_PROJ:.1f}mm  height {WALL_H:.1f}mm")
print(f"  Front panel {FRONT_W:.1f}mm  side panels {BAY_PROJ*SQ2:.2f}mm")
print(f"  #8024 front window margins: {(FRONT_W-CENTER_WIN_W)/2:.2f}mm each side")
print(f"  #8028/69 side window margins: {(BAY_PROJ*SQ2-WIN_W)/2:.2f}mm each side")

# ---- Wall panels ------------------------------------------------------

# Left side panel: 45-deg, cross-section polygon extruded to WALL_H.
# Inner back corner clipped to Y=0 (avoids small below-zero geometry).
left_pts = [
    FreeCAD.Vector(-HW,           0,              0),   # outer-back
    FreeCAD.Vector(-FHW,          BAY_PROJ,       0),   # outer-front
    FreeCAD.Vector(-FHW + WT/SQ2, BAY_PROJ-WT/SQ2, 0), # inner-front
    FreeCAD.Vector(-HW  + WT/SQ2, 0,              0),   # inner-back
    FreeCAD.Vector(-HW,           0,              0),   # close
]
left_panel = Part.Face(Part.makePolygon(left_pts)).extrude(FreeCAD.Vector(0, 0, WALL_H))

# Right side panel: mirror of left in X
right_pts = [
    FreeCAD.Vector( HW,           0,              0),
    FreeCAD.Vector( FHW,          BAY_PROJ,       0),
    FreeCAD.Vector( FHW - WT/SQ2, BAY_PROJ-WT/SQ2, 0),
    FreeCAD.Vector( HW  - WT/SQ2, 0,              0),
    FreeCAD.Vector( HW,           0,              0),
]
right_panel = Part.Face(Part.makePolygon(right_pts)).extrude(FreeCAD.Vector(0, 0, WALL_H))

# Front panel: box, exterior face at Y=BAY_PROJ
front_panel = Part.makeBox(FRONT_W, WT, WALL_H,
                            FreeCAD.Vector(-FHW, BAY_PROJ - WT, 0))

# Base plate: spans full bay footprint, holds panels together on plate
base = Part.makeBox(TICKET_W, BAY_PROJ, BASE_T,
                    FreeCAD.Vector(-HW, 0, 0))

bay = left_panel.fuse(right_panel).fuse(front_panel).fuse(base)

# ---- Front panel window (#8024) ---------------------------------------
# Axis-aligned cut through front panel (Y direction, centered on front face)
front_win = Part.makeBox(
    CENTER_WIN_W, WT + 0.2, CENTER_WIN_H,
    FreeCAD.Vector(-CENTER_WIN_W/2, BAY_PROJ - WT - 0.1, WIN_SILL)
)
bay = bay.cut(front_win)

# ---- Side panel windows (#8028/#8069) ---------------------------------
# Panels are at 45°, so the cut is a parallelogram in XY extruded in Z.
# Panel direction for left:  (1/SQ2, 1/SQ2)
# Inward normal for left:    (1/SQ2, -1/SQ2)  (toward bay interior)
# Panel direction for right: (-1/SQ2, 1/SQ2)
# Inward normal for right:   (-1/SQ2, -1/SQ2)

hww = WIN_W / (2 * SQ2)   # half window width projected onto each XY axis

# Left side panel window: center at midpoint of panel exterior face
lc_x = -(HW + FHW) / 2
lc_y = BAY_PROJ / 2
lp1 = FreeCAD.Vector(lc_x - hww,        lc_y - hww,        WIN_SILL)
lp2 = FreeCAD.Vector(lc_x + hww,        lc_y + hww,        WIN_SILL)
lp3 = FreeCAD.Vector(lc_x + hww + WT/SQ2, lc_y + hww - WT/SQ2, WIN_SILL)
lp4 = FreeCAD.Vector(lc_x - hww + WT/SQ2, lc_y - hww - WT/SQ2, WIN_SILL)
left_win = Part.Face(Part.makePolygon([lp1, lp2, lp3, lp4, lp1])).extrude(
    FreeCAD.Vector(0, 0, WIN_H))
bay = bay.cut(left_win)

# Right side panel window: mirror of left in X
rc_x = (HW + FHW) / 2
rc_y = BAY_PROJ / 2
rp1 = FreeCAD.Vector(rc_x + hww,         rc_y - hww,        WIN_SILL)
rp2 = FreeCAD.Vector(rc_x - hww,         rc_y + hww,        WIN_SILL)
rp3 = FreeCAD.Vector(rc_x - hww - WT/SQ2, rc_y + hww - WT/SQ2, WIN_SILL)
rp4 = FreeCAD.Vector(rc_x + hww - WT/SQ2, rc_y - hww - WT/SQ2, WIN_SILL)
right_win = Part.Face(Part.makePolygon([rp1, rp2, rp3, rp4, rp1])).extrude(
    FreeCAD.Vector(0, 0, WIN_H))
bay = bay.cut(right_win)

# ---- Export -----------------------------------------------------------

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/Bay3DTest.FCStd"
os.makedirs(os.path.dirname(fc_path), exist_ok=True)

try: FreeCAD.closeDocument("Bay3DTest")
except: pass
doc = FreeCAD.newDocument("Bay3DTest")
obj = doc.addObject("Part::Feature", "Bay3D")
obj.Shape = bay
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)
mesh = MeshPart.meshFromShape(Shape=bay, LinearDeflection=0.05,
                               AngularDeflection=0.1, Relative=False)
out = os.path.join(stl_dir, "Bay3DTest.stl")
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
