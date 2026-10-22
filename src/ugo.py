"""Условные графические обозначения для схем электрических принципиальных (Э3).

ГОСТ 2.721-74 (общие), 2.723-68 (катушки, дроссели), 2.728-74 (резисторы, конденсаторы),
2.730-73 (полупроводниковые приборы), 2.735-68 (антенны), 2.736-68 (пьезо- и ПАВ-элементы),
2.743-91 (элементы цифровой техники, микросхемы), 2.755-87 (соединения контактные), 2.751-73 (линии связи).
Размеры — в мм по рекомендациям стандартов: резистор 10×4, конденсатор — пластины 8 мм с зазором 1,5 мм,
шаг выводов микросхем 5 мм. Все функции возвращают координаты точек подключения выводов.
"""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

import gost
from gost import Pen

LW = 0.35        # линии УГО
LWC = 0.3        # линии связи
TH = 2.5         # шрифт выводов, позиционных обозначений — 3,5
PITCH = 5.0


def tw(s, h=TH):
    return stringWidth(s, "GOST", gost.fs(h)) / mm


def dot(p: Pen, x, y):
    p.circle(x, y, 0.6, 0.1, fill=colors.black)


def wire(p: Pen, pts):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        p.line(x1, y1, x2, y2, LWC)


def ground(p: Pen, x, y, down=True):
    """Корпус/общий провод (ГОСТ 2.721): отвод 3 мм и черта 6 мм."""
    s = -1 if down else 1
    p.line(x, y, x, y + s * 3, LWC)
    p.line(x - 3, y + s * 3, x + 3, y + s * 3, 0.5)


def net_label(p: Pen, x, y, name, side="r", h=TH):
    """Обрыв линии связи с наименованием цепи (ГОСТ 2.702, п. 5.3.10)."""
    if side == "r":
        p.text(x + 0.8, y + 0.6, name, h)
    elif side == "l":
        p.text(x - 0.8, y + 0.6, name, h, "r")
    elif side == "u":
        p.text(x - 0.6, y + 0.8, name, h, rot=90)
    else:
        p.text(x + 0.6 + h * 0.7, y - 0.8, name, h, "r", rot=90)


def ref_text(p: Pen, x, y, ref, value="", align="l"):
    p.text(x, y, ref, 3.5, align)
    if value:
        p.text(x, y - 3.6, value, TH, align)


# ------------------------------------------------------------------ двухвыводные
def resistor(p: Pen, x, y, vertical=False, ref="", value="", lead=2.5):
    """Резистор 10×4 мм с выводами по `lead` мм; (x, y) — центр. Возвращает (a, b) — концы выводов."""
    if vertical:
        p.rect(x - 2, y - 5, 4, 10, LW)
        p.line(x, y + 5, x, y + 5 + lead, LWC)
        p.line(x, y - 5, x, y - 5 - lead, LWC)
        if ref:
            ref_text(p, x + 3, y + 1, ref, value)
        return (x, y + 5 + lead), (x, y - 5 - lead)
    p.rect(x - 5, y - 2, 10, 4, LW)
    p.line(x - 5 - lead, y, x - 5, y, LWC)
    p.line(x + 5, y, x + 5 + lead, y, LWC)
    if ref:
        ref_text(p, x - 5, y + 3, ref, value) if not value else (p.text(x, y + 3, ref, 3.5, "c"),
                                                                   p.text(x, y - 5.6, value, TH, "c"))
    return (x - 5 - lead, y), (x + 5 + lead, y)


def capacitor(p: Pen, x, y, vertical=True, ref="", value="", polar=False, lead=3.0):
    """Конденсатор: пластины 8 мм, зазор 1,5 мм. Полярный — «+» у положительной обкладки (первой)."""
    g = 0.75
    if vertical:
        p.line(x - 4, y + g, x + 4, y + g, 0.5)
        if polar:
            p.rect(x - 4, y - g - 0.8, 8, 0.8, LW)
            p.text(x - 4.8, y + 1.2, "+", TH, "r")
        else:
            p.line(x - 4, y - g, x + 4, y - g, 0.5)
        p.line(x, y + g, x, y + g + lead, LWC)
        p.line(x, y - g - (0.8 if polar else 0), x, y - g - lead, LWC)
        if ref:
            ref_text(p, x + 5, y + 0.8, ref, value)
        return (x, y + g + lead), (x, y - g - lead)
    p.line(x - g, y - 4, x - g, y + 4, 0.5)
    p.line(x + g, y - 4, x + g, y + 4, 0.5)
    p.line(x - g - lead, y, x - g, y, LWC)
    p.line(x + g, y, x + g + lead, y, LWC)
    if ref:
        p.text(x, y + 5, ref, 3.5, "c")
        if value:
            p.text(x, y - 7.5, value, TH, "c")
    return (x - g - lead, y), (x + g + lead, y)


def inductor(p: Pen, x, y, vertical=False, ref="", value="", lead=2.5, core=False):
    """Катушка/дроссель (ГОСТ 2.723): 4 полуокружности диаметром 2,5 мм."""
    c = p.c
    c.setLineWidth(LW * mm)
    n, d = 4, 2.5
    L = n * d
    if vertical:
        for i in range(n):
            cy = y + L / 2 - d / 2 - i * d
            c.arc((x - d / 2) * mm, (cy - d / 2) * mm, (x + d / 2) * mm, (cy + d / 2) * mm, 270, 180)
        p.line(x, y + L / 2, x, y + L / 2 + lead, LWC)
        p.line(x, y - L / 2, x, y - L / 2 - lead, LWC)
        if core:
            p.line(x - 2.2, y - L / 2, x - 2.2, y + L / 2, LW)
        if ref:
            ref_text(p, x + 2.5, y + 1, ref, value)
        return (x, y + L / 2 + lead), (x, y - L / 2 - lead)
    for i in range(n):
        cx = x - L / 2 + d / 2 + i * d
        c.arc((cx - d / 2) * mm, (y - d / 2) * mm, (cx + d / 2) * mm, (y + d / 2) * mm, 0, 180)
    p.line(x - L / 2 - lead, y, x - L / 2, y, LWC)
    p.line(x + L / 2, y, x + L / 2 + lead, y, LWC)
    if core:
        p.line(x - L / 2, y + 2.2, x + L / 2, y + 2.2, LW)
    if ref:
        p.text(x, y + 3.2, ref, 3.5, "c")
        if value:
            p.text(x, y - 4.8, value, TH, "c")
    return (x - L / 2 - lead, y), (x + L / 2 + lead, y)


def ferrite(p: Pen, x, y, vertical=False, ref="", value="", lead=2.5):
    """Ферритовая бусина: прямоугольник 8×3 с косой чертой (ГОСТ 2.723, ферромагнитный элемент)."""
    if vertical:
        p.rect(x - 1.5, y - 4, 3, 8, LW, fill=colors.Color(0.25, 0.25, 0.25))
        p.line(x, y + 4, x, y + 4 + lead, LWC)
        p.line(x, y - 4, x, y - 4 - lead, LWC)
        if ref:
            ref_text(p, x + 3, y + 1, ref, value)
        return (x, y + 4 + lead), (x, y - 4 - lead)
    p.rect(x - 4, y - 1.5, 8, 3, LW, fill=colors.Color(0.25, 0.25, 0.25))
    p.line(x - 4 - lead, y, x - 4, y, LWC)
    p.line(x + 4, y, x + 4 + lead, y, LWC)
    if ref:
        p.text(x, y + 2.5, ref, 3.5, "c")
        if value:
            p.text(x, y - 5.5, value, TH, "c")
    return (x - 4 - lead, y), (x + 4 + lead, y)


def tvs(p: Pen, x, y, ref="", value=""):
    """Двунаправленный ограничитель напряжения (ГОСТ 2.730), вертикально; возвращает (верх, низ)."""
    c = p.c
    c.setLineWidth(LW * mm)
    for s in (1, -1):
        path = c.beginPath()
        path.moveTo((x - 2) * mm, (y + s * 3) * mm)
        path.lineTo((x + 2) * mm, (y + s * 3) * mm)
        path.lineTo(x * mm, y * mm)
        path.close()
        c.drawPath(path, stroke=1, fill=0)
    p.line(x - 2, y, x + 2, y, LW)
    p.line(x - 2, y, x - 2.8, y - 0.8, LW)
    p.line(x + 2, y, x + 2.8, y + 0.8, LW)
    p.line(x, y + 3, x, y + 5.5, LWC)
    p.line(x, y - 3, x, y - 5.5, LWC)
    if ref:
        ref_text(p, x + 3.5, y + 1, ref, value)
    return (x, y + 5.5), (x, y - 5.5)


# ------------------------------------------------------------------ многовыводные
class Box:
    """Микросхема/модуль (ГОСТ 2.743): основное поле с функциональным обозначением и дополнительные поля
    с метками выводов слева и справа. pins_l/pins_r: [(номер, метка) | None (пропуск)]."""

    def __init__(self, p: Pen, x, y, pins_l, pins_r, func="", ref="", value="", w_main=12.0,
                 w_lab=None, lead=5.0, pitch=PITCH, top_pad=5.0):
        self.p = p
        lab_l = max([tw(n) for x_ in pins_l if x_ for n in [x_[1]]] + [0])
        lab_r = max([tw(n) for x_ in pins_r if x_ for n in [x_[1]]] + [0])
        self.wl = w_lab if w_lab is not None else (max(lab_l + 2.5, 6.0) if pins_l else 0)
        self.wr = w_lab if w_lab is not None else (max(lab_r + 2.5, 6.0) if pins_r else 0)
        self.w = self.wl + w_main + self.wr
        n = max(len(pins_l), len(pins_r), 1)
        self.h = (n - 1) * pitch + 2 * top_pad
        self.x, self.ytop = x, y                    # левый верхний угол
        self.pins = {}
        lw = 0.5
        p.rect(x, y - self.h, self.w, self.h, lw)
        if self.wl:
            p.line(x + self.wl, y - self.h, x + self.wl, y, lw)
        if self.wr:
            p.line(x + self.w - self.wr, y - self.h, x + self.w - self.wr, y, lw)
        if func:
            cx = x + self.wl + w_main / 2
            for i, s in enumerate(func.split("\n")):
                p.text(cx, y - 4.5 - i * 4.2, s, 3.5, "c")
        for i, pin in enumerate(pins_l):
            if not pin:
                continue
            num, lab = pin
            py = y - top_pad - i * pitch
            p.line(x - lead, py, x, py, LWC)
            p.text(x - lead + 0.6, py + 0.6, num, TH)
            p.text(x + 1.0, py - TH * 0.36, lab, TH)
            self.pins[num] = (x - lead, py)
        for i, pin in enumerate(pins_r):
            if not pin:
                continue
            num, lab = pin
            py = y - top_pad - i * pitch
            p.line(x + self.w, py, x + self.w + lead, py, LWC)
            p.text(x + self.w + lead - 0.6, py + 0.6, num, TH, "r")
            p.text(x + self.w - 1.0, py - TH * 0.36, lab, TH, "r")
            self.pins[num] = (x + self.w + lead, py)
        if ref:
            p.text(x + self.w / 2, y + 1.5 + (4.0 if value else 0), ref, 3.5, "c")
            if value:
                p.text(x + self.w / 2, y + 1.5, value, TH, "c")

    def pt(self, num):
        return self.pins[str(num)]


def coax_socket(p: Pen, x, y, ref=""):
    """Розетка коаксиальная (ГОСТ 2.755): окружность Ø4 с центральным контактом; вывод — вправо."""
    p.circle(x, y, 2.0, LW)
    dot(p, x, y)
    p.line(x, y, x + 6, y, LWC)
    p.line(x, y - 2, x, y - 5, LWC)
    if ref:
        p.text(x - 3, y + 3, ref, 3.5, "c")
    return (x + 6, y), (x, y - 5)


def antenna(p: Pen, x, y, ref=""):
    """Антенна (ГОСТ 2.735): вертикальный отвод и треугольник."""
    p.line(x, y, x, y + 6, LWC)
    p.line(x, y + 6, x - 3, y + 11, LW)
    p.line(x, y + 6, x + 3, y + 11, LW)
    p.line(x - 3, y + 11, x + 3, y + 11, LW)
    if ref:
        p.text(x + 4, y + 8, ref, 3.5)
    return (x, y)
