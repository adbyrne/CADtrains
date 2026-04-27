#!/usr/bin/env python3
"""
Station Planning Token - HO Scale NY&E Layout
Generates two-piece planning token: Building (A + B mirror) and Platform.

Prototype basis: New Haven standard combination station (Fig. 172)
  Freight Room 26'6" | Ticket Office 10'2" | Waiting Room 15'2"
  Building: 54'0" x 15'0" exterior
  Passenger platform (track side): 8'0"
  Non-track side: 3'0" (planning minimum)

HO scale: 1:87 -- 1 prototype foot = 3.508mm

Pieces:
  Building_A -- freight room at left (x=0) end, waiting room at right
  Building_B -- mirror: waiting room at left, freight room at right
  Platform   -- single piece (symmetric), slot accepts either building

Opening positions (Building A, prototype feet from freight/left end):
  Front face (passenger/track side, Y=0):
    Freight window 1:  center  9.0', width 8.5'  (bay 4'5"--13'7" from floor plan)
    Freight window 2:  center 18.2', width 8.5'  (bay 13'7"--22'9")
    Ticket window:     center 32.2', width 4.0'
    Waiting window:    center 43.5', width 6.0'
    Waiting door:      center 50.5', width 4.0'  (full-height)
  Back face (non-track side, Y=BLDG_D):
    Freight door:      center 13.0', width 10.0' (large sliding door, full-height)
    Waiting door:      center 46.0', width  4.0' (full-height)
  End walls (center along building depth, 0=front):
    Left  (freight end): window center 7.5', width 4.0'
    Right (waiting end): window center 7.5', width 4.0'
"""

import xmlrpc.client
import sys

proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, os

# ---- Dimensions (HO 1:87) ---------------------------------------------------

def ft(feet, inches=0):
    return (feet * 12 + inches) * (25.4 / 87.0)

BLDG_L    = ft(54, 0)    # exterior length  ~189mm
BLDG_D    = ft(15, 0)    # exterior depth   ~52.6mm
BLDG_H    = 8.0          # increased for door/window notch visibility
WALL_T    = 2.0          # wall thickness (printable min)
DOOR_SILL = 2.0          # door sill keeps walls connected at base
WIN_SILL  = 4.0          # window sill (taller than door sill)

FREIGHT_W = ft(26, 6)    # ~92.8mm
TICKET_W  = ft(10, 2)    # ~35.6mm
WAITING_W = BLDG_L - 4 * WALL_T - FREIGHT_W - TICKET_W  # exact remainder ~52.7mm

BAY_W    = ft(6, 0)      # operator bay width      ~21mm  (6'0" measured from Fig. 172)
BAY_PROJ = ft(2, 6)      # operator bay projection  ~8.75mm (2'6" measured from Fig. 172)

NON_TRACK  = ft(3, 0)    # non-track side ~10.5mm
PASSENGER  = ft(8, 0)    # track side     ~28.0mm
PLAT_EXTRA = 5.0         # end overhang beyond building
PLAT_L     = BLDG_L + 2 * PLAT_EXTRA
PLAT_D     = NON_TRACK + BLDG_D + PASSENGER
PLAT_H     = 2.0
CLEARANCE  = 0.5         # slip-fit clearance per side

print(f"Building {BLDG_L:.1f}x{BLDG_D:.1f}mm h={BLDG_H}  "
      f"Rooms F={FREIGHT_W:.1f} T={TICKET_W:.1f} W={WAITING_W:.1f}  "
      f"Platform {PLAT_L:.1f}x{PLAT_D:.1f}mm")
print(f"Operator bay: {BAY_W:.1f} x {BAY_PROJ:.1f}mm  "
      f"passenger clearance past bay: {PASSENGER - BAY_PROJ:.1f}mm  "
      f"({(PASSENGER - BAY_PROJ) / ft(1,0):.1f}')")

# ---- Opening definitions (Building A) ---------------------------------------
# Format: (center_ft, width_ft, is_door, face)
# face 'front'/'back': center_ft measured from freight (left) end along building length
# face 'left'/'right': center_ft measured from front (passenger side) along building depth
#
# Derived from Fig.172 floor plan bay dimensions and elevation drawing.
# Top dim row: 4'5"|9'2"|9'2"|7'0"|4'10"|7'4"|3'8"|3'8"|4'9" = 54'0"

OPENINGS_A = [
    # Front face (passenger/track side, Y=0)
    ( 9.0, 8.5, False, "front"),  # freight window 1 (bay 4'5"--13'7")
    (18.2, 8.5, False, "front"),  # freight window 2 (bay 13'7"--22'9")
    (32.2, 4.0, False, "front"),  # ticket office window
    (43.5, 6.0, False, "front"),  # waiting room window
    (50.5, 4.0, True,  "front"),  # waiting room entrance door (full height)
    # Back face (non-track side, Y=BLDG_D)
    (13.0, 10.0, True,  "back"),  # freight sliding door (large, full height)
    (46.0,  4.0, True,  "back"),  # waiting room back door (full height)
    # End walls (center along depth from passenger/front side)
    (7.5,  4.0, False, "left"),   # freight room gable window
    (7.5,  4.0, False, "right"),  # waiting room gable window
]

def mirror_openings(openings, bldg_l_ft=54.0):
    result = []
    for (c, w, is_door, face) in openings:
        if face in ("front", "back"):
            result.append((bldg_l_ft - c, w, is_door, face))
        elif face == "left":
            result.append((c, w, is_door, "right"))
        elif face == "right":
            result.append((c, w, is_door, "left"))
    return result

def apply_opening(shape, opening):
    c_ft, w_ft, is_door, face = opening
    w  = ft(w_ft)
    z0 = DOOR_SILL if is_door else WIN_SILL
    h  = BLDG_H - DOOR_SILL if is_door else BLDG_H - WIN_SILL

    if face == "front":
        cx = ft(c_ft)
        notch = Part.makeBox(w, WALL_T, h, FreeCAD.Vector(cx - w/2, 0, z0))
    elif face == "back":
        cx = ft(c_ft)
        notch = Part.makeBox(w, WALL_T, h, FreeCAD.Vector(cx - w/2, BLDG_D - WALL_T, z0))
    elif face == "left":
        cy = ft(c_ft)
        notch = Part.makeBox(WALL_T, w, h, FreeCAD.Vector(0, cy - w/2, z0))
    elif face == "right":
        cy = ft(c_ft)
        notch = Part.makeBox(WALL_T, w, h, FreeCAD.Vector(BLDG_L - WALL_T, cy - w/2, z0))
    else:
        return shape
    return shape.cut(notch)

# ---- Building shape ---------------------------------------------------------

def make_building(freight_left=True):
    outer = Part.makeBox(BLDG_L, BLDG_D, BLDG_H)
    room_widths = [FREIGHT_W, TICKET_W, WAITING_W] if freight_left \
                  else [WAITING_W, TICKET_W, FREIGHT_W]
    shape = outer
    x = WALL_T
    for w in room_widths:
        cut = Part.makeBox(w, BLDG_D - 2 * WALL_T, BLDG_H,
                           FreeCAD.Vector(x, WALL_T, 0))
        shape = shape.cut(cut)
        x += w + WALL_T

    openings = OPENINGS_A if freight_left else mirror_openings(OPENINGS_A)
    for opening in openings:
        shape = apply_opening(shape, opening)
    # Operator bay on back face (track/passenger side, Y=BLDG_D)
    T_cx = WALL_T + room_widths[0] + WALL_T + TICKET_W / 2
    bay = Part.makeBox(BAY_W, BAY_PROJ, BLDG_H,
                       FreeCAD.Vector(T_cx - BAY_W / 2, BLDG_D, 0))
    shape = shape.fuse(bay)
    return shape

# ---- Platform shape ---------------------------------------------------------

def make_platform():
    slab = Part.makeBox(PLAT_L, PLAT_D, PLAT_H)
    # Building slot
    slot_x = PLAT_EXTRA - CLEARANCE / 2
    slot_y = NON_TRACK  - CLEARANCE / 2
    slot   = Part.makeBox(BLDG_L + CLEARANCE, BLDG_D + CLEARANCE, PLAT_H,
                          FreeCAD.Vector(slot_x, slot_y, 0))
    slab = slab.cut(slot)
    # Bay notch at Building_A ticket office position.
    # Flip platform end-to-end for Building_B (notch mirrors to correct position).
    T_cx_A = WALL_T + FREIGHT_W + WALL_T + TICKET_W / 2
    bay_nx = PLAT_EXTRA + T_cx_A - (BAY_W + CLEARANCE) / 2
    bay_ny = NON_TRACK + BLDG_D - CLEARANCE / 2
    bay_notch = Part.makeBox(BAY_W + CLEARANCE, BAY_PROJ + CLEARANCE / 2, PLAT_H,
                             FreeCAD.Vector(bay_nx, bay_ny, 0))
    return slab.cut(bay_notch)

# ---- Build FreeCAD document -------------------------------------------------

doc_path = "/home/abyrne/Projects/Trains/CADtrains/Station/freecad/StationPlanToken.FCStd"
os.makedirs(os.path.dirname(doc_path), exist_ok=True)

try:
    FreeCAD.closeDocument("StationPlanToken")
except Exception:
    pass

doc = FreeCAD.newDocument("StationPlanToken")

obj_a = doc.addObject("Part::Feature", "Building_A")
obj_a.Shape = make_building(freight_left=True)
obj_a.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation())

obj_b = doc.addObject("Part::Feature", "Building_B")
obj_b.Shape = make_building(freight_left=False)
obj_b.Placement = FreeCAD.Placement(FreeCAD.Vector(BLDG_L + 20, 0, 0), FreeCAD.Rotation())

obj_p = doc.addObject("Part::Feature", "Platform")
obj_p.Shape = make_platform()
obj_p.Placement = FreeCAD.Placement(FreeCAD.Vector(0, -(PLAT_D + 20), 0), FreeCAD.Rotation())

doc.recompute()
doc.saveAs(doc_path)
print(f"Saved {doc_path}")

# ---- Export STLs -------------------------------------------------------------

stl_dir = "/home/abyrne/Projects/Trains/CADtrains/Station/printed_files"
os.makedirs(stl_dir, exist_ok=True)

for obj, name in [(obj_a, "Building_A"), (obj_b, "Building_B"), (obj_p, "Platform")]:
    saved = FreeCAD.Placement(obj.Placement.Base, obj.Placement.Rotation)
    obj.Placement = FreeCAD.Placement()
    doc.recompute()
    mesh = MeshPart.meshFromShape(
        Shape=obj.Shape,
        LinearDeflection=0.05,
        AngularDeflection=0.1,
        Relative=False
    )
    out = os.path.join(stl_dir, f"StationPlan_{name}.stl")
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
