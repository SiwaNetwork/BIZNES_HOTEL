"""Схема электрическая принципиальная (Э3) по ГОСТ 2.701-2008, 2.702-2011 из модели Design.

Линии связи между элементами показаны обрывами с наименованиями цепей (ГОСТ 2.702, п. 5.3.10:
«линии связи … допускается обрывать … обрывы помечают наименованием цепи»). Общий провод — знаком «корпус».
Элементы сгруппированы по функциональным узлам: микросхема и её обвязка образуют «ячейку».
Лист 1 — основная надпись по форме 1, последующие — по форме 2а (ГОСТ 2.104).
"""
import re

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import gost
import ugo
from gost import Pen

W, H = gost.A3L
X_MIN, X_MAX, Y_TOP = 26.0, 413.0, 288.0
STAMP_X, STAMP_Y = W - 5 - 185, 62.0       # верх основной надписи формы 1 (+ поле примечаний)
GND_NETS = ("GND",)
PASSIVE_KINDS = ("R", "C", "L", "FB", "D")


def _label_w(s):
    return ugo.tw(s) + 2.0


class Cell:
    """Ячейка: основной элемент (микросхема, соединитель) + двухвыводные элементы обвязки."""

    def __init__(self, design, main, passives, title=""):
        self.d, self.main, self.passives, self.title = design, main, passives, title
        part = design.parts[main]
        conn = design.pins_of(main)
        pl = [p for p in part.pins if p.side in ("L", "T")]
        pr = [p for p in part.pins if p.side in ("R", "B")]
        self.pins_l = [(p.num, p.name) for p in pl]
        self.pins_r = [(p.num, p.name) for p in pr]
        self.lab_l = max([_label_w(conn.get(p.num, "")) for p in pl] + [0])
        self.lab_r = max([_label_w(conn.get(p.num, "")) for p in pr] + [0])
        name_w = lambda lst: max([ugo.tw(n) for _, n in lst] + [0])
        self.box_w = (max(name_w(self.pins_l) + 2.5, 6) if pl else 0) + 14 + (max(name_w(self.pins_r) + 2.5, 6) if pr else 0)
        n = max(len(pl), len(pr), 1)
        self.box_h = (n - 1) * ugo.PITCH + 10
        self.ic_w = self.lab_l + 5 + self.box_w + 5 + self.lab_r
        # обвязка: по 4 элемента в ряд, шаг 22 мм, высота ряда 34 мм
        self.cols = max(1, min(len(passives), int(max(self.ic_w, 88) // 22)))
        rows = (len(passives) + self.cols - 1) // self.cols
        self.w = max(self.ic_w, self.cols * 22) + 6
        self.h = 12 + self.box_h + (rows * 34 + 4 if passives else 0) + 4

    def draw(self, p: Pen, x, y_top):
        d = self.d
        part = d.parts[self.main]
        conn = d.pins_of(self.main)
        bx = x + self.lab_l + 5
        by = y_top - 10
        func = {"IC": "", "CONN": "", "COAX": ""}.get(part.kind, "")
        box = ugo.Box(p, bx, by, self.pins_l, self.pins_r, func=func, ref=self.main, value=part.value,
                      w_main=14)
        for num, (px, py) in box.pins.items():
            net = conn.get(num)
            left = px < bx
            if net is None:
                p.line(px - 1 if left else px + 1, py - 1, px + 1 if left else px - 1, py + 1, ugo.LWC)   # «не подключён»
                p.line(px - 1, py + 1, px + 1, py - 1, ugo.LWC)
            elif net in GND_NETS:
                ugo.ground(p, px, py)
            else:
                ugo.net_label(p, px, py, net, "l" if left else "r")
        # обвязка
        y0 = by - self.box_h - 8
        for i, ref in enumerate(self.passives):
            r, c = divmod(i, self.cols)
            cx = x + 11 + c * 22
            cy = y0 - r * 34 - 13
            self._passive(p, ref, cx, cy)

    def _passive(self, p: Pen, ref, cx, cy):
        d = self.d
        part = d.parts[ref]
        conn = d.pins_of(ref)
        n1, n2 = conn.get(part.pins[0].num), conn.get(part.pins[1].num)
        # общий провод — вниз
        if n1 in GND_NETS and n2 not in GND_NETS:
            n1, n2 = n2, n1
        k = part.kind
        val = part.value
        if k == "C":
            a, b = ugo.capacitor(p, cx, cy, True, ref, val, polar=part.mpn.startswith(("T52", "TPS", "T55")) if part.mpn else False, lead=4)
        elif k == "R":
            a, b = ugo.resistor(p, cx, cy, True, ref, val)
        elif k == "L":
            a, b = ugo.inductor(p, cx, cy, True, ref, val)
        elif k == "FB":
            a, b = ugo.ferrite(p, cx, cy, True, ref, val)
        elif k == "D":
            a, b = ugo.tvs(p, cx, cy, ref, val)
        else:
            a, b = ugo.resistor(p, cx, cy, True, ref, val)
        for (px, py), net, up in ((a, n1, True), (b, n2, False)):
            if net in GND_NETS:
                ugo.ground(p, px, py, down=not up)
            elif net:
                ugo.net_label(p, px, py, net, "u" if up else "d")


def auto_cells(design, order):
    """order: [(главный элемент, заголовок)] — обвязка распределяется автоматически по общим цепям."""
    mains = [m for m, _ in order]
    owner = {}
    for ref, part in design.parts.items():
        if ref in mains or part.kind not in PASSIVE_KINDS:
            continue
        conn = design.pins_of(ref)
        nets = [n for n in conn.values() if n not in GND_NETS]
        best = None
        for m in mains:
            mnets = set(design.pins_of(m).values())
            if any(n in mnets for n in nets):
                best = m
                break
        owner.setdefault(best or mains[-1], []).append(ref)
    key = lambda r: (re.match(r"[A-Z]+", r).group(0), int(re.search(r"\d+", r).group(0)))
    return [Cell(design, m, sorted(owner.get(m, []), key=key), t) for m, t in order]


def build(path, design, sheets, product, code, notes=(), lit="Т"):
    """sheets: [[Cell, ...], ...] — по листам; ячейки раскладываются построчно."""
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{code} Э3 — Схема электрическая принципиальная")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    total = len(sheets)
    for n, cells in enumerate(sheets, 1):
        x, y, row_h = X_MIN, Y_TOP, 0
        bottom_lim = STAMP_Y + (6 + 4.2 * len(notes) if n == 1 and notes else 0) if n == 1 else 22.0
        for cell in cells:
            if x + cell.w > X_MAX:
                x, y, row_h = X_MIN, y - row_h, 0
            if y - cell.h < bottom_lim and x + cell.w > STAMP_X:
                x, y, row_h = X_MIN, y - row_h, 0
            if y - cell.h < (bottom_lim if x + cell.w > STAMP_X else 10):
                print(f"[Э3] лист {n}: ячейка {cell.main} не помещается (y={y - cell.h:.0f})")
            if cell.title:
                p.text(x + 2, y - 3.5, cell.title, 3.5)
            cell.draw(p, x, y - 6)
            x += cell.w
            row_h = max(row_h, cell.h + 6)
        gost.frame(p, W, H, drawing=True, first=n == 1, code=code + " Э3")
        if n == 1:
            if notes:
                yy = STAMP_Y + 4.2 * len(notes) + 2
                p.text(STAMP_X + 92, yy + 2, "Примечания", 3.5, "c")
                for i, s in enumerate(notes, 1):
                    yy -= 4.2
                    p.text(STAMP_X + 2, yy, f"{i} {s}", 2.5)
            gost.stamp_form1(p, W, product, "Схема электрическая\nпринципиальная", code=code + " Э3", lit=lit,
                             sheet="" if total == 1 else 1, sheets=total)
        else:
            gost.stamp_form2a(p, W, n, code=code + " Э3")
        c.showPage()
    c.save()
