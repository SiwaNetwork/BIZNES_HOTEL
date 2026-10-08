"""Элементы чертежей: размеры (ГОСТ 2.307), таблицы, выносные надписи."""
from reportlab.lib.utils import simpleSplit

import gost
from gost import Pen, S3

LW_DIM = 0.18


def dim_h(p: Pen, x1, x2, y_obj, y_dim, text, h=3.5, ext=2.0, text_dx=0.0, outside=False):
    """Горизонтальный линейный размер: выносные линии от y_obj до y_dim."""
    sgn = 1 if y_dim >= y_obj else -1
    for x in (x1, x2):
        p.line(x, y_obj + sgn * 0.8, x, y_dim + sgn * ext, LW_DIM)
    if outside:
        p.line(x1 - 8, y_dim, x2 + 8, y_dim, LW_DIM)
        p.arrow(x1 - 5, y_dim, x1, y_dim, LW_DIM, 2.5)
        p.arrow(x2 + 5, y_dim, x2, y_dim, LW_DIM, 2.5)
    else:
        p.arrow(x1, y_dim, x2, y_dim, LW_DIM, 2.5, both=True)
    p.text((x1 + x2) / 2 + text_dx, y_dim + 1.0, text, h, "c")


def dim_v(p: Pen, y1, y2, x_obj, x_dim, text, h=3.5, ext=2.0, outside=False):
    sgn = 1 if x_dim >= x_obj else -1
    for y in (y1, y2):
        p.line(x_obj + sgn * 0.8, y, x_dim + sgn * ext, y, LW_DIM)
    if outside:
        p.line(x_dim, y1 - 8, x_dim, y2 + 8, LW_DIM)
        p.arrow(x_dim, y1 - 5, x_dim, y1, LW_DIM, 2.5)
        p.arrow(x_dim, y2 + 5, x_dim, y2, LW_DIM, 2.5)
    else:
        p.arrow(x_dim, y1, x_dim, y2, LW_DIM, 2.5, both=True)
    p.text(x_dim - 1.0, (y1 + y2) / 2, text, h, "c", rot=90)


def leader(p: Pen, x, y, x2, y2, text, h=3.5, shelf=None):
    """Линия-выноска с полкой."""
    p.line(x, y, x2, y2, LW_DIM)
    p.circle(x, y, 0.35, LW_DIM)
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.lib.units import mm
    w = shelf or stringWidth(text, "GOST", gost.fs(h)) / mm + 2
    if x2 >= x:
        p.line(x2, y2, x2 + w, y2, LW_DIM)
        p.text(x2 + 1, y2 + 1, text, h)
    else:
        p.line(x2 - w, y2, x2, y2, LW_DIM)
        p.text(x2 - w + 1, y2 + 1, text, h)


def table(p: Pen, x, y_top, cols, rows, header, row_h=6.0, h=2.5, head_h=None, title=None):
    """Таблица: cols — ширины, rows — списки строк. Возвращает y низа."""
    head_h = head_h or row_h + 2
    if title:
        p.text(x, y_top + 2, title, 3.5)
    W = sum(cols)
    n = len(rows)
    y_bot = y_top - head_h - n * row_h
    p.rect(x, y_bot, W, y_top - y_bot, gost.S)
    p.line(x, y_top - head_h, x + W, y_top - head_h, gost.S)
    xx = x
    for i, w in enumerate(cols):
        if i:
            p.line(xx, y_bot, xx, y_top, gost.S)
        lines = header[i].split("\n")
        for j, s in enumerate(lines):
            p.text(xx + w / 2, y_top - head_h / 2 + (len(lines) - 1) * h * 0.8 - j * h * 1.6 - h * 0.36,
                   s, p.fit(s, w - 1.5, h), "c")
        xx += w
    for r, row in enumerate(rows):
        yy = y_top - head_h - (r + 1) * row_h
        if r:
            p.line(x, yy + row_h, x + W, yy + row_h, S3)
        xx = x
        for i, w in enumerate(cols):
            s = str(row[i])
            p.text(xx + w / 2, yy + row_h / 2 - h * 0.36, s, p.fit(s, w - 1.5, h), "c")
            xx += w
    return y_bot


def wrap(text, width_mm, h):
    from reportlab.lib.units import mm
    return simpleSplit(text, "GOST", gost.fs(h), width_mm * mm)
