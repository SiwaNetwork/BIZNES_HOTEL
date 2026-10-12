"""Оформление листов по ЕСКД средствами reportlab.

ГОСТ 2.301-68  — форматы (A4 210×297, A3 420×297);
ГОСТ 2.104-2006 — основные надписи: форма 1 (чертежи и схемы),
                  форма 2 (первый лист текстовых документов),
                  форма 2а (последующие листы), дополнительные графы 19–26;
ГОСТ 2.303-68  — линии (сплошная основная S = 0,7 мм, тонкая S/3);
ГОСТ 2.304-81  — шрифты чертёжные (используется osifont, тип Б, наклонный).
Все координаты — в миллиметрах от левого нижнего угла листа.
"""
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

S = 0.7       # толщина сплошной основной линии, мм
S3 = 0.25     # тонкая линия, мм

A4 = (210.0, 297.0)
A3L = (420.0, 297.0)

# Общие данные комплекта документов
ORG = ""                       # графа 9 — заполняется организацией-разработчиком
PRODUCT = "Модуль спутниковой связи\nсверхкомпактный"
CODE = "ТЕНШ.464512.001"       # обозначение по ГОСТ 2.201: код организации ТЕНШ
YEAR = "2026"
DATE = "10.26"
PEOPLE = [("Разраб.", ""), ("Пров.", ""), ("Т.контр.", ""), ("", ""), ("Н.контр.", ""), ("Утв.", "")]


def register_fonts():
    pdfmetrics.registerFont(TTFont("GOST", str(FONTS / "osifont-ru.ttf")))
    pdfmetrics.registerFont(TTFont("Serif", str(FONTS / "LiberationSerif-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Serif-Bold", str(FONTS / "LiberationSerif-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Serif-Italic", str(FONTS / "LiberationSerif-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Serif-BoldItalic", str(FONTS / "LiberationSerif-BoldItalic.ttf")))
    from reportlab.lib.fonts import addMapping
    addMapping("Serif", 0, 0, "Serif")
    addMapping("Serif", 1, 0, "Serif-Bold")
    addMapping("Serif", 0, 1, "Serif-Italic")
    addMapping("Serif", 1, 1, "Serif-BoldItalic")


def fs(h_mm: float) -> float:
    """Кегль (pt) для высоты прописной буквы h, мм (ГОСТ 2.304: 2,5; 3,5; 5; 7…)."""
    return h_mm * mm / 0.72


class Pen:
    """Тонкая обёртка над canvas с координатами в мм."""

    def __init__(self, c):
        self.c = c

    def line(self, x1, y1, x2, y2, w=S3, dash=None):
        c = self.c
        c.setLineWidth(w * mm)
        c.setDash([d * mm for d in dash] if dash else [])
        c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
        c.setDash([])

    def rect(self, x, y, w, h, lw=S3, fill=None, stroke=True, dash=None):
        c = self.c
        c.setLineWidth(lw * mm)
        c.setDash([d * mm for d in dash] if dash else [])
        if fill:
            c.setFillColor(fill)
        c.rect(x * mm, y * mm, w * mm, h * mm, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])
        c.setFillColorRGB(0, 0, 0)

    def circle(self, x, y, r, lw=S3, fill=None, dash=None):
        c = self.c
        c.setLineWidth(lw * mm)
        c.setDash([d * mm for d in dash] if dash else [])
        if fill:
            c.setFillColor(fill)
        c.circle(x * mm, y * mm, r * mm, stroke=1, fill=1 if fill else 0)
        c.setDash([])
        c.setFillColorRGB(0, 0, 0)

    def text(self, x, y, s, h=2.5, align="l", font="GOST", rot=0, color=None):
        c = self.c
        c.saveState()
        if color is not None:
            c.setFillColor(color)
        c.setFont(font, fs(h))
        c.translate(x * mm, y * mm)
        c.rotate(rot)
        if align == "c":
            c.drawCentredString(0, 0, s)
        elif align == "r":
            c.drawRightString(0, 0, s)
        else:
            c.drawString(0, 0, s)
        c.restoreState()

    def ctext(self, x, y, w, h, s, th=2.5, font="GOST", rot=0):
        """Текст по центру ячейки (x, y, w, h)."""
        if rot == 90:
            self.text(x + w / 2 + th * 0.35, y + h / 2, s, th, "c", font, 90)
        else:
            self.text(x + w / 2, y + h / 2 - th * 0.36, s, th, "c", font)

    STD_H = (10.0, 7.0, 5.0, 3.5, 2.5)

    def fit(self, s, max_w, h, font="GOST"):
        """Подбирает высоту шрифта из ряда ГОСТ 2.304 (не более h), при которой строка умещается в max_w."""
        for hh in [x for x in self.STD_H if x <= h + 1e-6]:
            if pdfmetrics.stringWidth(s, font, fs(hh)) / mm <= max_w:
                return hh
        print(f"[gost.fit] строка не умещается в {max_w:.1f} мм при 2,5 мм: {s!r}")
        return 2.5

    def arrow(self, x1, y1, x2, y2, w=S3, size=2.5, both=False, filled=True):
        import math
        self.line(x1, y1, x2, y2, w)
        pts = [(x2, y2, x1, y1)] + ([(x1, y1, x2, y2)] if both else [])
        for tx, ty, fx, fy in pts:
            a = math.atan2(ty - fy, tx - fx)
            p = self.c.beginPath()
            p.moveTo(tx * mm, ty * mm)
            for da in (0.28, -0.28):
                p.lineTo((tx - size * math.cos(a + da)) * mm, (ty - size * math.sin(a + da)) * mm)
            p.close()
            self.c.setLineWidth(w * mm)
            self.c.drawPath(p, fill=1 if filled else 0, stroke=1)


# ------------------------------------------------------------------ рамка
def margin_graphs(pen: Pen):
    """Дополнительные графы 19–23 на поле подшивки (снизу вверх)."""
    y = 5
    for label, h in (("Инв. № подл.", 25), ("Подп. и дата", 35), ("Взам. инв. №", 25),
                     ("Инв. № дубл.", 25), ("Подп. и дата", 35)):
        pen.rect(8, y, 12, h, S)
        pen.line(13, y, 13, y + h, S)
        pen.ctext(8, y, 5, h, label, 2.5, rot=90)
        y += h


def frame(pen: Pen, W, H, drawing=True, first=True, code=CODE, first_use="", fmt=None):
    """Рамка листа (поле подшивки 20 мм), графы 19–26, графы 31–32 под рамкой.

    first_use — обозначение изделия, в котором документ (деталь) применён впервые (графа 25),
    пусто — графа не заполняется; fmt — обозначение формата для графы 32.
    """
    pen.rect(20, 5, W - 25, H - 10, S)
    margin_graphs(pen)
    if drawing and first:
        # графы 24, 25 — «Перв. примен.», «Справ. №»
        y = H - 5
        for label in ("Перв. примен.", "Справ. №"):
            pen.rect(8, y - 60, 12, 60, S)
            pen.line(13, y - 60, 13, y, S)
            pen.ctext(8, y - 60, 5, 60, label, 2.5, rot=90)
            y -= 60
        if first_use:
            pen.text(13 + 4.6, H - 5 - 30, first_use, 2.5, "c", rot=90)
    if first:
        # графа 26 — обозначение, повёрнутое на 180°
        pen.rect(20, H - 19, 70, 14, S)
        pen.text(55, H - 12 + 1.3, code, 3.5, "c", rot=180)
    # графы 31 («Копировал») и 32 («Формат») под рамкой
    fmt = fmt or ("А4" if W < 300 else "А3")
    pen.text(W - 5 - 120, 1.3, "Копировал", 2.5)
    pen.text(W - 5 - 45, 1.3, f"Формат {fmt}", 2.5)


def _left_block(pen: Pen, x0, y0, n_change_rows, people, form1=True):
    """Левая часть основной надписи: изменения + подписи (ширины 7/10/23/15/10)."""
    xs = [x0, x0 + 7, x0 + 17, x0 + 40, x0 + 55, x0 + 65]
    n_people = len(people)
    total = n_change_rows + 1 + n_people
    top = y0 + total * 5
    for i in range(total + 1):
        yy = y0 + i * 5
        thick = i in (n_people, n_people + 1) or i == total
        pen.line(x0, yy, x0 + 65, yy, S if thick else S3)
    # вертикали
    for i, x in enumerate(xs):
        if i in (0, 5):
            pen.line(x, y0, x, top, S)
        elif i in (1,):  # граница «Изм.»/«Лист» только в зоне изменений
            pen.line(x, y0 + n_people * 5, x, top, S)
        else:
            pen.line(x, y0, x, top, S)
    hdr_y = y0 + n_people * 5
    for (a, b), s in zip(zip(xs, xs[1:]), ("Изм.", "Лист", "№ докум.", "Подп.", "Дата")):
        pen.ctext(a, hdr_y, b - a, 5, s, 2.5)
    for i, (role, name) in enumerate(people):
        yy = y0 + (n_people - 1 - i) * 5
        if role:
            pen.text(x0 + 0.8, yy + 1.4, role, 2.5)
        if name:
            pen.text(x0 + 17.8, yy + 1.4, name, 2.5)
        if role and role != "Т.контр.":
            pass
    return top


def stamp_form1(pen: Pen, W, name, doc_title="", code=CODE, lit="Т", mass="",
                scale="", sheet="", sheets="1", material="", org=ORG):
    """Основная надпись по форме 1 (185×55)."""
    x0, y0 = W - 5 - 185, 5
    _left_block(pen, x0, y0, 4, PEOPLE)
    xr = x0 + 65
    pen.rect(x0, y0, 185, 55, S)
    pen.line(xr, y0, xr, y0 + 55, S)
    pen.line(xr, y0 + 40, xr + 120, y0 + 40, S)    # под графой 2
    pen.line(xr, y0 + 15, xr + 120, y0 + 15, S)    # над графой 3
    pen.line(xr + 70, y0, xr + 70, y0 + 40, S)
    # графа 2 — обозначение
    pen.text(xr + 60, y0 + 45.5, code, pen.fit(code, 115, 5), "c")
    # графа 1 — наименование
    lines = name.split("\n") + ([doc_title] if doc_title else [])
    n = len(lines)
    h0 = 5.0 if n == 1 else 3.5
    for i, s in enumerate(lines):
        h = pen.fit(s, 66, h0)
        pen.text(xr + 35, y0 + 15 + 12.5 + (n - 1) * 3.0 - i * 6.0 - h * 0.36, s, h, "c")
    # графа 3 — материал
    if material:
        for i, s in enumerate(material.split("\n")):
            pen.text(xr + 35, y0 + 9 - i * 5, s, pen.fit(s, 66, 3.5), "c")
    xb = xr + 70
    # Лит. / Масса / Масштаб
    pen.line(xb, y0 + 35, xb + 50, y0 + 35, S)
    pen.line(xb, y0 + 20, xb + 50, y0 + 20, S)
    pen.line(xb + 15, y0 + 20, xb + 15, y0 + 40, S)
    pen.line(xb + 32, y0 + 20, xb + 32, y0 + 40, S)
    pen.line(xb + 5, y0 + 20, xb + 5, y0 + 35, S3)
    pen.line(xb + 10, y0 + 20, xb + 10, y0 + 35, S3)
    pen.ctext(xb, y0 + 35, 15, 5, "Лит.")
    pen.ctext(xb + 15, y0 + 35, 17, 5, "Масса")
    pen.ctext(xb + 32, y0 + 35, 18, 5, "Масштаб")
    pen.ctext(xb, y0 + 20, 5, 15, lit, 3.5)
    pen.ctext(xb + 15, y0 + 20, 17, 15, mass, 3.5)
    pen.ctext(xb + 32, y0 + 20, 18, 15, scale, 3.5)
    # Лист / Листов
    pen.line(xb, y0 + 15, xb + 50, y0 + 15, S)
    pen.line(xb + 20, y0 + 15, xb + 20, y0 + 20, S)
    pen.text(xb + 1, y0 + 16.4, f"Лист {sheet}", 2.5)
    pen.text(xb + 21, y0 + 16.4, f"Листов {sheets}", 2.5)
    if org:
        pen.ctext(xb, y0, 50, 15, org, 3.5)


def stamp_form2(pen: Pen, W, name, doc_title, code=CODE, lit="Т", sheet="", sheets="", org=ORG):
    """Основная надпись по форме 2 (185×40) — первый лист текстового документа."""
    x0, y0 = W - 5 - 185, 5
    _left_block(pen, x0, y0, 2, [p for p in PEOPLE if p[0] != "Т.контр."])
    xr = x0 + 65
    pen.rect(x0, y0, 185, 40, S)
    pen.line(xr, y0, xr, y0 + 40, S)
    pen.line(xr, y0 + 25, xr + 120, y0 + 25, S)
    pen.line(xr + 70, y0, xr + 70, y0 + 25, S)
    pen.text(xr + 60, y0 + 30.5, code, pen.fit(code, 115, 5), "c")
    lines = name.split("\n") + [doc_title]
    n = len(lines)
    for i, s in enumerate(lines):
        h = pen.fit(s, 66, 3.5)
        pen.text(xr + 35, y0 + 12.5 + (n - 1) * 3.0 - i * 6.0 - h * 0.36, s, h, "c")
    xb = xr + 70
    pen.line(xb, y0 + 20, xb + 50, y0 + 20, S)
    pen.line(xb, y0 + 15, xb + 50, y0 + 15, S)
    pen.line(xb + 15, y0 + 15, xb + 15, y0 + 25, S)
    pen.line(xb + 30, y0 + 15, xb + 30, y0 + 25, S)
    pen.line(xb + 5, y0 + 15, xb + 5, y0 + 20, S3)
    pen.line(xb + 10, y0 + 15, xb + 10, y0 + 20, S3)
    pen.ctext(xb, y0 + 20, 15, 5, "Лит.")
    pen.ctext(xb + 15, y0 + 20, 15, 5, "Лист")
    pen.ctext(xb + 30, y0 + 20, 20, 5, "Листов")
    pen.ctext(xb, y0 + 15, 5, 5, lit)
    pen.ctext(xb + 15, y0 + 15, 15, 5, str(sheet))
    pen.ctext(xb + 30, y0 + 15, 20, 5, str(sheets))
    if org:
        pen.ctext(xb, y0, 50, 15, org, 3.5)


def stamp_form2a(pen: Pen, W, sheet, code=CODE):
    """Основная надпись по форме 2а (185×15) — последующие листы."""
    x0, y0 = W - 5 - 185, 5
    xs = [x0, x0 + 7, x0 + 17, x0 + 40, x0 + 55, x0 + 65]
    pen.rect(x0, y0, 185, 15, S)
    for x in xs[1:]:
        pen.line(x, y0, x, y0 + 15, S)
    pen.line(x0, y0 + 5, x0 + 65, y0 + 5, S)
    pen.line(x0, y0 + 10, x0 + 65, y0 + 10, S3)
    for (a, b), s in zip(zip(xs, xs[1:]), ("Изм.", "Лист", "№ докум.", "Подп.", "Дата")):
        pen.ctext(a, y0, b - a, 5, s)
    pen.line(x0 + 175, y0, x0 + 175, y0 + 15, S)
    pen.line(x0 + 175, y0 + 8, x0 + 185, y0 + 8, S)
    pen.ctext(x0 + 175, y0 + 8, 10, 7, "Лист")
    pen.ctext(x0 + 175, y0, 10, 8, str(sheet), 3.5)
    pen.text(x0 + 120, y0 + 5.7, code, pen.fit(code, 105, 5), "c")


def tech_requirements(pen: Pen, x, y_top, width, items, h=2.5, title=None):
    """Технические требования на чертеже (ГОСТ 2.316): нумерованный перечень над основной надписью."""
    from reportlab.lib.utils import simpleSplit
    y = y_top
    if title:
        pen.text(x + width / 2, y, title, 3.5, "c")
        y -= 6
    for i, s in enumerate(items, 1):
        lines = simpleSplit(f"{i} {s}", "GOST", fs(h), (width - 4) * mm)
        for j, ln in enumerate(lines):
            pen.text(x + (0 if j == 0 else 4), y, ln, h)
            y -= h * 1.75
        y -= 0.6
    return y
