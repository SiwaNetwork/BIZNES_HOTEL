"""Табличные документы ЕСКД: перечень элементов (ГОСТ 2.701-2008) и спецификация (ГОСТ 2.106-96).

Первый лист — основная надпись по форме 2 (ГОСТ 2.104), последующие — форма 2а. Строки таблицы по 8 мм,
длинные наименования переносятся на следующие строки; между группами оставляется свободная строка.
"""
from reportlab.lib.utils import simpleSplit
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import gost
from gost import Pen, S, S3

ROW = 8.0
HEAD = 15.0
TOP = 292.0
TOP1 = 278.0     # первый лист: таблица ниже графы 26 (14 мм)
H_TXT = 3.5

PE3_COLS = [(20, "Поз.\nобозна-\nчение"), (110, "Наименование"), (10, "Кол."), (45, "Примечание")]
SP_COLS = [(6, "Формат"), (6, "Зона"), (8, "Поз."), (70, "Обозначение"), (63, "Наименование"), (10, "Кол."),
           (22, "Приме-\nчание")]


def _wrap(text, width, h=H_TXT):
    out = []
    for part in str(text).split("\n"):
        out += simpleSplit(part, "GOST", gost.fs(h), (width - 2.5) * mm) or [""]
    return out


def _expand(rows, cols):
    """Строки таблицы -> физические строки по 8 мм. row: dict(cells=[...], head=bool, blank=bool)."""
    phys = []
    for r in rows:
        if r.get("blank"):
            phys.append(dict(cells=[""] * len(cols), kind="blank"))
            continue
        wrapped = [_wrap(c, w, r.get("h", H_TXT)) for c, (w, _) in zip(r["cells"], cols)]
        n = max(len(x) for x in wrapped)
        for i in range(n):
            phys.append(dict(cells=[x[i] if i < len(x) else "" for x in wrapped],
                             kind="head" if r.get("head") else "row", h=r.get("h", H_TXT),
                             first=i == 0, group=r.get("group", 0)))
    return phys


def _grid(p: Pen, x0, y_top, y_bot, cols):
    W = sum(w for w, _ in cols)
    p.line(x0, y_top - HEAD, x0 + W, y_top - HEAD, S)
    x = x0
    for i, (w, title) in enumerate(cols):
        lines = title.split("\n")
        if w < 9:                                    # узкие графы — надпись вдоль графы
            p.text(x + w / 2 + 1.2, y_top - HEAD / 2, title.replace("\n", ""), 2.5, "c", rot=90)
        else:
            for j, s in enumerate(lines):
                yy = y_top - HEAD / 2 + (len(lines) - 1) * 2.2 - j * 4.4 - 1.25
                p.text(x + w / 2, yy, s, p.fit(s, w - 1, 3.5), "c")
        x += w
        if i < len(cols) - 1:
            p.line(x, y_bot, x, y_top, S)
    y = y_top - HEAD - ROW
    while y > y_bot + 0.1:
        p.line(x0, y, x0 + W, y, S3)
        y -= ROW


def _doc(path, code, product, doc_title, cols, rows, align, lit="Т"):
    W, H = gost.A4
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{code} — {doc_title}")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    phys = _expand(rows, cols)
    cap1 = int((TOP1 - HEAD - 45) // ROW)
    capn = int((TOP - HEAD - 20) // ROW)
    pages, i = [], 0
    while i < len(phys) or not pages:
        cap = cap1 if not pages else capn
        chunk = phys[i:i + cap]
        # заголовок группы не оставляется последней строкой листа
        if i + cap < len(phys) and chunk and chunk[-1]["kind"] == "head":
            chunk = chunk[:-1]
        pages.append(chunk)
        i += len(chunk)
    x0 = 20.0
    for n, chunk in enumerate(pages, 1):
        y_bot = 45.0 if n == 1 else 20.0
        top = TOP1 if n == 1 else TOP
        p.rect(x0, y_bot, 185, top - y_bot, S)
        _grid(p, x0, top, y_bot, cols)
        y = top - HEAD
        for r in chunk:
            x = x0
            for (w, _), s, a in zip(cols, r["cells"], align):
                if s:
                    h = r.get("h", H_TXT)
                    tx = {"l": x + 1.2, "c": x + w / 2, "r": x + w - 1.2}[a if r["kind"] != "head" else "c"]
                    p.text(tx, y - ROW / 2 - h * 0.36, s, p.fit(s, w - 1.5, h), a if r["kind"] != "head" else "c")
                    if r["kind"] == "head" and r.get("underline", True):
                        from reportlab.pdfbase.pdfmetrics import stringWidth
                        tw = stringWidth(s, "GOST", gost.fs(h)) / mm
                        p.line(tx - tw / 2, y - ROW / 2 - h * 0.36 - 0.8, tx + tw / 2, y - ROW / 2 - h * 0.36 - 0.8, S3)
                x += w
            y -= ROW
        gost.frame(p, W, H, drawing=False, first=n == 1, code=code)
        if n == 1:
            gost.stamp_form2(p, W, product, doc_title, code=code, lit=lit, sheet="" if len(pages) == 1 else 1,
                             sheets=len(pages))
        else:
            gost.stamp_form2a(p, W, n, code=code)
        c.showPage()
    c.save()
    return len(pages)


def build_pe3(path, code, product, groups, lit="Т"):
    """groups: [(заголовок группы или "", [(поз_обозн, наименование, кол, примечание)])]."""
    rows = []
    for title, items in groups:
        if rows:
            rows.append(dict(blank=True))
        if title:
            rows.append(dict(cells=["", title, "", ""], head=True))
        for ref, name, qty, note in items:
            rows.append(dict(cells=[ref, name, str(qty), note]))
    return _doc(path, code + " ПЭ3", product, "Перечень элементов", PE3_COLS, rows, "llcl", lit)


def build_sp(path, code, product, sections, lit="Т"):
    """sections: [(раздел, [(формат, зона, поз, обозначение, наименование, кол, примечание)])]."""
    rows = []
    for title, items in sections:
        rows.append(dict(blank=True))
        rows.append(dict(cells=["", "", "", "", title, "", ""], head=True))
        rows.append(dict(blank=True))
        for it in items:
            if it is None:
                rows.append(dict(blank=True))
                continue
            rows.append(dict(cells=[str(v) for v in it]))
    return _doc(path, code, product, "", SP_COLS, rows[1:], "cccllcl", lit)
