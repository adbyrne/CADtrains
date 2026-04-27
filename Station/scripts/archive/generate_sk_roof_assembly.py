#!/usr/bin/env python3
"""
SK station — integrated roof panel visual.
Panels have integral ribs and ridge connector tab.

Output:
  FCStd: CADtrains/Station/freecad/SK_RoofAssembly.FCStd
  PNG:   CADtrains/Station/images/SK_RoofAssembly_ISO.png
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, math

def ft(f, i=0): return (f*12+i)*25.4/87.0
V = FreeCAD.Vector

# ---- Dims
WALL_T = 2.0;  WALL_H = ft(10,6);  BLDG_D = 40.0
BLDG_L = ft(7,7)+ft(10,2)+ft(13,3)+4*WALL_T
CEIL_T = 2.5;  EAVE_SIDE = 24.0;  EAVE_END = 11.0

PITCH = 5/12;  HALF_SPAN = BLDG_D/2
RIDGE_H = HALF_SPAN*PITCH;  RIDGE_Z = WALL_H+RIDGE_H
RIDGE_X0 = HALF_SPAN;  RIDGE_X1 = BLDG_L-HALF_SPAN

ESP = EAVE_SIDE+1.0;  EEP = EAVE_END+1.0   # 1mm overhang
z_hip = WALL_H - math.sqrt(EEP**2+ESP**2)*RIDGE_H/(HALF_SPAN*math.sqrt(2))

PANEL_T = 2.0;  RIB_H = 4.0;  RIB_W = 1.5;  RIB_SP = 14.0

print(f"BLDG_L={BLDG_L:.2f}  RIDGE_Z={RIDGE_Z:.3f}  z_hip={z_hip:.3f}")

HWS = V(-EEP,        -ESP,        z_hip)
HFS = V(BLDG_L+EEP,  -ESP,        z_hip)
HFP = V(BLDG_L+EEP,   BLDG_D+ESP, z_hip)
HWP = V(-EEP,          BLDG_D+ESP, z_hip)
RW  = V(RIDGE_X0, BLDG_D/2, RIDGE_Z)
RF  = V(RIDGE_X1, BLDG_D/2, RIDGE_Z)

def panel_normal(pts):
    e1 = pts[1]-pts[0];  e2 = pts[2]-pts[0]
    n = e1.cross(e2)
    m = math.sqrt(n.x**2+n.y**2+n.z**2)
    return V(n.x/m, n.y/m, n.z/m)

def make_long_panel(A, B, C, D):
    """
    A=eave-waiting, B=eave-freight, C=ridge-freight, D=ridge-waiting.
    Outward normal computed from A,B,C winding. Ribs on inner face.
    """
    pts = [A, B, C, D]
    norm = panel_normal(pts)
    nx, ny, nz = norm.x, norm.y, norm.z
    inward = V(-nx*PANEL_T, -ny*PANEL_T, -nz*PANEL_T)

    # Panel body
    body = Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(inward)

    # Slope direction (eave midpoint → ridge midpoint)
    eave_my = (A.y+B.y)/2;  eave_mz = (A.z+B.z)/2
    ridg_my = (D.y+C.y)/2;  ridg_mz = (D.z+C.z)/2
    s_dy = ridg_my-eave_my;  s_dz = ridg_mz-eave_mz
    s_len = math.sqrt(s_dy**2+s_dz**2)
    suy = s_dy/s_len;  suz = s_dz/s_len
    print(f"  slope_len={s_len:.2f}mm")

    # Ribs: start half-spacing from eave, stop before ridge connector zone
    d = RIB_SP/2
    n_ribs = 0
    while d < s_len - RIB_SP:
        t = d/s_len
        # Centre of rib on inner surface
        yc = eave_my + t*s_dy - ny*PANEL_T
        zc = eave_mz + t*s_dz - nz*PANEL_T
        xl = min(A.x + t*(D.x-A.x), B.x + t*(C.x-B.x))
        xr = max(A.x + t*(D.x-A.x), B.x + t*(C.x-B.x))
        if xr <= xl+0.5: break
        hw_y = RIB_W/2*suy;  hw_z = RIB_W/2*suz
        p1=V(xl,yc-hw_y,zc-hw_z); p2=V(xr,yc-hw_y,zc-hw_z)
        p3=V(xr,yc+hw_y,zc+hw_z); p4=V(xl,yc+hw_y,zc+hw_z)
        rib = Part.Face(Part.makePolygon([p1,p2,p3,p4,p1])).extrude(
              V(-nx*RIB_H, -ny*RIB_H, -nz*RIB_H))
        body = body.fuse(rib)
        d += RIB_SP;  n_ribs += 1

    # Ridge connector tab: raised rib along ridge edge (shows half-lap location)
    # Tab runs full ridge length at the ridge edge of the panel
    TAB_W = 2.5;  TAB_H = 2.0
    t_tab = 1.0 - TAB_W/s_len
    yc_tab = eave_my + t_tab*s_dy - ny*PANEL_T
    zc_tab = eave_mz + t_tab*s_dz - nz*PANEL_T
    hw_y = TAB_W/2*suy;  hw_z = TAB_W/2*suz
    rl = RIDGE_X0;  rr = RIDGE_X1
    t1=V(rl,yc_tab-hw_y,zc_tab-hw_z); t2=V(rr,yc_tab-hw_y,zc_tab-hw_z)
    t3=V(rr,yc_tab+hw_y,zc_tab+hw_z); t4=V(rl,yc_tab+hw_y,zc_tab+hw_z)
    tab = Part.Face(Part.makePolygon([t1,t2,t3,t4,t1])).extrude(
          V(-nx*TAB_H, -ny*TAB_H, -nz*TAB_H))
    body = body.fuse(tab)

    print(f"  ribs={n_ribs}  ridge_tab added")
    return body

def make_hip_panel(pts):
    """Triangular hip panel — body only, no ribs."""
    norm = panel_normal(pts)
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(
           V(-norm.x*PANEL_T, -norm.y*PANEL_T, -norm.z*PANEL_T))

print("Building siding panel...")
siding    = make_long_panel(HWS, HFS, RF, RW)
print("Building passenger panel...")
passenger = make_long_panel(HFP, HWP, RW, RF)
print("Building hip panels...")
hip_w = make_hip_panel([HWS, RW, HWP])
hip_f = make_hip_panel([HFS, HFP, RF])

ceil_slab = Part.makeBox(BLDG_L+2*EAVE_END+2, BLDG_D+2*EAVE_SIDE+2, CEIL_T,
                         V(-EAVE_END-1, -EAVE_SIDE-1, WALL_H))
outer = Part.makeBox(BLDG_L, BLDG_D, WALL_H)
inner = Part.makeBox(BLDG_L-2*WALL_T, BLDG_D-2*WALL_T, WALL_H, V(WALL_T,WALL_T,0))
building = outer.cut(inner)

# ---- Document
fc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/SK_RoofAssembly.FCStd"
try: FreeCAD.closeDocument("SK_RoofAssembly")
except: pass
doc = FreeCAD.newDocument("SK_RoofAssembly")

def add(name, shape, color):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if FreeCAD.GuiUp:
        obj.ViewObject.ShapeColor = color
    return obj

add("Building",   building,   (0.75,0.72,0.68))
add("CeilSlab",   ceil_slab,  (0.85,0.85,0.80))
add("Siding",     siding,     (0.60,0.45,0.30))
add("Passenger",  passenger,  (0.60,0.45,0.30))
add("HipW",       hip_w,      (0.60,0.45,0.30))
add("HipF",       hip_f,      (0.60,0.45,0.30))

doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

if FreeCAD.GuiUp:
    import FreeCADGui
    FreeCADGui.updateGui()
    view = FreeCADGui.ActiveDocument.ActiveView
    view.viewIsometric()
    view.fitAll()
    FreeCADGui.updateGui()
    img = "/home/abyrne/Projects/Trains/CADtrains/Station/images/SK_RoofAssembly_ISO.png"
    view.saveImage(img, 1600, 1000, "White")
    print(f"Saved {img}")

_result_ = "Done"
'''

result = proxy.execute(CODE)
if result.get("success"):
    print(result.get("stdout",""))
    print("OK:", result.get("result"))
else:
    print("ERROR:", result.get("error_message"))
    print(result.get("error_traceback",""))
    sys.exit(1)
