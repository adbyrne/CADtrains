#!/usr/bin/env python3
"""
Standard station — trackside platform slab.

Open-bottomed shell: top face on build plate, four walls hanging down.
Exterior vertical faces have 12" plank grooves + 6"×6" footer course at base.

Orientation A: waiting end at X=0 (matches siding/floor wall orientation)
Orientation B: freight end at X=0 (matches passenger wall orientation, mirror)

Set PLATFORM_VARIANT and PLATFORM_ORIENTATION at top of CODE.

NMRA RP-7.1 Classic era (1920–1969) HO dimensions:
  E = 14mm  platform height above rail top (Classic; Old-Time: 10mm)

Print orientation: top surface (Z=0) on build plate; shell opens downward; no supports.

Output:
  FCStd: CADtrains/Station/freecad/Std_Platform[_B][_Passenger].FCStd
  STL:   CADtrains/Station/printed_files/Std_Platform[_B][_Passenger].stl
  PNG:   CADtrains/Station/images/Std_Platform[_B]_ISO.png  (freight only)
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, math

def ft(f, i=0): return (f*12+i)*25.4/87.0
V = FreeCAD.Vector

# ---- Platform variant — change these lines to switch output ------------------
PLATFORM_VARIANT     = "freight"      # "freight" or "passenger"
PLATFORM_ORIENTATION = "A"            # "A" (waiting@X=0) or "B" (freight@X=0)

# ---- Building dimensions (standard variant) ---------------------------------
WALL_T    = 2.0
WAITING_W = ft(15, 2)   # 53.1mm
TICKET_W  = ft(10, 2)   # 35.6mm
FREIGHT_W = ft(26, 6)   # 92.8mm
BLDG_D    = ft(15, 0)   # 52.55mm
BLDG_L    = WAITING_W + TICKET_W + FREIGHT_W + 4 * WALL_T
EAVE_SIDE = 24.0

# Partition wall X positions for each orientation (used for wire hole placement)
if PLATFORM_ORIENTATION == "A":
    # Waiting end at X=0 — siding wall orientation
    # Partition centres from waiting end
    X_WALL_1 = WALL_T + WAITING_W               # WT wall left face: ~55.1mm
    X_WALL_2 = X_WALL_1 + WALL_T + TICKET_W     # TF wall left face: ~92.8mm
else:
    # Freight end at X=0 — passenger wall orientation
    # Partition centres from freight end
    X_WALL_1 = WALL_T + FREIGHT_W               # FT wall left face: ~94.8mm
    X_WALL_2 = X_WALL_1 + WALL_T + TICKET_W     # TW wall left face: ~132.4mm

# ---- NMRA RP-7.1 Classic era HO
RAIL_H    = 4.0
NMRA_E    = 14.0 if PLATFORM_VARIANT == "freight" else 6.0
STYRENE_T = 1.0

# ---- Platform dims
PLAT_H  = RAIL_H + NMRA_E - STYRENE_T   # 17mm freight / 9mm passenger
PLAT_L  = BLDG_L + 10.0                 # ~199.6mm (5mm overhang each end)
PLAT_D  = BLDG_D + 2*EAVE_SIDE          # ~100.55mm
SHELL_T = 2.0

# ---- Plank / footer geometry (print Z=0 is top/plate face)
BOARD_H  = 12*25.4/87.0    # = 3.503mm  (12" HO)
FOOTER_H =  6*25.4/87.0    # = 1.751mm  ( 6" HO)
n_boards = int(PLAT_H / BOARD_H)
board_zone  = n_boards * BOARD_H
footer_zone = PLAT_H - board_zone
GROOVE_D = 0.3
GROOVE_W = 0.4

groove_z = ([BOARD_H * i for i in range(1, n_boards + 1)]
          + [board_zone + FOOTER_H])

print(f"Std Platform  variant={PLATFORM_VARIANT}  orient={PLATFORM_ORIENTATION}")
print(f"  NMRA_E={NMRA_E}  PLAT_H={PLAT_H}")
print(f"  BLDG_L={BLDG_L:.2f}  PLAT_L={PLAT_L:.2f}  PLAT_D={PLAT_D:.2f}")
print(f"  Boards: {n_boards} × {BOARD_H:.3f}mm")
print(f"  X_WALL_1={X_WALL_1:.2f}  X_WALL_2={X_WALL_2:.2f}")

# ---- Shell (open bottom)
outer = Part.makeBox(PLAT_L, PLAT_D, PLAT_H)
inner = Part.makeBox(PLAT_L - 2*SHELL_T, PLAT_D - 2*SHELL_T, PLAT_H - SHELL_T,
                     V(SHELL_T, SHELL_T, SHELL_T))
shell = outer.cut(inner)

# ---- Groove cuts on all 4 exterior faces
def cut_groove(body, z):
    gz = z - GROOVE_W/2
    body = body.cut(Part.makeBox(PLAT_L,   GROOVE_D, GROOVE_W, V(0,               0,               gz)))
    body = body.cut(Part.makeBox(PLAT_L,   GROOVE_D, GROOVE_W, V(0,               PLAT_D-GROOVE_D, gz)))
    body = body.cut(Part.makeBox(GROOVE_D, PLAT_D,   GROOVE_W, V(0,               0,               gz)))
    body = body.cut(Part.makeBox(GROOVE_D, PLAT_D,   GROOVE_W, V(PLAT_L-GROOVE_D, 0,               gz)))
    return body

for z in groove_z:
    shell = cut_groove(shell, z)

# ---- Vertical board-butt grooves (post lines)
vpost_xs = [PLAT_L / 3, 2 * PLAT_L / 3]
vpost_ys = [PLAT_D / 2]

for vx in vpost_xs:
    gx = vx - GROOVE_W / 2
    shell = shell.cut(Part.makeBox(GROOVE_W, GROOVE_D, PLAT_H, V(gx, 0,               0)))
    shell = shell.cut(Part.makeBox(GROOVE_W, GROOVE_D, PLAT_H, V(gx, PLAT_D-GROOVE_D, 0)))

for vy in vpost_ys:
    gy = vy - GROOVE_W / 2
    shell = shell.cut(Part.makeBox(GROOVE_D, GROOVE_W, PLAT_H, V(0,               gy, 0)))
    shell = shell.cut(Part.makeBox(GROOVE_D, GROOVE_W, PLAT_H, V(PLAT_L-GROOVE_D, gy, 0)))

print(f"  Post grooves: long sides X={[round(x,1) for x in vpost_xs]}  ends Y={[round(y,1) for y in vpost_ys]}")

# ---- Wire holes through top slab
BLDG_X0 = (PLAT_L - BLDG_L) / 2          # centre building on platform
WIRE_Y   = EAVE_SIDE + WALL_T + 3.0      # = 29mm: aligns with partition siding exit
WIRE_D   = 2.0
wire_xs  = [BLDG_X0 + X_WALL_1 + WALL_T/2,
            BLDG_X0 + X_WALL_2 + WALL_T/2]
for wx in wire_xs:
    shell = shell.cut(Part.makeCylinder(WIRE_D/2, SHELL_T, V(wx, WIRE_Y, 0), V(0, 0, 1)))
print(f"  Wire holes: platform X={[round(x,1) for x in wire_xs]}  Y={WIRE_Y:.1f}mm")

# ---- JST-XH 2P connector boss — horizontal channel on inner face of top slab
BODY_SQ = 5.8
BODY_H  = 7.8
LIP     = 1.5
WALL    = 1.5

boss_w  = BODY_SQ + 2*WALL
boss_d  = BODY_H + WALL
boss_hz = WALL + BODY_SQ + LIP

boss_cx = (wire_xs[0] + wire_xs[1]) / 2
boss_x0 = boss_cx - boss_w / 2
boss_y0 = EAVE_SIDE + WALL_T + 2.0

boss = Part.makeBox(boss_w, boss_d, boss_hz, V(boss_x0, boss_y0, SHELL_T))
shell = shell.fuse(boss)

ch_z0  = SHELL_T + WALL
lip_z0 = ch_z0 + BODY_SQ

shell = shell.cut(Part.makeBox(BODY_SQ, BODY_H, BODY_SQ,
                               V(boss_x0 + WALL, boss_y0, ch_z0)))
shell = shell.cut(Part.makeBox(BODY_SQ - 2*LIP, BODY_H, LIP,
                               V(boss_x0 + WALL + LIP, boss_y0, lip_z0)))
shell = shell.cut(Part.makeBox(BODY_SQ, WALL, BODY_SQ,
                               V(boss_x0 + WALL, boss_y0 + BODY_H, ch_z0)))

overhang = max(0.0, SHELL_T + boss_hz - PLAT_H)
print(f"  Boss: {boss_w}×{boss_d}×{boss_hz}mm  X={boss_x0:.1f}–{boss_x0+boss_w:.1f}  Y={boss_y0:.1f}–{boss_y0+boss_d:.1f}")
if overhang > 0:
    print(f"  NOTE: boss extends {overhang:.1f}mm below platform open bottom — needs layout access hole")

# ---- Export
BASE   = "/home/abyrne/Projects/Trains/CADtrains/Station/"
b_tag  = "" if PLATFORM_ORIENTATION == "A" else "_B"
v_tag  = "" if PLATFORM_VARIANT == "freight" else f"_{PLATFORM_VARIANT.capitalize()}"
doc_name = f"Std_Platform{b_tag}{v_tag}"
fc_path  = BASE + f"freecad/{doc_name}.FCStd"
stl_path = BASE + f"printed_files/{doc_name}.stl"
img_path = BASE + f"images/{doc_name}_ISO.png"

try: FreeCAD.closeDocument(doc_name)
except: pass
doc = FreeCAD.newDocument(doc_name)

obj = doc.addObject("Part::Feature", "Platform")
obj.Shape = shell
if FreeCAD.GuiUp:
    obj.ViewObject.ShapeColor = (0.75, 0.70, 0.60)

doc.recompute()
doc.saveAs(fc_path)
print(f"Saved {fc_path}")

m = MeshPart.meshFromShape(Shape=shell, LinearDeflection=0.05, AngularDeflection=0.1)
m.write(stl_path)
print(f"Saved {stl_path}")

if FreeCAD.GuiUp and PLATFORM_VARIANT == "freight":
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
