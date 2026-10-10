"""Исправление шрифта osifont (ГОСТ 2.304, тип Б): в исходном файле глифы «Э», «ё», «Ё»
повреждены (выводятся сплошным прямоугольником), а «…» отсутствует.
Скрипт пересобирает их из исправных глифов и сохраняет fonts/osifont-ru.ttf.
Лицензия исходного шрифта — LGPLv3 с исключением для шрифтов (см. fonts/README.md).
"""
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from gost import FONTS

SRC = FONTS / "osifont-lgpl3fe.ttf"
DST = FONTS / "osifont-ru.ttf"


def main():
    f = TTFont(SRC)
    cm = f.getBestCmap()
    glyf, hmtx = f["glyf"], f["hmtx"]
    gs = f.getGlyphSet()

    def draw(pen, name, dx=0, mirror_adv=None):
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        if mirror_adv is not None:
            rec.replay(ReverseContourPen(TransformPen(pen, (-1, 0, 0, 1, mirror_adv, 0))))
        else:
            rec.replay(TransformPen(pen, (1, 0, 0, 1, dx, 0)))

    def put(name, pen, adv, lsb=None):
        g = pen.glyph()
        g.recalcBounds(glyf)
        glyf[name] = g
        hmtx[name] = (adv, g.xMin if lsb is None else lsb)

    # Э = зеркальная С + средняя перекладина
    es = cm[ord("С")]
    adv = hmtx[es][0]
    pen = TTGlyphPen(gs)
    draw(pen, es, mirror_adv=adv)
    y0, t = 690, 140
    pen.moveTo((330, y0)); pen.lineTo((330, y0 + t)); pen.lineTo((adv - 180, y0 + t))
    pen.lineTo((adv - 180, y0)); pen.closePath()
    put("uni042D", pen, adv)

    # ё / Ё = е / Е + трема
    a_adv, A_adv = hmtx["a"][0], hmtx["A"][0]
    for ch, base, ref, dx, dy in (("ё", "е", a_adv, 82, -275), ("Ё", "Е", A_adv, 230, 190)):
        b = cm[ord(base)]
        badv = hmtx[b][0]
        pen = TTGlyphPen(gs)
        draw(pen, b)
        rec = DecomposingRecordingPen(gs)
        gs["uni0308"].draw(rec)
        rec.replay(TransformPen(pen, (1, 0, 0, 1, dx + (badv - ref) / 2, dy)))
        put(cm[ord(ch)], pen, badv)

    # … = три точки
    per = cm[ord(".")]
    padv = hmtx[per][0]
    name = "ellipsis"
    if name not in f.getGlyphOrder():
        f.setGlyphOrder(f.getGlyphOrder() + [name])
    pen = TTGlyphPen(gs)
    for i in range(3):
        draw(pen, per, dx=i * (padv - 60))
    put(name, pen, 3 * (padv - 60) + 60)
    for tbl in f["cmap"].tables:
        if tbl.isUnicode():
            tbl.cmap[0x2026] = name
    f["maxp"].numGlyphs = len(f.getGlyphOrder())
    f.save(DST)
    print("saved", DST)


if __name__ == "__main__":
    main()
