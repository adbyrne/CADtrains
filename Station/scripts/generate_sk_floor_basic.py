#!/usr/bin/env python3
"""
SK station — floor / interior piece.

Standard features:
  - Floor slab with 4 registration tongues
  - Floor plank grooves (2.0mm pitch)
  - Partition walls WT and TF: door #8032, wainscot grooves, cap rail + miters
  - Ticket wicket (WT wall): sill 4'0"=14.0mm, top aligns with door opening top
  - Clock discs on both faces of both partition walls
  - Notice board relief on both faces of both partition walls
  - Bay counter across front of bay (parallel to front window)
  - Operator bay: 45° panels, front panel, windows #8028/#8069/#8024

Optional (INTERIOR_DETAILS=True):
  - Waiting room: benches ×2, stove stub
  - Ticket office: desk+clutter, filing cabinets ×2, waste bucket, stove stub,
    pigeon hole shelf (WT wall beside wicket), bay counter clutter
  - Freight room: crates ×4, barrels ×3, bags ×2, stove stub, standup desk

Coordinate system:
  X: building length  (waiting end X=0 → freight end X=BLDG_L)
  Y: building depth   (siding face Y=0 → passenger face Y=BLDG_D)
  Z: height           (floor surface Z=FLOOR_T, wall top Z=WALL_H)

Print orientation: face-down (Z=0 on plate). No supports needed.

Output:
  FCStd: CADtrains/Station/freecad/SK_FloorBasic.FCStd
  STL:   CADtrains/Station/printed_files/SK_FloorBasic.stl
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, math
V = FreeCAD.Vector

FLOOR_VARIANT = "detailed"   # "detailed" (full interior) or "plain" (walls only)

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Building dimensions ----------------------------------------------------
WALL_T    = 2.0
WALL_H    = ft(10, 6)    # 36.8mm
WAITING_W = ft( 7,  7)   # 26.56mm
TICKET_W  = ft(10,  2)   # 35.60mm
FREIGHT_W = ft(13,  3)   # 46.40mm
BLDG_L    = WAITING_W + TICKET_W + FREIGHT_W + 4 * WALL_T
BLDG_D    = 40.0

W_CX      = WALL_T + WAITING_W / 2
T_CX      = WALL_T + WAITING_W + WALL_T + TICKET_W / 2
F_CX      = WALL_T + WAITING_W + WALL_T + TICKET_W + WALL_T + FREIGHT_W / 2
X_WT_WALL = WALL_T + WAITING_W
X_TF_WALL = WALL_T + WAITING_W + WALL_T + TICKET_W

# ---- Floor slab -------------------------------------------------------------
FLOOR_T   = 2.0
RABBET_D  = 1.0
RABBET_H  = 1.5

# ---- Partition walls --------------------------------------------------------
DADO_D    = 0.5

# ---- Interior door #8032 ----------------------------------------------------
INT_DOOR_W  = 10.30
INT_DOOR_H  = 24.75   # casting height confirmed from test print
CAP_NOTCH_W = 11.75

# ---- Door frame (raised, non-office face of interior partition doors) --------
FRAME_D = 0.6     # frame proud of wall face
FRAME_W = 1.45    # frame leg width

# ---- Wainscot / cap rail ----------------------------------------------------
WAINSCOT_H = 9.65
CAP_H      = 1.5
CAP_T      = 0.8
CAP_Z0     = WAINSCOT_H - CAP_H
GROOVE_P   = 1.2
GROOVE_W   = 0.3
GROOVE_D   = 0.3

# ---- Partition wall passenger-end chamfer -----------------------------------
CHAMFER_P  = 1.0

# ---- Wire notch on siding-face tongue at WT/TF partition wall ---------------
WIRE_NOTCH_W = 1.5

# ---- Floor plank grooves ----------------------------------------------------
PL_PITCH   = 2.0
PL_W       = 0.3
PL_D       = 0.3

# ---- Bay geometry -----------------------------------------------------------
BAY_PROJ = ft(2, 6)
FRONT_W  = TICKET_W - 2 * BAY_PROJ
HW       = TICKET_W / 2
FHW      = FRONT_W  / 2
SQ2      = math.sqrt(2)
WT       = WALL_T
BAY_Y0   = BLDG_D

WIN_SILL     = WAINSCOT_H
WIN_W_SIDE   =  9.38
WIN_H_SIDE   = 19.85
CENTER_WIN_W = 11.70
CENTER_WIN_H = 19.80

# ---- Ticket wicket ----------------------------------------------------------
WICKET_W = 7.0                            # 2'0" confirmed from test print
WICKET_Z = ft(4, 0)                       # 14.0mm — counter sill / 4'0" prototype
WICKET_H = FLOOR_T + INT_DOOR_H - WICKET_Z  # 12.75mm — top at door opening top

# ---- Notice board (standard, both partition wall faces) ---------------------
NB_W = ft(1, 6)   # 18" wide = 5.3mm
NB_H = ft(1, 0)   # 12" tall = 3.5mm
NB_D = 0.3        # emboss depth
NB_Z = WAINSCOT_H + 3.0   # above cap rail

# ---- Interior detail flag ---------------------------------------------------
INTERIOR_DETAILS = (FLOOR_VARIANT == "detailed")

# ---- Stove stub + floor guard -----------------------------------------------
STOVE_S = ft(1, 6)   # 18"×18" footprint = 5.3mm
GUARD_S = 7.0        # 24"×24" floor guard tile
GUARD_T = 0.4        # guard tile thickness

print(f"SK Floor  BLDG_L={BLDG_L:.2f}  BLDG_D={BLDG_D}  WALL_H={WALL_H:.2f}")
print(f"  WICKET_Z={WICKET_Z:.2f}  WICKET_H={WICKET_H:.2f}  INT_DOOR_H={INT_DOOR_H}")
print(f"  INTERIOR_DETAILS={INTERIOR_DETAILS}")

door_cy = BLDG_D / 2
door_y0 = door_cy - INT_DOOR_W / 2

# =============================================================================
# 1. FLOOR SLAB + TONGUES
# =============================================================================
floor = Part.makeBox(BLDG_L - 2*WALL_T, BLDG_D - 2*WALL_T, FLOOR_T,
                     V(WALL_T, WALL_T, 0))
floor = floor.fuse(Part.makeBox(BLDG_L - 2*WALL_T, RABBET_D, RABBET_H,
                                 V(WALL_T, WALL_T - RABBET_D, 0)))
floor = floor.fuse(Part.makeBox(BLDG_L - 2*WALL_T, RABBET_D, RABBET_H,
                                 V(WALL_T, BLDG_D - WALL_T, 0)))
floor = floor.fuse(Part.makeBox(RABBET_D, BLDG_D - 2*WALL_T + 2*RABBET_D, RABBET_H,
                                 V(WALL_T - RABBET_D, WALL_T - RABBET_D, 0)))
floor = floor.fuse(Part.makeBox(RABBET_D, BLDG_D - 2*WALL_T + 2*RABBET_D, RABBET_H,
                                 V(BLDG_L - WALL_T, WALL_T - RABBET_D, 0)))
print(f"  Floor slab + 4 registration tongues")

# =============================================================================
# 2. FLOOR PLANK GROOVES + WIRE NOTCHES
# =============================================================================
cnt = 0
for i in range(int((BLDG_D - 2*WALL_T) / PL_PITCH) + 2):
    gy = WALL_T + i * PL_PITCH
    if gy >= BLDG_D - WALL_T: break
    floor = floor.cut(Part.makeBox(BLDG_L - 2*WALL_T, PL_W, PL_D,
                                    V(WALL_T, gy - PL_W/2, FLOOR_T - PL_D)))
    cnt += 1
print(f"  Floor planks: {cnt} grooves  pitch={PL_PITCH}mm")

for wlabel, wpx in [("WT", X_WT_WALL), ("TF", X_TF_WALL)]:
    nx = wpx + WALL_T/2 - WIRE_NOTCH_W/2
    floor = floor.cut(Part.makeBox(WIRE_NOTCH_W, RABBET_D + 0.1, RABBET_H,
                                    V(nx, WALL_T - RABBET_D - 0.05, 0)))
    print(f"  Wire notch {wlabel}: X={nx:.1f}..{nx+WIRE_NOTCH_W:.1f}")

# =============================================================================
# 3. PARTITION WALLS (WT and TF)
# =============================================================================
for label, px in [("WT", X_WT_WALL), ("TF", X_TF_WALL)]:
    pw = Part.makeBox(WALL_T, BLDG_D - 2*WALL_T + 2*DADO_D, WALL_H,
                      V(px, WALL_T - DADO_D, 0))

    # Interior door opening
    pw = pw.cut(Part.makeBox(WALL_T + 0.2, INT_DOOR_W, INT_DOOR_H,
                              V(px - 0.1, door_y0, FLOOR_T)))

    # Cap rail — both faces
    cap_len = BLDG_D - 2*WALL_T
    pw = pw.fuse(Part.makeBox(CAP_T, cap_len, CAP_H, V(px - CAP_T, WALL_T, CAP_Z0)))
    pw = pw.fuse(Part.makeBox(CAP_T, cap_len, CAP_H, V(px + WALL_T, WALL_T, CAP_Z0)))

    # Cap rail notch at door opening
    for cx in [px - CAP_T, px + WALL_T]:
        pw = pw.cut(Part.makeBox(CAP_T + 0.1, CAP_NOTCH_W, CAP_H + 0.1,
                                  V(cx - 0.05, door_cy - CAP_NOTCH_W/2, CAP_Z0 - 0.05)))

    # Cap rail 45° miters at siding and passenger wall ends
    for face_x, outer_x in [(px, px - CAP_T), (px + WALL_T, px + WALL_T + CAP_T)]:
        v1 = V(face_x,  WALL_T,         CAP_Z0)
        v2 = V(outer_x, WALL_T,         CAP_Z0)
        v3 = V(outer_x, WALL_T + CAP_T, CAP_Z0)
        pw = pw.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(V(0, 0, CAP_H)))
        is_noface = (label == "WT" and face_x == px) or \
                    (label == "TF" and face_x == px + WALL_T)
        p_leg = CHAMFER_P if is_noface else CAP_T
        v1 = V(face_x,  BLDG_D - WALL_T,          CAP_Z0)
        v2 = V(outer_x, BLDG_D - WALL_T,          CAP_Z0)
        v3 = V(outer_x, BLDG_D - WALL_T - p_leg,  CAP_Z0)
        pw = pw.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(V(0, 0, CAP_H)))

    # Ticket wicket + waiting-room counter shelf (WT wall only)
    if label == "WT":
        wicket_y = door_y0 + INT_DOOR_W + 2.0
        pw = pw.cut(Part.makeBox(WALL_T + 0.2, WICKET_W, WICKET_H,
                                  V(px - 0.1, wicket_y, WICKET_Z)))
        pw = pw.fuse(Part.makeBox(2.0, WICKET_W + 2.0, 1.0,
                                   V(px - 2.0, wicket_y - 1.0, WICKET_Z - 1.0)))
        print(f"  Ticket wicket: Y={wicket_y:.2f}..{wicket_y+WICKET_W:.2f}"
              f"  Z={WICKET_Z:.2f}..{WICKET_Z+WICKET_H:.2f}")

    # Clock discs on both faces
    clock_z = WALL_H - 6.0
    clock_y = BLDG_D / 2
    pw = pw.fuse(Part.makeCylinder(1.5, 0.5, V(px,          clock_y, clock_z), V(-1, 0, 0)))
    pw = pw.fuse(Part.makeCylinder(1.5, 0.5, V(px + WALL_T, clock_y, clock_z), V( 1, 0, 0)))

    # Notice board relief — siding-side of door, both faces
    nb_cy = (WALL_T + door_y0) / 2
    nb_y  = nb_cy - NB_W / 2
    pw = pw.cut(Part.makeBox(NB_D,           NB_W, NB_H, V(px,                nb_y, NB_Z)))
    pw = pw.cut(Part.makeBox(NB_D,           NB_W, NB_H, V(px + WALL_T - NB_D, nb_y, NB_Z)))
    print(f"  Notice board {label}: Y={nb_y:.1f}..{nb_y+NB_W:.1f}  Z={NB_Z:.1f}..{NB_Z+NB_H:.1f}")

    # Wainscot grooves on both faces
    wg_cnt = 0
    for i in range(int(cap_len / GROOVE_P) + 2):
        gy = WALL_T + i * GROOVE_P
        if gy >= BLDG_D - WALL_T: break
        pw = pw.cut(Part.makeBox(GROOVE_D, GROOVE_W, WAINSCOT_H,
                                  V(px,                  gy - GROOVE_W/2, 0)))
        pw = pw.cut(Part.makeBox(GROOVE_D, GROOVE_W, WAINSCOT_H,
                                  V(px + WALL_T - GROOVE_D, gy - GROOVE_W/2, 0)))
        wg_cnt += 1

    # Raised door frame on non-office face (waiting/freight room side)
    fx = px - FRAME_D if label == "WT" else px + WALL_T
    pw = pw.fuse(Part.makeBox(FRAME_D, FRAME_W, INT_DOOR_H + FRAME_W,
                               V(fx, door_y0 - FRAME_W, FLOOR_T)))
    pw = pw.fuse(Part.makeBox(FRAME_D, FRAME_W, INT_DOOR_H + FRAME_W,
                               V(fx, door_y0 + INT_DOOR_W, FLOOR_T)))
    pw = pw.fuse(Part.makeBox(FRAME_D, INT_DOOR_W + 2 * FRAME_W, FRAME_W,
                               V(fx, door_y0 - FRAME_W, FLOOR_T + INT_DOOR_H)))
    floor = floor.fuse(pw)
    print(f"  Partition {label}: X={px:.1f}..{px+WALL_T:.1f}"
          f"  door Y={door_y0:.1f}..{door_y0+INT_DOOR_W:.1f}  {wg_cnt} wainscot/face + door frame")

# ---- Bay inner corner fillers -----------------------------------------------
gap_y0    = BLDG_D - WALL_T + DADO_D
gap_depth = WALL_T - DADO_D
bay_inner_w = WT / SQ2
floor = floor.fuse(Part.makeBox(bay_inner_w, gap_depth, WALL_H,
                                 V(T_CX - HW, gap_y0, 0)))
floor = floor.fuse(Part.makeBox(bay_inner_w, gap_depth, WALL_H,
                                 V(T_CX + HW - bay_inner_w, gap_y0, 0)))

# ---- 45° tongue-corner chamfers at passenger wall end -----------------------
py_pass   = BLDG_D - WALL_T
py_tongue = py_pass + DADO_D

v1 = V(X_WT_WALL,          py_pass,   0)
v2 = V(X_WT_WALL,          py_tongue, 0)
v3 = V(X_WT_WALL + DADO_D, py_tongue, 0)
floor = floor.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(V(0, 0, WALL_H)))
floor = floor.fuse(Part.makeBox(bay_inner_w, DADO_D, WALL_H, V(T_CX - HW, py_pass, 0)))

v1 = V(X_TF_WALL + WALL_T,          py_pass,   0)
v2 = V(X_TF_WALL + WALL_T,          py_tongue, 0)
v3 = V(X_TF_WALL + WALL_T - DADO_D, py_tongue, 0)
floor = floor.cut(Part.Face(Part.makePolygon([v1, v2, v3, v1])).extrude(V(0, 0, WALL_H)))
floor = floor.fuse(Part.makeBox(bay_inner_w, DADO_D, WALL_H,
                                 V(T_CX + HW - bay_inner_w, py_pass, 0)))
print(f"  Bay inner fillers + passenger-end tongue chamfers done")

# =============================================================================
# 4. BAY FLOOR + BAY PANELS + WINDOWS
# =============================================================================
bay_floor_pts = [
    V(T_CX - HW,  BLDG_D - WALL_T, 0),
    V(T_CX + HW,  BLDG_D - WALL_T, 0),
    V(T_CX + HW,  BLDG_D,          0),
    V(T_CX + FHW, BLDG_D + BAY_PROJ, 0),
    V(T_CX - FHW, BLDG_D + BAY_PROJ, 0),
    V(T_CX - HW,  BLDG_D,          0),
    V(T_CX - HW,  BLDG_D - WALL_T, 0),
]
floor = floor.fuse(Part.Face(Part.makePolygon(bay_floor_pts)).extrude(V(0, 0, FLOOR_T)))

left_pts = [
    V(T_CX - HW,           BAY_Y0,                      0),
    V(T_CX - FHW,          BAY_Y0 + BAY_PROJ,           0),
    V(T_CX - FHW + WT/SQ2, BAY_Y0 + BAY_PROJ - WT/SQ2, 0),
    V(T_CX - HW  + WT/SQ2, BAY_Y0,                      0),
    V(T_CX - HW,           BAY_Y0,                      0),
]
right_pts = [
    V(T_CX + HW,           BAY_Y0,                      0),
    V(T_CX + FHW,          BAY_Y0 + BAY_PROJ,           0),
    V(T_CX + FHW - WT/SQ2, BAY_Y0 + BAY_PROJ - WT/SQ2, 0),
    V(T_CX + HW  - WT/SQ2, BAY_Y0,                      0),
    V(T_CX + HW,           BAY_Y0,                      0),
]
bay = (Part.Face(Part.makePolygon(left_pts)).extrude(V(0, 0, WALL_H))
       .fuse(Part.Face(Part.makePolygon(right_pts)).extrude(V(0, 0, WALL_H)))
       .fuse(Part.makeBox(FRONT_W, WT, WALL_H,
                          V(T_CX - FHW, BAY_Y0 + BAY_PROJ - WT, 0))))

bay = bay.cut(Part.makeBox(CENTER_WIN_W, WT + 0.2, CENTER_WIN_H,
    V(T_CX - CENTER_WIN_W/2, BAY_Y0 + BAY_PROJ - WT - 0.1, WIN_SILL)))

floor = floor.fuse(bay)

# Side window cuts through angled bay panels.
# The outer face vertices (A,B) follow the panel diagonal: for the left panel
# (+1,+1)/SQ2, outer-bottom is at cx+sign*hww; for right panel (-1,+1)/SQ2,
# outer-bottom is at cx+sign*hww too — sign encodes both.
# Inner face offset per panel: X shifts by -sign*WT/SQ2, Y by -WT/SQ2.
# Inner-bottom vertex D lands at Y≈39.64 (0.36mm below BAY_Y0=40), which
# triggers an OCCT degenerate-compound on a 1000+ face shape. Clip to BAY_Y0+0.2.
hww = WIN_W_SIDE / (2 * SQ2)
for sign, cx in [(-1, T_CX - (HW + FHW)/2), (1, T_CX + (HW + FHW)/2)]:
    cy = BAY_Y0 + BAY_PROJ / 2
    y_D = max(cy - hww - WT/SQ2, BAY_Y0 + 0.2)   # inner-bottom, clipped
    lp = [V(cx + sign*hww,              cy - hww,            WIN_SILL),   # A outer bottom
          V(cx - sign*hww,              cy + hww,            WIN_SILL),   # B outer top
          V(cx - sign*(hww + WT/SQ2),   cy + hww - WT/SQ2,  WIN_SILL),   # C inner top
          V(cx + sign*(hww - WT/SQ2),   y_D,                 WIN_SILL),   # D inner bottom
          V(cx + sign*hww,              cy - hww,            WIN_SILL)]   # back to A
    floor = floor.cut(Part.Face(Part.makePolygon(lp)).extrude(V(0, 0, WIN_H_SIDE)))

# Center bay window frame (raised 0.6mm × 1.45mm on interior face of bay front panel)
bay_inner_y = BAY_Y0 + BAY_PROJ - WT
cx0 = T_CX - CENTER_WIN_W / 2
cx1 = T_CX + CENTER_WIN_W / 2
z_sill = WIN_SILL - FRAME_W
z_head = WIN_SILL + CENTER_WIN_H
for lx in [cx0 - FRAME_W, cx1]:
    floor = floor.fuse(Part.makeBox(FRAME_W, FRAME_D, z_head - z_sill + FRAME_W,
                                     V(lx, bay_inner_y - FRAME_D, z_sill)))
floor = floor.fuse(Part.makeBox(CENTER_WIN_W + 2*FRAME_W, FRAME_D, FRAME_W,
                                 V(cx0 - FRAME_W, bay_inner_y - FRAME_D, z_head)))   # head
floor = floor.fuse(Part.makeBox(CENTER_WIN_W + 2*FRAME_W, FRAME_D, FRAME_W,
                                 V(cx0 - FRAME_W, bay_inner_y - FRAME_D, z_sill)))   # sill

# Side bay window frames — inner face of each 45° angled panel.
# The cut polygon corners C (inner top) and D (inner bottom) define the inner face.
# Frame parallelogram strips sit on that face and protrude FRAME_D into the office.
# pdx/pdy = panel direction D→C; ndx/ndy = inward normal (toward office).
for sign, cx in [(-1, T_CX - (HW + FHW)/2), (1, T_CX + (HW + FHW)/2)]:
    cy   = BAY_Y0 + BAY_PROJ / 2
    y_D  = max(cy - hww - WT/SQ2, BAY_Y0 + 0.2)
    Dx = cx + sign * (hww - WT/SQ2);  Dy = y_D
    Cx = cx - sign * (hww + WT/SQ2);  Cy = cy + hww - WT/SQ2
    pdx = -sign / SQ2;  pdy = 1.0 / SQ2   # D→C along inner face
    ndx = -sign / SQ2;  ndy = -1.0 / SQ2  # inward normal toward office
    fw = FRAME_W
    fd = FRAME_D
    z_sf = WIN_SILL - fw
    z_hd = WIN_SILL + WIN_H_SIDE

    def _sfstrip(x1, y1, x2, y2, zb, zt, _nx=ndx, _ny=ndy):
        pts = [V(x1,        y1,        zb),
               V(x2,        y2,        zb),
               V(x2+fd*_nx, y2+fd*_ny, zb),
               V(x1+fd*_nx, y1+fd*_ny, zb),
               V(x1,        y1,        zb)]
        return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, zt - zb))

    # Sill (below window opening)
    floor = floor.fuse(_sfstrip(
        Dx - fw*pdx, Dy - fw*pdy, Cx + fw*pdx, Cy + fw*pdy, z_sf, z_sf + fw))
    # Head (above window opening)
    floor = floor.fuse(_sfstrip(
        Dx - fw*pdx, Dy - fw*pdy, Cx + fw*pdx, Cy + fw*pdy, z_hd, z_hd + fw))
    # D-end leg (full height, at the D / outer-corner side of the opening)
    floor = floor.fuse(_sfstrip(
        Dx - fw*pdx, Dy - fw*pdy, Dx, Dy, z_sf, z_hd + fw))
    # C-end leg (full height, at the C / inner-corner side of the opening)
    floor = floor.fuse(_sfstrip(
        Cx, Cy, Cx + fw*pdx, Cy + fw*pdy, z_sf, z_hd + fw))

print(f"  Bay floor + panels + windows done")

# =============================================================================
# 5. BAY DESK (standard — 1905 flat-top 30"×54" = 8.8mm×15.7mm)
#    Long axis parallel to front window (X), deep axis into bay (Y).
#    Positioned against building interior face — operator faces outward (+Y).
# =============================================================================
ctr_w = ft(4, 6)                                # 54" = 15.75mm  (long, runs in X)
ctr_d = ft(2, 6)                                # 30" =  8.76mm  (deep, runs in Y)
ctr_x = T_CX - ctr_w / 2
ctr_y = BLDG_D - WALL_T                         # against building interior face of bay
floor = floor.fuse(Part.makeBox(ctr_w, ctr_d, WICKET_Z - FLOOR_T,
                                 V(ctr_x, ctr_y, FLOOR_T)))
print(f"  Bay desk (1905 30x54in): X={ctr_x:.1f}..{ctr_x+ctr_w:.1f}"
      f"  Y={ctr_y:.1f}..{ctr_y+ctr_d:.1f}  H={WICKET_Z-FLOOR_T:.2f}mm")

# =============================================================================
# 6. INTERIOR DETAILS (optional)
# =============================================================================
if INTERIOR_DETAILS:

    def desk_clutter(shape, cx, cy, z):
        """Small items on a work surface: telegraph key, lamp, coffee, papers."""
        shape = shape.fuse(Part.makeBox(1.5, 0.8, 0.4, V(cx - 0.75, cy - 0.4, z)))
        shape = shape.fuse(Part.makeBox(0.4, 0.8, 0.8, V(cx - 0.2,  cy - 0.4, z + 0.4)))
        shape = shape.fuse(Part.makeCylinder(0.5, 1.5, V(cx + 1.5, cy, z)))
        shape = shape.fuse(Part.makeCylinder(0.5, 0.8, V(cx - 1.8, cy + 0.5, z)))
        shape = shape.fuse(Part.makeBox(2.5, 2.0, 0.2, V(cx - 1.25, cy + 1.2, z)))
        return shape

    def add_stove_with_guard(shape, sx, sy):
        """Floor guard tile + pot belly stove with flue indent."""
        off = (GUARD_S - STOVE_S) / 2
        cx  = sx + STOVE_S / 2
        cy  = sy + STOVE_S / 2
        shape = shape.fuse(Part.makeBox(GUARD_S, GUARD_S, GUARD_T,
                                         V(sx - off, sy - off, FLOOR_T)))
        z = FLOOR_T + GUARD_T
        shape = shape.fuse(Part.makeBox(STOVE_S, STOVE_S, 0.8, V(sx, sy, z)))
        z += 0.8
        shape = shape.fuse(Part.makeCylinder(2.2, 2.5, V(cx, cy, z)))
        z += 2.5
        shape = shape.fuse(Part.makeCone(2.2, 3.0, 1.5, V(cx, cy, z)))
        z += 1.5
        shape = shape.fuse(Part.makeCone(3.0, 1.5, 2.0, V(cx, cy, z)))
        z += 2.0
        shape = shape.fuse(Part.makeCylinder(1.3, 1.5, V(cx, cy, z)))
        z += 1.5
        shape = shape.fuse(Part.makeCylinder(1.2, 1.2, V(cx, cy, z)))
        z += 1.2
        shape = shape.cut(Part.makeCylinder(0.8, 0.81, V(cx, cy, z - 0.8)))
        return shape

    # ---- WAITING ROOM -------------------------------------------------------
    # Benches ×2 — against waiting-end gable wall, Y-centred, clear of door
    bench_x = WALL_T + 0.5
    bench_len = 8.0;  bench_w = 3.0;  bench_h = 5.3
    for bench_yc in [door_cy - 10.0, door_cy + 10.0]:
        floor = floor.fuse(Part.makeBox(bench_w, bench_len, bench_h,
                                         V(bench_x, bench_yc - bench_len / 2, FLOOR_T)))
    # Stove stub — WT wall, siding side (own chimney)
    floor = add_stove_with_guard(floor, X_WT_WALL - STOVE_S - 0.5, WALL_T + 0.5)
    print("  Waiting room: 2 benches (gable wall, Y-centred) + stove stub (WT wall)")

    # ---- TICKET OFFICE ------------------------------------------------------
    TO_X0 = X_WT_WALL + WALL_T + 0.5
    cab_w = ft(1,6);  cab_d = ft(2,0);  cab_h = ft(4,4)
    desk_l = ft(3, 0);  desk_d = ft(2, 0);  desk_h = ft(2, 6)
    # Filing cabinets ×2 near WT wall corner (away from windows)
    for i in range(2):
        floor = floor.fuse(Part.makeBox(cab_w, cab_d, cab_h,
                                         V(TO_X0 + i*(cab_w+0.5), WALL_T, FLOOR_T)))
    # Seated desk near window (further from WT wall)
    desk_x = TO_X0 + 2*(cab_w + 0.5) + 1.0
    floor = floor.fuse(Part.makeBox(desk_l, desk_d, desk_h,
                                     V(desk_x, WALL_T, FLOOR_T)))
    floor = desk_clutter(floor, desk_x + desk_l/2, WALL_T + desk_d/2,
                         FLOOR_T + desk_h)
    # Waste bucket beside desk
    bkt_x = desk_x + desk_l + 0.5
    floor = floor.fuse(Part.makeCylinder(1.5, ft(0,9),
                                          V(bkt_x, WALL_T + 1.5, FLOOR_T)))
    # Stove stub — TF wall, ticket-office side, passenger corner (shares chimney with freight)
    stove_y_pass = BLDG_D - WALL_T - STOVE_S - (GUARD_S - STOVE_S) / 2
    floor = add_stove_with_guard(floor, X_TF_WALL - STOVE_S - 0.5, stove_y_pass)
    # Pigeon hole shelf — WT wall ticket-office face, passenger side of wicket
    wicket_y = door_y0 + INT_DOOR_W + 2.0
    shelf_y0 = wicket_y + WICKET_W + 0.5
    shelf_y1 = BLDG_D - WALL_T - 0.5
    if shelf_y1 > shelf_y0 + 1.0:
        sh_d = ft(0, 8)              # 8" depth protruding from wall
        sh_h = ft(2, 0)              # 24" tall
        sh_w = shelf_y1 - shelf_y0
        sh_x = X_WT_WALL + WALL_T
        floor = floor.fuse(Part.makeBox(sh_d, sh_w, sh_h,
                                         V(sh_x, shelf_y0, WICKET_Z)))
        # Groove lines to suggest pigeon holes (2 verticals, 2 horizontals)
        gv_w = 0.3
        for i in [1, 2]:
            gy = shelf_y0 + i * sh_w / 3
            floor = floor.cut(Part.makeBox(sh_d + 0.1, gv_w, sh_h,
                                            V(sh_x - 0.05, gy - gv_w/2, WICKET_Z)))
        for i in [1, 2]:
            gz = WICKET_Z + i * sh_h / 3
            floor = floor.cut(Part.makeBox(sh_d + 0.1, sh_w, gv_w,
                                            V(sh_x - 0.05, shelf_y0, gz - gv_w/2)))
        print(f"  Pigeon hole shelf: X={sh_x:.1f}  Y={shelf_y0:.1f}..{shelf_y1:.1f}"
              f"  Z={WICKET_Z:.1f}..{WICKET_Z+sh_h:.1f}")
    # Bay counter clutter
    floor = desk_clutter(floor, T_CX, ctr_y + ctr_d/2, WICKET_Z)
    print("  Ticket office: desk+clutter, 2 filing cabinets, waste bucket, stove, shelf")
    print("  Bay counter: clutter added")

    # ---- FREIGHT ROOM -------------------------------------------------------
    FR_X0 = X_TF_WALL + WALL_T
    FR_X1 = BLDG_L - WALL_T
    cL = ft(2, 0)    # large crate A: 24" = 7mm
    cB = ft(2, 6)    # large crate B: 30" = 8.7mm (different size)
    cS = ft(1, 4)    # small crate:   16" = 4.6mm

    # Corner 1 — TF-siding: two large-A crates side by side + small crates on top
    cx1 = FR_X0 + STOVE_S + 1.0   # start after stove stub
    floor = floor.fuse(Part.makeBox(cL, cL, cL, V(cx1,        WALL_T+0.5, FLOOR_T)))
    floor = floor.fuse(Part.makeBox(cL, cL, cL, V(cx1+cL+0.3, WALL_T+0.5, FLOOR_T)))
    for i, sc_x in enumerate([cx1, cx1+cS+0.3, cx1+2*(cS+0.3)]):
        floor = floor.fuse(Part.makeBox(cS, cS, cS, V(sc_x, WALL_T+0.5, FLOOR_T+cL)))

    # Corner 2 — freight-end-siding: one large-B crate + 2 barrels beside it
    cx2 = FR_X1 - cB - 0.5
    floor = floor.fuse(Part.makeBox(cB, cB, cB, V(cx2, WALL_T+0.5, FLOOR_T)))
    for i in range(2):
        bx = cx2 - (i + 1) * (2 * 2.9 + 0.5)
        floor = floor.fuse(Part.makeCylinder(2.9, ft(1, 10),
                                              V(bx, WALL_T + 2.9 + 0.5, FLOOR_T)))

    # Center — mixed small crates and bags (scattered)
    for sc_x, sc_y in [(F_CX-8, 18), (F_CX-4, 22), (F_CX, 16), (F_CX+5, 21)]:
        floor = floor.fuse(Part.makeBox(cS, cS, cS, V(sc_x, sc_y, FLOOR_T)))
    for bg_x, bg_y in [(F_CX-5, 28), (F_CX+2, 26), (F_CX+6, 15)]:
        floor = floor.fuse(Part.makeBox(ft(1,0)*1.5, ft(1,0), ft(0,8),
                                         V(bg_x, bg_y, FLOOR_T)))

    # Stove stub — TF wall, freight side, passenger corner (back-to-back with ticket office)
    floor = add_stove_with_guard(floor, FR_X0 + 0.5, stove_y_pass)

    # Standup desk — TF wall, beside notice board (notice board siding-side of door)
    sd = ft(1, 0)   # 12" footprint = 3.5mm
    nb_cy_fr = (WALL_T + door_y0) / 2
    nb_y_fr  = nb_cy_fr - NB_W / 2
    floor = floor.fuse(Part.makeBox(sd, sd, ft(3, 6),
                                     V(FR_X0 + 0.5, nb_y_fr + NB_W + 0.5, FLOOR_T)))
    print("  Freight room: corner1(2×large+small stack), corner2(large-B+2 barrels),"
          " center scatter, stove stub (TF wall), standup desk (by notice board)")

# =============================================================================
# EXPORT
# =============================================================================
BASE     = "/home/abyrne/Projects/Trains/CADtrains/Station/"
vtag     = "" if FLOOR_VARIANT == "detailed" else "_Plain"
doc_name = f"SK_FloorBasic{vtag}"
fc_path  = BASE + f"freecad/{doc_name}.FCStd"
stl_path = BASE + f"printed_files/{doc_name}.stl"

try: FreeCAD.closeDocument(doc_name)
except: pass
doc = FreeCAD.newDocument(doc_name)
obj = doc.addObject("Part::Feature", "FloorBasic")
obj.Shape = floor
doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

MeshPart.meshFromShape(Shape=floor, LinearDeflection=0.05,
                        AngularDeflection=0.1, Relative=False).write(stl_path)
print(f"Wrote {stl_path}")
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
