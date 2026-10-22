"""ТЕНШ.464512.002 — модуль спутниковой связи Iridium SBD: плата-носитель модема Iridium 9603N.

Источники (открытые проекты, файлы проверены построчно): SparkFun Qwiic Iridium 9603N, SparkFun Artemis Global
Tracker, PaulZC Iridium 9603N Beacon V5 / 9603 Lite; символы ACRONET, NOAA-PMEL. Распиновка разъёма модема,
LTC3225, TPS22918, SN74LVC1G125 сверена не менее чем в двух независимых файлах.

Питание: LTC3225 (подкачка заряда ×2) заряжает последовательную пару ионисторов до 5,3 В током 150 мА —
от батареи потребляется не более ≈0,3 А, импульсы передачи 1,3 А (8,3 мс) отдают ионисторы. Ключ TPS22918
с плавным нарастанием (ограничение пускового тока модема ≤ 4 А) и разрядом выхода (требование выдержки 2 с при 0 В).
Буфер SN74LVC1G125 с питанием от SUPPLY_OUT модема исключает подпитку выключенного модема по линии TX.
"""
from eda.netlist import Design, Part, Pin

from .common import C, R, ic

CODE = "ТЕНШ.464512.002"
PCB_CODE = "ТЕНШ.758726.002"
PRODUCT = "Модуль спутниковой связи\nIridium SBD"
BOARD = (32.0, 45.0)
THICK = 0.6
LAYERS = 2
CORNER_R = 1.0
ROUTE_PASSES = 50
RULES = dict(track=0.15, clearance=0.15, via=0.5, drill=0.25,  # класс 4 по ГОСТ Р 53429
             classes={"PWR": {"track": 0.25}, "PWR2": {"track": 0.4}})
X1_FP = "TENSH:Castellated_1x12_P2.54mm_1.2x1.6mm_D0.8mm"

# разъём модема (координаты контактов относительно центра, вид сверху, Y вверх): нечётные — ряд y=+2,435
SOCKET_PINS = [Pin(str(i), n, "L" if i % 2 else "R", t) for i, n, t in [
    (1, "EXT_PWR", "power_in"), (2, "EXT_PWR", "power_in"), (3, "EXT_GND", "power_in"), (4, "EXT_GND", "power_in"),
    (5, "ON/OFF", "input"), (6, "TX", "input"), (7, "RX", "output"), (8, "SIG_GND", "power_in"),
    (9, "DCD", "no_connect"), (10, "DSR", "no_connect"), (11, "CTS", "no_connect"), (12, "RI", "output"),
    (13, "RTS", "input"), (14, "DTR", "input"), (15, "SIG_GND", "power_in"), (16, "RES", "no_connect"),
    (17, "RES", "no_connect"), (18, "SIG_GND", "power_in"), (19, "NET_AV", "output"), (20, "SUP_OUT", "power_out")]]

HOST = [  # краевые контакты X1 (слева направо), шаг 2,54
    "VBAT", "GND", "VIO", "TXD", "RXD", "ON_OFF", "RI", "NETAV", "CHG_EN", "PGOOD", "PWR_EN", "GND"]
PAD_PITCH = 2.54

# положение разъёма модема и крепёжных стоек (Y вверх, от левого нижнего угла платы)
SOCK = (13.5, BOARD[1] - 3.9)
HOLES = [(SOCK[0] - 10.0, SOCK[1] - 25.6), (SOCK[0] + 15.0, SOCK[1] - 25.6)]
MODULE_BOX = (SOCK[0] - 12.3, SOCK[1] - 28.1, 29.6, 31.5)     # x, y, ширина, высота корпуса 9603N
MODULE_GAP = 6.0                                              # стойки 6 мм (гнездо SS4-10-3.50 + вилка ST4-10-2.50)


# ---------------------------------------------------------------- документы (Э3, ПЭ3, спецификация)
E3_SHEETS = [[("X1", "Краевые контакты"), ("DA1", "Заряд ионисторов"), ("DA2", "Ключ питания модема"),
              ("DD1", "Буфер линии TX"), ("X2", "Розетка модема Iridium 9603N")]]
E3_NOTES = [
    "Модем Iridium 9603N устанавливают в розетку X2 и крепят на две стойки М2 (см. спецификацию).",
    "До появления напряжения V_IRI линии ON_OFF и RXD хоста должны удерживаться в низком уровне.",
    f"X1 — краевые полуотверстия платы {PCB_CODE}.",
]
SP_DOCS = [("A3", "", "", f"{CODE} ГЧ", "Габаритный чертёж", "", ""),
           ("A4", "", "", f"{CODE} ПЗ", "Пояснительная записка", "", "")]
SP_PARTS = [("det", "A3", PCB_CODE, "Плата печатная", 1, "")]
SP_OTHER = [("Модем спутниковый Iridium 9603N", 1, "Iridium"),
            ("Антенна Maxtena M1621HCT-P-UFL", 1, "Maxtena"),
            ("Стойка М2×6 латунная, внутренняя резьба с обеих сторон", 2, ""),
            ("Винт М2×4 DIN 7985", 2, "")]
SP_MATERIALS = ["Паста паяльная SAC305, тип 4", "Лак защитный УР-231 ТУ 6-21-14-90",
                "Клей-герметик Пентэласт-1143 (фиксация ионисторов)"]


def pads_xy():
    x0 = BOARD[0] / 2 - (len(HOST) - 1) * PAD_PITCH / 2
    return [(i + 1, x0 + i * PAD_PITCH) for i in range(len(HOST))]


def design():
    d = Design(CODE, "Модуль спутниковой связи Iridium SBD")
    W, H = BOARD
    # краевой соединитель X1 (полуотверстия)
    x1_pins = [Pin(str(i + 1), n, "L", "passive") for i, n in enumerate(HOST)]
    d.add(Part("X1", "PAD", "Краевые контакты", X1_FP, x1_pins, name_ru="Контакты краевые (полуотверстия платы)",
               pos=(W / 2, 0.0, 0), body=(30.5, 1.6), height=0),
          **{str(i + 1): n for i, n in enumerate(HOST)})
    # гнездо разъёма модема
    d.add(ic("X2", "SS4-10-3.50-L-D-K-TR", "TENSH:Samtec_SS4-10_P0.4mm_Iridium9603", SOCKET_PINS,
             "Розетка SS4-10-3.50-L-D-K-TR", mfr="Samtec", pos=(SOCK[0], SOCK[1], 0), body=(5.2, 4.0), height=3.5,
             kind="CONN", mass=0.15),
          **{"1": "V_IRI", "2": "V_IRI", "3": "GND", "4": "GND", "5": "IRI_ON", "6": "IRI_TX", "7": "IRI_RX",
             "8": "GND", "12": "IRI_RI", "13": "GND", "14": "GND", "15": "GND", "18": "GND", "19": "IRI_NA",
             "20": "IRI_3V3"})
    # зарядное устройство ионисторов DA1 LTC3225
    d.add(ic("DA1", "LTC3225EDDB#TRMPBF", "Package_DFN_QFN:DFN-10-1EP_2x3mm_P0.5mm_EP0.64x2.4mm",
             "1:C+:R:passive, 2:C-:R:passive, 3:CX:R:passive, 4:~SHDN:L:input, 5:PGOOD:L:output, 6:VSEL:L:input, "
             "7:PROG:L:passive, 8:GND:B:power_in, 9:VIN:L:power_in, 10:COUT:R:power_out, 11:EP:B:power_in",
             "Микросхема LTC3225EDDB#TRMPBF", mfr="Analog Devices", pos=(12.0, 21.0, 90), body=(3.0, 2.0),
             height=0.75, mass=0.02),
          **{"1": "CP_P", "2": "CP_N", "3": "SC_MID", "4": "CHG_EN", "5": "PGOOD", "6": "VBAT", "7": "PROG",
             "8": "GND", "9": "VBAT", "10": "V_SC", "11": "GND"})
    d.add(C("C3", "2,2 мкФ", "0603", "10 В X7R", mpn="GRM188R71A225KE15", mfr="Murata", pos=(12.0, 17.5, 0)),
          **{"1": "VBAT", "2": "GND"})
    d.add(C("C4", "1 мкФ", "0603", "16 В X7R", mpn="GRM188R71C105KA12", mfr="Murata", pos=(15.5, 21.0, 90)),
          **{"1": "CP_P", "2": "CP_N"})
    d.add(C("C5", "0,22 мкФ", "0603", "10 В X7R", mpn="GRM188R71A224KA01", mfr="Murata", pos=(15.5, 17.5, 90)),
          **{"1": "V_SC", "2": "GND"})
    d.add(R("R1", "12,1 кОм", "0402", mpn="RC0402FR-0712K1L", mfr="Yageo", pos=(12.6, 24.4, 90)),
          **{"1": "PROG", "2": "GND"})
    d.add(R("R2", "100 кОм", "0402", mpn="RC0402FR-07100KL", mfr="Yageo", pos=(8.5, 24.5, 90)),
          **{"1": "CHG_EN", "2": "GND"})
    d.add(R("R3", "100 кОм", "0402", mpn="RC0402FR-07100KL", mfr="Yageo", pos=(6.5, 24.5, 90)),
          **{"1": "PGOOD", "2": "VIO"})
    # ионисторы: последовательная пара 2 × 1 Ф / 2,7 В, лежа на плате, выводы к краям
    for ref, x, conn in (("C1", 9.0, {"1": "V_SC", "2": "SC_MID"}), ("C2", 23.0, {"1": "SC_MID", "2": "GND"})):
        p = Part(ref, "C", "1 Ф", "TENSH:SuperCap_Radial_D8.0mm_L13.5mm_Horizontal" + ("_L" if ref == "C1" else "_R"),
                 [Pin("1", "+"), Pin("2", "-")], name_ru="Ионистор HV0810-2R7105-R 1 Ф 2,7 В", mpn="HV0810-2R7105-R",
                 mfr="Eaton", pos=(x, 6.85, 0), body=(13.5, 8.5), height=8.5, mass_g=1.2)
        d.add(p, **conn)
    # ключ питания модема DA2 TPS22918
    d.add(ic("DA2", "TPS22918DBVR", "Package_TO_SOT_SMD:SOT-23-6",
             "1:VIN:L:power_in, 2:GND:B:power_in, 3:ON:L:input, 4:CT:L:passive, 5:QOD:R:passive, 6:VOUT:R:power_out",
             "Микросхема TPS22918DBVR", mfr="Texas Instruments", pos=(22.0, 22.0, 0), body=(2.9, 1.6), height=1.45,
             mass=0.015),
          **{"1": "V_SC", "2": "GND", "3": "PWR_EN", "4": "CT", "5": "V_IRI", "6": "V_IRI"})
    d.add(C("C6", "1 мкФ", "0603", "10 В X7R", mpn="GRM188R71A105KA61", mfr="Murata", pos=(19.0, 25.0, 90)),
          **{"1": "V_SC", "2": "GND"})
    d.add(C("C7", "3300 пФ", "0402", "50 В X7R", mpn="GRM155R71H332KA01", mfr="Murata", pos=(22.0, 18.5, 0)),
          **{"1": "CT", "2": "GND"})
    d.add(R("R4", "100 кОм", "0402", mpn="RC0402FR-07100KL", mfr="Yageo", pos=(19.0, 19.0, 90)),
          **{"1": "PWR_EN", "2": "GND"})
    d.add(C("C8", "10 мкФ", "0603", "10 В X5R", mpn="GRM188R61A106KE69", mfr="Murata", pos=(25.5, 25.0, 90)),
          **{"1": "V_IRI", "2": "GND"})
    # буфер линии TX DD1 SN74LVC1G125 (питание от SUPPLY_OUT модема)
    d.add(ic("DD1", "SN74LVC1G125DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5",
             "1:~OE:L:input, 2:A:L:input, 3:GND:B:power_in, 4:Y:R:output, 5:VCC:R:power_in",
             "Микросхема SN74LVC1G125DCKR", mfr="Texas Instruments", pos=(8.0, 31.0, 0), body=(2.0, 1.25),
             height=1.0, mass=0.006),
          **{"1": "GND", "2": "TXD", "3": "GND", "4": "IRI_TX", "5": "IRI_3V3"})
    d.add(C("C9", "0,1 мкФ", "0402", "16 В X7R", mpn="GRM155R71C104KA88", mfr="Murata", pos=(10.8, 31.0, 90)),
          **{"1": "IRI_3V3", "2": "GND"})
    # последовательные резисторы и подтяжка
    d.add(R("R5", "100 Ом", "0402", mpn="RC0402FR-07100RL", mfr="Yageo", pos=(14.0, 31.0, 90)), **{"1": "IRI_RX", "2": "RXD"})
    d.add(R("R6", "100 Ом", "0402", mpn="RC0402FR-07100RL", mfr="Yageo", pos=(15.8, 31.0, 90)), **{"1": "IRI_RI", "2": "RI"})
    d.add(R("R7", "100 Ом", "0402", mpn="RC0402FR-07100RL", mfr="Yageo", pos=(17.6, 31.0, 90)), **{"1": "IRI_NA", "2": "NETAV"})
    d.add(R("R8", "1 кОм", "0402", mpn="RC0402FR-071KL", mfr="Yageo", pos=(20.0, 31.0, 90)), **{"1": "ON_OFF", "2": "IRI_ON"})
    d.add(R("R9", "100 кОм", "0402", mpn="RC0402FR-07100KL", mfr="Yageo", pos=(21.8, 31.0, 90)), **{"1": "IRI_ON", "2": "GND"})
    # крепление модема: стойки M2
    for i, (x, y) in enumerate(HOLES, 1):
        d.add(Part(f"MH{i}", "MH", "M2", "MountingHole:MountingHole_2.2mm_M2", [], name_ru="Отверстие крепёжное",
                   pos=(x, y, 0), body=(2.2, 2.2), height=0))
    d.net_class.update({"VBAT": "PWR", "V_SC": "PWR2", "SC_MID": "PWR2", "V_IRI": "PWR", "GND": "PWR"})
    return d


def pre_route(b):
    """Отводы с переходными отверстиями от площадок «земли» (до трассировки — трассировщик их обходит)."""
    return b.pad_vias("GND", refs=[r for r in b.fps if r != "X2"])


def post_route(b):
    """Сшивка земли верхнего и нижнего слоёв (кроме зоны под ионисторами — там выводы и клей)."""
    n = b.stitch("GND", pitch=1.2, keepout=[(0, 0, BOARD[0], 11.8)])
    return n + b.fix_islands("GND")


def pcb_extra(b):
    """Полигоны земли на обоих слоях, маркировка."""
    import pcbnew
    W, H = BOARD
    poly = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]
    b.zone("GND", pcbnew.B_Cu, poly, clearance=0.2)
    b.zone("GND", pcbnew.F_Cu, poly, clearance=0.2)
    b.text(PCB_CODE, W / 2, H / 2, layer=pcbnew.B_SilkS, h=0.8)      # сторона 2: сторону 1 закрывает модем
    for i, n in enumerate(HOST):
        x = W / 2 - (len(HOST) - 1) * PAD_PITCH / 2 + i * PAD_PITCH
        b.text(str(i + 1), x, 2.6, h=0.8)
