"""ТЕНШ.687281.001 СБ — Плата печатная многослойная. Сборочный чертёж (ГОСТ 2.417-91, ГОСТ 2.109-73), А3, М 4:1.

Многослойная печатная плата по ГОСТ 2.417-91 является сборочной единицей: оформляется сборочным
чертежом (код СБ) и спецификацией; слои L1–L4 документируются при разработке РКД.
"""
import numpy as np
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import design as D
import gost
from drawing import LW_DIM, dim_h, dim_v, leader, table
from gost import Pen, S, S3

DESIGNATION = "ТЕНШ.687281.001"
CODE = DESIGNATION + " СБ"
MODULE = gost.CODE
K = 4.0                 # масштаб 4:1
X0, Y0 = 52.0, 150.0    # положение начала координат платы на листе
LW_THIN = 0.25


def P(x, y):
    return X0 + K * x, Y0 + K * y


def fence_vias():
    """Переходные отверстия «забора» по контуру зоны экрана (шаг 1,0 мм)."""
    sh = D.SHIELD
    pts = []
    for t in np.arange(sh["x"] + 0.5, sh["x"] + sh["l"], 1.0):
        pts += [(t, sh["y"] + 0.3), (t, sh["y"] + sh["w"] - 0.3)]
    for t in np.arange(sh["y"] + 0.8, sh["y"] + sh["w"], 1.0):
        pts += [(sh["x"] + 0.3, t), (sh["x"] + sh["l"] - 0.3, t)]
    return pts


def sign_castellated(p: Pen, x, y):
    p.c.saveState()
    p.c.setFillColorRGB(1, 1, 1)
    p.c.setLineWidth(LW_THIN * mm)
    p.c.circle(x * mm, y * mm, K * D.PAD_HOLE_D / 2 * mm, stroke=1, fill=1)
    p.c.restoreState()


def sign_mounting(p: Pen, x, y):
    r = K * D.HOLE_D / 2
    p.circle(x, y, r, S)
    p.line(x - r - 1.5, y, x + r + 1.5, y, LW_THIN)
    p.line(x, y - r - 1.5, x, y + r + 1.5, LW_THIN)


def sign_via(p: Pen, x, y):
    p.circle(x, y, 0.5, 0.15, fill=colors.black)


def build(path):
    W, H = gost.A3L
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{CODE} — Плата печатная многослойная. Сборочный чертёж")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    gost.frame(p, W, H, drawing=True, code=CODE, first_use=MODULE)

    # ---------------------------------------------------- главный вид
    c.setLineWidth(S * mm)
    x, y = P(0, 0)
    c.roundRect(x * mm, y * mm, K * D.BOARD_L * mm, K * D.BOARD_W * mm, K * D.CORNER_R * mm, stroke=1, fill=0)
    sh = D.SHIELD
    sx, sy = P(sh["x"], sh["y"])
    p.rect(sx, sy, K * sh["l"], K * sh["w"], LW_THIN, dash=(4, 1.5))
    vias = fence_vias()
    for vx, vy in vias:
        sign_via(p, *P(vx, vy))
    ex, ey = P(sh["x"] + 0.9, sh["y"] + sh["w"] - 1.9)
    p.text(ex, ey, "Э", 3.5)
    # посадочные места элементов (условно)
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        px, py = P(x - l / 2, y - w / 2)
        p.rect(px, py, K * l, K * w, LW_THIN, fill=colors.Color(0.93, 0.93, 0.93))
        cx, cy = P(x, y)
        from reportlab.pdfbase.pdfmetrics import stringWidth
        if stringWidth(name, "GOST", gost.fs(2.5)) / mm <= K * l - 0.6:
            p.text(cx, cy - 0.9, name, 2.5, "c")
        else:
            p.text(px + K * l + 0.6, cy - 0.9, name, 2.5)
    for x, y, r in D.PASSIVES:
        l, w = (1.0, 0.5) if r == 0 else (0.5, 1.0)
        px, py = P(x - l / 2, y - w / 2)
        p.rect(px, py, K * l, K * w, LW_THIN, fill=colors.Color(0.85, 0.85, 0.85))
    # краевые контакты (полуотверстия) и нумерация — внутри контура платы
    for n, x, y, side in D.pad_positions():
        yc = 0 if side == "bottom" else D.BOARD_W - D.PAD_L
        px, py = P(x - D.PAD_W / 2, yc)
        p.rect(px, py, K * D.PAD_W, K * D.PAD_L, LW_THIN, fill=colors.Color(0.78, 0.78, 0.78))
        cx, cy = P(x, y)
        sign_castellated(p, cx, cy)
        ty = Y0 + K * D.PAD_L + 1.0 if side == "bottom" else Y0 + K * (D.BOARD_W - D.PAD_L) - 3.6
        p.text(cx, ty, str(n), 2.5, "c")
    # ключ — первый вывод
    kx, ky = P(D.pad_positions()[0][1] - 1.75, 2.0)
    pth = c.beginPath()
    pth.moveTo(kx * mm, ky * mm); pth.lineTo((kx + 3) * mm, ky * mm); pth.lineTo(kx * mm, (ky + 3) * mm); pth.close()
    c.drawPath(pth, fill=1, stroke=0)
    # крепёжные отверстия
    for hx, hy in D.HOLES:
        sign_mounting(p, *P(hx, hy))

    # ---------------------------------------------------- размеры
    x_l, y_b = P(0, 0)
    x_r, y_t = P(D.BOARD_L, D.BOARD_W)
    dim_h(p, x_l, x_r, y_t, y_t + 22, "32±0,1")
    dim_v(p, y_b, y_t, x_l, x_l - 20, "22±0,1")
    xa, _ = P(D.PADS_X0, 0)
    xb, _ = P(D.PADS_X0 + 9 * D.PAD_PITCH, 0)
    dim_h(p, xa, xb, y_b, y_b - 14, "9×2,54=22,86")
    dim_h(p, x_l, xa, y_b, y_b - 24, "4,57*", outside=True)
    xa2, _ = P(D.PADS_X0 + D.PAD_PITCH, 0)
    dim_h(p, xa, xa2, y_t, y_t + 12, "2,54", outside=True)
    # крепёжные отверстия: нижнее левое и верхнее правое
    h1x, h1y = P(*D.HOLES[0])
    h2x, h2y = P(*D.HOLES[1])
    dim_v(p, y_b, h1y, x_l, x_l - 10, "1,6", outside=True)
    p.line(h1x - 4.0, h1y, x_l - 0.8, h1y, LW_DIM)
    dim_h(p, x_l, h1x, y_b, y_b - 34, "1,6", outside=True)
    p.line(h1x, h1y - 4.0, h1x, y_b - 0.8, LW_DIM)
    dim_v(p, h2y, y_t, x_r, x_r + 10, "1,6", outside=True)
    p.line(h2x + 4.0, h2y, x_r + 0.8, h2y, LW_DIM)
    dim_h(p, h2x, x_r, y_t, y_t + 12, "1,6", outside=True, text_left=True)
    p.line(h2x, h2y + 4.0, h2x, y_t + 0.8, LW_DIM)
    leader(p, h2x + K * D.HOLE_D / 2 * 0.7, h2y - K * D.HOLE_D / 2 * 0.7, x_r + 30, h2y - 25, "⌀1,1 (2 отв.)")
    # контактная площадка
    n10 = D.pad_positions()[9]
    px, py = P(n10[1] + D.PAD_W / 2 - 0.2, 1.0)
    leader(p, px, py, x_r + 8, y_b - 20, "1,2×1,6, ⌀0,8 (20 шт.)")
    # зона экрана Э — расстояние от нижней кромки
    _, syb = P(sh["x"], sh["y"])
    sxr, _ = P(sh["x"] + sh["l"], 0)
    dim_v(p, y_b, syb, x_r, x_r + 22, "2,6", outside=True)
    p.line(sxr, syb, x_r + 0.8, syb, LW_DIM)

    # вид с торца (проекционная связь, без обозначения)
    ys = Y0 - 78
    p.rect(x_l, ys, K * D.BOARD_L, K * D.BOARD_T, S)
    dim_v(p, ys, ys + K * D.BOARD_T, x_l, x_l - 10, "0,6±0,06", outside=True)

    # ---------------------------------------------------- таблицы справа
    rows = [(n, D.PIN_NAMES[n], {
        "GND": "Общий", "VBAT": "Питание 3,3…4,2 В", "UART_TX": "Выход UART (данные)",
        "UART_RX": "Вход UART (данные)", "WAKE": "Вход пробуждения", "IRQ": "Выход прерывания",
        "PPS": "Вход секундной метки", "SWDIO": "Отладка SWD", "SWCLK": "Отладка SWD",
        "nRST": "Сброс (активный 0)", "BOOT": "Режим загрузчика", "I2C_SDA": "I²C (резерв)",
        "I2C_SCL": "I²C (резерв)", "VIO": "Уровни интерфейса 1,8…3,3 В"}[D.PIN_NAMES[n]])
        for n in range(1, 21)]
    table(p, 238, 284, [12, 24, 60], rows, ["Конт.", "Цепь", "Назначение"], row_h=5.0, head_h=7,
          title="Таблица 1 — Контакты X1")
    table(p, 340, 284, [16, 30, 24], [
        ("L1", "Сигнальный, РЧ", "0,035"),
        ("—", "Препрег", "0,10"),
        ("L2", "Земля", "0,035"),
        ("—", "Ядро", "0,26"),
        ("L3", "Питание, сигн.", "0,035"),
        ("—", "Препрег", "0,10"),
        ("L4", "Сигнальный", "0,035"),
        ("", "Итого", "0,6±0,06"),
    ], ["Слой", "Назначение", "Толщ., мм"], row_h=5.0, head_h=7, title="Таблица 2 — Структура платы")
    yb3 = table(p, 340, 226, [12, 12, 18, 12, 16], [
        ("", "0,8", "1,2×1,6", "20", "есть"),
        ("", "1,1", "—", "2", "нет"),
        ("", "0,2", "0,45", str(len(vias)) + "*", "есть"),
    ], ["Знак", "⌀ отв.", "Площадка", "Кол.", "Металл."], row_h=6.0, head_h=7,
        title="Таблица 3 — Отверстия")
    # условные знаки отверстий в графе «Знак»
    for i, fn in enumerate((sign_castellated, sign_mounting, sign_via)):
        fn(p, 346, 226 - 7 - 6 * i - 3)

    # ---------------------------------------------------- технические требования
    items = [
        "* Размеры и количество для справок; количество переходных отверстий вне зоны Э — по электронной "
        "модели платы.",
        "Плата должна соответствовать ГОСТ Р 55693-2013. Основные параметры конструкции — по ГОСТ Р 53429-2009, "
        "класс точности 5.",
        "Состав сборочной единицы (слои L1–L4, препреги) — по спецификации " + DESIGNATION + ", разрабатываемой "
        "в составе рабочей конструкторской документации (РКД).",
        "Материал: стеклотекстолит с Tg ≥ 170 °C; допускается гибридная структура с СВЧ-материалом "
        "(εr = 3,4…3,7, tgδ ≤ 0,004) между слоями L1–L2. Выбор — при разработке РКД.",
        "Волновое сопротивление РЧ-линий (копланарная линия с землёй, слой L1 над L2) — 50 Ом ±10 %.",
        "Покрытие контактных площадок и полуотверстий — иммерсионное золото по никелю (ENIG). Защитная "
        "паяльная маска — с обеих сторон, кроме контактных площадок; маркировка — белой краской.",
        "Э — зона установки экрана РЧ-тракта 13,6×16,8 мм; левый нижний угол зоны — 4,6 мм от левой и 2,6 мм "
        "от нижней кромки платы. Переходные отверстия по контуру зоны — с шагом не более 1,0 мм.",
        "Рисунок проводников и посадочные места — по РКД; посадочные места и позиционные обозначения "
        "элементов показаны условно для оценки компоновки.",
        "Радиус скругления углов платы — 1 мм. Неуказанные предельные отклонения размеров — ±0,1 мм. "
        "Вид с торца показан без элементов.",
        "Маркировать обозначение платы и номер партии на стороне L4 шрифтом высотой 1 мм.",
    ]
    gost.tech_requirements(p, 240, min(160, yb3 - 8), 172, items, h=2.5)

    gost.stamp_form1(p, W, "Плата печатная\nмногослойная", "Сборочный чертёж", code=CODE, lit="Т",
                     mass="0,9 г", scale="4:1", sheet="", sheets="1", material="")
    c.showPage()
    c.save()


if __name__ == "__main__":
    import sys
    gost.register_fonts()
    build(sys.argv[1] if len(sys.argv) > 1 else "pcb.pdf")
