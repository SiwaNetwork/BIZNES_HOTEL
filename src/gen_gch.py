"""ТЕНШ.464512.001 ГЧ — Габаритный чертёж модуля и антенны WA1 (ГОСТ 2.109-73, ГОСТ 2.102-2013), А3, М 2:1."""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import design as D
import gost
from drawing import LW_DIM, dim_h, dim_v, leader, table
from gost import Pen, S, S3

K = 2.0
CODE = gost.CODE + " ГЧ"
GREY = colors.Color(0.9, 0.9, 0.9)
H_MODULE = D.BOARD_T + 1.9          # по конденсаторам C1, C2
H_ANT = D.ANT_PCB_T + D.ANT_T
LW_THIN = 0.25
DASHDOT = (10, 3, 0.5, 3)           # штрихпунктирная тонкая (ГОСТ 2.303)


def g(x):
    return f"{x:.1f}".replace(".", ",")


def build(path, render_png):
    W, H = gost.A3L
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{CODE} — Габаритный чертёж")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    gost.frame(p, W, H, drawing=True, code=CODE)
    c.drawImage(str(render_png), 262 * mm, 160 * mm, width=148 * mm, height=128 * mm,
                preserveAspectRatio=True, anchor="c", mask="auto")
    p.text(336, 156, "Изометрия (справочно, без масштаба). Кабель ⌀1,13 мм, длина 60 мм", 2.5, "c")

    # ---------------- модуль, вид сверху
    mx, my = 50.0, 204.0
    xr, yt = mx + K * D.BOARD_L, my + K * D.BOARD_W
    c.setLineWidth(S * mm)
    c.roundRect(mx * mm, my * mm, K * D.BOARD_L * mm, K * D.BOARD_W * mm, K * D.CORNER_R * mm)
    sh = D.SHIELD
    p.rect(mx + K * sh["x"], my + K * sh["y"], K * sh["l"], K * sh["w"], LW_THIN, fill=GREY)
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        if sh["x"] < x < sh["x"] + sh["l"] and sh["y"] < y < sh["y"] + sh["w"]:
            continue
        p.rect(mx + K * (x - l / 2), my + K * (y - w / 2), K * l, K * w, LW_THIN)
    for n, x, y, side in D.pad_positions():
        yc = 0 if side == "bottom" else D.BOARD_W - D.PAD_L
        p.rect(mx + K * (x - D.PAD_W / 2), my + K * yc, K * D.PAD_W, K * D.PAD_L, LW_THIN)
        if n in (1, 10, 11, 20):
            ty = my + K * D.PAD_L + 0.8 if side == "bottom" else yt - K * D.PAD_L - 3.3
            p.text(mx + K * x, ty, str(n), 2.5, "c")
    kx, ky = mx + K * (D.PADS_X0 - 1.75), my + K * 2.0           # ключ — контакт 1
    pth = c.beginPath()
    pth.moveTo(kx * mm, ky * mm); pth.lineTo((kx + 2) * mm, ky * mm); pth.lineTo(kx * mm, (ky + 2) * mm); pth.close()
    c.drawPath(pth, fill=1, stroke=0)
    for hx, hy in D.HOLES:                                        # крепёжные отверстия ⌀1,1
        cx, cy = mx + K * hx, my + K * hy
        r = K * D.HOLE_D / 2
        p.circle(cx, cy, r, S)
        p.line(cx - r - 1.5, cy, cx + r + 1.5, cy, LW_THIN)
        p.line(cx, cy - r - 1.5, cx, cy + r + 1.5, LW_THIN)
    xw = next(cc for cc in D.COMPONENTS if cc[0] == "XW1")
    p.circle(mx + K * xw[1], my + K * xw[2], K * 1.0, LW_THIN)
    p.text((mx + xr) / 2, yt + 24, "Модуль (без кабеля)", 3.5, "c")
    # габаритные, установочные и присоединительные размеры
    dim_h(p, mx, xr, yt, yt + 12, "32±0,1")
    dim_v(p, my, yt, mx, mx - 20, "22±0,1")
    xa, xb = mx + K * D.PADS_X0, mx + K * (D.PADS_X0 + 9 * D.PAD_PITCH)
    dim_h(p, xa, xb, my, my - 10, "9×2,54=22,86")
    dim_h(p, mx, xa, my, my - 19, "4,57±0,1", outside=True)
    h1x, h1y = mx + K * D.HOLES[0][0], my + K * D.HOLES[0][1]
    dim_h(p, mx, h1x, my, my - 28, "1,6±0,1", outside=True)
    p.line(h1x, h1y - 3.0, h1x, my - 0.8, LW_DIM)
    dim_v(p, my, h1y, mx, mx - 9, "1,6±0,1", outside=True)
    p.line(h1x - 3.0, h1y, mx - 0.8, h1y, LW_DIM)
    leader(p, xr - K * 1.6 - 0.8, yt - K * 1.6 - 0.8, xr + 6, yt + 2, "⌀1,1 (2 отв.)")
    leader(p, mx + K * 16, my + K * 17, xr + 6, my + 36, "Экран РЧ-тракта")
    leader(p, mx + K * xw[1], my + K * xw[2], xr + 6, my + 26, "XW1 (центр 2,3; 11,0)")
    leader(p, mx + K * 27.43, my + K * 0.8, xr + 6, my + 14, "X1 — 1,2×1,6, 20 конт.")

    # модуль, вид сбоку
    sy = my - 62
    p.rect(mx, sy, K * D.BOARD_L, K * D.BOARD_T, S)
    p.rect(mx + K * sh["x"], sy + K * D.BOARD_T, K * sh["l"], K * sh["h"], S)
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        if name in ("C1", "XW1", "DD1", "L1"):
            p.rect(mx + K * (x - l / 2), sy + K * D.BOARD_T, K * l, K * h, S)
    c1 = next(cc for cc in D.COMPONENTS if cc[0] == "C1")
    dim_v(p, sy, sy + K * H_MODULE, xr, xr + 12, "2,5 max", outside=True,
          x_obj2=mx + K * (c1[1] + c1[3] / 2))
    dim_v(p, sy, sy + K * D.BOARD_T, mx, mx - 9, "0,6", outside=True)

    # ---------------- антенна, вид сверху
    ax, ay = 212.0, 228.0       # центр
    L, PCB = D.ANT_L, D.ANT_PCB_L
    c.setLineWidth(S * mm)
    c.roundRect((ax - K * PCB / 2) * mm, (ay - K * PCB / 2) * mm, K * PCB * mm, K * PCB * mm, K * 1.5 * mm)
    p.rect(ax - K * L / 2, ay - K * L / 2, K * L, K * L, S, fill=colors.Color(0.96, 0.95, 0.92))
    p.rect(ax - K * D.ANT_PATCH / 2, ay - K * D.ANT_PATCH / 2, K * D.ANT_PATCH, K * D.ANT_PATCH, LW_THIN, fill=GREY)
    for fx, fy in ((-3.6, 0), (0, -3.6)):
        p.circle(ax + K * fx, ay + K * fy, K * 0.7, LW_THIN)
    p.line(ax - K * PCB / 2 - 5, ay, ax + K * PCB / 2 + 5, ay, LW_THIN, dash=DASHDOT)
    p.line(ax, ay - K * PCB / 2 - 5, ax, ay + K * PCB / 2 + 5, LW_THIN, dash=DASHDOT)
    p.text(ax, ay + K * PCB / 2 + 24, "Антенна WA1 (базовый вариант)", 3.5, "c")
    dim_h(p, ax - K * PCB / 2, ax + K * PCB / 2, ay + K * PCB / 2, ay + K * PCB / 2 + 12, "30")
    dim_v(p, ay - K * L / 2, ay + K * L / 2, ax + K * L / 2, ax + K * PCB / 2 + 10, "25")
    leader(p, ax - K * 5, ay - K * 5, ax - K * PCB / 2 - 6, ay - K * PCB / 2 - 8, "Излучатель (RHCP)")
    # антенна, вид сбоку
    asy = ay - K * PCB / 2 - 40
    p.rect(ax - K * PCB / 2, asy, K * PCB, K * D.ANT_PCB_T, S)
    p.rect(ax - K * L / 2, asy + K * D.ANT_PCB_T, K * L, K * D.ANT_T, S)
    p.rect(ax - K * 10.5 - K * 1.5, asy - K * 1.25, K * 3, K * 1.25, S)
    dim_v(p, asy, asy + K * H_ANT, ax + K * PCB / 2, ax + K * PCB / 2 + 10, "4,8", outside=True,
          x_obj2=ax + K * L / 2)
    dim_v(p, asy - K * 1.25, asy, ax - K * 9, ax - K * PCB / 2 - 9, "1,3", outside=True)
    p.text(ax + 8, asy - 7, "Разъём антенны WA1 — снизу", 2.5, "c")

    # ---------------- таблица масс
    rows = [
        ("Модуль (плата, элементы, экран)", g(D.MASS_MODULE)),
        ("Антенна WA1 25×25×4 на плате 30×30", g(D.MASS_ANTENNA)),
        ("Кабель коаксиальный с разъёмами", g(D.MASS_CABLE)),
        ("Крепление, клей", g(D.MASS_MOUNT)),
        ("Итого комплект связи", g(D.MASS_KIT)),
    ]
    table(p, 30, 112, [70, 22], rows, ["Составная часть", "Масса, г"], row_h=5.5, head_h=7,
          title="Таблица 1 — Масса (расчётная оценка)")

    items = [
        "Чертёж для оценки массогабаритных характеристик и изготовления массогабаритного макета "
        "(печать по электронной модели с догрузкой до расчётной массы).",
        f"Масса модуля — {g(D.MASS_MODULE)} г; масса комплекта связи с антенной WA1 — {g(D.MASS_KIT)} г "
        "(таблица 1). Размеры и масса — расчётные, уточняются при разработке РКД.",
        "Модуль устанавливается пайкой краевыми контактами X1 на плату полётного контроллера или на "
        "переходную плату; допускается крепление винтами М1 через 2 отверстия ⌀1,1, расположенные "
        "симметрично относительно центра модуля.",
        "Антенна устанавливается на спине носителя излучателем вверх; металлизация основания "
        "антенны обращена к телу носителя.",
        "Длина кабеля между XW1 модуля и антенной — не более 80 мм (потери не более 0,3 дБ).",
        "Облегчённый вариант антенны (керамическая спиральная ⌀12×30 мм, масса 5…7 г) — по результатам "
        "макетирования, см. ТЕНШ.464512.001 ПЗ, подраздел 5.4.",
        "Неуказанные предельные отклонения размеров — ±0,2 мм.",
    ]
    gost.tech_requirements(p, 232, 140, 180, items, h=2.5)

    gost.stamp_form1(p, W, gost.PRODUCT, "Габаритный чертёж", code=CODE, lit="Т",
                     mass=g(D.MASS_MODULE) + " г", scale="2:1", sheet="", sheets="1")
    c.showPage()
    c.save()


if __name__ == "__main__":
    import sys
    gost.register_fonts()
    build(sys.argv[1] if len(sys.argv) > 1 else "gch.pdf", gost.ROOT / "cad" / "renders" / "assembly_iso.png")
