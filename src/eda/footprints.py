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
