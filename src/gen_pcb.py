"""ТЕНШ.758726.001 — Плата печатная. Чертёж (ГОСТ 2.417-91, ГОСТ 2.109-73), А3, М 4:1."""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import design as D
import gost
from drawing import dim_h, dim_v, leader, table
from gost import Pen, S, S3

CODE = "ТЕНШ.758726.001"
K = 4.0                 # масштаб 4:1
X0, Y0 = 52.0, 150.0    # положение начала координат платы на листе


def P(x, y):
    return X0 + K * x, Y0 + K * y


def rounded_outline(p: Pen):
    c = p.c
    c.setLineWidth(S * mm)
    x, y = P(0, 0)
    c.roundRect(x * mm, y * mm, K * D.BOARD_L * mm, K * D.BOARD_W * mm, K * D.CORNER_R * mm, stroke=1, fill=0)


def build(path):
    W, H = gost.A3L
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{CODE} — Плата печатная")
    p = Pen(c)
    gost.frame(p, W, H, drawing=True, code=CODE)

    # ---------------------------------------------------- главный вид
    rounded_outline(p)
    # зоны: РЧ (под экраном) и цифровая
    sh = D.SHIELD
    sx, sy = P(sh["x"], sh["y"])
    p.rect(sx, sy, K * sh["l"], K * sh["w"], 0.3, dash=(6, 1.5, 1, 1.5))
    sx2, _ = P(sh["x"] + sh["l"], 0)
    # переходные отверстия «забора» экрана (условно, шаг 1,0)
    import numpy as np
    for t in np.arange(sh["x"] + 0.5, sh["x"] + sh["l"], 1.0):
        for yy in (sh["y"] + 0.3, sh["y"] + sh["w"] - 0.3):
            xx, y2 = P(t, yy)
            p.circle(xx, y2, 0.45, 0.13)
    for t in np.arange(sh["y"] + 0.8, sh["y"] + sh["w"], 1.0):
        for xx0 in (sh["x"] + 0.3, sh["x"] + sh["l"] - 0.3):
            xx, y2 = P(xx0, t)
            p.circle(xx, y2, 0.45, 0.13)
    # посадочные места элементов (тонко, условно)
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        px, py = P(x - l / 2, y - w / 2)
        p.rect(px, py, K * l, K * w, 0.13, fill=colors.Color(0.93, 0.93, 0.93))
        cx, cy = P(x, y)
        p.text(cx, cy - 1.0, name, 2.5 if l * K > 8 else 2.0, "c")
    for x, y, r in D.PASSIVES:
        l, w = (1.0, 0.5) if r == 0 else (0.5, 1.0)
        px, py = P(x - l / 2, y - w / 2)
        p.rect(px, py, K * l, K * w, 0.1, fill=colors.Color(0.85, 0.85, 0.85))
    # краевые контакты (полуотверстия) и нумерация
    for n, x, y, side in D.pad_positions():
        yc = 0 if side == "bottom" else D.BOARD_W - D.PAD_L
        px, py = P(x - D.PAD_W / 2, yc)
        p.rect(px, py, K * D.PAD_W, K * D.PAD_L, 0.25, fill=colors.Color(0.78, 0.78, 0.78))
        cx, cy = P(x, y)
        p.c.saveState()
        p.c.setFillColorRGB(1, 1, 1)
        p.c.circle(cx * mm, cy * mm, K * D.PAD_HOLE_D / 2 * mm, stroke=1, fill=1)
        p.c.restoreState()
        ty = cy - 7.5 if side == "bottom" else cy + 4.5
        p.text(cx, ty, str(n), 2.5, "c")
    # ключ — первый вывод
    kx, ky = P(D.pad_positions()[0][1] - 1.6, 1.9)
    pth = c.beginPath()
    pth.moveTo(kx * mm, ky * mm); pth.lineTo((kx + 3) * mm, ky * mm); pth.lineTo(kx * mm, (ky + 3) * mm); pth.close()
    c.drawPath(pth, fill=1, stroke=0)
    # крепёжные отверстия
    for hx, hy in D.HOLES:
        cx, cy = P(hx, hy)
        p.circle(cx, cy, K * D.HOLE_D / 2, S)
        p.line(cx - 4, cy, cx + 4, cy, 0.13, dash=(3, 1, 0.5, 1))
        p.line(cx, cy - 4, cx, cy + 4, 0.13, dash=(3, 1, 0.5, 1))
    # надписи зон
    zx, zy = P(sh["x"] + sh["l"] / 2, sh["y"] + sh["w"] + 0.15)
    p.text(zx, zy - 5, "", 2.5, "c")

    # ---------------------------------------------------- размеры
    x_l, y_b = P(0, 0)
    x_r, y_t = P(D.BOARD_L, D.BOARD_W)
    dim_h(p, x_l, x_r, y_t, y_t + 20, "32±0,1")
    dim_v(p, y_b, y_t, x_l, x_l - 18, "22±0,1")
    # шаг контактов
    xa, _ = P(D.PADS_X0, 0)
    xb, _ = P(D.PADS_X0 + 9 * D.PAD_PITCH, 0)
    dim_h(p, xa, xb, y_b, y_b - 14, "9×2,54=22,86")
    dim_h(p, x_l, xa, y_b, y_b - 24, "4,57*", outside=True)
    xa2, _ = P(D.PADS_X0 + D.PAD_PITCH, 0)
    dim_h(p, xa, xa2, y_t, y_t + 10, "2,54", outside=True)
    # отверстия крепёжные
    hx, hy = P(*D.HOLES[1])
    dim_v(p, hy, y_t, x_r, x_r + 10, "1,6", outside=True)
    dim_h(p, hx, x_r, y_b, y_b - 34, "1,6", outside=True)
    leader(p, hx + K * D.HOLE_D / 2 * 0.7, hy + K * D.HOLE_D / 2 * 0.7, hx + 22, hy + 22, "⌀1,1 (2 отв.)")
    # контактная площадка
    n1 = D.pad_positions()[6]
    px, py = P(n1[1] + D.PAD_W / 2, 0.4)
    leader(p, px - 0.5, py, px + 10, y_b - 42, "1,2×1,6; ⌀0,8 (20 полуотв.)")
    # зона экрана
    sxl, syb = P(sh["x"], sh["y"])
    sxr, syt = P(sh["x"] + sh["l"], sh["y"] + sh["w"])
    dim_v(p, y_b, syb, x_r, x_r + 20, "2,6", outside=True)
    p.line(sxr, syb, x_r + 22, syb, 0.13)
    leader(p, sxl + 10, syt - 0.5, sxl + 30, y_t + 32, "Зона установки экрана РЧ-тракта 13,6×16,8")

    # вид сбоку (М 4:1)
    ys = Y0 - 72
    p.rect(x_l, ys, K * D.BOARD_L, K * D.BOARD_T, S)
    dim_v(p, ys, ys + K * D.BOARD_T, x_l, x_l - 10, "0,6±0,06", outside=True)
    p.text((x_l + x_r) / 2, ys + 6, "Вид А (без элементов)", 3.5, "c")
    p.text((x_l + x_r) / 2, Y0 + K * D.BOARD_W + 32, "", 3.5, "c")

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
    table(p, 340, 284, [18, 26, 26], [
        ("L1", "Сигнальный, РЧ", "0,035"),
        ("—", "Препрег", "0,10"),
        ("L2", "Земля", "0,035"),
        ("—", "Ядро", "0,23"),
        ("L3", "Питание/сигн.", "0,035"),
        ("—", "Препрег", "0,10"),
        ("L4", "Сигнальный", "0,035"),
        ("", "Итого", "0,6±0,06"),
    ], ["Слой", "Назначение", "Толщина, мм"], row_h=5.0, head_h=7, title="Таблица 2 — Структура платы")
    table(p, 340, 226, [16, 22, 32], [
        ("⌀0,8", "20", "Металлизир., полуотв."),
        ("⌀1,1", "2", "Без металлизации"),
        ("⌀0,2", "по РКД", "Переходные, металл."),
    ], ["Диаметр", "Кол-во", "Примечание"], row_h=5.0, head_h=7, title="Таблица 3 — Отверстия")

    # ---------------------------------------------------- технические требования
    items = [
        "* Размеры для справок.",
        "Плата должна соответствовать ГОСТ Р 55693-2013, группа жёсткости 2. Основные параметры конструкции — "
        "по ГОСТ Р 53429-2009, класс точности 5.",
        "Материал: стеклотекстолит с Tg ≥ 170 °C; допускается гибридная структура с СВЧ-материалом "
        "(εr = 3,4…3,7, tgδ ≤ 0,004) между слоями L1–L2. Выбор — на стадии рабочего проекта.",
        "Волновое сопротивление РЧ-линий (копланарная линия с землёй, слой L1 над L2) — 50 Ом ±10 %.",
        "Покрытие контактных площадок и полуотверстий — иммерсионное золото по никелю (ENIG).",
        "Защитная паяльная маска — с обеих сторон, кроме контактных площадок; маркировка — белой краской.",
        "Переходные отверстия по контуру зоны экрана — с шагом не более 1,0 мм (не более λ/20 на 1,66 ГГц).",
        "Рисунок проводников, расположение переходных отверстий и посадочных мест элементов — по РКД; "
        "на чертеже посадочные места и обозначения элементов показаны условно для оценки компоновки.",
        "Радиус скругления углов платы — 1 мм. Неуказанные предельные отклонения размеров — ±0,1 мм.",
        "Маркировать обозначение платы и номер партии на стороне L4 шрифтом высотой 1 мм.",
    ]
    gost.tech_requirements(p, 232, 160, 180, items, h=2.5)

    gost.stamp_form1(p, W, "Плата печатная", "", code=CODE, lit="Т", mass="0,9", scale="4:1",
                     sheet="", sheets="1",
                     material="Стеклотекстолит, Tg ≥ 170 °C\nh = 0,6 мм, 4 слоя")
    c.showPage()
    c.save()


if __name__ == "__main__":
    import sys
    gost.register_fonts()
    build(sys.argv[1] if len(sys.argv) > 1 else "pcb.pdf")
