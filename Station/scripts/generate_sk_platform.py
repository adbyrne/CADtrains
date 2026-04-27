#!/usr/bin/env python3
"""
SK station — trackside platform slab.

Open-bottomed shell: top face on build plate, four walls hanging down.
Exterior vertical faces have 12" plank grooves + 6"×6" footer course at base.

NMRA RP-7.1 Classic era (1920–1969) HO dimensions used:
  E = 14mm  platform height above rail top (Classic; Old-Time: 10mm)
  P = 21mm  track centre to platform face min (Classic; Old-Time: 19mm)

Height math (freight/Classic):
  4mm rail height + 14mm Classic E - 1mm styrene plank sheet = 17mm printed
  Finished surface = 18mm above layout ground.

Height math (passenger, 8mm lower than freight):
  4mm rail height + 6mm E - 1mm styrene = 9mm printed
  Finished surface = 10mm above layout ground.

Plank layout on exterior faces (Z=0 = top/plate face):
  12" board = 3.5mm HO;  6"×6" footer = 1.75mm HO
  Freight (17mm): 4 boards (14mm) + 1 footer (1.75mm) + 1.25mm plain at grade
  Passenger (9mm): 2 boards (7mm) + 1 footer (1.75mm) + 0.25mm plain at grade

Wire holes: 2mm dia through top slab at partition wall siding exits
  Platform X ≈ 53.1mm (building X=48.4) and X ≈ 92.7mm (building X=88.0)
  Platform Y = 29mm (eave 24mm + wall 2mm + 3mm partition exit offset)

JST-XH 2P receptacle pocket: interior siding wall face, at platform bottom,
  centered between wire holes; wires route up through top, mating plug from below.

Set PLATFORM_VARIANT at the top of CODE to switch between freight and passenger.

Print orientation: top surface (Z=0) on build plate; shell opens downward; no supports.

Output (freight):
  FCStd: CADtrains/Station/freecad/SK_Platform.FCStd
  STL:   CADtrains/Station/printed_files/SK_Platform.stl
  PNG:   CADtrains/Station/images/SK_Platform_ISO.png
Output (passenger):
  FCStd: CADtrains/Station/freecad/SK_Platform_Passenger.FCStd
  STL:   CADtrains/Station/printed_files/SK_Platform_Passenger.stl
  PNG:   CADtrains/Station/images/SK_Platform_Passenger_ISO.png
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

CODE = '''
import FreeCAD, Part, MeshPart, math

def ft(f, i=0): return (f*12+i)*25.4/87.0
V = FreeCAD.Vector

# ---- Platform variant — change this line to switch output
# "freight"   → 17mm printed / 18mm finished  (NMRA Classic E=14mm)
# "passenger" →  9mm printed / 10mm finished  (E=6mm, 8mm lower than freight)
PLATFORM_VARIANT = "freight"

# ---- Building dims (shared with other SK scripts)
WALL_T    = 2.0
BLDG_D    = 40.0
FREIGHT_W = ft(13, 3)   # 46.40mm
TICKET_W  = ft(10, 2)   # 35.60mm
BLDG_L    = ft(7, 7) + TICKET_W + FREIGHT_W + 4 * WALL_T
EAVE_SIDE = 24.0
# Partition wall X positions (freight end = X=0, matching passenger wall orientation)
X_FT_WALL = WALL_T + FREIGHT_W                       # freight/ticket partition left face: 48.40mm
X_TW_WALL = WALL_T + FREIGHT_W + WALL_T + TICKET_W  # ticket/waiting partition left face: 86.00mm

# ---- NMRA RP-7.1 Classic era HO
RAIL_H    = 4.0    # rail top above ground
NMRA_E    = 14.0 if PLATFORM_VARIANT == "freight" else 6.0  # Old-Time = 10mm / 2mm
NMRA_P    = 21.0   # track centre to platform face min (Classic; Old-Time = 19mm)
STYRENE_T = 1.0    # styrene wood plank sheet

# ---- Platform dims
PLAT_H  = RAIL_H + NMRA_E - STYRENE_T   # 17mm freight / 9mm passenger
PLAT_L  = 126.0                          # site constraint
PLAT_D  = BLDG_D + 2*EAVE_SIDE          # = 88mm
SHELL_T = 2.0                            # wall thickness

# ---- Plank / footer geometry (print Z=0 is top/plate face)
BOARD_H  = 12*25.4/87.0    # = 3.503mm  (12" HO)
FOOTER_H =  6*25.4/87.0    # = 1.751mm  ( 6" HO)
n_boards = int(PLAT_H / BOARD_H)
board_zone  = n_boards * BOARD_H
footer_zone = PLAT_H - board_zone
GROOVE_D = 0.3   # depth into exterior face
GROOVE_W = 0.4   # groove width in Z

groove_z = ([BOARD_H * i for i in range(1, n_boards + 1)]
          + [board_zone + FOOTER_H])

print(f"Variant: {PLATFORM_VARIANT}  NMRA_E={NMRA_E}  PLAT_H={PLAT_H}")
print(f"BLDG_L={BLDG_L:.2f}  PLAT_L={PLAT_L}  PLAT_D={PLAT_D}")
print(f"Boards: {n_boards} × {BOARD_H:.3f}mm = {board_zone:.3f}mm")
print(f"Footer zone: {footer_zone:.3f}mm → 1 footer ({FOOTER_H:.3f}mm) + {footer_zone-FOOTER_H:.3f}mm plain at grade")
print(f"Groove Z positions: {[round(z,3) for z in groove_z]}")

# ---- Shell (open bottom: inner cavity from Z=SHELL_T to Z=PLAT_H)
outer = Part.makeBox(PLAT_L, PLAT_D, PLAT_H)
inner = Part.makeBox(PLAT_L - 2*SHELL_T, PLAT_D - 2*SHELL_T, PLAT_H - SHELL_T,
                     V(SHELL_T, SHELL_T, SHELL_T))
shell = outer.cut(inner)

# ---- Groove cuts on all 4 exterior faces
def cut_groove(body, z):
    gz = z - GROOVE_W/2
    # Siding face (Y=0, inward +Y)
    body = body.cut(Part.makeBox(PLAT_L,   GROOVE_D, GROOVE_W, V(0,               0,               gz)))
    # Passenger face (Y=PLAT_D, inward -Y)
    body = body.cut(Part.makeBox(PLAT_L,   GROOVE_D, GROOVE_W, V(0,               PLAT_D-GROOVE_D, gz)))
    # Waiting-end face (X=0, inward +X)
    body = body.cut(Part.makeBox(GROOVE_D, PLAT_D,   GROOVE_W, V(0,               0,               gz)))
    # Freight-end face (X=PLAT_L, inward -X)
    body = body.cut(Part.makeBox(GROOVE_D, PLAT_D,   GROOVE_W, V(PLAT_L-GROOVE_D, 0,               gz)))
    return body

for z in groove_z:
    shell = cut_groove(shell, z)

# ---- Vertical board-butt grooves (post lines, ~12ft spacing)
# Long sides (PLAT_L=126mm): 2 posts → 3 equal bays of 42mm ≈ ft(12)
# Short ends (PLAT_D=88mm): 1 post centred → 2 bays of 44mm
vpost_xs = [PLAT_L / 3, 2 * PLAT_L / 3]   # long-side post X: 42.0, 84.0mm
vpost_ys = [PLAT_D / 2]                     # end-face post Y: 44.0mm

for vx in vpost_xs:
    gx = vx - GROOVE_W / 2
    shell = shell.cut(Part.makeBox(GROOVE_W, GROOVE_D, PLAT_H, V(gx, 0,               0)))
    shell = shell.cut(Part.makeBox(GROOVE_W, GROOVE_D, PLAT_H, V(gx, PLAT_D-GROOVE_D, 0)))

for vy in vpost_ys:
    gy = vy - GROOVE_W / 2
    shell = shell.cut(Part.makeBox(GROOVE_D, GROOVE_W, PLAT_H, V(0,               gy, 0)))
    shell = shell.cut(Part.makeBox(GROOVE_D, GROOVE_W, PLAT_H, V(PLAT_L-GROOVE_D, gy, 0)))

print(f"Post grooves: long sides X={[round(x,1) for x in vpost_xs]}mm; ends Y={[round(y,1) for y in vpost_ys]}mm")
print("Shell + grooves done.")

# ---- Wire holes through top slab
# Building is centered on platform; BLDG_X0 = platform X where building X=0 begins
BLDG_X0 = (PLAT_L - BLDG_L) / 2          # ≈ 4.70mm
WIRE_Y  = EAVE_SIDE + WALL_T + 3.0        # = 29mm: aligns with partition siding exit (Y=3mm bldg interior)
WIRE_D  = 2.0                              # wire hole diameter
# Partition wall X in building coords → platform coords
wire_xs = [BLDG_X0 + X_FT_WALL + WALL_T/2,   # FT partition center (was using outer face — 1mm inward)
           BLDG_X0 + X_TW_WALL + WALL_T/2]   # TW partition center
for wx in wire_xs:
    shell = shell.cut(Part.makeCylinder(WIRE_D/2, SHELL_T, V(wx, WIRE_Y, 0), V(0, 0, 1)))
print(f"Wire holes: platform X={[round(x,1) for x in wire_xs]}  Y={WIRE_Y:.1f}mm")

# ---- JST-XH 2P connector boss — horizontal channel on inner face of top slab
# Connector lies along Y (depth direction):
#   collar end (wire exit) at open entry side (siding-facing, Y=boss_y0)
#   mating face at far end; mating connector enters through 5.8×5.8mm end-wall opening
# Lips (LIP mm inward from each X side wall) at boss bottom (Z face) retain
# connector from falling — lip opening = BODY_SQ - 2*LIP = 2.8mm.
# Connector body slides in from open Y entry end; collar (wider than channel) stops at entry face.
# Physically measured connector: body 5.8mm sq × 7.8mm; collar 6.6×7.6mm × 6.3mm.
BODY_SQ = 5.8   # body cross-section (square, mm) — no added clearance for press fit
BODY_H  = 7.8   # body length along Y
LIP     = 1.5   # retaining lip width (inward in X from side walls)
WALL    = 1.5   # wall thickness (top Z, X sides, far Y end wall)

boss_w  = BODY_SQ + 2*WALL    # = 8.8mm (X)
boss_d  = BODY_H + WALL       # = 9.3mm (Y: open at entry, WALL at far end)
boss_hz = WALL + BODY_SQ + LIP # = 8.8mm (Z from SHELL_T: top wall + channel + lips)

# Center X between wire holes; Y entry clears building siding wall inner face (Y=EAVE_SIDE+WALL_T)
boss_cx = (wire_xs[0] + wire_xs[1]) / 2
boss_x0 = boss_cx - boss_w / 2
boss_y0 = EAVE_SIDE + WALL_T + 2.0   # 2mm clearance past building siding wall inner face

boss = Part.makeBox(boss_w, boss_d, boss_hz, V(boss_x0, boss_y0, SHELL_T))
shell = shell.fuse(boss)

ch_z0  = SHELL_T + WALL        # Z: top of channel (below boss top wall)
lip_z0 = ch_z0 + BODY_SQ      # Z: bottom of channel / top of lips

# Channel cut: full BODY_SQ × BODY_H × BODY_SQ; open at entry end (Y=boss_y0)
shell = shell.cut(Part.makeBox(BODY_SQ, BODY_H, BODY_SQ,
                               V(boss_x0 + WALL, boss_y0, ch_z0)))

# Lip opening: narrow slot between the two lips at boss bottom face
shell = shell.cut(Part.makeBox(BODY_SQ - 2*LIP, BODY_H, LIP,
                               V(boss_x0 + WALL + LIP, boss_y0, lip_z0)))

# Far end wall opening: 5.8×5.8mm for mating connector approach from platform interior
shell = shell.cut(Part.makeBox(BODY_SQ, WALL, BODY_SQ,
                               V(boss_x0 + WALL, boss_y0 + BODY_H, ch_z0)))

overhang = max(0.0, SHELL_T + boss_hz - PLAT_H)
print(f"Boss (horizontal): {boss_w}×{boss_d}×{boss_hz}mm")
print(f"  X={boss_x0:.1f}–{boss_x0+boss_w:.1f}  Y={boss_y0:.1f}–{boss_y0+boss_d:.1f}  Z={SHELL_T}–{SHELL_T+boss_hz:.1f}")
print(f"  Open entry at Y={boss_y0:.1f} (collar/wire side);  mating opening at Y={boss_y0+BODY_H:.1f}")
print(f"  Lips: {LIP}mm × 2;  drop-out gap {BODY_SQ-2*LIP:.1f}mm at Z={lip_z0:.1f}–{SHELL_T+boss_hz:.1f}")
if overhang > 0:
    print(f"  NOTE: boss extends {overhang:.1f}mm below platform open bottom — needs layout access hole")

# ---- Document
BASE       = "/home/abyrne/Projects/Trains/CADtrains/Station/"
vtag       = "" if PLATFORM_VARIANT == "freight" else f"_{PLATFORM_VARIANT.capitalize()}"
doc_name   = f"SK_Platform{vtag}"
fc_path    = BASE + f"freecad/{doc_name}.FCStd"
stl_path   = BASE + f"printed_files/{doc_name}.stl"
img_path   = BASE + f"images/{doc_name}_ISO.png"

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
