"""Единые геометрические данные модуля ТЕНШ.464512.001 (мм).

Используются 3D-моделью (model3d.py), чертежом платы (gen_pcb.py)
и габаритным чертежом (gen_gch.py), чтобы документы не расходились.
Начало координат — левый нижний угол платы, вид сверху (сторона установки элементов).
"""

# ------------------------------------------------------------ плата
BOARD_L = 32.0
BOARD_W = 22.0
BOARD_T = 0.6          # 4 слоя, номинальная толщина
CORNER_R = 1.0

# краевые полуотверстия (castellated) — 2 ряда по 10, шаг 2,54
PAD_PITCH = 2.54
PADS_PER_SIDE = 10
PAD_HOLE_D = 0.8
PAD_W, PAD_L = 1.2, 1.6     # ширина вдоль кромки, длина вглубь платы
PADS_X0 = (BOARD_L - (PADS_PER_SIDE - 1) * PAD_PITCH) / 2


def pad_positions():
    """[(номер, x, y_кромки, сторона)] — нумерация против часовой стрелки от левого нижнего."""
    out = []
    for i in range(PADS_PER_SIDE):
        out.append((i + 1, PADS_X0 + i * PAD_PITCH, 0.0, "bottom"))
    for i in range(PADS_PER_SIDE):
        out.append((PADS_PER_SIDE + i + 1, PADS_X0 + (PADS_PER_SIDE - 1 - i) * PAD_PITCH, BOARD_W, "top"))
    return out


PIN_NAMES = {
    1: "GND", 2: "VBAT", 3: "VBAT", 4: "GND", 5: "UART_TX", 6: "UART_RX", 7: "WAKE", 8: "IRQ",
    9: "PPS", 10: "GND", 11: "GND", 12: "SWDIO", 13: "SWCLK", 14: "nRST", 15: "BOOT",
    16: "I2C_SDA", 17: "I2C_SCL", 18: "VIO", 19: "GND", 20: "GND",
}

# крепёжные отверстия (неметаллизированные)
HOLES = [(1.6, 1.6), (BOARD_L - 1.6, BOARD_W - 1.6)]
HOLE_D = 1.1

# экран РЧ-тракта (рамка + крышка); проём в левой стенке — под линию к XW1 (сторона, смещение от середины, ширина)
SHIELD = dict(x=4.0, y=2.3, l=17.4, w=17.4, h=1.6)
SHIELD_GAP = ("L", 1.0, 1.6)
FENCE_PITCH = 1.5      # шаг переходных отверстий по рамке экрана: между ними проходят дорожки внутренних слоёв


def fence_points(inset=0.2):
    """Переходные отверстия по рамке экрана (центры на оси стенки шириной 0,4 мм)."""
    import math
    x0, y0 = SHIELD["x"], SHIELD["y"]
    x1, y1 = x0 + SHIELD["l"], y0 + SHIELD["w"]
    gy = y0 + SHIELD["w"] / 2 + SHIELD_GAP[1]
    pts = []
    n = math.ceil((x1 - x0 - 1.2) / FENCE_PITCH)
    for i in range(n + 1):
        x = x0 + 0.6 + i * (x1 - x0 - 1.2) / n
        pts += [(round(x, 3), y0 + inset), (round(x, 3), y1 - inset)]
    n = math.ceil((y1 - y0) / FENCE_PITCH)
    for i in range(1, n):
        y = round(y0 + i * (y1 - y0) / n, 3)
        pts.append((x1 - inset, y))
        if abs(y - gy) > SHIELD_GAP[2] / 2 + 0.5:
            pts.append((x0 + inset, y))
    return pts

# ------------------------------------------------------------ элементы
# Координаты — из платы KiCad (расстановка выполняется при сборке проекта и сохраняется в placement_001.json).
# COMPONENTS: поз. обозначение, x центра, y центра, длина(x), ширина(y), высота, наименование, вид (цвет 3D)
# PASSIVES:   x, y, поворот, длина, ширина, высота — R, C, L типоразмеров 0201…0603
COMP_INFO = {
    "XW1": ("Розетка коаксиальная 50 Ом", "gold"), "DA1": ("Коммутатор ПР/ПД", "ic"),
    "DA9": ("Конденсатор перестраиваемый", "ic"), "Z1": ("Фильтр ПАВ ПД", "metal"), "Z2": ("Фильтр ПАВ ПР", "metal"),
    "DA2": ("Усилитель мощности", "ic"), "DA3": ("МШУ", "ic"), "DA4": ("Приёмопередатчик РЧ", "ic"),
    "G1": ("Генератор TCXO 32 МГц", "metal"), "DA8": ("Детектор мощности", "ic"),
    "DD1": ("Микроконтроллер-модем", "ic"), "BQ1": ("Резонатор 32,768 кГц", "metal"),
    "DA5": ("Стабилизатор 3,0 В", "ic"), "DA6": ("Стабилизатор 3,0 В (РЧ)", "ic"), "DA7": ("Ключ питания УМ", "ic"),
    "C1": ("Конденсатор полимерный 220 мкФ", "tant"), "C2": ("Конденсатор полимерный 220 мкФ", "tant"),
}


def _load_placement():
    import json
    from pathlib import Path
    f = Path(__file__).with_name("placement_001.json")
    if not f.exists():
        return [], []
    comps, passives = [], []
    for r in json.loads(f.read_text(encoding="utf-8")):
        l, w = r["body"]
        if r["rot"] % 180:
            l, w = w, l
        if r["ref"] in COMP_INFO:
            name, kind = COMP_INFO[r["ref"]]
            comps.append((r["ref"], r["x"], r["y"], l, w, r["h"], name, kind))
        elif r["kind"] in ("R", "C", "L", "FB"):
            passives.append((r["x"], r["y"], r["rot"], l, w, r["h"]))
    return comps, passives


COMPONENTS, PASSIVES = _load_placement()

# ------------------------------------------------------------ антенна WA1 (базовый вариант)
ANT_L = 25.0           # керамическая микрополосковая антенна 25×25×4, круговая поляризация
ANT_T = 4.0
ANT_PATCH = 20.6       # излучатель (серебрение)
ANT_PCB_T = 0.8        # плата-носитель антенны с тюнером/кабельным вводом
ANT_PCB_L = 30.0
CABLE_LEN = 60.0
CABLE_D = 1.13

# соответствие функциональных частей схемы Э1 элементам платы
E1_TO_PCB = [
    ("A1", "DA1, DA9, L12"), ("A2", "DA2, DA8"), ("A3", "DA3"), ("A4", "DA4"), ("A5", "DD1"),
    ("A6", "DD1 (встроенная флеш-память)"), ("A7", "DA5–DA7, C1, C2"), ("G1", "G1"), ("Z1", "Z1"), ("Z2", "Z2"),
    ("XW1", "XW1"),
]

# ------------------------------------------------------------ массы (оценка), г
MASS_MODULE_PARTS = [
    ("Плата печатная 32×22×0,6 мм, 4 слоя", 0.9),
    ("Электрорадиоэлементы (ИС, пассивные)", 1.6),
    ("Экран РЧ-тракта (рамка и крышка, луженая сталь 0,1 мм)", 0.4),
    ("Накопительные конденсаторы (2 шт.)", 0.4),
    ("Влагозащитное покрытие, припой", 0.2),
    ("Резерв массы (неучтённые элементы, разброс)", 0.5),
]
MASS_MODULE = round(sum(m for _, m in MASS_MODULE_PARTS), 2)
MASS_ANTENNA = 10.5    # 25×25×4 керамика + плата-носитель 30×30×0,8
MASS_CABLE = 0.6
MASS_MOUNT = 0.5
MASS_KIT = round(MASS_MODULE + MASS_ANTENNA + MASS_CABLE + MASS_MOUNT, 2)
MASS_QHA = 6.0         # облегчённый вариант: керамическая спиральная антенна ⌀12×30 мм, 5–7 г
MASS_KIT_LIGHT = round(MASS_MODULE + MASS_QHA + MASS_CABLE + MASS_MOUNT, 2)
