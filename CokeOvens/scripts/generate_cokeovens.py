"""
generate_cokeovens.py — v8
HO scale (1:87) bank coke oven section + stone end caps.
C&O Railway prototype, circa 1900, West Virginia coalfields.

v8 changes vs v7:
  - Fix alignment hole on section left face: hole was mis-positioned outside the
    part (started at X=-PEG_H-0.5, never intersected the base slab). Now starts
    at X=0 and cuts 3.5 mm into the left face. Peg on right face unchanged.
  - Add alignment hole on end cap right face (X=END_CAP_W) — receives the peg
    from the last section (or a separate metal pin for left-end cap). Mirror
    transform propagates the hole to the mirror cap's left face automatically.
  - 1.5 mm fillet behind the front wall (at slope fill / front wall junction) to
    ease the overhang when printing back-side-down (+Y on platter). Covered by
    scenery. Retaining wall inner corner has stepped topology that prevents filleting.
  - STL export included in script (CokeOven_*_v8.stl).

v6 changes vs v5:
  - Master stone courses: all stone-faced surfaces share course Z heights.
    Horizontal mortar joints align at the same elevation on every face.
    seed parameter controls per-face stone widths only.
  - Slope fill: solid wedge from back of oven wall (Y=FW_THICK) to back of
    back shelf (Y=CAP_BACK_Y), sloping from OW_H_TOTAL-2 mm at front to
    SHELF_H-2 mm at back. Dome spheres cut from fill so shells remain hollow.
    Encloses the void between oven wall and dome; supports upright printing.
  - Parapet zone trim: base slab in parapet strip trimmed to parapet-top height
    so section end-face yard zone matches end cap yard block height.
  - End cap multi-step profile (4 zones):
      Zone A: Y=-YARD_DEPTH to 0,        H=YARD_BASE_H  (~12 mm, yard)
      Zone B: Y=0 to FW_THICK,           H=OW_H_TOTAL   (~38 mm, oven wall)
      Zone C: Y=FW_THICK to CAP_BACK_Y,  3 equal steps  (~38→52 mm)
  - End cap stone courses on oven wall face (Y=0 riser, Z=YARD_BASE_H→OW_H_TOTAL).
  - End cap stone courses on 3 step-riser faces in zone C.
  - Larry track grooves on end cap back shelf top (matching section grooves).
  - Mirrored end cap updated with new profile.
"""

import FreeCAD
import Part
import random
import math

try:
    FreeCAD.closeDocument("CokeOvens")
except Exception:
    pass
doc = FreeCAD.newDocument("CokeOvens")

# ============================================================
# PARAMETERS
# ============================================================
SCALE = 87.0
def ft(feet): return feet * 304.8 / SCALE

N_OVENS      = 4
OVEN_ID      = ft(12)
OVEN_WALL    = ft(1.375)
OVEN_OD      = OVEN_ID + 2 * OVEN_WALL
OVEN_RI      = OVEN_ID / 2
OVEN_RE      = OVEN_OD / 2
OVEN_SPACING = ft(14.75)
LARRY_R      = ft(1.25)

ARCH_W       = ft(5)
ARCH_R       = ARCH_W / 2
ARCH_RECT_H  = ft(1)
ARCH_RAISE   = ft(2.5)          # plinth height below arch opening

FW_THICK     = ft(2)
FW_H         = ARCH_RAISE + ARCH_RECT_H + ARCH_R + ft(1.5)

YARD_DEPTH   = ft(14)
YARD_BASE_H  = ft(3.5)
YARD_SLAB    = ft(0.75)
LEDGE_H      = ft(0.75)
LEDGE_THICK  = ft(0.75)
YARD_DROP    = 1.5              # mm

Z_YARD       = YARD_BASE_H
Z_DOME       = YARD_BASE_H + ARCH_RAISE
Z_CROWN      = Z_DOME + OVEN_RE
BASE_H       = Z_DOME + 1.0

SHELF_Y0     = FW_THICK + OVEN_OD
SHELF_DEPTH  = ft(4)
SHELF_H      = Z_CROWN + ft(1.5)

DOME_CY      = FW_THICK + OVEN_RE
FULL_DEPTH   = YARD_DEPTH + SHELF_Y0 + SHELF_DEPTH

ARCH_CUT_D   = DOME_CY - OVEN_RI + 3

# Larry track grooves (N scale)
LARRY_GAUGE  = 9.0
LARRY_GW     = 1.8
LARRY_GD     = 0.9

# Alignment pegs
PEG_R        = 1.0
PEG_H        = 3.0
PEG_HOLE_R   = 1.15

# Stone course parameters
STONE_LARGE  = 3.6
STONE_SMALL  = 1.7
STONE_MORTAR = 0.42
STONE_GD     = 0.9

# Brick courses (arch front wall)
BRICK_PITCH  = (5.5 / 12) * 304.8 / SCALE
BRICK_GD     = 0.8
BRICK_GW     = 0.45

# End cap dimensions
END_CAP_W    = ft(2)
CAP_BACK_Y   = SHELF_Y0 + SHELF_DEPTH   # full depth of back block
CAP_BACK_H   = SHELF_H                  # full cap height = Larry track shelf top

# Oven wall total absolute height (Z=0 to top of front wall)
OW_H_TOTAL   = YARD_BASE_H + FW_H       # ≈ 38 mm

# End cap zone-C step profile (3 equal steps from OW_H_TOTAL to CAP_BACK_H)
CAP_N_STEPS  = 3
_zone_c_y0   = FW_THICK
_zone_c_depth = CAP_BACK_Y - FW_THICK
_step_d      = _zone_c_depth / CAP_N_STEPS
_step_h      = [OW_H_TOTAL + (s + 1) * (CAP_BACK_H - OW_H_TOTAL) / CAP_N_STEPS
                for s in range(CAP_N_STEPS)]

# Inter-dome fill piers
PIER_W       = 4.0
PIER_H       = OVEN_RE * 0.35

# Print-assist fillet radius (behind front wall, covered by scenery)
# 2 mm exceeds face width near section ends; 1.5 mm is the maximum that succeeds.
FILLET_R     = 1.5


# ============================================================
# HELPERS
# ============================================================
def safe_cut(base, tool, lbl=""):
    try:
        r = base.cut(tool)
        return r if not r.isNull() else base
    except Exception:
        return base


def _try_fillet(shape, r, edges, label=""):
    """Apply fillet; return original shape on failure."""
    if not edges:
        print(f"  Fillet {label}: no edges found, skipping")
        return shape
    try:
        result = shape.makeFillet(r, edges)
        if not result.isNull():
            print(f"  Fillet {label}: {len(edges)} edge(s) filleted r={r}")
            return result
    except Exception as ex:
        print(f"  Fillet {label} failed: {ex}")
    return shape


def _build_courses(z_bot, z_top, seed):
    """Return list of (z_bottom, height) for variable-height stone courses."""
    rng = random.Random(seed)
    courses = []
    z = z_bot
    total = max(1.0, z_top - z_bot)
    while z < z_top - STONE_SMALL * 0.4:
        progress = min(1.0, (z - z_bot) / total)
        if progress < 0.25:
            center = STONE_LARGE
        elif progress > 0.75:
            center = STONE_SMALL
        else:
            t = (progress - 0.25) / 0.5
            center = STONE_LARGE + t * (STONE_SMALL - STONE_LARGE)
        sigma = (STONE_LARGE - STONE_SMALL) * 0.18
        h = rng.gauss(center, sigma)
        h = max(STONE_SMALL, min(STONE_LARGE, h))
        if z + h > z_top:
            h = z_top - z
        if h >= STONE_SMALL * 0.5:
            courses.append((z, h))
        z += h
    return courses


# Master course list — all stone-faced surfaces use this for Z alignment.
# Horizontal mortar joints fall at the same elevation on every face.
MASTER_COURSES = _build_courses(0, SHELF_H + 10, seed=42)

# Course-aligned yard height: first course boundary at or above YARD_BASE_H.
# Used on both the retaining wall face and the end cap front face so both
# show complete courses rather than a cut-off half-course at the top.
CAP_YARD_H = YARD_BASE_H
for _zc, _hc in MASTER_COURSES:
    if _zc < YARD_BASE_H <= _zc + _hc:
        CAP_YARD_H = _zc + _hc
        break
    if _zc >= YARD_BASE_H:
        break


def _filter_courses(courses, z_bot, z_top):
    """Filter master course list to [z_bot, z_top], clipping the last if needed."""
    result = []
    for z_c, h in courses:
        if z_c >= z_top - STONE_SMALL * 0.4:
            break
        if z_c < z_bot:
            continue
        if z_c + h > z_top:
            h = z_top - z_c
        if h >= STONE_SMALL * 0.5:
            result.append((z_c, h))
    return result


def _split_x_segments(x0, x1, excludes):
    """Return sub-spans of [x0, x1] that don't overlap any (ex0, ex1) in excludes."""
    segs, cur = [], x0
    for ex0, ex1 in sorted(excludes):
        if ex0 > cur and cur < x1:
            segs.append((cur, min(ex0, x1)))
        cur = max(cur, ex1)
        if cur >= x1:
            break
    if cur < x1:
        segs.append((cur, x1))
    return [(s, e) for s, e in segs if e - s > 0.4]


def stone_courses_y(x_span, z_bot, z_top, face_y, g_depth=STONE_GD, seed=42, courses=None, x_offset=0.0, arch_rings=None):
    """
    Variable-height stone courses on a Y-normal face.
    face_y: Y coordinate of face; material on +Y side.
    x_offset: X origin of this span in world space.
    arch_rings: list of (cx, spring_z, r_outer) — voussoir arch rings to exclude.
                Horizontal joints are split using the actual semicircle chord width at
                each course height, so no rectangular ghost appears above/below the ring.
                Vertical joints whose x falls within the ring extents are also suppressed.
    """
    use_courses = (_filter_courses(courses, z_bot, z_top) if courses is not None
                   else _build_courses(z_bot, z_top, seed))
    rng = random.Random(seed)
    tools = []
    for idx, (z_c, h) in enumerate(use_courses):
        top_z = z_c + h
        if top_z < z_top - STONE_MORTAR * 0.3:
            # Z-aware exclusion: chord width of ring at this course-top height
            x_excl = []
            if arch_rings:
                for acx, aspz, r_out in arch_rings:
                    dz = top_z - aspz
                    if 0 < dz < r_out:
                        chord_hw = math.sqrt(r_out ** 2 - dz ** 2)
                        x_excl.append((acx - chord_hw, acx + chord_hw))
            if x_excl:
                for sx0, sx1 in _split_x_segments(x_offset, x_offset + x_span, x_excl):
                    tools.append(Part.makeBox(
                        sx1 - sx0 + 2, g_depth + 0.5, STONE_MORTAR,
                        FreeCAD.Vector(sx0 - 1, face_y - 0.5, top_z - STONE_MORTAR / 2)
                    ))
            else:
                tools.append(Part.makeBox(
                    x_span + 2, g_depth + 0.5, STONE_MORTAR,
                    FreeCAD.Vector(x_offset - 1, face_y - 0.5, top_z - STONE_MORTAR / 2)
                ))
        size_t = max(0.0, min(1.0, (h - STONE_SMALL) / max(0.01, STONE_LARGE - STONE_SMALL)))
        ratio = 2.0 + (1.0 - size_t)
        ratio += rng.uniform(-0.15, 0.15)
        ratio = max(1.9, min(3.1, ratio))
        stone_w = h * ratio
        offset = stone_w * 0.5 if (idx % 2 == 1) else 0.0
        x = -offset
        while x < x_span + stone_w:
            jx = x + stone_w
            wx = x_offset + jx
            in_ring = arch_rings and any(
                abs(wx - acx) < r_out and z_c < aspz + r_out and z_c + h > aspz
                for acx, aspz, r_out in arch_rings
            )
            if 0.4 < jx < x_span - 0.4 and not in_ring:
                tools.append(Part.makeBox(
                    STONE_MORTAR, g_depth + 0.5, h,
                    FreeCAD.Vector(wx - STONE_MORTAR / 2, face_y - 0.5, z_c)
                ))
            x += stone_w
    return Part.makeCompound(tools) if tools else None


def stone_courses_x(y_start, y_span, z_bot, z_top, face_x, g_depth=STONE_GD, seed=42, courses=None):
    """
    Variable-height stone courses on an X-normal face.
    face_x: X coordinate of face; material on +X side.
    courses: pre-built master list for Z alignment. seed controls stone widths.
    """
    use_courses = (_filter_courses(courses, z_bot, z_top) if courses is not None
                   else _build_courses(z_bot, z_top, seed))
    rng = random.Random(seed)
    y_end = y_start + y_span
    tools = []
    for idx, (z_c, h) in enumerate(use_courses):
        top_z = z_c + h
        if top_z < z_top - STONE_MORTAR * 0.3:
            tools.append(Part.makeBox(
                g_depth + 0.5, y_span + 2, STONE_MORTAR,
                FreeCAD.Vector(face_x - 0.5, y_start - 1, top_z - STONE_MORTAR / 2)
            ))
        size_t = max(0.0, min(1.0, (h - STONE_SMALL) / max(0.01, STONE_LARGE - STONE_SMALL)))
        ratio = 2.0 + (1.0 - size_t)
        ratio += rng.uniform(-0.15, 0.15)
        ratio = max(1.9, min(3.1, ratio))
        stone_w = h * ratio
        offset = stone_w * 0.5 if (idx % 2 == 1) else 0.0
        y = y_start - offset
        while y < y_end + stone_w:
            jy = y + stone_w
            if y_start + 0.4 < jy < y_end - 0.4:
                tools.append(Part.makeBox(
                    g_depth + 0.5, STONE_MORTAR, h,
                    FreeCAD.Vector(face_x - 0.5, jy - STONE_MORTAR / 2, z_c)
                ))
            y += stone_w
    return Part.makeCompound(tools) if tools else None


def brick_courses_y(x_span, z_bot, z_top, face_y):
    """Uniform brick courses on a Y-normal face."""
    tools = []
    z = z_bot + BRICK_PITCH
    while z < z_top - BRICK_GW:
        tools.append(Part.makeBox(
            x_span + 2, BRICK_GD + 0.5, BRICK_GW,
            FreeCAD.Vector(-1, face_y - 0.5, z - BRICK_GW / 2)
        ))
        z += BRICK_PITCH
    return Part.makeCompound(tools) if tools else None


def arch_voussoir_joints(n_ovens, face_y=0):
    """
    Radial voussoir joints on each arch ring (7 voussoirs = 6 joints per arch),
    plus vertical jamb joints on the rectangular reveal below the spring line.
    Ring: ARCH_R → ARCH_R + OVEN_WALL.  Joints straddle face_y at STONE_GD depth.
    """
    N_VOUS   = 9
    spring_z = Z_DOME + ARCH_RECT_H    # spring line elevation (arch center Z)
    hw       = STONE_MORTAR / 2

    tools = []
    for i in range(n_ovens):
        cx = OVEN_RE + i * OVEN_SPACING

        # --- Radial voussoir joints ---
        for k in range(1, N_VOUS):
            theta = math.pi * k / N_VOUS   # angle from +X (right spring), 0→π
            dx =  math.cos(theta)
            dz =  math.sin(theta)
            px = -math.sin(theta)           # perpendicular in XZ plane
            pz =  math.cos(theta)

            r0 = ARCH_R - 0.5               # slightly inside arch opening
            r1 = ARCH_R + OVEN_WALL + 0.5  # slightly outside ring

            corners = [
                FreeCAD.Vector(cx + r0*dx - hw*px, face_y - 0.5, spring_z + r0*dz - hw*pz),
                FreeCAD.Vector(cx + r1*dx - hw*px, face_y - 0.5, spring_z + r1*dz - hw*pz),
                FreeCAD.Vector(cx + r1*dx + hw*px, face_y - 0.5, spring_z + r1*dz + hw*pz),
                FreeCAD.Vector(cx + r0*dx + hw*px, face_y - 0.5, spring_z + r0*dz + hw*pz),
            ]
            edges = [Part.LineSegment(corners[j], corners[(j + 1) % 4]).toShape()
                     for j in range(4)]
            slot = Part.Face(Part.Wire(edges)).extrude(FreeCAD.Vector(0, STONE_GD + 0.5, 0))
            tools.append(slot)

        # --- Extrados groove (outer edge of arch ring — voussoir tops) ---
        r_out = ARCH_R + OVEN_WALL
        ext_outer = Part.makeCylinder(
            r_out + hw, STONE_GD + 0.5,
            FreeCAD.Vector(cx, face_y - 0.5, spring_z), FreeCAD.Vector(0, 1, 0)
        )
        ext_inner = Part.makeCylinder(
            r_out - hw, STONE_GD + 0.5,
            FreeCAD.Vector(cx, face_y - 0.5, spring_z), FreeCAD.Vector(0, 1, 0)
        )
        ext_groove = ext_outer.cut(ext_inner)
        # Clip to upper half (Z >= spring_z) only
        clip = Part.makeBox(
            (r_out + 2) * 2, STONE_GD + 2, r_out + 2,
            FreeCAD.Vector(cx - r_out - 2, face_y - 1, spring_z)
        )
        tools.append(ext_groove.common(clip))

        # --- Vertical jamb joints on rectangular reveal ---
        for sign in (-1.0, 1.0):
            jx = cx + sign * ARCH_R
            tools.append(Part.makeBox(
                STONE_MORTAR, STONE_GD + 0.5, ARCH_RECT_H + 0.5,
                FreeCAD.Vector(jx - hw, face_y - 0.5, Z_DOME - 0.25)
            ))

    return Part.makeCompound(tools) if tools else None


# ============================================================
# SECTION BUILDER
# ============================================================
def make_section(n_ovens):
    sect_w = (n_ovens - 1) * OVEN_SPACING + OVEN_OD

    # ---- 1. BASE SLAB
    peg_y = -YARD_DEPTH / 2
    peg_z = YARD_BASE_H / 2

    yard_base = Part.makeBox(
        sect_w, FULL_DEPTH, BASE_H,
        FreeCAD.Vector(0, -YARD_DEPTH, 0)
    )
    # Alignment peg on right face
    peg = Part.makeCylinder(PEG_R, PEG_H,
                            FreeCAD.Vector(sect_w, peg_y, peg_z),
                            FreeCAD.Vector(1, 0, 0))
    yard_base = yard_base.fuse(peg)
    # Alignment hole on left face — starts at X=0 (face) and cuts into part (+X)
    hole = Part.makeCylinder(PEG_HOLE_R, PEG_H + 0.5,
                             FreeCAD.Vector(0, peg_y, peg_z),
                             FreeCAD.Vector(1, 0, 0))
    yard_base = safe_cut(yard_base, hole, "peg_hole_left")

    # Trim yard area (Y=-YARD_DEPTH+LEDGE_THICK+0.5 to Y=0) to retaining wall height
    yard_trim = Part.makeBox(
        sect_w + 2, YARD_DEPTH - LEDGE_THICK - 0.5, BASE_H - YARD_BASE_H + 0.5,
        FreeCAD.Vector(-1, -YARD_DEPTH + LEDGE_THICK + 0.5, YARD_BASE_H)
    )
    yard_base = safe_cut(yard_base, yard_trim, "yard_height_trim")

    # Retaining wall stone courses moved to post-fuse (see step 9.5) so the
    # parapet fuse doesn't fill back grooves in the CAP_YARD_H zone.

    # Yard drop pocket
    yard_pocket = Part.makeBox(
        sect_w, YARD_DEPTH - LEDGE_THICK - 1.0, YARD_DROP + 0.5,
        FreeCAD.Vector(0, -YARD_DEPTH + LEDGE_THICK + 1.0, YARD_BASE_H - YARD_DROP)
    )
    yard_base = safe_cut(yard_base, yard_pocket, "yard_drop")

    # ---- 2. PARAPET LIP
    parapet = Part.makeBox(
        sect_w, LEDGE_THICK, LEDGE_H,
        FreeCAD.Vector(0, -YARD_DEPTH, Z_YARD)
    )

    # ---- 3. FRONT WALL
    fw = Part.makeBox(sect_w, FW_THICK, FW_H,
                      FreeCAD.Vector(0, 0, Z_YARD))

    # ---- 4. DOME SHELLS (hollow hemispheres, raised by ARCH_RAISE)
    domes = []
    for i in range(n_ovens):
        cx = OVEN_RE + i * OVEN_SPACING
        cy, cz = DOME_CY, Z_DOME
        outer = Part.makeSphere(OVEN_RE, FreeCAD.Vector(cx, cy, cz))
        inner = Part.makeSphere(OVEN_RI, FreeCAD.Vector(cx, cy, cz))
        csz   = OVEN_OD * 3
        clip  = Part.makeBox(csz, csz, csz,
                             FreeCAD.Vector(cx - csz/2, cy - csz/2, cz))
        shell = outer.common(clip).cut(inner.common(clip))
        larry_z = cz + OVEN_RE - OVEN_WALL - 0.5
        shell = safe_cut(shell, Part.makeCylinder(
            LARRY_R, OVEN_WALL + 2,
            FreeCAD.Vector(cx, cy, larry_z), FreeCAD.Vector(0, 0, 1)
        ), f"larry_{i}")
        domes.append(shell)

    # ---- 5. BACK SHELF (larry track grooves on top)
    back_shelf = Part.makeBox(
        sect_w, SHELF_DEPTH, SHELF_H - Z_YARD,
        FreeCAD.Vector(0, SHELF_Y0, Z_YARD)
    )
    larry_y_c = SHELF_Y0 + SHELF_DEPTH / 2
    for dY in (-LARRY_GAUGE / 2, LARRY_GAUGE / 2):
        groove = Part.makeBox(
            sect_w + 2, LARRY_GW, LARRY_GD + 0.5,
            FreeCAD.Vector(-1, larry_y_c + dY - LARRY_GW / 2, SHELF_H - LARRY_GD)
        )
        back_shelf = safe_cut(back_shelf, groove, f"larry_{dY:.1f}")

    # ---- 6. INTER-DOME FILL PIERS
    piers = []
    for i in range(n_ovens - 1):
        x_tan = OVEN_OD + i * OVEN_SPACING
        piers.append(Part.makeBox(
            PIER_W, OVEN_OD, PIER_H,
            FreeCAD.Vector(x_tan - PIER_W / 2, FW_THICK, Z_DOME)
        ))

    # ---- 7. SLOPE FILL (oven wall back → back shelf rear face)
    # Trapezoidal wedge: top slopes from OW_H_TOTAL-2 at Y=FW_THICK to
    # SHELF_H-2 at Y=CAP_BACK_Y, leaving 2 mm recess for scenic material.
    # Dome outer spheres cut from fill so dome shells remain hollow.
    fill_front_h = OW_H_TOTAL - 2.0
    fill_back_h  = SHELF_H - 2.0
    fill_y0      = FW_THICK
    fill_y1      = CAP_BACK_Y

    # Build trapezoid profile in YZ plane (X=0), extrude +X by sect_w
    _p = [
        FreeCAD.Vector(0, fill_y0, 0),
        FreeCAD.Vector(0, fill_y1, 0),
        FreeCAD.Vector(0, fill_y1, fill_back_h),
        FreeCAD.Vector(0, fill_y0, fill_front_h),
    ]
    _edges = [
        Part.LineSegment(_p[0], _p[1]).toShape(),
        Part.LineSegment(_p[1], _p[2]).toShape(),
        Part.LineSegment(_p[2], _p[3]).toShape(),
        Part.LineSegment(_p[3], _p[0]).toShape(),
    ]
    fill_shape = Part.Face(Part.Wire(_edges)).extrude(FreeCAD.Vector(sect_w, 0, 0))

    # Cut dome outer spheres (upper half) from fill
    for i in range(n_ovens):
        cx = OVEN_RE + i * OVEN_SPACING
        cy, cz = DOME_CY, Z_DOME
        csz = OVEN_OD * 3
        clip = Part.makeBox(csz, csz, csz,
                            FreeCAD.Vector(cx - csz/2, cy - csz/2, cz))
        dome_cut = Part.makeSphere(OVEN_RE, FreeCAD.Vector(cx, cy, cz)).common(clip)
        fill_shape = safe_cut(fill_shape, dome_cut, f"fill_dome_{i}")

    # ---- 8. FUSE ALL PARTS
    section = yard_base.fuse(parapet).fuse(fw)
    for d in domes:
        section = section.fuse(d)
    section = section.fuse(back_shelf)
    for p in piers:
        section = section.fuse(p)
    section = section.fuse(fill_shape)

    # Trim parapet zone base slab to parapet-top height.
    # yard_trim leaves a LEDGE_THICK strip untrimmed at Y=-YARD_DEPTH; trim it here.
    parapet_top_z = YARD_BASE_H + LEDGE_H
    parapet_zone_trim = Part.makeBox(
        sect_w + 2, LEDGE_THICK + 0.5, BASE_H - parapet_top_z + 0.5,
        FreeCAD.Vector(-1, -YARD_DEPTH, parapet_top_z)
    )
    section = safe_cut(section, parapet_zone_trim, "parapet_zone_trim")

    # ---- 9. ARCH CUTS (applied to fully fused solid)
    for i in range(n_ovens):
        cx = OVEN_RE + i * OVEN_SPACING
        z_ab = Z_DOME
        section = safe_cut(section, Part.makeBox(
            ARCH_W, ARCH_CUT_D, ARCH_RECT_H,
            FreeCAD.Vector(cx - ARCH_W / 2, -1, z_ab)
        ), f"arch_rect_{i}")
        arch_cyl = Part.makeCylinder(
            ARCH_R, ARCH_CUT_D,
            FreeCAD.Vector(cx, -1, z_ab + ARCH_RECT_H),
            FreeCAD.Vector(0, 1, 0)
        )
        upper_clip = Part.makeBox(
            ARCH_W + 4, ARCH_CUT_D + 4, ARCH_R + 2,
            FreeCAD.Vector(cx - ARCH_W / 2 - 2, -2, z_ab + ARCH_RECT_H)
        )
        section = safe_cut(section, arch_cyl.common(upper_clip), f"arch_semi_{i}")

    # ---- 9.5 RETAINING WALL STONE COURSES (post-fuse, post-parapet-trim)
    # Cut after fuse so parapet material doesn't fill back the top course grooves.
    g = stone_courses_y(sect_w, 0, CAP_YARD_H, -YARD_DEPTH, seed=1, courses=MASTER_COURSES)
    if g: section = safe_cut(section, g, "retaining_stone")

    # ---- 10. ARCH VOUSSOIR JOINTS (radial + jamb reveals)
    g = arch_voussoir_joints(n_ovens)
    if g: section = safe_cut(section, g, "voussoir_joints")

    # ---- 11. FRONT WALL STONE COURSES (post-fuse, arch ring zones excluded)
    # Horizontal joints use circular chord width at each course height — no
    # rectangular ghost above/below the ring. Vertical joints in ring also skipped.
    _arch_rings = [(OVEN_RE + _i * OVEN_SPACING, Z_DOME + ARCH_RECT_H, ARCH_R + OVEN_WALL)
                   for _i in range(n_ovens)]
    g = stone_courses_y(sect_w, Z_YARD, OW_H_TOTAL, 0,
                        seed=14, courses=MASTER_COURSES, arch_rings=_arch_rings)
    if g: section = safe_cut(section, g, "fw_stone")

    section = section.removeSplitter()

    # ---- 12. PRINT-ASSIST FILLET (behind front wall, covered by scenery)
    # Printing back-side-down (+Y on platter): the back face of the front wall
    # faces downward in print space above the slope fill termination.
    # Fillet at Y=FW_THICK, Z=fill_front_h (where fill top meets front wall back face).
    # Retaining wall inner corner has complex step topology (yard trim/parapet) that
    # prevents filleting; it is naturally supported by the base slab.
    fill_front_h = OW_H_TOTAL - 2.0
    fw_back_edges = [e for e in section.Edges
                     if hasattr(e.Curve, 'Direction')
                     and abs(e.Curve.Direction.x) > 0.9
                     and all(abs(v.Point.y - FW_THICK) < 0.6 for v in e.Vertexes)
                     and all(abs(v.Point.z - fill_front_h) < 0.6 for v in e.Vertexes)]
    section = _try_fillet(section, FILLET_R, fw_back_edges, "fw_back")

    return section, sect_w


# ============================================================
# 4-OVEN SECTION
# ============================================================
section4, sect_w4 = make_section(N_OVENS)
feat4 = doc.addObject("Part::Feature", "CokeOvenSection")
feat4.Shape = section4
feat4.Label = "CokeOvenSection_4ovens_v8"

# ============================================================
# 1-OVEN TEST PIECE
# ============================================================
section1, sect_w1 = make_section(1)
feat1 = doc.addObject("Part::Feature", "CokeOvenSection_1")
feat1.Shape = section1
feat1.Label = "CokeOvenSection_1oven_v8"

# ============================================================
# END CAP — MULTI-STEP PROFILE
# ============================================================
# Zone A: yard block
yard_block = Part.makeBox(
    END_CAP_W, YARD_DEPTH, CAP_YARD_H,
    FreeCAD.Vector(0, -YARD_DEPTH, 0)
)
# Zone B: oven wall block
ow_block = Part.makeBox(
    END_CAP_W, FW_THICK, OW_H_TOTAL,
    FreeCAD.Vector(0, 0, 0)
)
# Zone C: 3 stepping blocks (each taller than the last)
_step_blocks = []
for _s in range(CAP_N_STEPS):
    _sy  = _zone_c_y0 + _s * _step_d
    _sd  = _step_d + (0.1 if _s < CAP_N_STEPS - 1 else 0.0)  # small overlap for clean fuse
    _step_blocks.append(Part.makeBox(
        END_CAP_W, _sd, _step_h[_s],
        FreeCAD.Vector(0, _sy, 0)
    ))

end_cap = yard_block.fuse(ow_block)
for _sb in _step_blocks:
    end_cap = end_cap.fuse(_sb)
end_cap = end_cap.removeSplitter()

# -- Alignment hole on right face (X=END_CAP_W) — receives peg from adjacent section
# Mirror transform propagates this hole to the mirror cap's left face automatically.
_peg_y = -YARD_DEPTH / 2
_peg_z = YARD_BASE_H / 2
_cap_hole = Part.makeCylinder(PEG_HOLE_R, PEG_H + 0.5,
                               FreeCAD.Vector(END_CAP_W + 0.5, _peg_y, _peg_z),
                               FreeCAD.Vector(-1, 0, 0))
end_cap = safe_cut(end_cap, _cap_hole, "cap_hole_right")

# -- Stone courses: outward face (X=0, full height/depth)
g = stone_courses_x(-YARD_DEPTH, FULL_DEPTH, 0, CAP_BACK_H, 0, seed=10, courses=MASTER_COURSES)
if g: end_cap = safe_cut(end_cap, g, "cap_outward_stone")

# -- Stone courses: track-facing front face (Y=-YARD_DEPTH, Z=0→CAP_YARD_H)
g = stone_courses_y(END_CAP_W, 0, CAP_YARD_H, -YARD_DEPTH, seed=12, courses=MASTER_COURSES)
if g: end_cap = safe_cut(end_cap, g, "cap_front_stone")

# -- Stone courses: oven wall face (Y=0 riser, Z=CAP_YARD_H→OW_H_TOTAL)
g = stone_courses_y(END_CAP_W, CAP_YARD_H, OW_H_TOTAL, 0, seed=14, courses=MASTER_COURSES)
if g: end_cap = safe_cut(end_cap, g, "cap_ow_face_stone")

# -- Stone courses: zone-C step riser faces (3 risers, each facing -Y)
_riser_face_y  = [_zone_c_y0 + _s * _step_d for _s in range(CAP_N_STEPS)]
_riser_z_bot   = [OW_H_TOTAL] + _step_h[: CAP_N_STEPS - 1]
_riser_z_top   = _step_h[:]
for _s in range(CAP_N_STEPS):
    g = stone_courses_y(
        END_CAP_W, _riser_z_bot[_s], _riser_z_top[_s],
        _riser_face_y[_s], seed=16 + _s * 2, courses=MASTER_COURSES
    )
    if g: end_cap = safe_cut(end_cap, g, f"cap_riser{_s + 1}_stone")

# -- Larry track grooves on end cap back shelf top (matching section)
_larry_y_c = SHELF_Y0 + SHELF_DEPTH / 2
for _dY in (-LARRY_GAUGE / 2, LARRY_GAUGE / 2):
    _groove = Part.makeBox(
        END_CAP_W + 2, LARRY_GW, LARRY_GD + 0.5,
        FreeCAD.Vector(-1, _larry_y_c + _dY - LARRY_GW / 2, SHELF_H - LARRY_GD)
    )
    end_cap = safe_cut(end_cap, _groove, f"cap_larry_{_dY:.1f}")

feat_cap = doc.addObject("Part::Feature", "EndCapStoneWall")
feat_cap.Shape = end_cap
feat_cap.Label = "EndCapStoneWall_v8"

# ============================================================
# MIRRORED END CAP (for opposite bank end)
# ============================================================
mat = FreeCAD.Matrix()
mat.A11 = -1
mat.A14 = END_CAP_W   # x' = -x + END_CAP_W
end_cap_m = end_cap.transformGeometry(mat)

feat_cap_m = doc.addObject("Part::Feature", "EndCapStoneWall_Mirror")
feat_cap_m.Shape = end_cap_m
feat_cap_m.Label = "EndCapStoneWall_Mirror_v8"

# ============================================================
# RECOMPUTE, COLOURS, POSITIONS, SAVE
# ============================================================
doc.recompute()

if FreeCAD.GuiUp:
    import FreeCADGui
    colours = {
        "CokeOvenSection":        (0.75, 0.72, 0.68),
        "CokeOvenSection_1":      (0.75, 0.72, 0.68),
        "EndCapStoneWall":        (0.58, 0.55, 0.50),
        "EndCapStoneWall_Mirror": (0.58, 0.55, 0.50),
    }
    for name, col in colours.items():
        vc = FreeCADGui.activeDocument().getObject(name)
        if vc:
            vc.ShapeColor = col

    doc.getObject("EndCapStoneWall").Placement = FreeCAD.Placement(
        FreeCAD.Vector(-END_CAP_W - 5, 0, 0), FreeCAD.Rotation()
    )
    doc.getObject("EndCapStoneWall_Mirror").Placement = FreeCAD.Placement(
        FreeCAD.Vector(sect_w4 + 5, 0, 0), FreeCAD.Rotation()
    )
    doc.getObject("CokeOvenSection_1").Placement = FreeCAD.Placement(
        FreeCAD.Vector(0, FULL_DEPTH + 15, 0), FreeCAD.Rotation()
    )

    view = FreeCADGui.activeDocument().activeView()
    view.viewIsometric()
    FreeCADGui.SendMsgToActiveView("ViewFit")

doc.saveAs("/home/abyrne/Projects/Trains/CADtrains/CokeOvens/freecad/CokeOvens.FCStd")

# ============================================================
# STL EXPORT
# ============================================================
import MeshPart
_stl_dir = "/home/abyrne/Projects/Trains/CADtrains/CokeOvens/printed_files/"

def _export_stl(shape, path):
    mesh = MeshPart.meshFromShape(
        Shape=shape, LinearDeflection=0.05, AngularDeflection=0.1, Relative=False
    )
    mesh.write(path)
    return mesh.CountFacets

_facets = {}
_facets["4ov"]  = _export_stl(feat4.Shape,    _stl_dir + "CokeOven_Section_4ovens_v8.stl")
_facets["1ov"]  = _export_stl(feat1.Shape,    _stl_dir + "CokeOven_Section_1oven_v8.stl")
_facets["cap"]  = _export_stl(feat_cap.Shape,  _stl_dir + "CokeOven_EndCap_v8.stl")
_facets["capm"] = _export_stl(feat_cap_m.Shape, _stl_dir + "CokeOven_EndCap_Mirror_v8.stl")

# ============================================================
# ISO SCREENSHOT
# ============================================================
if FreeCAD.GuiUp:
    _img_path = "/home/abyrne/Projects/Trains/CADtrains/CokeOvens/images/cokeovens_iso.png"
    FreeCADGui.activeDocument().activeView().saveImage(_img_path, 1920, 1080, 'White')

# ============================================================
# REPORT
# ============================================================
bb4  = feat4.Shape.BoundBox
bb1  = feat1.Shape.BoundBox
bbc  = feat_cap.Shape.BoundBox
bbcm = feat_cap_m.Shape.BoundBox
_result_ = (
    f"CokeOvens v8\n"
    f"  Section 4ov : {bb4.XLength:.1f} x {bb4.YLength:.1f} x {bb4.ZLength:.1f} mm"
    f"  valid={feat4.Shape.isValid()} solids={len(feat4.Shape.Solids)}"
    f"  facets={_facets['4ov']}\n"
    f"  Section 1ov : {bb1.XLength:.1f} x {bb1.YLength:.1f} x {bb1.ZLength:.1f} mm"
    f"  valid={feat1.Shape.isValid()} solids={len(feat1.Shape.Solids)}"
    f"  facets={_facets['1ov']}\n"
    f"  End cap     : {bbc.XLength:.1f} x {bbc.YLength:.1f} x {bbc.ZLength:.1f} mm"
    f"  valid={feat_cap.Shape.isValid()}  facets={_facets['cap']}\n"
    f"  Cap mirror  : {bbcm.XLength:.1f} x {bbcm.YLength:.1f} x {bbcm.ZLength:.1f} mm"
    f"  valid={feat_cap_m.Shape.isValid()}  facets={_facets['capm']}\n"
    f"  Key dims: Z_DOME={Z_DOME:.1f}  OW_H_TOTAL={OW_H_TOTAL:.1f}  SHELF_H={SHELF_H:.1f} mm\n"
    f"  Step heights: {[round(h, 1) for h in _step_h]} mm\n"
    f"  Fill: Y={FW_THICK:.1f}..{CAP_BACK_Y:.1f}  top {OW_H_TOTAL-2:.1f}→{SHELF_H-2:.1f} mm\n"
    f"  Fits 250x210: 4ov={'YES' if bb4.XLength<=250 else 'NO'}"
    f"  1ov={'YES' if bb1.XLength<=250 else 'NO'}\n"
    f"  CAP_YARD_H={CAP_YARD_H:.2f} (YARD_BASE_H={YARD_BASE_H:.2f})\n"
    f"  STLs: {list(_facets.items())}\n"
    f"  Saved: freecad/CokeOvens.FCStd"
)
