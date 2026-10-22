"""ТЕНШ.464512.001 Э1 — схема электрическая структурная (ГОСТ 2.701-2008, ГОСТ 2.702-2011)."""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

import design as D
import gost
from gost import Pen

LW_BLOCK = 0.5
LW_LINE = 0.35
LW_PWR = 0.25
DASH_PWR = (2, 1)
DASH_EXT = (4, 1.5)
PCB_CODE = "ТЕНШ.687281.001"


def block(p: Pen, x, y, w, h, title, params=(), ref=None, dashed=False):
    p.rect(x, y, w, h, LW_BLOCK, dash=DASH_EXT if dashed else None)
    lines = [(s, 3.5) for s in title.split("\n")] + [(s, 2.5) for s in params]
    total = sum(hh * 1.75 for _, hh in lines)
    yy = y + h / 2 + total / 2 - 3.5
    for s, hh in lines:
        p.text(x + w / 2, yy, s, p.fit(s, w - 3, hh), "c")
        yy -= hh * 1.75
    if ref:
        p.text(x + 1.2, y + h - 4, ref, 2.5)


def antenna(p: Pen, x, y):
    """Условное графическое обозначение антенны (ГОСТ 2.735)."""
    p.line(x, y, x, y + 16, LW_LINE)
    p.line(x - 6, y + 16, x, y + 8, LW_LINE)
    p.line(x + 6, y + 16, x, y + 8, LW_LINE)
    p.line(x - 6, y + 16, x + 6, y + 16, LW_LINE)


def coax_socket(p: Pen, x, y):
    """Соединитель коаксиальный (ГОСТ 2.755, упрощённо): окружность с центральным контактом."""
    p.circle(x, y, 2.2, LW_LINE)
    p.circle(x, y, 0.6, LW_LINE, fill=colors.black)


def poly(p: Pen, pts, arrow=True, w=LW_LINE, dash=None):
    for (x1, y1), (x2, y2) in zip(pts[:-2], pts[1:-1]):
        p.line(x1, y1, x2, y2, w, dash)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    if arrow:
        p.line(x1, y1, x2, y2, w, dash)
        p.arrow(x2 - (x2 - x1) * 1e-3, y2 - (y2 - y1) * 1e-3, x2, y2, w, 3)
    else:
        p.line(x1, y1, x2, y2, w, dash)


def pwr(p: Pen, pts, arrow=True):
    poly(p, pts, arrow=arrow, w=LW_PWR, dash=DASH_PWR)


def dot(p: Pen, x, y):
    p.circle(x, y, 0.6, 0.2, fill=colors.black)


NOTES = [
    "Параметры функциональных частей ориентировочные.",
    "Сплошные линии со стрелками — сигналы, штриховые — цепи питания; обрывы цепей питания обозначены адресами.",
    "Штриховые рамки — устройства вне модуля: антенна WA1 (из комплекта связи), полётный контроллер и АКБ.",
    "При переходе на S-диапазон (1980–2010/2170–2200 МГц) заменяются A1–A4, Z1, Z2 и антенна WA1.",
    "X1 — краевые полуотверстия, шаг 2,54 мм, 20 контактов; XW1 — розетка коаксиальная 50 Ом.",
    "Элементы платы " + PCB_CODE + ": " + "; ".join(f"{a} — {b}" for a, b in D.E1_TO_PCB if a != b) + ".",
]


def draw_scheme(p: Pen):
    """Поле схемы (без рамки, основной надписи и примечаний)."""
    # --- антенна (вне модуля), розетка XW1, антенный коммутатор
    p.rect(26, 186, 30, 44, LW_BLOCK, dash=DASH_EXT)
    antenna(p, 38, 199)
    p.text(31, 224, "WA1", 3.5)
    p.line(38, 199, 49, 199, LW_LINE)
    coax_socket(p, 51.2, 199)
    p.text(51.2, 203, "XW1", 2.5, "c")
    p.arrow(53.4, 199, 60, 199, LW_LINE, 3, both=True)
    block(p, 60, 182, 40, 34, "Антенный\nкоммутатор", ("ПР/ПД, Pвх до 37 дБм,", "перестройка согл. WA1"), "A1")
    # --- тракт передачи (верх) и приёма (низ)
    block(p, 172, 228, 42, 30, "Фильтр\nполосовой ПД", ("1626,5–1660,5 МГц",), "Z1")
    block(p, 110, 228, 50, 30, "Усилитель\nмощности", ("Pвых 27…30 дБм, ФНЧ,", "детектор мощности"), "A2")
    block(p, 172, 140, 42, 30, "Фильтр\nполосовой ПР", ("1525–1559 МГц",), "Z2")
    block(p, 110, 140, 50, 30, "Малошумящий\nусилитель", ("Кш ≤ 1 дБ, Ку ≥ 18 дБ",), "A3")
    block(p, 232, 132, 46, 134, "Приёмопередатчик\nРЧ", (
        "модулятор BPSK/GFSK,", "демодулятор LoRa", "(полоса 7,8–10,4 кГц),", "синтезатор частот,",
        "SIMO-преобразователь", "", "1,5–2,5 ГГц"), "A4")
    block(p, 296, 132, 50, 134, "Микроконтроллер-\nмодем", (
        "протокол канального", "уровня, кодирование,", "шифрование AES-128,", "управление режимами,",
        "контроль АКБ", "и мощности ПД"), "A5")
    block(p, 296, 272, 50, 16, "Память", ("буфер сообщений, ПО",), "A6")
    # --- соединитель X1 и внешние устройства
    p.rect(356, 102, 8, 164, LW_BLOCK)
    p.text(360, 268, "X1", 3.5, "c")
    block(p, 374, 192, 38, 60, "Полётный\nконтроллер\nБПЛА", ("(внешнее", "устройство)"), dashed=True)
    block(p, 374, 104, 38, 26, "АКБ Li-Ion\n1S 3,7 В", ("(внешняя)",), dashed=True)
    # --- опорный генератор и узел питания
    block(p, 232, 104, 46, 22, "Опорный\nгенератор", ("TCXO 32 МГц, ±0,5 ppm",), "G1")
    block(p, 40, 20, 185, 36, "Узел питания", (
        "ключ питания УМ с плавным включением, накопитель энергии 440 мкФ,",
        "стабилизаторы линейные 3,0 В: постоянный и отключаемый (РЧ), контроль напряжения АКБ"), "A7")

    # --- РЧ-тракт
    poly(p, [(232, 243), (214, 243)])                       # A4 -> Z1
    p.text(223, 245, "ПД", 2.5, "c")
    poly(p, [(172, 243), (160, 243)])                       # Z1 -> A2
    poly(p, [(110, 243), (82, 243), (82, 216)])             # A2 -> A1
    poly(p, [(82, 182), (82, 155), (110, 155)])             # A1 -> A3
    poly(p, [(160, 155), (172, 155)])                       # A3 -> Z2
    poly(p, [(214, 155), (232, 155)])                       # Z2 -> A4
    p.text(223, 157, "ПР", 2.5, "c")
    # детектор мощности -> A5 (АЦП), обход A4 сверху
    poly(p, [(135, 258), (135, 270), (288, 270), (288, 252), (296, 252)])
    p.text(240, 271.6, "уровень мощности", 2.5, "c")
    # управление коммутатором и МШУ — выводы DIO приёмопередатчика
    poly(p, [(245, 132), (245, 126), (104, 126), (104, 199), (100, 199)])
    p.text(192, 127.6, "ПР/ПД (управление коммутатором)", 2.5, "c")
    poly(p, [(140, 126), (140, 140)])
    dot(p, 140, 126)
    p.text(124, 131, "вкл. МШУ", 2.5)
    # A4 <-> A5
    p.arrow(278, 220, 296, 220, LW_LINE, 3, both=True)
    p.text(287, 222, "SPI", 2.5, "c")
    p.arrow(278, 200, 296, 200, LW_LINE, 3)
    p.text(287, 202, "IRQ, BUSY", 2.5, "c")
    p.arrow(296, 180, 278, 180, LW_LINE, 3)
    p.text(287, 182, "сброс", 2.5, "c")
    # A5 <-> A6
    p.arrow(321, 266, 321, 272, LW_LINE, 2.5, both=True)
    # G1 -> A4
    poly(p, [(255, 126), (255, 132)])
    p.text(262, 128, "32 МГц", 2.5)
    # A5 <-> X1 <-> полётный контроллер
    for name, yy in (("UART", 244), ("WAKE", 230), ("IRQ", 216), ("PPS", 202)):
        if name == "UART":
            p.arrow(346, yy, 356, yy, LW_LINE, 2.5, both=True)
            p.arrow(364, yy, 374, yy, LW_LINE, 2.5, both=True)
        elif name == "IRQ":
            p.arrow(346, yy, 356, yy, LW_LINE, 2.5)
            p.arrow(364, yy, 374, yy, LW_LINE, 2.5)
        else:
            p.arrow(356, yy, 346, yy, LW_LINE, 2.5)
            p.arrow(374, yy, 364, yy, LW_LINE, 2.5)
        p.text(351, yy + 1.5, name, 2.5, "c")

    # --- цепи питания (штриховые)
    pwr(p, [(374, 112), (364, 112)])                        # АКБ -> X1
    p.text(369, 114, "+VBAT", 2.5, "c")
    pwr(p, [(356, 112), (340, 112)])                        # X1 -> обрыв (к A7)
    p.text(318, 106.5, "+VBAT 3,3…4,2 В → A7", 2.5, "c")
    pwr(p, [(28, 44), (40, 44)])                            # обрыв (от X1) -> A7
    p.text(30, 46, "+VBAT от X1", 2.5)
    pwr(p, [(164, 56), (164, 222), (155, 222), (155, 228)])  # +VPA -> A2
    p.text(165.5, 62, "+VPA", 2.5)
    pwr(p, [(200, 56), (200, 118), (226, 118), (226, 140), (232, 140)])    # +3,0 В РЧ -> A4
    pwr(p, [(200, 100), (145, 100), (145, 140)])            # -> A3
    dot(p, 200, 100)
    p.text(201.5, 62, "+3,0 В (РЧ)", 2.5)
    pwr(p, [(64, 172), (64, 182)])                          # обрыв (от A7) -> A1
    p.text(48, 167, "+3,0 В (РЧ) от A7", 2.5)
    pwr(p, [(70, 56), (70, 68)])                            # +3,0 В -> обрыв (к A5, A6, X1)
    p.text(72, 66, "+3,0 В → A5, A6, X1 (VIO)", 2.5)
    pwr(p, [(334, 123), (334, 132)])                        # обрыв (от A7) -> A5
    p.text(336, 125, "+3,0 В от A7", 2.5)
    pwr(p, [(352, 280), (346, 280)])                        # обрыв (от A7) -> A6
    p.text(353, 279, "+3,0 В от A7", 2.5)


def build(path, bare=False):
    """bare=True — только поле схемы (для иллюстрации в ПЗ), без рамки, надписи и примечаний."""
    W, H = gost.A3L
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{gost.CODE} Э1 — Схема электрическая структурная")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    draw_scheme(p)
    if not bare:
        gost.frame(p, W, H, drawing=True, code=gost.CODE + " Э1")
        # примечания — над основной надписью (ГОСТ 2.316)
        x0, w = W - 5 - 185, 183
        y = 99
        p.text(x0 + w / 2, y, "Примечания", 3.5, "c")
        y -= 6
        for i, s in enumerate(NOTES, 1):
            for j, ln in enumerate(simpleSplit(f"{i} {s}", "GOST", gost.fs(2.5), (w - 3) * mm)):
                p.text(x0 + (0 if j == 0 else 3), y, ln, 2.5)
                y -= 4.0
        gost.stamp_form1(p, W, gost.PRODUCT, "Схема электрическая структурная",
                         code=gost.CODE + " Э1", lit="Т", sheet="", sheets="1")
    c.showPage()
    c.save()


if __name__ == "__main__":
    import sys
    gost.register_fonts()
    build(sys.argv[1] if len(sys.argv) > 1 else "e1.pdf")
