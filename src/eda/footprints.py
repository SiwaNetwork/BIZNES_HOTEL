"""Посадочные места проекта (TENSH.pretty), которых нет в стандартной библиотеке KiCad 7."""
from pathlib import Path


def _hdr(name, descr, smd=True):
    return [f'(footprint "{name}" (version 20221018) (generator pcbnew)', '  (layer "F.Cu")',
            f'  (descr "{descr}")', f'  (attr {"smd" if smd else "through_hole"})',
            '  (fp_text reference "REF**" (at 0 -1.5) (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.1))))',
            f'  (fp_text value "{name}" (at 0 1.5) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))']


def _rect(layer, x1, y1, x2, y2, w=0.1):
    return (f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) '
            f'(fill none) (layer "{layer}"))')


def _line(layer, x1, y1, x2, y2, w=0.1):
    return f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}"))'


def smd_pad(num, x, y, w, h, shape="roundrect", paste=True, rr=0.15):
    layers = '"F.Cu" "F.Mask"' + (' "F.Paste"' if paste else '')
    extra = f" (roundrect_rratio {rr})" if shape == "roundrect" else ""
    return f'  (pad "{num}" smd {shape} (at {x:.3f} {y:.3f}) (size {w:.3f} {h:.3f}) (layers {layers}){extra})'


def write(lib_dir, name, lines):
    p = Path(lib_dir)
    p.mkdir(parents=True, exist_ok=True)
    (p / f"{name}.kicad_mod").write_text("\n".join(lines + [")"]) + "\n", encoding="utf-8")
    return f"TENSH:{name}"


def castellated(lib_dir, w=1.2, l=1.6, drill=0.8):
    """Краевой контакт-полуотверстие: металлизированное отверстие на кромке (центр в начале координат,
    плата — в сторону +Y посадочного места) и площадки на F.Cu/B.Cu."""
    name = f"EdgePad_Castellated_{w}x{l}mm_D{drill}mm"
    lines = _hdr(name, "Castellated edge pad, plated half-hole", smd=False)
    lines.append(f'  (pad "1" thru_hole roundrect (at 0 {l / 2 - 0.0:.3f}) (size {w} {l}) (drill {drill} (offset 0 {-(l / 2):.3f})) '
                 f'(layers "*.Cu" "*.Mask") (roundrect_rratio 0.15) (property pad_prop_castellated))')
    lines.append(_rect("F.Fab", -w / 2, 0, w / 2, l))
    return write(lib_dir, name, lines)


def shield_frame(lib_dir, L, W, wall=0.4, gap_every=None):
    """Рамка экрана, припаиваемая по периметру: четыре полосковые площадки шириной wall (центр рамки — 0,0)."""
    name = f"RF_Shield_Frame_{L}x{W}mm"
    lines = _hdr(name, f"Solder-down RF shield frame {L}x{W} mm")
    hl, hw = L / 2, W / 2
    pads = [((0, -hw + wall / 2), (L, wall)), ((0, hw - wall / 2), (L, wall)),
            ((-hl + wall / 2, 0), (wall, W - 2 * wall)), ((hl - wall / 2, 0), (wall, W - 2 * wall))]
    for (x, y), (a, b) in pads:
        lines.append(smd_pad("1", x, y, a, b, "rect"))
    lines.append(_rect("F.Fab", -hl, -hw, hl, hw))
    lines.append(_rect("F.CrtYd", -hl - 0.2, -hw - 0.2, hl + 0.2, hw + 0.2, 0.05))
    return write(lib_dir, name, lines)


def generic_smd(lib_dir, name, descr, pads, body, silk=True):
    """pads: [(num, x, y, w, h)] — прямоугольные площадки; body: (L, W) корпуса."""
    lines = _hdr(name, descr)
    for num, x, y, w, h in pads:
        lines.append(smd_pad(num, x, y, w, h))
    L, W = body
    lines.append(_rect("F.Fab", -L / 2, -W / 2, L / 2, W / 2))
    if silk:
        lines.append(_rect("F.SilkS", -L / 2 - 0.1, -W / 2 - 0.1, L / 2 + 0.1, W / 2 + 0.1, 0.1))
    xs = [x for _, x, _, w, _ in pads] or [0]
    ys = [y for _, _, y, _, h in pads] or [0]
    cx = max(L / 2, max(abs(x) + w / 2 for _, x, _, w, _ in pads)) + 0.25
    cy = max(W / 2, max(abs(y) + h / 2 for _, _, y, _, h in pads)) + 0.25
    lines.append(_rect("F.CrtYd", -cx, -cy, cx, cy, 0.05))
    return write(lib_dir, name, lines)


def castellated_row(lib_dir, n, pitch=2.54, w=1.2, l=1.6, drill=0.8, name=None):
    """Ряд краевых полуотверстий: начало координат — середина ряда на кромке платы;
    площадки уходят внутрь платы (−Y в системе KiCad, т. е. вверх для нижней кромки)."""
    name = name or f"Castellated_1x{n:02d}_P{pitch}mm_{w}x{l}mm_D{drill}mm"
    lines = _hdr(name, f"Castellated edge pads 1x{n}, pitch {pitch} mm", smd=False)
    x0 = -(n - 1) * pitch / 2
    for i in range(n):
        x = x0 + i * pitch
        # металлизированное отверстие на кромке (кольцо 0,2 мм) + площадки внутрь платы на обоих слоях
        lines.append(f'  (pad "{i + 1}" thru_hole circle (at {x:.3f} 0) (size {drill + 0.4:.2f} {drill + 0.4:.2f}) '
                     f'(drill {drill}) (layers "*.Cu" "*.Mask") (property pad_prop_castellated))')
        for lay in ('"F.Cu" "F.Mask"', '"B.Cu" "B.Mask"'):     # площадка отступает от кромки на 0,3 мм
            lines.append(f'  (pad "{i + 1}" smd roundrect (at {x:.3f} {-(l + 0.3) / 2:.3f}) (size {w} {l - 0.3:.2f}) '
                         f'(layers {lay}) (roundrect_rratio 0.15))')
    lines.append(_rect("F.Fab", x0 - w / 2, -l, -x0 + w / 2, 0))
    lines.append(_rect("F.CrtYd", x0 - w / 2 - 0.25, -l - 0.25, -x0 + w / 2 + 0.25, drill / 2, 0.05))
    return write(lib_dir, name, lines)


def samtec_ss4_iridium(lib_dir):
    """Гнездо Samtec SS4-10 (2×10, шаг 0,4 мм) под модем Iridium 9603N. Площадки 0,23×1,2 мм по открытой
    библиотеке SparkFun (IRIDIUM_9603N); на слое F.Fab — контур модема 29,6×31,5 мм."""
    name = "Samtec_SS4-10_P0.4mm_Iridium9603"
    lines = _hdr(name, "Samtec SS4-10-x.xx-L-D-K-TR socket for Iridium 9603/9603N; module outline on F.Fab")
    for i in range(1, 21):
        k = (i - 1) // 2
        x = 1.8 - 0.4 * k
        y = -2.435 if i % 2 else 2.435
        lines.append(smd_pad(str(i), x, y, 0.23, 1.2, "rect"))
    lines.append(_rect("F.SilkS", -2.6, -3.35, 2.6, 3.35, 0.12))
    lines.append(_line("F.SilkS", 2.1, -3.6, 2.6, -3.6, 0.15))
    lines.append(_rect("F.Fab", -12.3, -3.4, 17.3, 28.1, 0.1))
    lines.append(_rect("F.CrtYd", -2.85, -3.6, 2.85, 3.6, 0.05))
    return write(lib_dir, name, lines)


def supercap_horizontal(lib_dir, d=8.0, length=13.5, pitch=3.5, side="L", drill=0.8, pad=1.6):
    """Ионистор радиальный, уложенный на плату: начало координат — центр корпуса;
    выводы загнуты к плате у торца (L — слева, R — справа)."""
    name = f"SuperCap_Radial_D{d}mm_L{length}mm_Horizontal_{side}"
    lines = _hdr(name, f"Radial EDLC D{d} L{length} mm laid flat, leads at {side} end", smd=False)
    s = -1 if side == "L" else 1
    xp = s * (length / 2 + 1.0)
    lines.append(f'  (pad "1" thru_hole rect (at {xp:.3f} {-pitch / 2:.3f}) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))')
    lines.append(f'  (pad "2" thru_hole circle (at {xp:.3f} {pitch / 2:.3f}) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))')
    hw = (d + 0.5) / 2
    lines.append(_rect("F.Fab", -length / 2, -hw, length / 2, hw))
    lines.append(_rect("F.SilkS", -length / 2 - 0.1, -hw - 0.1, length / 2 + 0.1, hw + 0.1, 0.12))
    lines.append(_line("F.SilkS", xp - s * 1.3, -pitch / 2 - 1.2, xp - s * 1.3, -pitch / 2 - 0.4, 0.12))
    lines.append(_rect("F.CrtYd", min(-length / 2, xp - pad / 2) - 0.25, -hw - 0.25,
                       max(length / 2, xp + pad / 2) + 0.25, hw + 0.25, 0.05))
    return write(lib_dir, name, lines)


def tiny6(lib_dir, name, descr, pads, body):
    """Безвыводные корпуса 0,7×1,1 мм с площадками 0,25×0,25 мм (TSNP-6-2, TSLP-6-4).
    pads: [(номер, x, y)] в системе KiCad (вид сверху)."""
    lines = _hdr(name, descr)
    for num, x, y in pads:
        lines.append(f'  (pad "{num}" smd rect (at {x:.3f} {y:.3f}) (size 0.25 0.25) (layers "F.Cu" "F.Mask" "F.Paste"))')
    L, W = body
    lines.append(_rect("F.Fab", -L / 2, -W / 2, L / 2, W / 2, 0.05))
    lines.append(_rect("F.CrtYd", -L / 2 - 0.2, -W / 2 - 0.2, L / 2 + 0.2, W / 2 + 0.2, 0.05))
    return write(lib_dir, name, lines)


def bga524n6(lib_dir):
    """Infineon BGA524N6, PG-TSNP-6-2 (по brunoeagle/kicad-open-modules): 1(−0,4;0,2) … 6(−0,4;−0,2)."""
    pads = [(1, -0.4, 0.2), (2, 0.0, 0.2), (3, 0.4, 0.2), (4, 0.4, -0.2), (5, 0.0, -0.2), (6, -0.4, -0.2)]
    return tiny6(lib_dir, "Infineon_PG-TSNP-6-2_0.7x1.1mm", "Infineon PG-TSNP-6-2 (BGA524N6)", pads, (1.1, 0.7))


def bgs12p2l6(lib_dir):
    """Infineon BGS12P2L6, PG-TSLP-6-4 (по отчёту jazari-akuna/kicad-shared-libs, рис. 2 техописания, вид сверху)."""
    pads = [(1, 0.2, 0.4), (2, 0.2, 0.0), (3, 0.2, -0.4), (4, -0.2, -0.4), (5, -0.2, 0.0), (6, -0.2, 0.4)]
    return tiny6(lib_dir, "Infineon_PG-TSLP-6-4_0.7x1.1mm", "Infineon PG-TSLP-6-4 (BGS12P2L6)", pads, (0.7, 1.1))


def qfn10_2x2(lib_dir):
    """pSemi PE64906 QFN-10 2×2 мм (QFN50P200X200X60-11N): по 4 вывода на боковых сторонах (шаг 0,5),
    выводы 5 и 10 — на торцах, теплоотвод 0,95×0,95 (вывод 11)."""
    name = "pSemi_QFN-10-1EP_2x2mm_P0.5mm_EP0.95mm"
    lines = _hdr(name, "pSemi PE64906 DTC, 10-lead QFN 2x2 mm")
    for i, y in enumerate((-0.75, -0.25, 0.25, 0.75), 1):
        lines.append(smd_pad(str(i), -1.0, y, 0.6, 0.25, "rect"))
        lines.append(smd_pad(str(10 - i), 1.0, y, 0.6, 0.25, "rect"))
    lines.append(smd_pad("5", 0.0, 1.0, 0.25, 0.6, "rect"))
    lines.append(smd_pad("10", 0.0, -1.0, 0.25, 0.6, "rect"))
    lines.append(smd_pad("11", 0.0, 0.0, 0.95, 0.95, "rect"))
    lines.append(_rect("F.Fab", -1.0, -1.0, 1.0, 1.0, 0.05))
    lines.append(_rect("F.CrtYd", -1.55, -1.55, 1.55, 1.55, 0.05))
    return write(lib_dir, name, lines)
