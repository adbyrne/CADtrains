#!/usr/bin/env python3
"""
Station Planning Token - SK (Stans Knob) variant
Generates planning token for location testing at the Stans Knob site.

Site constraints: siding track along Y=0; right boundary X=200,Y=94;
arc from (0,63) to (200,94), R=661mm, center (200,-567).
Building right edge fixed at X=200 (HC/freight direction).
Arc clearance at platform left edge X=74: Y=81.9mm.

SK vs. standard:
  Half-size freight room (13'3" vs 26'6")
  Half-size waiting room (7'7" vs 15'2")
  Reduced depth: 12'0" (vs 15'0")
  Siding platform (non-track, Y=0 side):  6'0" = ~21mm
  Passenger platform (main track, +Y side): 5'0" = ~17.5mm
  Total platform Y: ~80.5mm  (arc allows 81.9mm at left edge -- OK)

Building orientation: B (waiting at x=0/left/JC end, freight at x=max/right/HC end)

Openings:
  Siding face (Y=0, "front" in code) -- freight operations side:
    Waiting room door  (centered in waiting section, full height)
    Freight sliding door (centered in freight section, 10' wide, full height)
  Passenger face (Y=BLDG_D, "back" in code) -- main track/arc side:
    Waiting room window (5' wide)
    Ticket window       (4' wide -- operator bay in detail model)
    Freight room window (5' wide)
  End walls:
    Left  (waiting / JC  direction): gable window 3' wide
    Right (freight / HC  direction): gable window 3' wide

Output:
  FreeCAD: CADtrains/Station/freecad/StationPlanSK.FCStd
  STLs:    CADtrains/Station/printed_files/StationPlanSK_Building.stl
           CADtrains/Station/printed_files/StationPlanSK_Platform.stl
"""

import xmlrpc.client
import sys

proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

# ---- Dimensions (HO 1:87) ---------------------------------------------------

WALL_T    = 2.0
DOOR_SILL = 2.0
WIN_SILL  = 4.0
BLDG_H    = 8.0

# SK room widths (halved freight and waiting vs. standard)
FREIGHT_W_SK = ft(13, 3)    # ~46.5mm  (standard 26'6" halved to 13'3")
TICKET_W_SK  = ft(10, 2)    # ~35.6mm  (same as standard)
WAITING_W_SK = ft(7,  7)    # ~26.6mm  (standard 15'2" halved to 7'7")

BLDG_L_SK = WAITING_W_SK + TICKET_W_SK + FREIGHT_W_SK + 4 * WALL_T  # ~116.6mm
BLDG_D_SK = ft(12, 0)       # ~42.1mm  (reduced from standard 15'0")

BAY_W    = ft(6, 0)    # operator bay width  ~21mm  (6' prototype)
BAY_PROJ = ft(2, 6)    # bay projection      ~8.75mm  (2'6" prototype, measured from Fig. 172)

# Platform: siding side (Y=0) + building + passenger side (+Y/arc side)
NON_TRACK_SK = ft(6, 0)     # siding platform  ~21.0mm
PASSENGER_SK = ft(5, 0)     # passenger platform ~17.5mm
PLAT_EXTRA   = 5.0          # end overhang beyond building
PLAT_L_SK    = BLDG_L_SK + 2 * PLAT_EXTRA
PLAT_D_SK    = NON_TRACK_SK + BLDG_D_SK + PASSENGER_SK  # ~80.5mm (<81.9mm arc OK)
PLAT_H       = 2.0
CLEARANCE    = 0.5           # slip-fit clearance per side

# Room center X positions (Building B: waiting left / JC end, freight right / HC end)
W_cx = WALL_T + WAITING_W_SK / 2
T_cx = WALL_T + WAITING_W_SK + WALL_T + TICKET_W_SK / 2
F_cx = WALL_T + WAITING_W_SK + WALL_T + TICKET_W_SK + WALL_T + FREIGHT_W_SK / 2

# End wall gable window center (along depth, measured from siding/Y=0 face)
END_CY = BLDG_D_SK / 2

# Opening widths from physical measurements of Tichy castings
WIN_W          =  9.38   # #8028/#8069 standard window
WIN_W_DOUBLE   = 19.00   # #8070 double window — all gable ends (standard + SK)
PASS_DOOR_W    =  9.55   # #8033 passenger/external door
INT_DOOR_W     = 10.30   # #8032 interior 4-panel door
FREIGHT_DW_STD = 30.38   # #8038 freight sliding door (standard stations)
FREIGHT_DW_SK  = 23.90   # #8125 freight door/transom (SK half-size freight room)
TICKET_WK_W    =  5.0    # ticket wicket notch (~1'6" prototype, small indicator only)

# Interior wall between waiting room and ticket office
X_WT_WALL   = WALL_T + WAITING_W_SK          # left face of interior wall (in X)
INT_DOOR_CY = WALL_T + 2.0 + INT_DOOR_W / 2  # door near siding side of wall
INT_WIN_CY  = INT_DOOR_CY + INT_DOOR_W / 2 + 2.0 + TICKET_WK_W / 2  # wicket beside door

# Interior wall between ticket office and freight room
X_TF_WALL   = WALL_T + WAITING_W_SK + WALL_T + TICKET_W_SK  # left face of wall (in X)
TF_DOOR_CY  = WALL_T + 2.0 + INT_DOOR_W / 2  # door near siding side, same position as WT door

bay_tip = NON_TRACK_SK + BLDG_D_SK + BAY_PROJ   # passenger platform Y at bay tip
arc_at_left = 81.9                               # arc Y limit at left edge (X=74)
print(f"SK Building {BLDG_L_SK:.1f} x {BLDG_D_SK:.1f} x {BLDG_H}mm")
print(f"  Rooms W={WAITING_W_SK:.1f}  T={TICKET_W_SK:.1f}  F={FREIGHT_W_SK:.1f}")
print(f"  Room centers: W_cx={W_cx:.1f}  T_cx={T_cx:.1f}  F_cx={F_cx:.1f}")
print(f"  Platform {PLAT_L_SK:.1f} x {PLAT_D_SK:.1f}mm  "
      f"(siding={NON_TRACK_SK:.1f} + bldg={BLDG_D_SK:.1f} + pass={PASSENGER_SK:.1f})")
print(f"  Operator bay: {BAY_W:.1f} x {BAY_PROJ:.1f}mm  "
      f"tip at Y={bay_tip:.1f}mm  arc limit={arc_at_left}mm  clearance={arc_at_left - bay_tip:.1f}mm")

# ---- Opening definitions (mm positions) -------------------------------------
# Format: (cx_mm, width_mm, is_door, face)
# front = siding face (Y=0);  back = passenger face (Y=BLDG_D_SK)
# left  = waiting end (x=0);  right = freight end (x=BLDG_L_SK)

OPENINGS_SK = [
    # Siding face (front, Y=0) -- freight operations + waiting access from siding
    (W_cx,   PASS_DOOR_W, True,  "front"),   # waiting room door (#8033)
    (T_cx,   WIN_W,       False, "front"),   # ticket office window (#8028/69, opposite bay)
    (F_cx,   FREIGHT_DW_SK, True,  "front"),   # freight door (#8125, SK half-size)
    # Passenger face (back, Y=BLDG_D_SK) -- main track/arc side
    (W_cx,   PASS_DOOR_W,  True,  "back"),    # waiting room door (#8033, matches front)
    (F_cx,   FREIGHT_DW_SK, True, "back"),    # freight door (#8125, SK half-size, matches front)
    # ticket office back face: operator bay only, no wall opening
    # End walls -- double window #8070 (all stations including SK)
    (END_CY, WIN_W_DOUBLE, False, "left"),    # left (waiting / JC) gable window
    (END_CY, WIN_W_DOUBLE, False, "right"),   # right (freight / HC) gable window
    # Interior wall: waiting room / ticket office
    (INT_DOOR_CY, INT_DOOR_W,  True,  "int_wt"),  # interior door (#8032)
    (INT_WIN_CY,  TICKET_WK_W, False, "int_wt"),  # ticket wicket notch (small)
    # Interior wall: ticket office / freight room
    (TF_DOOR_CY,  INT_DOOR_W,  True,  "int_tf"),  # interior door (#8032)
]

def apply_opening_mm(shape, cx, w, is_door, face):
    z0 = DOOR_SILL if is_door else WIN_SILL
    h  = BLDG_H - z0
    if face == "front":
        notch = Part.makeBox(w, WALL_T, h, FreeCAD.Vector(cx - w/2, 0, z0))
    elif face == "back":
        notch = Part.makeBox(w, WALL_T, h,
                             FreeCAD.Vector(cx - w/2, BLDG_D_SK - WALL_T, z0))
    elif face == "left":
        notch = Part.makeBox(WALL_T, w, h, FreeCAD.Vector(0, cx - w/2, z0))
    elif face == "right":
        notch = Part.makeBox(WALL_T, w, h,
                             FreeCAD.Vector(BLDG_L_SK - WALL_T, cx - w/2, z0))
    elif face == "int_wt":
        # Interior wall between waiting room and ticket office
        # cx = Y center of opening; wall runs in X at X_WT_WALL
        notch = Part.makeBox(WALL_T, w, h, FreeCAD.Vector(X_WT_WALL, cx - w/2, z0))
    elif face == "int_tf":
        # Interior wall between ticket office and freight room
        # cx = Y center of opening; wall runs in X at X_TF_WALL
        notch = Part.makeBox(WALL_T, w, h, FreeCAD.Vector(X_TF_WALL, cx - w/2, z0))
    else:
        return shape
    return shape.cut(notch)

# ---- Building shape ---------------------------------------------------------

def make_building_sk():
    outer = Part.makeBox(BLDG_L_SK, BLDG_D_SK, BLDG_H)
    shape = outer
    # Cut room interiors: B orientation -- waiting, ticket, freight (left to right)
    x = WALL_T
    for w in [WAITING_W_SK, TICKET_W_SK, FREIGHT_W_SK]:
        cut = Part.makeBox(w, BLDG_D_SK - 2 * WALL_T, BLDG_H,
                           FreeCAD.Vector(x, WALL_T, 0))
        shape = shape.cut(cut)
        x += w + WALL_T
    for opening in OPENINGS_SK:
        shape = apply_opening_mm(shape, *opening)
    # Operator bay: rectangular protrusion from ticket office on passenger face
    bay = Part.makeBox(BAY_W, BAY_PROJ, BLDG_H,
                       FreeCAD.Vector(T_cx - BAY_W / 2, BLDG_D_SK, 0))
    shape = shape.fuse(bay)
    return shape

# ---- Platform shape ---------------------------------------------------------

def make_platform_sk():
    slab = Part.makeBox(PLAT_L_SK, PLAT_D_SK, PLAT_H)
    # Building slot
    slot_x = PLAT_EXTRA - CLEARANCE / 2
    slot_y = NON_TRACK_SK - CLEARANCE / 2
    slot = Part.makeBox(BLDG_L_SK + CLEARANCE, BLDG_D_SK + CLEARANCE, PLAT_H,
                        FreeCAD.Vector(slot_x, slot_y, 0))
    slab = slab.cut(slot)
    # Bay notch: slot in passenger platform to accept operator bay protrusion
    bay_nx = PLAT_EXTRA + T_cx - (BAY_W + CLEARANCE) / 2
    bay_ny = NON_TRACK_SK + BLDG_D_SK - CLEARANCE / 2   # overlap slot edge slightly
    bay_notch = Part.makeBox(BAY_W + CLEARANCE, BAY_PROJ + CLEARANCE / 2, PLAT_H,
                             FreeCAD.Vector(bay_nx, bay_ny, 0))
    return slab.cut(bay_notch)

# ---- Build FreeCAD document -------------------------------------------------

doc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/StationPlanSK.FCStd"
os.makedirs(os.path.dirname(doc_path), exist_ok=True)

try:
    FreeCAD.closeDocument("StationPlanSK")
except Exception:
    pass

doc = FreeCAD.newDocument("StationPlanSK")

obj_b = doc.addObject("Part::Feature", "SK_Building")
obj_b.Shape = make_building_sk()

obj_p = doc.addObject("Part::Feature", "SK_Platform")
obj_p.Shape = make_platform_sk()
obj_p.Placement = FreeCAD.Placement(FreeCAD.Vector(0, -(PLAT_D_SK + 20), 0),
                                    FreeCAD.Rotation())

doc.recompute()
doc.saveAs(doc_path)
print(f"Saved {doc_path}")

# ---- Export STLs -------------------------------------------------------------

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)

for obj, fname in [(obj_b, "Building"), (obj_p, "Platform")]:
    # Reset placement to origin for export so STL vertices are in positive space,
    # then restore so the FCStd visual layout is unchanged.
    saved = FreeCAD.Placement(obj.Placement.Base, obj.Placement.Rotation)
    obj.Placement = FreeCAD.Placement()
    doc.recompute()
    mesh = MeshPart.meshFromShape(
        Shape=obj.Shape,
        LinearDeflection=0.05,
        AngularDeflection=0.1,
        Relative=False
    )
    out = os.path.join(stl_dir, f"StationPlanSK_{fname}.stl")
    mesh.write(out)
    print(f"Wrote {out}")
    obj.Placement = saved
doc.recompute()

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
