#!/usr/bin/env python3
"""
SK station — production roof panel prints.
Long panel (×2 identical — flip one 180° for passenger side; tabs interlock).
Hip panel (×2 identical).
Print orientation: outer face down on build plate, ribs face up.

Long panel features:
  - Body + ribs + ridge tabs (4 sections × 25%, tabs at 0-25% and 50-75%)
    Flipping panel 180° inverts tab pattern to 25-50% and 75-100% — panels interlock.
  - Eave rib (first rib) angled at roof pitch so outer face mates flush with ceiling/eave top
  - 1×1mm rabbet ledge on hip edges

Hip panel features:
  - Body + ribs tapering toward apex
  - Eave rib angled at hip-panel pitch

Output:
  FCStd: CADtrains/Station/freecad/SK_RoofPanels.FCStd
  STL:   CADtrains/Station/printed_files/SK_RoofPanel_Long.stl  (print ×2, flip one)
  STL:   CADtrains/Station/printed_files/SK_RoofPanel_Hip.stl   (print ×2)
  PNG:   CADtrains/Station/images/SK_RoofPanels_ISO.png
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, math

def ft(f, i=0): return (f*12+i)*25.4/87.0
V = FreeCAD.Vector

# ---- Shared dims
WALL_T = 2.0;  WALL_H = ft(10,6);  BLDG_D = 40.0
BLDG_L = ft(7,7)+ft(10,2)+ft(13,3)+4*WALL_T
EAVE_SIDE = 24.0;  EAVE_END = 11.0
PITCH = 5/12;  HALF_SPAN = BLDG_D/2
RIDGE_H = HALF_SPAN*PITCH;  RIDGE_Z = WALL_H+RIDGE_H
RIDGE_X0 = HALF_SPAN;  RIDGE_X1 = BLDG_L-HALF_SPAN
RIDGE_L = RIDGE_X1 - RIDGE_X0
ESP = EAVE_SIDE+1.0;  EEP = EAVE_END+1.0
z_hip = WALL_H - math.sqrt(EEP**2+ESP**2)*RIDGE_H/(HALF_SPAN*math.sqrt(2))

PANEL_T = 2.0;  RIB_H = 4.0;  RIB_W = 1.5;  RIB_SP = 14.0
TAB_W = 2.5;  TAB_H = 1.0
RABBET_W = 1.0;  RABBET_D = 1.0

# ---- Long panel dims (print orientation: Y=0 eave, Y=s_len ridge)
eave_w  = BLDG_L + 2*EEP
ridge_w = RIDGE_L
hip_ovh = (eave_w - ridge_w) / 2
s_dy = BLDG_D/2 - (-ESP)     # horizontal run along slope
s_dz = RIDGE_Z - z_hip        # vertical rise along slope
s_len = math.sqrt(s_dy**2 + s_dz**2)
# Eave-rib taper: rib height difference across RIB_W to present horizontal face when assembled
LONG_TAPER = s_dz / s_len     # rise per mm of panel-plane travel

print(f"Long panel: eave_w={eave_w:.1f}  ridge_w={ridge_w:.1f}  s_len={s_len:.2f}  taper={LONG_TAPER:.4f}")

def lp_xl(y): return -hip_ovh * (1.0 - y/s_len)
def lp_xr(y): return  ridge_w + hip_ovh * (1.0 - y/s_len)

def cut_rabbet(body, x1, y1, x2, y2, inx, iny):
    A=V(x1,               y1,               PANEL_T-RABBET_D)
    B=V(x2,               y2,               PANEL_T-RABBET_D)
    C=V(x2+inx*RABBET_W,  y2+iny*RABBET_W,  PANEL_T-RABBET_D)
    D=V(x1+inx*RABBET_W,  y1+iny*RABBET_W,  PANEL_T-RABBET_D)
    return body.cut(Part.Face(Part.makePolygon([A,B,C,D,A])).extrude(V(0,0,RABBET_D)))

def make_flat_rib(xl, xr, d):
    """Standard rectangular rib."""
    hw = RIB_W/2
    r1=V(xl,d-hw,PANEL_T); r2=V(xr,d-hw,PANEL_T)
    r3=V(xr,d+hw,PANEL_T); r4=V(xl,d+hw,PANEL_T)
    return Part.Face(Part.makePolygon([r1,r2,r3,r4,r1])).extrude(V(0,0,RIB_H))

def make_wedge_rib(xl_fn, xr_fn, d, taper):
    """
    Eave rib as a right-triangle wedge at roof pitch.
    Full height at eave side (Y=d), tapers to zero at Y=d+W where W=RIB_H/taper.
    Hypotenuse angle matches the roof pitch — lies flat on ceiling when assembled.
    X extent clipped to panel width at Y=d+W (narrower end) to stay within panel silhouette.
    """
    W  = RIB_H / taper          # wedge base width along slope direction
    xl = xl_fn(d + W)           # clip X to narrower (ridge) end of wedge
    xr = xr_fn(d + W)
    # Right-triangle cross-section in YZ plane at X=xl, extruded in +X
    P1 = V(xl, d,   PANEL_T)          # eave corner on panel face (zero height)
    P2 = V(xl, d+W, PANEL_T)          # ridge base on panel face  (full height side)
    P3 = V(xl, d+W, PANEL_T+RIB_H)   # ridge top (full height)
    return Part.Face(Part.makePolygon([P1,P2,P3,P1])).extrude(V(xr-xl, 0, 0))

def make_long_panel():
    """
    Ridge tabs at X sections 0-25% and 50-75%.
    Flip panel 180° for the other side — tab pattern inverts to 25-50% and 75-100%.
    Both panels interlock at the ridge.
    """
    # Body
    P1=V(lp_xl(0),     0,     0)
    P2=V(lp_xr(0),     0,     0)
    P3=V(lp_xr(s_len), s_len, 0)
    P4=V(lp_xl(s_len), s_len, 0)
    body = Part.Face(Part.makePolygon([P1,P2,P3,P4,P1])).extrude(V(0,0,PANEL_T))

    # First (eave) rib — wedge at roof pitch
    d = RIB_SP/2
    body = body.fuse(make_wedge_rib(lp_xl, lp_xr, d, LONG_TAPER))
    d += 2*RIB_SP  # skip one spacing to clear hip-panel wedge-rib zone at corners

    # Remaining ribs — flat (1 rib near mid-panel, above hip interference zone)
    n_ribs = 0
    while d < s_len - RIB_SP/2:
        body = body.fuse(make_flat_rib(lp_xl(d), lp_xr(d), d))
        d += RIB_SP;  n_ribs += 1

    # Ridge half-lap: tabs at sections 0 and 2, recesses at 1 and 3
    # Flipping panel 180° swaps tab/recess positions — identical print interlocks at ridge.
    seg = ridge_w / 4
    y0  = s_len - TAB_W
    for i in [0, 2]:
        x0=i*seg; x1=(i+1)*seg
        t1=V(x0,y0,PANEL_T); t2=V(x1,y0,PANEL_T)
        t3=V(x1,s_len,PANEL_T); t4=V(x0,s_len,PANEL_T)
        body = body.fuse(Part.Face(Part.makePolygon([t1,t2,t3,t4,t1])).extrude(V(0,0,TAB_H)))
    for i in [1, 3]:
        x0=i*seg; x1=(i+1)*seg
        r1=V(x0,y0,PANEL_T-TAB_H); r2=V(x1,y0,PANEL_T-TAB_H)
        r3=V(x1,s_len,PANEL_T-TAB_H); r4=V(x0,s_len,PANEL_T-TAB_H)
        body = body.cut(Part.Face(Part.makePolygon([r1,r2,r3,r4,r1])).extrude(V(0,0,TAB_H)))

    # Rabbet ledges on hip edges
    e_len = math.sqrt(hip_ovh**2 + s_len**2)
    body = cut_rabbet(body, -hip_ovh, 0,          0,       s_len,
                       s_len/e_len, -hip_ovh/e_len)
    body = cut_rabbet(body, ridge_w+hip_ovh, 0, ridge_w, s_len,
                      -s_len/e_len, -hip_ovh/e_len)

    print(f"  Long: {n_ribs} flat + 1 wedge ribs, half-lap tabs/recesses (0-25%/50-75%), rabbets")
    return body

# ---- Hip panel dims (isoceles triangle: Y=0 base/eave, Y=hip_h apex)
hip_base = 2*ESP + BLDG_D
hip_dx   = RIDGE_X0 + EEP
hip_dy   = BLDG_D/2 + ESP
hip_dz   = RIDGE_Z - z_hip
hip_side = math.sqrt(hip_dx**2 + hip_dy**2 + hip_dz**2)
hip_h    = math.sqrt(hip_side**2 - (hip_base/2)**2)
HIP_TAPER = hip_dz / hip_h

print(f"Hip panel: base={hip_base:.1f}  h={hip_h:.2f}  taper={HIP_TAPER:.4f}")

def hp_xl(y):
    w = hip_base * (1.0 - y/hip_h)
    return (hip_base - w) / 2.0

def hp_xr(y):
    w = hip_base * (1.0 - y/hip_h)
    return (hip_base + w) / 2.0

def make_hip_panel():
    P1=V(0,          0,     0)
    P2=V(hip_base,   0,     0)
    P3=V(hip_base/2, hip_h, 0)
    body = Part.Face(Part.makePolygon([P1,P2,P3,P1])).extrude(V(0,0,PANEL_T))

    # First (eave) rib — wedge at hip-panel pitch
    d = RIB_SP/2
    body = body.fuse(make_wedge_rib(hp_xl, hp_xr, d, HIP_TAPER))
    d += RIB_SP

    print(f"  Hip: 1 wedge rib only")
    return body

print("Building long panel...")
long_panel = make_long_panel()
print("Building hip panel...")
hip_panel = make_hip_panel()

# ---- Document
BASE     = "/home/abyrne/Projects/Trains/CADtrains/Station/"
fc_path  = BASE + "freecad/SK_RoofPanels.FCStd"
stl_long = BASE + "printed_files/SK_RoofPanel_Long.stl"
stl_hip  = BASE + "printed_files/SK_RoofPanel_Hip.stl"
img_path = BASE + "images/SK_RoofPanels_ISO.png"

try: FreeCAD.closeDocument("SK_RoofPanels")
except: pass
doc = FreeCAD.newDocument("SK_RoofPanels")

def add(name, shape, color, offset=None):
    s = shape.copy()
    if offset: s.translate(offset)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = s
    if FreeCAD.GuiUp:
        obj.ViewObject.ShapeColor = color
    return obj

# Long panel + flipped copy (to verify tab interlock) + hip panel
add("LongPanel",        long_panel, (0.65,0.50,0.35))
add("LongPanel_Flipped",long_panel, (0.55,0.40,0.25), V(eave_w+15, 0, 0))
add("HipPanel",         hip_panel,  (0.65,0.50,0.35), V((eave_w+15)*2, 0, 0))

doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

for mesh_shape, path in [(long_panel, stl_long), (hip_panel, stl_hip)]:
    m = MeshPart.meshFromShape(Shape=mesh_shape, LinearDeflection=0.05, AngularDeflection=0.1)
    m.write(path)
    print(f"Saved {path}")

if FreeCAD.GuiUp:
    import FreeCADGui
    FreeCADGui.updateGui()
    view = FreeCADGui.ActiveDocument.ActiveView
    view.viewIsometric()
    view.fitAll()
    FreeCADGui.updateGui()
    view.saveImage(img_path, 1600, 1000, "White")
    print(f"Saved {img_path}")

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
