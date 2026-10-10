"""ТЕНШ.464512.001 ГЧ — Габаритный чертёж модуля и антенны WA1 (ГОСТ 2.109-73, ГОСТ 2.102-2013), А3, М 2:1."""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import design as D
import gost
from drawing import dim_h, dim_v, leader, table
from gost import Pen, S, S3

K = 2.0
CODE = gost.CODE + " ГЧ"
GREY = colors.Color(0.9, 0.9, 0.9)
H_MODULE = D.BOARD_T + 1.9          # по конденсаторам C1, C2
H_ANT = D.ANT_PCB_T + D.ANT_T


def build(path, render_png):
    W, H = gost.A3L
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{CODE} — Габаритный чертёж")
    p = Pen(c)
    gost.frame(p, W, H, drawing=True, code=CODE)
    c.drawImage(str(render_png), 252 * mm, 150 * mm, width=158 * mm, height=140 * mm,
                preserveAspectRatio=True, anchor="c", mask="auto")

    # ---------------- модуль, вид сверху
    mx, my = 48.0, 196.0
    c.setLineWidth(S * mm)
    c.roundRect(mx * mm, my * mm, K * D.BOARD_L * mm, K * D.BOARD_W * mm, K * D.CORNER_R * mm)
    sh = D.SHIELD
    p.rect(mx + K * sh["x"], my + K * sh["y"], K * sh["l"], K * sh["w"], S3, fill=GREY)
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        if sh["x"] < x < sh["x"] + sh["l"] and sh["y"] < y < sh["y"] + sh["w"]:
            continue
        p.rect(mx + K * (x - l / 2), my + K * (y - w / 2), K * l, K * w, S3)
    for n, x, y, side in D.pad_positions():
        yc = 0 if side == "bottom" else D.BOARD_W - D.PAD_L
        p.rect(mx + K * (x - D.PAD_W / 2), my + K * yc, K * D.PAD_W, K * D.PAD_L, S3)
    xw = next(cc for cc in D.COMPONENTS if cc[0] == "XW1")
    p.circle(mx + K * xw[1], my + K * xw[2], K * 1.0, S3)
    p.text(mx + K * D.BOARD_L / 2, my + K * D.BOARD_W + 22, "Модуль (без кабеля)", 3.5, "c")
    dim_h(p, mx, mx + K * D.BOARD_L, my + K * D.BOARD_W, my + K * D.BOARD_W + 12, "32")
    dim_v(p, my, my + K * D.BOARD_W, mx, mx - 10, "22")
    leader(p, mx + K * xw[1], my + K * xw[2], mx + 10, my - 34, "XW1 — подключение WA1")
    leader(p, mx + K * 10, my + K * 0.5, mx + 26, my - 22, "X1 — краевые контакты 1…20")
    leader(p, mx + K * 10, my + K * 12, mx + 50, my - 10, "Экран РЧ-тракта")

    # модуль, вид сбоку
    sy = my - 48
    p.rect(mx, sy, K * D.BOARD_L, K * D.BOARD_T, S)
    p.rect(mx + K * sh["x"], sy + K * D.BOARD_T, K * sh["l"], K * sh["h"], S)
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        if name in ("C1", "XW1", "DD1", "L1"):
            p.rect(mx + K * (x - l / 2), sy + K * D.BOARD_T, K * l, K * h, S)
    dim_v(p, sy, sy + K * H_MODULE, mx + K * D.BOARD_L, mx + K * D.BOARD_L + 12, "2,5 max", outside=True)
    dim_v(p, sy, sy + K * D.BOARD_T, mx, mx - 8, "0,6", outside=True)

    # ---------------- антенна, вид сверху
    ax, ay = 186.0, 230.0       # центр
    L, PCB = D.ANT_L, D.ANT_PCB_L
    c.setLineWidth(S * mm)
    c.roundRect((ax - K * PCB / 2) * mm, (ay - K * PCB / 2) * mm, K * PCB * mm, K * PCB * mm, K * 1.5 * mm)
    p.rect(ax - K * L / 2, ay - K * L / 2, K * L, K * L, S, fill=colors.Color(0.96, 0.95, 0.92))
    p.rect(ax - K * D.ANT_PATCH / 2, ay - K * D.ANT_PATCH / 2, K * D.ANT_PATCH, K * D.ANT_PATCH, S3, fill=GREY)
    for fx, fy in ((-3.6, 0), (0, -3.6)):
        p.circle(ax + K * fx, ay + K * fy, K * 0.7, S3)
    p.line(ax - K * PCB / 2 - 4, ay, ax + K * PCB / 2 + 4, ay, 0.13, dash=(6, 1.5, 1, 1.5))
    p.line(ax, ay - K * PCB / 2 - 4, ax, ay + K * PCB / 2 + 4, 0.13, dash=(6, 1.5, 1, 1.5))
    p.text(ax, ay + K * PCB / 2 + 22, "Антенна WA1 (базовый вариант)", 3.5, "c")
    dim_h(p, ax - K * PCB / 2, ax + K * PCB / 2, ay + K * PCB / 2, ay + K * PCB / 2 + 12, "30")
    dim_v(p, ay - K * L / 2, ay + K * L / 2, ax + K * PCB / 2, ax + K * PCB / 2 + 10, "25")
    leader(p, ax + K * 6, ay + K * 6, ax + 26, ay + 40, "Излучатель (RHCP)")
    # антенна, вид сбоку
    asy = ay - K * PCB / 2 - 40
    p.rect(ax - K * PCB / 2, asy, K * PCB, K * D.ANT_PCB_T, S)
    p.rect(ax - K * L / 2, asy + K * D.ANT_PCB_T, K * L, K * D.ANT_T, S)
    p.rect(ax - K * 10.5 - K * 1.5, asy - K * 1.25, K * 3, K * 1.25, S)
    dim_v(p, asy, asy + K * H_ANT, ax + K * PCB / 2, ax + K * PCB / 2 + 10, "4,8", outside=True)
    dim_v(p, asy - K * 1.25, asy, ax - K * PCB / 2, ax - K * PCB / 2 - 8, "1,3", outside=True)
    p.text(ax, asy - 12, "Разъём XW1 антенны — снизу", 2.5, "c")

    # ---------------- 3D-вид
    p.text(328, 152, "Изометрия (3D-модель cad/assembly.step). Кабель ⌀1,13 мм, 60 мм", 2.5, "c")

    # ---------------- таблица масс
    rows = [
        ("Модуль (плата, элементы, экран)", f"{D.MASS_MODULE:.1f}".replace(".", ",")),
        ("Антенна WA1 25×25×4 на плате 30×30", f"{D.MASS_ANTENNA:.1f}".replace(".", ",")),
        ("Кабель коаксиальный с разъёмами", f"{D.MASS_CABLE:.1f}".replace(".", ",")),
        ("Крепление, клей", f"{D.MASS_MOUNT:.1f}".replace(".", ",")),
        ("Итого", f"{D.MASS_MODULE + D.MASS_ANTENNA + D.MASS_CABLE + D.MASS_MOUNT:.1f}".replace(".", ",")),
    ]
    table(p, 30, 112, [70, 22], rows, ["Составная часть", "Масса, г"], row_h=5.5, head_h=7,
          title="Таблица 1 — Масса (расчётная оценка)")

    items = [
        "Чертёж для оценки массогабаритных характеристик и изготовления массогабаритного макета "
        "(печать по cad/mockup_module.stl и cad/mockup_antenna.stl с догрузкой до расчётной массы).",
        "Размеры и масса — расчётные, уточняются на стадии рабочего проекта.",
        "Модуль устанавливается пайкой краевыми контактами X1 на плату полётного контроллера "
        "или на переходную плату; допускается крепление винтами М1 через 2 отверстия ⌀1,1.",
        "Антенна устанавливается на спине носителя излучателем вверх; металлизация основания "
        "антенны обращена к телу носителя (экранирует тело от излучения).",
        "Длина кабеля между XW1 модуля и антенной — не более 80 мм (потери не более 0,3 дБ).",
        "Вариант антенны (керамическая спиральная ⌀12×30 мм, масса 5…7 г) — по результатам "
        "макетирования, см. ТЕНШ.464512.001 ПЗ, раздел 5.",
    ]
    gost.tech_requirements(p, 232, 140, 180, items, h=2.5)

    total = D.MASS_MODULE + D.MASS_ANTENNA + D.MASS_CABLE + D.MASS_MOUNT
    gost.stamp_form1(p, W, gost.PRODUCT, "Габаритный чертёж", code=CODE, lit="Т",
                     mass=f"{total:.1f}".replace(".", ",") + " г", scale="2:1", sheet="", sheets="1")
    c.showPage()
    c.save()


if __name__ == "__main__":
    import sys
    gost.register_fonts()
    build(sys.argv[1] if len(sys.argv) > 1 else "gch.pdf", gost.ROOT / "cad" / "renders" / "assembly_iso.png")
