"""Схема KiCad 7 (.kicad_sch) из модели Design: собственные символы, соединения метками цепей."""
import hashlib
import re
import uuid

from .netlist import Design

GRID = 1.27
PIN_LEN = 2.54
PITCH = 2.54
STUB = 2.54
FONT = 1.27


def uid(*names):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "/".join(map(str, names))))


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def snap(v):
    return round(round(v / GRID) * GRID, 2)


def sym_key(part):
    """Одинаковые по выводам элементы используют один символ."""
    sig = "|".join(f"{p.num}:{p.name}:{p.side}" for p in part.pins)
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", part.mpn or part.value or part.kind)
    return f"{part.kind}_{base}_{hashlib.md5(sig.encode()).hexdigest()[:6]}"


def sym_geometry(part):
    """Размеры прямоугольника и координаты концов выводов в системе символа (Y вверх)."""
    sides = {s: [p for p in part.pins if p.side == s] for s in "LRTB"}
    if part.kind in ("R", "C", "L", "FB") and len(part.pins) == 2:
        w, h = 5.08, 2.54
        pts = {part.pins[0].num: (-w / 2 - PIN_LEN, 0, 0), part.pins[1].num: (w / 2 + PIN_LEN, 0, 180)}
        return w, h, pts
    n_lr = max(len(sides["L"]), len(sides["R"]), 1)
    n_tb = max(len(sides["T"]), len(sides["B"]), 0)
    name_len = max([len(p.name) for p in sides["L"] + sides["R"]] + [4])
    w = max(snap(2 * name_len * FONT * 0.65 + 5.08), snap((n_tb + 1) * PITCH), 10.16)
    h = snap((n_lr + 1) * PITCH)
    w = snap(round(w / (2 * PITCH)) * 2 * PITCH)
    pts = {}
    top = h / 2 - PITCH
    for i, p in enumerate(sides["L"]):
        pts[p.num] = (-w / 2 - PIN_LEN, snap(top - i * PITCH), 0)
    for i, p in enumerate(sides["R"]):
        pts[p.num] = (w / 2 + PIN_LEN, snap(top - i * PITCH), 180)
    for s, y, ang in (("T", h / 2 + PIN_LEN, 270), ("B", -h / 2 - PIN_LEN, 90)):
        lst = sides[s]
        x0 = -(len(lst) - 1) * PITCH / 2
        for i, p in enumerate(lst):
            pts[p.num] = (snap(x0 + i * PITCH), y, ang)
    return w, h, pts


def lib_symbol(name, part):
    w, h, pts = sym_geometry(part)
    out = [f'(symbol {q("TENSH:" + name)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes)',
           f'(property "Reference" {q(re.match(r"[A-Z]+", part.ref).group(0))} (at 0 {h / 2 + 3.81:.2f} 0) (effects (font (size {FONT} {FONT}))))',
           f'(property "Value" {q(part.value)} (at 0 {-h / 2 - 3.81:.2f} 0) (effects (font (size {FONT} {FONT}))))',
           f'(property "Footprint" "" (at 0 0 0) (effects (font (size {FONT} {FONT})) hide))',
           f'(property "Datasheet" "" (at 0 0 0) (effects (font (size {FONT} {FONT})) hide))',
           f'(symbol {q(name + "_0_1")}']
    if part.kind == "C" and len(part.pins) == 2:
        out.append("(polyline (pts (xy -0.508 1.27) (xy -0.508 -1.27)) (stroke (width 0.3) (type default)) (fill (type none)))")
        out.append("(polyline (pts (xy 0.508 1.27) (xy 0.508 -1.27)) (stroke (width 0.3) (type default)) (fill (type none)))")
        out.append(f"(polyline (pts (xy {-w / 2:.3f} 0) (xy -0.508 0)) (stroke (width 0) (type default)) (fill (type none)))")
        out.append(f"(polyline (pts (xy 0.508 0) (xy {w / 2:.3f} 0)) (stroke (width 0) (type default)) (fill (type none)))")
    else:
        hh = 1.016 if part.kind in ("R", "L", "FB") and len(part.pins) == 2 else h / 2
        fill = "outline" if part.kind == "L" and len(part.pins) == 2 else "background"
        out.append(f"(rectangle (start {-w / 2:.3f} {hh:.3f}) (end {w / 2:.3f} {-hh:.3f}) "
                   f"(stroke (width 0.254) (type default)) (fill (type {fill})))")
    out.append(")")
    out.append(f'(symbol {q(name + "_1_1")}')
    for p in part.pins:
        x, y, ang = pts[p.num]
        hide_name = part.kind in ("R", "C", "L", "FB") and len(part.pins) == 2
        nm = "~" if hide_name else p.name
        out.append(f"(pin {p.etype if p.etype != 'no_connect' else 'no_connect'} line (at {x:.3f} {y:.3f} {ang}) "
                   f"(length {PIN_LEN}) (name {q(nm)} (effects (font (size {FONT} {FONT})))) "
                   f"(number {q(p.num)} (effects (font (size {FONT} {FONT})))))")
    out.append(")")
    out.append(")")
    return "\n".join(out), (w, h, pts)


def layout(design: Design, sheet_w):
    """Автоматическая раскладка элементов по строкам (если координаты не заданы)."""
    placed = {}
    x, y, row_h = 25.4, 30.48, 0
    for ref, part in design.parts.items():
        w, h, pts = sym_geometry(part)
        names = [n for n in design.pins_of(ref).values()]
        lab = max([len(n) for n in names] + [3]) * FONT * 0.75 + STUB + PIN_LEN
        bw = w + 2 * lab + 5.08
        bh = h + (2 * lab if any(p.side in "TB" for p in part.pins) else 0) + 10.16
        if part.sch:
            placed[ref] = part.sch
            continue
        if x + bw > sheet_w - 25.4:
            x, y, row_h = 25.4, y + row_h, 0
        placed[ref] = (snap(x + bw / 2), snap(y + bh / 2))
        x += bw
        row_h = max(row_h, bh)
    return placed


def write(design: Design, path, project, paper="A1", sheet_w=841):
    root = uid(project, "root")
    syms, geo, defs = {}, {}, []
    for ref, part in design.parts.items():
        k = sym_key(part)
        if k not in syms:
            text, g = lib_symbol(k, part)
            syms[k] = text
        geo[ref] = (k, sym_geometry(part))
    pos = layout(design, sheet_w)
    body = []
    for ref, part in design.parts.items():
        k, (w, h, pts) = geo[ref]
        X, Y = pos[ref]
        props = [("Reference", ref, (X, Y - h / 2 - 2.54)), ("Value", part.value, (X, Y + h / 2 + 2.54)),
                 ("Footprint", part.footprint, (X, Y)), ("Datasheet", "", (X, Y)),
                 ("MPN", part.mpn, (X, Y)), ("Manufacturer", part.mfr, (X, Y))]
        pr = []
        for i, (n, v, (px, py)) in enumerate(props):
            hide = " hide" if i >= 2 else ""
            pr.append(f'(property {q(n)} {q(v)} (at {px:.2f} {py:.2f} 0) (effects (font (size {FONT} {FONT})){hide}))')
        pins = " ".join(f'(pin {q(p.num)} (uuid {uid(project, ref, "pin", p.num)}))' for p in part.pins)
        body.append(f'(symbol (lib_id {q("TENSH:" + k)}) (at {X:.2f} {Y:.2f} 0) (unit 1) (in_bom {"no" if part.kind in ("MH", "TP") else "yes"}) '
                    f'(on_board yes) (dnp {"yes" if part.dnp else "no"}) (uuid {uid(project, ref)}) ' + " ".join(pr) +
                    f' {pins} (instances (project {q(project)} (path "/{root}" (reference {q(ref)}) (unit 1)))))')
        conn = design.pins_of(ref)
        for p in part.pins:
            px, py, ang = pts[p.num]
            sx, sy = X + px, Y - py                       # Y схемы направлен вниз
            net = conn.get(p.num)
            if net is None:
                body.append(f'(no_connect (at {sx:.2f} {sy:.2f}) (uuid {uid(project, ref, p.num, "nc")}))')
                continue
            dx, dy = {0: (-STUB, 0), 180: (STUB, 0), 270: (0, -STUB), 90: (0, STUB)}[ang]
            ex, ey = sx + dx, sy + dy
            body.append(f'(wire (pts (xy {sx:.2f} {sy:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) '
                        f'(uuid {uid(project, ref, p.num, "w")}))')
            la = {0: 180, 180: 0, 270: 90, 90: 270}[ang]
            just = "right" if la in (180, 270) else "left"
            body.append(f'(label {q(net)} (at {ex:.2f} {ey:.2f} {la}) (fields_autoplaced) '
                        f'(effects (font (size {FONT} {FONT})) (justify {just} bottom)) (uuid {uid(project, ref, p.num, "l")}))')
    txt = [f"(kicad_sch (version 20230121) (generator eeschema)", f"(uuid {root})", f'(paper {q(paper)})',
           f'(title_block (title {q(design.title)}) (date "2026-10") (rev "") (company "ТЕНШ") (comment 1 {q(design.code + " Э3")}))',
           "(lib_symbols", *syms.values(), ")", *body,
           '(sheet_instances (path "/" (page "1")))', ")"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")
    return path


def write_sym_lib(design: Design, path):
    """Библиотека символов проекта (для редактирования схемы в KiCad)."""
    syms = {}
    for part in design.parts.values():
        k = sym_key(part)
        if k not in syms:
            syms[k] = lib_symbol(k, part)[0].replace('"TENSH:' + k + '"', q(k), 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write("(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n" + "\n".join(syms.values()) + "\n)\n")
