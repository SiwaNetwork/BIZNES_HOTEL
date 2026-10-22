"""Документы варианта на модеме Iridium 9603N (ТЕНШ.464512.002): 3D-модель, габаритный чертёж,
чертёж платы ТЕНШ.758726.002 и пояснительная записка (справка). Геометрия и состав — из hw/iridium.py.

  python3 src/gen_iri.py            (3D-рендер требует дисплея: xvfb-run -a python3 src/gen_iri.py)
"""
import re
import subprocess
import sys

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import gost
from drawing import LW_DIM, dim_h, dim_v, leader, table
from gost import Pen, S
from hw import iridium as I

ROOT = gost.ROOT
DOCS = ROOT / "docs"
CAD = ROOT / "cad"
KIPRJ = ROOT / "kicad" / "TENSH.464512.002"
CODE = I.CODE
PCB = I.PCB_CODE
W_B, H_B = I.BOARD
T_B = I.THICK
GAP = I.MODULE_GAP                      # высота стоек под модемом
MODEM = dict(l=29.6, w=31.5, h=8.1, m=11.4)
H_TOTAL = T_B + GAP + MODEM["h"]
LW_THIN = 0.25
GREY = colors.Color(0.9, 0.9, 0.9)

# масса, г: плата FR-4 1,86 г/см³; стойки латунные М2×6 с винтами
MASS_BOARD = round(W_B * H_B * T_B * 1.86e-3, 2)
MASS_STANDOFFS = 0.6
ANT_MASS = (3.0, 10.0)                  # Maxtena M1621HCT-P-UFL (по данным изготовителя, не подтверждено) — патч 25×25


def g(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


def masses():
    d = I.design()
    parts = sum(p.mass_g for p in d.parts.values())
    carrier = MASS_BOARD + parts + MASS_STANDOFFS + 0.2       # + припой, лак
    rows = [("Плата печатная 32×45×0,6 мм, 2 слоя", MASS_BOARD),
            ("Элементы платы (ионисторы, розетка, ИС и др.)", round(parts, 2)),
            ("Стойки М2×6 и винты (2 комплекта)", MASS_STANDOFFS),
            ("Припой, лак", 0.2),
            ("Модем Iridium 9603N", MODEM["m"])]
    module = carrier + MODEM["m"]
    return rows, round(carrier, 1), round(module, 1)


# ================================================================ 3D-модель
def parts3d(with_modem=True):
    import cadquery as cq
    d = I.design()
    b = cq.Workplane("XY").box(W_B, H_B, T_B, centered=False).edges("|Z").fillet(I.CORNER_R)
    pads = [(x, 0.0) for _, x in I.pads_xy()]
    b = b.faces(">Z").workplane(origin=(0, 0, T_B)).pushPoints(pads).hole(0.8)
    b = b.faces(">Z").workplane(origin=(0, 0, T_B)).pushPoints(I.HOLES).hole(2.2)
    out = [("board", b, "board")]
    for i, (x, _) in enumerate(pads):
        p = (cq.Workplane("XY").box(1.2, 1.3, 0.04).translate((x, 0.95, T_B + 0.02))
             .cut(cq.Workplane("XY").cylinder(1, 0.4).translate((x, 0, T_B))))
        out.append((f"pad{i + 1}", p, "pad"))
    for ref, p in d.parts.items():
        if p.kind in ("PAD", "MH"):
            continue
        x, y, rot = p.pos
        l, w = p.body
        if rot % 180:
            l, w = w, l
        if ref in ("C1", "C2"):         # ионисторы ⌀8 уложены на плату вдоль X
            s = cq.Workplane("YZ").circle(4.0).extrude(l).translate((x - l / 2, y, T_B + 4.0))
            out.append((ref, s, "tant"))
            continue
        kind = "metal" if p.kind == "CONN" else ("passive" if p.kind in ("R", "C", "L") else "ic")
        s = cq.Workplane("XY").box(l, w, p.height, centered=(True, True, False)).translate((x, y, T_B))
        out.append((ref, s, kind))
    for i, (x, y) in enumerate(I.HOLES, 1):
        out.append((f"standoff{i}", cq.Workplane("XY").polygon(6, 4.0).extrude(GAP).translate((x, y, T_B)), "metal"))
    if with_modem:
        mx, my, mw, mh = I.MODULE_BOX
        m = cq.Workplane("XY").box(mw, mh, MODEM["h"], centered=False).translate((mx, my, T_B + GAP))
        m = m.edges("|Z").fillet(0.8)
        out.append(("modem_9603N", m, "shield"))
        u = cq.Workplane("XY").circle(1.0).circle(0.6).extrude(1.2).translate((mx + mw - 5.0, my + mh - 5.0,
                                                                                 T_B + GAP + MODEM["h"]))
        out.append(("modem_ufl", u, "gold"))
    return out


def make_3d():
    import model3d as M3
    CAD.mkdir(exist_ok=True)
    (CAD / "renders").mkdir(exist_ok=True)
    full, bare = parts3d(True), parts3d(False)
    M3.to_assembly(full, "module_iridium").save(str(CAD / "module_iridium.step"))
    M3.render(full, CAD / "renders" / "iridium_iso.png", zoom=1.2)
    M3.render(bare, CAD / "renders" / "iridium_carrier.png", zoom=1.25)


# ================================================================ габаритный чертёж
def build_gch(path):
    W, H = gost.A3L
    K = 2.0
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{CODE} ГЧ — Габаритный чертёж")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    code = CODE + " ГЧ"
    gost.frame(p, W, H, drawing=True, code=code)
    render = CAD / "renders" / "iridium_iso.png"
    if render.exists():
        c.drawImage(str(render), 262 * mm, 165 * mm, width=148 * mm, height=118 * mm,
                    preserveAspectRatio=True, anchor="c", mask="auto")
        p.text(336, 161, "Изометрия (справочно, без масштаба)", 2.5, "c")
    # ---------------- вид сверху
    mx, my = 50.0, 160.0
    xr, yt = mx + K * W_B, my + K * H_B
    c.setLineWidth(S * mm)
    c.roundRect(mx * mm, my * mm, K * W_B * mm, K * H_B * mm, K * I.CORNER_R * mm)
    bx, by, bw, bh = I.MODULE_BOX
    p.rect(mx + K * bx, my + K * by, K * bw, K * bh, S, fill=GREY)
    p.text(mx + K * (bx + bw / 2), my + K * (by + bh / 2), "Модем Iridium 9603N", 3.5, "c")
    d = I.design()
    for ref in ("C1", "C2"):
        q = d.parts[ref]
        l, w = q.body
        p.rect(mx + K * (q.pos[0] - l / 2), my + K * (q.pos[1] - w / 2), K * l, K * w, S)
        p.text(mx + K * q.pos[0], my + K * q.pos[1] - 1.2, ref, 3.5, "c")
    for n, x in I.pads_xy():
        p.rect(mx + K * (x - 0.6), my, K * 1.2, K * 1.6, LW_THIN, fill=colors.Color(0.78, 0.78, 0.78))
        if n in (1, len(I.HOST)):
            p.text(mx + K * x, my + K * 1.6 + 1.0, str(n), 2.5, "c")
    for hx, hy in I.HOLES:
        p.circle(mx + K * hx, my + K * hy, K * 1.75, LW_THIN)     # стойка (шестигранник 4 мм — упрощённо)
    ux, uy = mx + K * (bx + bw - 5.0), my + K * (by + bh - 5.0)
    p.circle(ux, uy, K * 1.0, LW_THIN)
    leader(p, ux, uy, xr + 8, yt + 8, "Розетка U.FL модема (антенна)")
    dim_h(p, mx, xr, yt, yt + 12, "32±0,1")
    dim_v(p, my, yt, mx, mx - 18, "45±0,1")
    x1, x12 = I.pads_xy()[0][1], I.pads_xy()[-1][1]
    dim_h(p, mx + K * x1, mx + K * x12, my, my - 10, f"11×2,54={g(11 * 2.54, 2)}")
    dim_h(p, mx, mx + K * x1, my, my - 19, g(x1, 2) + "±0,1", outside=True)
    leader(p, mx + K * x12, my + K * 0.8, xr + 30, my + 14, "X1 — 1,2×1,6, 12 конт.")
    # ---------------- вид сбоку
    sy = my - 62
    p.rect(mx, sy, K * W_B, K * T_B, S)
    for ref in ("C1", "C2"):
        q = d.parts[ref]
        l = q.body[0]
        p.rect(mx + K * (q.pos[0] - l / 2), sy + K * T_B, K * l, K * 8.0, S)
    p.rect(mx + K * bx, sy + K * (T_B + GAP), K * bw, K * MODEM["h"], S, fill=GREY)
    for hx, _ in I.HOLES:
        p.rect(mx + K * (hx - 2.0), sy + K * T_B, K * 4.0, K * GAP, LW_THIN)
    dim_v(p, sy, sy + K * H_TOTAL, xr, xr + 14, g(H_TOTAL) + " max", outside=True,
          x_obj2=mx + K * (bx + bw))
    dim_v(p, sy + K * T_B, sy + K * (T_B + GAP), mx, mx - 10, g(GAP, 0), outside=True)
    p.text(mx + K * W_B / 2, sy - 8, "Вид спереди (со стороны контактов X1)", 3.5, "c")
    # ---------------- таблица масс и технические требования
    rows, carrier, module = masses()
    trows = [(n, g(m, 2 if m < 1 else 1)) for n, m in rows] + [("Итого модуль", g(module)),
                                                                ("Антенна (в зависимости от типа)",
                                                                 f"{g(ANT_MASS[0], 0)}…{g(ANT_MASS[1], 0)}")]
    table(p, 30, 76, [80, 22], trows, ["Составная часть", "Масса, г"], row_h=5.5, head_h=7,
          title="Таблица 1 — Масса (расчётная оценка)")
    items = [
        f"Масса модуля без антенны — {g(module)} г, с антенной — {g(module + ANT_MASS[0])}…"
        f"{g(module + ANT_MASS[1])} г (таблица 1). Размеры и масса — расчётные.",
        "Модуль устанавливается пайкой краевыми контактами X1 на плату полётного контроллера или на переходную "
        "плату. Антенна подключается кабелем U.FL непосредственно к модему и размещается на спине носителя "
        "излучателем к зениту.",
        f"Модем крепится к плате {PCB} двумя стойками М2×{g(GAP, 0)} и соединяется с ней через розетку X2 "
        "Samtec SS4-10.",
        "Ионисторы C1, C2 уложены на плату и фиксируются клеем-герметиком.",
        "Неуказанные предельные отклонения размеров — ±0,2 мм.",
    ]
    gost.tech_requirements(p, 232, 150, 180, items, h=2.5)
    gost.stamp_form1(p, W, I.PRODUCT, "Габаритный чертёж", code=code, lit="Т", mass=g(module) + " г",
                     scale="2:1", sheet="", sheets="1")
    c.showPage()
    c.save()


# ================================================================ чертёж платы
def _layer_png(layer, name):
    """Растр слоя платы KiCad (вид сверху), обрезанный по контуру платы."""
    from PIL import Image, ImageOps
    tmp = ROOT / "build"
    tmp.mkdir(exist_ok=True)
    pdf = tmp / f"iri_{name}.pdf"
    subprocess.run(["kicad-cli", "pcb", "export", "pdf", "--layers", f"{layer},Edge.Cuts", "--black-and-white",
                    "--exclude-refdes", "--exclude-value", "-o", str(pdf), str(KIPRJ / "TENSH.464512.002.kicad_pcb")]
                   + (["--mirror"] if layer.startswith("B.") else []), check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "600", "-png", "-singlefile", str(pdf), str(tmp / f"iri_{name}")], check=True)
    im = Image.open(tmp / f"iri_{name}.png").convert("RGB")
    im = im.crop(ImageOps.invert(im).getbbox())
    out = tmp / f"iri_{name}_c.png"
    im.save(out)
    return out


def build_pcb(path):
    W, H = gost.A3L
    K = 2.0
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(f"{PCB} — Плата печатная")
    c.setAuthor("ТЕНШ")
    p = Pen(c)
    gost.frame(p, W, H, drawing=True, code=PCB, first_use=CODE)
    mx, my = 48.0, 160.0
    xr, yt = mx + K * W_B, my + K * H_B
    c.setLineWidth(S * mm)
    c.roundRect(mx * mm, my * mm, K * W_B * mm, K * H_B * mm, K * I.CORNER_R * mm)
    for n, x in I.pads_xy():
        p.rect(mx + K * (x - 0.6), my + K * 0.3, K * 1.2, K * 1.3, LW_THIN, fill=colors.Color(0.78, 0.78, 0.78))
        c.saveState(); c.setFillColorRGB(1, 1, 1); c.setLineWidth(LW_THIN * mm)
        c.circle((mx + K * x) * mm, my * mm, K * 0.4 * mm, stroke=1, fill=1); c.restoreState()
        p.text(mx + K * x, my + K * 1.6 + 1.0, str(n), 2.5, "c")
    for hx, hy in I.HOLES:
        cx, cy = mx + K * hx, my + K * hy
        r = K * 1.1
        p.circle(cx, cy, r, S)
        p.line(cx - r - 1.5, cy, cx + r + 1.5, cy, LW_THIN)
        p.line(cx, cy - r - 1.5, cx, cy + r + 1.5, LW_THIN)
    sx, sy = I.SOCK
    p.rect(mx + K * (sx - 2.6), my + K * (sy - 3.35), K * 5.2, K * 6.7, LW_THIN, dash=(4, 1.5))
    leader(p, mx + K * (sx + 2.6), my + K * sy, xr + 2, yt - 6, "Зона розетки X2", h=2.5)
    dim_h(p, mx, xr, yt, yt + 12, "32±0,1")
    dim_v(p, my, yt, mx, mx - 18, "45±0,1")
    x1, x12 = I.pads_xy()[0][1], I.pads_xy()[-1][1]
    dim_h(p, mx + K * x1, mx + K * x12, my, my - 10, f"11×2,54={g(11 * 2.54, 2)}")
    dim_h(p, mx, mx + K * x1, my, my - 19, g(x1, 2), outside=True)
    (h1x, h1y), (h2x, h2y) = I.HOLES
    dim_v(p, my, my + K * h1y, xr, xr + 10, g(h1y, 2), outside=True)
    p.line(mx + K * h2x + 3, my + K * h2y, xr + 0.8, my + K * h1y, LW_DIM)
    dim_h(p, mx + K * h1x, mx + K * h2x, my + K * h1y, my - 28, g(h2x - h1x, 1), outside=False)
    leader(p, mx + K * h1x + 1.6, my + K * h1y + 1.6, mx - 6, my + K * h1y + 22, "⌀2,2 (2 отв.)")
    # торец
    ys = my - 52
    p.rect(mx, ys, K * W_B, K * T_B, S)
    dim_v(p, ys, ys + K * T_B, mx, mx - 10, "0,6±0,06", outside=True)
    # рисунок проводников (справочно)
    for i, (layer, title) in enumerate((("F.Cu", "Слой 1 (сторона установки элементов)"),
                                        ("B.Cu", "Слой 2 (вид сверху сквозь плату)"))):
        png = _layer_png(layer, layer[0])
        x0 = 135 + i * 78
        c.drawImage(str(png), x0 * mm, my * mm, width=K * W_B * mm, height=K * H_B * mm, mask="auto")
        p.text(x0 + K * W_B / 2, yt + 4, title, 2.5, "c")
    p.text(135 + 78 + K * W_B / 2 - 39, yt + 12, "Рисунок проводников (справочно)", 3.5, "c")
    # отверстия
    pcb_txt = (KIPRJ / "TENSH.464512.002.kicad_pcb").read_text(encoding="utf-8")
    n_via = len(re.findall(r"^\s*\(via ", pcb_txt, re.M))
    rows = [("0,8", "⌀1,2", str(len(I.HOST)), "есть", "полуотверстия X1"),
            ("0,25", "⌀0,5", f"{n_via}*", "есть", "переходные"),
            ("2,2", "—", "2", "нет", "крепёжные")]
    yb = table(p, 30, 80, [12, 16, 12, 14, 36], rows, ["⌀ отв.", "Площадка", "Кол.", "Металл.", "Назначение"],
               row_h=6.0, head_h=7, title="Таблица 1 — Отверстия")
    items = [
        "* Размер и количество — для справок, по электронной модели платы.",
        "Плата должна соответствовать ГОСТ Р 55693-2013; класс точности 4 по ГОСТ Р 53429-2009.",
        "Материал — стеклотекстолит FR-4 (Tg ≥ 150 °C) толщиной 0,6 мм, фольга 35 мкм с двух сторон.",
        "Рисунок проводников, контактных площадок и переходных отверстий — по файлам Gerber электронной "
        "модели платы; на чертеже показан справочно. Наименьшие ширина проводника и зазор — 0,15 мм.",
        "Краевые контакты X1 — металлизированные полуотверстия ⌀0,8 мм с шагом 2,54 мм.",
        "Покрытие контактных площадок — иммерсионное золото по никелю (ENIG); паяльная маска с двух сторон; "
        "маркировка белой краской.",
        "Радиус скругления углов — 1 мм. Неуказанные предельные отклонения размеров — ±0,1 мм.",
        "Маркировать обозначение платы на стороне 2 шрифтом высотой 0,8 мм.",
    ]
    gost.tech_requirements(p, 232, 150, 180, items, h=2.5)
    gost.stamp_form1(p, W, "Плата печатная", "", code=PCB, lit="Т", mass=g(MASS_BOARD) + " г", scale="2:1",
                     sheet="", sheets="1", material="Стеклотекстолит FR-4 0,6 мм")
    c.showPage()
    c.save()


# ================================================================ пояснительная записка
def build_pz(path):
    import gen_pz as G
    from reportlab.platypus import NextPageTemplate, PageBreak, Paragraph, Spacer, Table, TableStyle
    st = G.sty
    rows_m, carrier, module = masses()
    i_bat = 0.3
    v_bat = 3.7
    p_idle = 0.29                       # модем включён, приём (34–39 мА при 5 В через подкачку заряда)
    p_tx = round(i_bat * v_bat, 1)      # сеанс SBD: потребление ограничено током заряда ионисторов
    t_sess = 20.0                       # с — длительность сеанса AT+SBDIX (оценка, уточняется измерением)
    e_msg = p_tx * t_sess               # Дж
    q_msg = e_msg / v_bat / 3.6         # мА·ч
    e_cap = 0.5 * 0.5 * 5.3 ** 2        # Дж — заряд пары ионисторов 1 Ф (0,5 Ф) до 5,3 В
    t_chg = 0.5 * 5.3 / 0.15            # с — заряд током 150 мА

    def body():
        G.H1("1 Назначение")
        G.P(f"Модуль {CODE} — вариант спутниковой связи на готовом модеме Iridium 9603N. Он предназначен для "
            "случаев, когда ресурс КА на ГСО для основного варианта ТЕНШ.464512.001 недоступен, а также для работы "
            "в высоких широтах. Модуль обменивается короткими сообщениями SBD через низкоорбитальную группировку "
            "Iridium (66 КА на высоте около 780 км, глобальное покрытие, включая полярные районы). Интерфейс "
            "с полётным контроллером (ПК) — UART и сигналы управления на краевых контактах X1.")
        G.H1("2 Состав и принцип работы")
        G.P(f"Модуль состоит из модема Iridium 9603N, платы-носителя {PCB} и антенны, подключаемой к розетке U.FL "
            f"модема. Схема электрическая принципиальная — {CODE}&nbsp;Э3, перечень элементов — {CODE}&nbsp;ПЭ3. "
            "На плате-носителе размещены:")
        G.LI([
            "зарядное устройство ионисторов DA1 (LTC3225, подкачка заряда ×2): заряжает последовательную пару "
            "ионисторов C1, C2 по 1 Ф до 5,3 В током 150 мА; от АКБ при этом потребляется не более 0,3 А, "
            "а импульсы тока передачи модема до 1,3 А длительностью 8,3 мс отдают ионисторы;",
            "ключ питания модема DA2 (TPS22918) с плавным включением (пусковой ток модема — не более 4 А) "
            "и разрядом выхода — модем после выключения должен не менее 2 с находиться при нулевом напряжении;",
            "буфер линии TX DD1 (SN74LVC1G125) с питанием от выхода SUPPLY_OUT модема — исключает питание "
            "выключенного модема через линию данных;",
            "последовательные резисторы R5–R8 в линиях RX, RI, NETAV, ON/OFF и розетка X2 (Samtec SS4-10) "
            "для модема.",
        ])
        G.P("ПК включает заряд ионисторов (CHG_EN), дожидается сигнала PGOOD, включает питание модема (PWR_EN) "
            "и сигнал ON_OFF, после чего обменивается с модемом AT-командами (сеанс SBD — команда AT+SBDIX). "
            "Между сеансами модем и зарядное устройство выключены.")
        host = {"VBAT": "Питание 3,3…4,2 В от АКБ 1S", "GND": "Общий", "VIO": "Не используется (резерв)",
                "TXD": "Вход UART (данные к модему)", "RXD": "Выход UART (данные от модема)",
                "ON_OFF": "Включение модема", "RI": "Индикатор входящего сообщения",
                "NETAV": "Наличие сети", "CHG_EN": "Включение заряда ионисторов", "PGOOD": "Ионисторы заряжены",
                "PWR_EN": "Включение питания модема"}
        G.TBL("t_x1", "Назначение краевых контактов X1", ["Конт.", "Цепь", "Назначение"],
              [(str(i + 1), n, host[n]) for i, n in enumerate(I.HOST)], [18, 30, 127], align="ccl")
        G.H1("3 Основные характеристики")
        G.TBL("t_spec", "Основные характеристики модуля (оценка)", ["Параметр", "Значение"], [
            ("Система связи", "Iridium SBD, КА на низкой орбите (около 780 км)"),
            ("Диапазон частот", "1616–1626,5 МГц (ПД и ПР с временным разделением)"),
            ("Длина сообщения", "с борта до 340 байт, на борт до 270 байт"),
            ("Время сеанса SBD", f"около {g(t_sess, 0)} с (оценка; уточняется измерением с выбранной антенной)"),
            ("Напряжение питания", "3,3–4,2 В непосредственно от АКБ 1S"),
            ("Ток от АКБ", f"не более {g(i_bat)} А (ограничен током заряда ионисторов)"),
            ("Потребляемая мощность: модем выключен", "не более 0,1 мВт"),
            ("Потребляемая мощность: модем включён (ожидание, приём)", f"около {g(p_idle, 2)} Вт"),
            ("Потребляемая мощность: сеанс SBD", f"не более {g(p_tx)} Вт"),
            ("Интерфейс", "UART 19 200 бит/с (уровни 3,3 В), ON_OFF, RI, NETAV, CHG_EN, PGOOD, PWR_EN"),
            ("Габариты модуля", f"32 × 45 × {g(H_TOTAL)} мм"),
            ("Масса модуля без антенны / с антенной",
             f"{g(module)} г / {g(module + ANT_MASS[0])}…{g(module + ANT_MASS[1])} г"),
            ("Температура эксплуатации", "от минус 40 до плюс 65 °C (ограничена ионисторами)"),
        ], [80, 95])
        G.H1("4 Конструкция и масса")
        G.P(f"Плата-носитель {PCB} — двухслойная, 32 × 45 × 0,6 мм, с 12 краевыми полуотверстиями (шаг 2,54 мм) "
            f"вдоль одной кромки. Модем крепится над платой на двух стойках М2×{g(GAP, 0)} и соединяется с ней "
            "розеткой X2; ионисторы уложены на плату вне проекции модема. Проект платы выполнен в САПР KiCad: "
            "схема, топология, проверка конструктивных норм без нарушений, файлы Gerber и сверловки. Габаритные "
            f"размеры — {CODE}&nbsp;ГЧ, чертёж платы — {PCB}.")
        G.FIG("f_3d", CAD / "renders" / "iridium_iso.png", "3D-модель модуля на модеме Iridium 9603N", 120)
        G.TBL("t_mass", "Масса составных частей (оценка)", ["Составная часть", "Масса, г"],
              [(n, g(m, 2 if m < 1 else 1)) for n, m in rows_m] +
              [("Итого модуль без антенны", g(module)),
               ("Антенна Maxtena M1621HCT-P-UFL (масса по данным изготовителя не подтверждена)", g(ANT_MASS[0])),
               ("Антенна-патч 25 × 25 мм с кабелем U.FL (резерв)", g(ANT_MASS[1])),
               ("Итого с антенной", f"{g(module + ANT_MASS[0])}…{g(module + ANT_MASS[1])}")],
              [145, 30], align="lr")
        G.H1("5 Энергопотребление")
        G.P(f"Начальный заряд ионисторов до 5,3 В занимает около {g(t_chg, 0)} с и требует около {g(e_cap, 0)} Дж. "
            f"Сеанс SBD длительностью около {g(t_sess, 0)} с при потреблении {g(p_tx)} Вт расходует около "
            f"{g(e_msg, 0)} Дж, т. е. {g(q_msg, 1)} мА·ч заряда АКБ 3,7 В на сообщение. При передаче телеметрии "
            f"раз в 5 мин расход составит около {g(12 * q_msg, 0)} мА·ч за час без учёта ожидания; в режиме "
            f"постоянного ожидания входящих сообщений добавляется {g(p_idle / v_bat * 1000, 0)} мА·ч за час. "
            "Длительность сеанса зависит от видимости КА и положения антенны и подлежит измерению на макете.")
        G.H1("6 Ограничения и риски")
        G.TBL("t_risk", "Ограничения и риски варианта Iridium", ["Риск", "Последствие", "Мера снижения"], [
            ("Регуляторный статус: трафик Iridium в РФ проходит через собственный шлюз; порядок подключения "
             "абонентского терминала и регистрации РЭС не подтверждён",
             "невозможность законной эксплуатации", "уточнить у российского сервис-провайдера Iridium до "
                                                    "закупки"),
            ("Модем 9603N — изделие США; действуют экспортные ограничения", "срыв поставки",
             "оценка правовых рисков до принятия решения"),
            (f"Масса {g(module + ANT_MASS[0])}…{g(module + ANT_MASS[1])} г — в 4–5 раз больше модуля "
             "ТЕНШ.464512.001", "превышение бюджета массы", "применение при допустимом бюджете массы"),
            ("Питание модема через линии данных при выключенном питании", "сбой включения модема",
             "ПК удерживает ON_OFF и RXD в низком уровне до появления V_IRI; буфер DD1 в линии TX"),
            ("Расстройка антенны вблизи тела птицы, затенение крыльями", "увеличение времени сеанса",
             "выбор антенны по измерениям на фантоме, ориентация излучателя к зениту"),
        ], [62, 40, 73])
        G.H1("7 Сравнение с основным вариантом")
        G.TBL("t_cmp", "Сравнение вариантов модуля", ["Параметр", "ТЕНШ.464512.001 (ГСО, L)",
                                                       f"{CODE} (Iridium SBD)"], [
            ("Покрытие", "зона луча КА на ГСО, до широт 65–70°", "глобальное, включая полярные районы"),
            ("Зависимость от ресурса КА", "нужен КА с региональным или узким лучом", "готовая служба"),
            ("Габариты модуля", "32 × 22 × 2,5 мм", f"32 × 45 × {g(H_TOTAL)} мм"),
            ("Масса комплекта с антенной", "11–16 г", f"{g(module + ANT_MASS[0], 0)}–{g(module + ANT_MASS[1], 0)} г"),
            ("Потребление при приёме", "не более 85 мВт", f"около {g(p_idle, 2)} Вт"),
            ("Длина сообщения", "пакеты 64 байта, адаптивная скорость", "до 340 / 270 байт"),
            ("Разработка", "собственный модем и ПО", "плата-носитель и ПО ПК"),
        ], [50, 62, 63])
        G.P("Вариант Iridium SBD не требует разработки радиочасти и ресурса КА на ГСО, но втрое-вчетверо тяжелее "
            "и потребляет больше при приёме. Его целесообразно рассматривать как резервный канал или как "
            "решение для полярных районов при допустимом бюджете массы и подтверждённом регуляторном статусе.")

    def title():
        sig = "_______________ / _______________ /<br/>«____» _______________ 2026 г."
        t = Table([[Paragraph("СОГЛАСОВАНО<br/><br/>" + sig, st["t_left"]),
                    Paragraph("УТВЕРЖДАЮ<br/><br/>" + sig, st["t_left"])]], colWidths=[87 * mm, 87 * mm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, 0), 14 * mm)]))
        G.story.append(t)
        G.story.append(Spacer(1, 50 * mm))
        G.story.append(Paragraph("МОДУЛЬ СПУТНИКОВОЙ СВЯЗИ IRIDIUM SBD", st["t_big"]))
        G.story.append(Spacer(1, 3 * mm))
        G.story.append(Paragraph("для малоразмерного биогибридного летательного аппарата", st["t_mid"]))
        G.story.append(Paragraph("Вариант на модеме Iridium 9603N (справка)", st["t_mid"]))
        G.story.append(Spacer(1, 12 * mm))
        G.story.append(Paragraph("Пояснительная записка", st["t_big"]))
        G.story.append(Spacer(1, 6 * mm))
        G.story.append(Paragraph(G.CODE, st["t_big"]))
        G.story.append(Spacer(1, 26 * mm))
        G.story.append(Paragraph("Стадия: технический проект (проработка)", st["t_mid"]))
        G.story.append(Spacer(1, 40 * mm))
        G.story.append(Paragraph("2026", st["t_mid"]))
        G.story.append(NextPageTemplate("first"))
        G.story.append(PageBreak())

    def assemble():
        G.story.clear()
        for k in G._cnt:
            G._cnt[k] = 0
        G._new_refs.clear()
        title()
        G.toc()
        body()

    old = (G.CODE, gost.PRODUCT)
    G.CODE, gost.PRODUCT = CODE + " ПЗ", I.PRODUCT
    try:
        assemble()
        G._refs.clear()
        G._refs.update(G._new_refs)
        assemble()
        G.Doc(path).multiBuild(G.story, canvasmaker=G.StampCanvas)
    finally:
        G.CODE, gost.PRODUCT = old


def main(no_3d=False):
    gost.register_fonts()
    DOCS.mkdir(exist_ok=True)
    if not no_3d:
        make_3d()
    build_gch(DOCS / f"{CODE}_ГЧ.pdf")
    build_pcb(DOCS / f"{PCB}.pdf")
    build_pz(DOCS / f"{CODE}_ПЗ.pdf")


if __name__ == "__main__":
    main("--no-3d" in sys.argv)
