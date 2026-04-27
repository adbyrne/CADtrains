#!/usr/bin/env python3
"""
Bay test print — three panels connected L-center-R for window test fit.
Bay extended to full ticket office width (35.6mm SK) at 45° side panels.
Layout: Left side panel | tab | Front panel | tab | Right side panel
  - Left/right side panels: #8028/#8069 opening (9.38mm)
  - Front (center) panel:   #8024 opening (11.70mm) — 6/6 double-hung feature window
Panels connected by tabs at top so nothing gets lost.
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os, math

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

WALL_T   = 2.0
TEST_H   = 25.0    # tall enough for Tichy casting height (19.85mm)
WIN_W    = 9.38    # #8028/#8069 window width (side panels)
WIN_H    = 19.85   # #8028/#8069 window height
CENTER_WIN_W = 11.70   # #8024 6/6 double-hung window width (front panel)
CENTER_WIN_H = 19.80   # #8024 6/6 double-hung window height
WIN_SILL = 2.0

BAY_PROJ = ft(2, 6)    # 8.75mm -- keep same projection
TICKET_W = ft(10, 2)   # 35.6mm -- full SK office width = new bay opening width

SIDE_L  = BAY_PROJ * math.sqrt(2)   # 12.37mm side panel face
FRONT_W = TICKET_W - 2 * BAY_PROJ   # 18.1mm front panel face

print(f"Bay (full office width): {TICKET_W:.1f}mm wide x {BAY_PROJ:.1f}mm projection, 45 deg")
print(f"Side panel:  {SIDE_L:.2f}mm  #8028/69 margin each side: {(SIDE_L-WIN_W)/2:.2f}mm")
print(f"Front panel: {FRONT_W:.2f}mm  #8024 margin each side: {(FRONT_W-CENTER_WIN_W)/2:.2f}mm")

GAP   = 1.5   # gap between panels on build plate
TAB_H = 5.0   # height of connecting tab at top

def panel_at(x_off, width, win_w=WIN_W, win_h=WIN_H):
    """Flat wall panel at x_off with centered window opening."""
    slab = Part.makeBox(width, WALL_T, TEST_H, FreeCAD.Vector(x_off, 0, 0))
    cx = x_off + width / 2
    notch = Part.makeBox(win_w, WALL_T, win_h,
                         FreeCAD.Vector(cx - win_w/2, 0, WIN_SILL))
    return slab.cut(notch)

def tab_at(x_start, span):
    """Connecting tab spanning gap; overlaps 1mm into each adjacent panel."""
    return Part.makeBox(span + 2.0, WALL_T, TAB_H,
                        FreeCAD.Vector(x_start - 1.0, 0, TEST_H - TAB_H))

x_left  = 0.0
x_front = SIDE_L + GAP
x_right = x_front + FRONT_W + GAP

left_p  = panel_at(x_left,  SIDE_L)
front_p = panel_at(x_front, FRONT_W, win_w=CENTER_WIN_W, win_h=CENTER_WIN_H)
right_p = panel_at(x_right, SIDE_L)
tab1    = tab_at(x_left + SIDE_L, GAP)
tab2    = tab_at(x_front + FRONT_W, GAP)

assembly = left_p.fuse(front_p).fuse(right_p).fuse(tab1).fuse(tab2)

try: FreeCAD.closeDocument("BayTest")
except: pass
doc = FreeCAD.newDocument("BayTest")
obj = doc.addObject("Part::Feature", "Bay_Connected")
obj.Shape = assembly
doc.recompute()

fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/BayTest.FCStd"
os.makedirs(os.path.dirname(fc_path), exist_ok=True)
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)
mesh = MeshPart.meshFromShape(Shape=assembly, LinearDeflection=0.05,
                               AngularDeflection=0.1, Relative=False)
out = os.path.join(stl_dir, "BayTest_Connected.stl")
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
