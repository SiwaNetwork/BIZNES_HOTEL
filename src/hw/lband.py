"""ТЕНШ.464512.001 — модуль спутниковой связи сверхкомпактный (L-диапазон ПСС, ретранслятор на ГСО).

Элементная база выбрана по открытым данным и сверена по независимым источникам (см. ПЗ, раздел 5):
  A4  LR2021 (Semtech) — приёмопередатчик 1,5–2,5 ГГц: ПД BPSK/GFSK, ПР LoRa 7,8–10,4 кГц; G1 — TCXO 32 МГц;
  A2  GRF5616 (Guerrilla RF) — УМ 1625–1675 МГц, до +31 дБм, питание от АКБ через ключ TPS22918;
  A3  BGA524N6 (Infineon) — МШУ; A1 — BGS12P2L6 (коммутатор ПР/ПД) + PE64906 (перестраиваемый конденсатор);
  Z1  SF2236E (RFMi) — ПАВ-фильтр ПД (до УМ, вход не более +12 дБм); Z2 — TA1926A (TST) — ПАВ-фильтр ПР;
  A5/A6 STM32L442KC (ST) — МК-модем (AES), буфер сообщений и патч LR2021 — во внутренней флеш-памяти 256 Кбайт;
  A7  TPS7A0530 ×2 (3,0 В постоянное и отключаемое для ВЧ-узлов), TPS22918 (ключ УМ), 2 × 220 мкФ;
  детектор мощности ADL5501 с ёмкостным ответвителем после ФНЧ гармоник.
Номиналы цепей согласования, отмеченные «*», подбирают при настройке.
"""
from eda import footprints as fpl
from eda.netlist import Design, Part, Pin

import design as D

from . import lr2021
from .common import C, FB, L, R, ic

CODE = "ТЕНШ.464512.001"
PCB_CODE = "ТЕНШ.687281.001"
PRODUCT = "Модуль спутниковой связи\nсверхкомпактный"
BOARD = (D.BOARD_L, D.BOARD_W)
THICK = D.BOARD_T
LAYERS = 4
CORNER_R = D.CORNER_R
ROUTE_PASSES = 60
RULES = dict(track=0.1, clearance=0.1, via=0.45, drill=0.2,          # класс 5 по ГОСТ Р 53429
             classes={"RF": {"track": 0.2, "clearance": 0.2}, "PWR": {"track": 0.2}, "PA": {"track": 0.5}})
# экран: левый нижний угол, длина, ширина, высота; проём в левой стенке под линию к XW1 (смещение от середины)
SHIELD, SHIELD_GAP = D.SHIELD, D.SHIELD_GAP
PLACEMENT = "placement_001.json"          # расстановка для чертежей и 3D-модели (design.py)
SH_FP = f"TENSH:RF_Shield_Frame_{SHIELD['l']}x{SHIELD['w']}mm_gap"
X1_FP = f"TENSH:Castellated_2x10_P2.54mm_Span{D.BOARD_W}mm"
SAW_FP = "TENSH:SAW_SM3030-6_3.0x3.0mm"
PIN_NAMES = D.PIN_NAMES
M, Y = "Murata", "Yageo"

# привязка развязывающих и подтягивающих элементов к выводам ИС (для автоматической расстановки)
NEAR = {"C3": ("DA5", "1"), "C4": ("DA5", "5"), "C5": ("DA5", "5"), "C6": ("DA6", "1"), "C7": ("DA6", "5"),
        "R1": ("DA6", "3"), "C8": ("DA7", "1"), "R2": ("DA7", "3"), "R3": ("DD1", "6"), "R5": ("DD1", "6"),
        "C24": ("DD1", "6"), "C25": ("DD1", "1"), "C28": ("DD1", "4"), "R6": ("DD1", "31"), "C26": ("DD1", "17"), "C27": ("DD1", "5"), "R7": ("DD1", "20"),
        "R8": ("DD1", "19"), "R11": ("DA2", "1"), "C32": ("DA2", "13"), "C33": ("DA2", "12"),
        "C44": ("DA1", "4"), "C45": ("DA9", "4"), "C47": ("DA3", "2"), "C41": ("DA8", "1"), "C18": ("G1", "4")}


# ---------------------------------------------------------------- документы (Э3, ПЭ3, спецификация)
E3_SHEETS = [
    [("DD1", "Микроконтроллер-модем"), ("BQ1", "")],
    [("X1", "Краевые контакты"), ("DA5", "Стабилизатор 3,0 В"), ("DA6", "Стабилизатор 3,0 В (ВЧ-узлы)"),
     ("DA7", "Ключ питания УМ"), ("G1", "Опорный генератор")],
    [("DA4", "Приёмопередатчик")],
    [("Z1", "Фильтр ПД"), ("DA2", "Усилитель мощности"), ("DA8", "Детектор мощности")],
    [("DA1", "Коммутатор ПР/ПД"), ("DA9", "Согласование антенны"), ("XW1", "Антенный вход"), ("DA3", "МШУ"),
     ("Z2", "Фильтр ПР")],
]
E3_NOTES = [
    "Номиналы элементов, отмеченных «*», подбирают при настройке.",
    "Линии связи показаны обрывами с наименованиями цепей; общий провод — цепь GND.",
    f"X1 — краевые полуотверстия платы {PCB_CODE}; рамка экрана соединена с цепью GND.",
]
SP_DOCS = [("A3", "", "", f"{CODE} Э1", "Схема электрическая структурная", "", ""),
           ("A3", "", "", f"{CODE} ГЧ", "Габаритный чертёж", "", ""),
           ("A4", "", "", f"{CODE} ПЗ", "Пояснительная записка", "", "")]
SP_PARTS = [("asm", "A3", PCB_CODE, "Плата печатная многослойная", 1, ""),
            ("det", "БЧ", "ТЕНШ.735441.001", f"Рамка экрана {SHIELD['l']:g}×{SHIELD['w']:g} мм".replace(".", ","), 1, ""),
            ("det", "БЧ", "ТЕНШ.735441.002", "Крышка экрана", 1, "")]
SP_OTHER = []
SP_MATERIALS = ["Паста паяльная SAC305, тип 4", "Лак защитный УР-231 ТУ 6-21-14-90"]
E3_ALIAS = {}


def footprints(lib):
    fpl.castellated_2rows(lib, D.PADS_PER_SIDE, D.BOARD_W)
    fpl.saw_sm3030_6(lib)
    fpl.shield_frame_gaps(lib, SHIELD["l"], SHIELD["w"], gaps=[SHIELD_GAP])
    fpl.npth_hole(lib, D.HOLE_D)


def _c0g(ref, val, mpn, note=""):
    return C(ref, val, "0201", "25 В C0G", mpn=mpn, mfr=M, note=note)


def _cap(ref, val, net, size="0201"):
    spec, mpn = {"0,1 мкФ": ("10 В X5R", "GRM033R61A104KE15"), "1 мкФ": ("10 В X5R", "GRM155R61A105KE15"),
                 "4,7 мкФ": ("6,3 В X5R", "GRM155R60J475ME47"), "10 мкФ": ("10 В X5R", "GRM188R61A106KE69"),
                 "0,01 мкФ": ("25 В X7R", "GRM033R71E103KA01"), "100 пФ": ("25 В C0G", "GRM0335C1E101JA01"),
                 "22 пФ": ("25 В C0G", "GRM0335C1E220JA01")}[val]
    return C(ref, val, size, spec, mpn=mpn, mfr=M), {"1": net, "2": "GND"}


def design():
    d = Design(CODE, "Модуль спутниковой связи сверхкомпактный")
    cap = lambda *a: d.add(*_cap(*a)[:1], **_cap(*a)[1])
    # ------------------------------------------------------------ X1: краевые контакты 2×10
    host = {1: "GND", 2: "VBAT", 3: "VBAT", 4: "GND", 5: "UART_TX", 6: "UART_RX", 7: "WAKE", 8: "IRQ", 9: "PPS",
            10: "GND", 11: "GND", 12: "SWDIO", 13: "SWCLK", 14: "NRST", 15: "BOOT0", 16: "I2C_SDA", 17: "I2C_SCL",
            18: "V3", 19: "GND", 20: "GND"}
    x1 = [Pin(str(n), PIN_NAMES[n], "L" if n <= 10 else "R", "passive") for n in range(1, 21)]
    d.add(Part("X1", "PAD", "Краевые контакты", X1_FP, x1, name_ru="Контакты краевые (полуотверстия платы)",
               pos=(BOARD[0] / 2, 0.0, 0), body=(24.0, 22.0), height=0),
          **{str(k): v for k, v in host.items()})

    # ------------------------------------------------------------ A7: питание
    for ref, out, en, pos in (("DA5", "V3", "VBAT", (23.7, 10.4, 0)), ("DA6", "V3RF", "RF_EN", (28.3, 10.4, 0))):
        d.add(ic(ref, "TPS7A0530PDBVR", "Package_TO_SOT_SMD:SOT-23-5",
                 "1:IN:L:power_in, 2:GND:B:power_in, 3:EN:L:input, 4:NC:R:no_connect, 5:OUT:R:power_out",
                 "Микросхема TPS7A0530PDBVR", mfr="Texas Instruments", pos=pos, body=(2.9, 1.6), height=1.45,
                 mass=0.015, group="A7"),
              **{"1": "VBAT", "2": "GND", "3": en, "5": out})
    cap("C3", "1 мкФ", "VBAT", "0402")
    cap("C4", "1 мкФ", "V3", "0402")
    cap("C5", "4,7 мкФ", "V3", "0402")
    cap("C6", "1 мкФ", "VBAT", "0402")
    cap("C7", "1 мкФ", "V3RF", "0402")
    d.add(R("R1", "100 кОм", "0201", mpn="RC0201FR-07100KL", mfr=Y), **{"1": "RF_EN", "2": "GND"})
    # ключ питания УМ (плавное включение, разряд выхода) и накопительные конденсаторы
    d.add(ic("DA7", "TPS22918DBVR", "Package_TO_SOT_SMD:SOT-23-6",
             "1:VIN:L:power_in, 2:GND:B:power_in, 3:ON:L:input, 4:CT:L:passive, 5:QOD:R:passive, 6:VOUT:R:power_out",
             "Микросхема TPS22918DBVR", mfr="Texas Instruments", pos=(29.3, 4.5, 0), body=(2.9, 1.6),
             height=1.45, mass=0.015, group="A7"),
          **{"1": "VBAT", "2": "GND", "3": "PA_EN", "4": "PA_CT", "5": "VPA", "6": "VPA"})
    cap("C8", "10 мкФ", "VBAT", "0603")
    d.add(C("C9", "3300 пФ", "0201", "25 В X7R", mpn="GRM033R71E332KA01", mfr=M), **{"1": "PA_CT", "2": "GND"})
    d.add(R("R2", "100 кОм", "0201", mpn="RC0201FR-07100KL", mfr=Y), **{"1": "PA_EN", "2": "GND"})
    for ref, y in (("C1", 3.6), ("C2", 6.95)):
        d.add(Part(ref, "C", "220 мкФ", "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B", [Pin("1", "+"), Pin("2", "-")],
                   name_ru="Конденсатор T520B227M006ATE040 220 мкФ ±20 % 6,3 В", mpn="T520B227M006ATE040",
                   mfr="KEMET", pos=(24.2, y, 0), body=(3.5, 2.8), height=1.9, mass_g=0.07, group="A7"),
              **{"1": "VPA", "2": "GND"})
    # контроль напряжения АКБ: делитель 1 МОм / 1 МОм
    d.add(R("R3", "1 МОм", "0201", mpn="RC0201FR-071ML", mfr=Y), **{"1": "VBAT", "2": "ADC_VBAT"})
    d.add(R("R5", "1 МОм", "0201", mpn="RC0201FR-071ML", mfr=Y), **{"1": "ADC_VBAT", "2": "GND"})
    cap("C24", "0,1 мкФ", "ADC_VBAT")

    # ------------------------------------------------------------ A5/A6: микроконтроллер-модем
    mcu_pins = ("1:VDD:T:power_in, 2:PC14:L:bidirectional, 3:PC15:L:bidirectional, 4:NRST:L:input, "
                "5:VDDA:T:power_in, 6:PA0:L:bidirectional, 7:PA1:L:bidirectional, 8:PA2:L:bidirectional, "
                "9:PA3:L:bidirectional, 10:PA4:L:bidirectional, 11:PA5:L:bidirectional, 12:PA6:L:bidirectional, "
                "13:PA7:L:bidirectional, 14:PB0:L:bidirectional, 15:PB1:L:bidirectional, 16:VSS:B:power_in, "
                "17:VDD:T:power_in, 18:PA8:R:bidirectional, 19:PA9:R:bidirectional, 20:PA10:R:bidirectional, "
                "21:PA11:R:bidirectional, 22:PA12:R:bidirectional, 23:PA13:R:bidirectional, 24:PA14:R:bidirectional, "
                "25:PA15:R:bidirectional, 26:PB3:R:bidirectional, 27:PB4:R:bidirectional, 28:PB5:R:bidirectional, "
                "29:PB6:R:bidirectional, 30:PB7:R:no_connect, 31:PH3-BOOT0:R:bidirectional, 32:VSS:B:power_in, "
                "33:VSS:B:power_in")
    d.add(ic("DD1", "STM32L442KCU6", "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm", mcu_pins,
             "Микросхема STM32L442KCU6", mfr="STMicroelectronics", pos=(28.4, 16.3, 0), body=(5.0, 5.0),
             height=0.6, mass=0.06, group="A5"),
          **{"1": "V3", "2": "OSC32_IN", "3": "OSC32_OUT", "4": "NRST", "5": "V3", "6": "ADC_VBAT", "7": "ADC_PDET",
             "8": "UART_TX", "9": "UART_RX", "10": "LR_NSS", "11": "SCK", "12": "MISO", "13": "MOSI",
             "14": "LR_BUSY", "15": "LR_IRQ", "16": "GND", "17": "V3", "18": "PPS", "19": "I2C_SCL", "20": "I2C_SDA",
             "21": "PA_EN", "22": "PA_SHDN", "23": "SWDIO", "24": "SWCLK", "25": "RF_EN", "26": "LR_NRST",
             "27": "DTC_SEN", "28": "WAKE", "29": "IRQ", "31": "BOOT0", "32": "GND", "33": "GND"})
    for ref in ("C25", "C26", "C27"):
        cap(ref, "0,1 мкФ", "V3")
    cap("C28", "0,1 мкФ", "NRST")
    d.add(R("R6", "10 кОм", "0201", mpn="RC0201FR-0710KL", mfr=Y), **{"1": "BOOT0", "2": "GND"})
    d.add(R("R7", "4,7 кОм", "0201", mpn="RC0201FR-074K7L", mfr=Y), **{"1": "I2C_SDA", "2": "V3"})
    d.add(R("R8", "4,7 кОм", "0201", mpn="RC0201FR-074K7L", mfr=Y), **{"1": "I2C_SCL", "2": "V3"})
    d.add(ic("BQ1", "ECS-.327-6-12-TR", "Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm", "1:1:L:passive, 2:2:R:passive",
             "Резонатор кварцевый ECS-.327-6-12-TR 32,768 кГц", mfr="ECS", pos=(23.4, 18.3, 0), body=(2.0, 1.2),
             height=0.6, kind="XTAL", mass=0.005, group="A5"),
          **{"1": "OSC32_IN", "2": "OSC32_OUT"})
    d.add(C("C29", "8,2 пФ", "0201", "25 В C0G", mpn="GRM0335C1E8R2CA01", mfr=M), **{"1": "OSC32_IN", "2": "GND"})
    d.add(C("C30", "8,2 пФ", "0201", "25 В C0G", mpn="GRM0335C1E8R2CA01", mfr=M), **{"1": "OSC32_OUT", "2": "GND"})

    # ------------------------------------------------------------ A4/G1: приёмопередатчик LR2021 и TCXO
    lr2021.add(d, {"DA4": (15.8, 12.0, 90), "G1": (15.0, 7.2, 0)},
               dict(V3="V3", NSS="LR_NSS", SCK="SCK", MOSI="MOSI", MISO="MISO", BUSY="LR_BUSY", NRST="LR_NRST",
                    IRQ="LR_IRQ", TXEN="TRX_SEL", RXEN="LNA_ON", RFI="RX_Z2", RFO="TX_LR"))

    # ------------------------------------------------------------ Z1, A2: фильтр ПД и усилитель мощности
    saw = "1:GND:B:passive, 2:IN:L:passive, 3:GND:B:passive, 4:GND:B:passive, 5:OUT:R:passive, 6:GND:B:passive"
    d.add(ic("Z1", "SF2236E", SAW_FP, saw, "Фильтр ПАВ SF2236E 1642,5 МГц", mfr="RFMi", pos=(10.8, 6.6, 180),
             body=(3.0, 3.0), height=1.2, kind="SAW", mass=0.03, group="Z1"),
          **{"1": "GND", "2": "TX_LR", "3": "GND", "4": "GND", "5": "TX_Z1", "6": "GND"})
    d.add(_c0g("C31", "22 пФ", "GRM0335C1E220JA01"), **{"1": "TX_Z1", "2": "PA_IN"})
    pa_pins = ("1:VSHDN:L:input, 2:NC:B:passive, 3:RF_IN:L:input, 4:RF_IN:L:input, 5:NC:B:passive, 6:NC:B:passive, "
               "7:NC:B:passive, 8:NC:B:passive, 9:RF_OUT/VCC2:R:output, 10:RF_OUT/VCC2:R:output, 11:NC:B:passive, "
               "12:BIAS:T:power_in, 13:VCC1:T:power_in, 14:NC:B:passive, 15:VEN2:L:input, 16:VEN1:L:input, "
               "17:GND:B:power_in")
    d.add(ic("DA2", "GRF5616", "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm_ThermalVias", pa_pins,
             "Микросхема GRF5616", mfr="Guerrilla RF", pos=(6.6, 6.6, 180), body=(3.0, 3.0), height=0.85,
             mass=0.03, group="A2"),
          **{"1": "PA_SHDN", "2": "GND", "3": "PA_IN", "4": "PA_IN", "5": "GND", "6": "GND", "7": "GND", "8": "GND",
             "9": "PA_OUT", "10": "PA_OUT", "11": "GND", "12": "PA_BIAS", "13": "PA_VCC1", "14": "GND",
             "15": "PA_VEN", "16": "PA_VEN", "17": "GND"})
    d.add(L("L8", "18 нГн*", "0402", mpn="LQW15AN18NJ00", mfr=M, note="Подбирают при настройке"),
          **{"1": "VPA", "2": "PA_OUT"})
    d.add(FB("L9", "120 Ом", "0402", mpn="BLM15PX121SN1D", mfr=M), **{"1": "VPA", "2": "PA_VCC1"})
    d.add(R("R9", "1 кОм*", "0201", mpn="RC0201FR-071KL", mfr=Y, note="Подбирают при настройке"),
          **{"1": "VPA", "2": "PA_BIAS"})
    d.add(R("R10", "2,2 кОм*", "0201", mpn="RC0201FR-072K2L", mfr=Y, note="Подбирают при настройке"),
          **{"1": "PA_EN", "2": "PA_VEN"})
    d.add(R("R11", "100 кОм", "0201", mpn="RC0201FR-07100KL", mfr=Y), **{"1": "PA_SHDN", "2": "V3"})
    cap("C32", "1 мкФ", "VPA", "0402")
    cap("C33", "22 пФ", "VPA")
    cap("C34", "22 пФ", "PA_VCC1")
    # выход УМ: согласование, разделительный конденсатор, ФНЧ гармоник (5 звеньев), ответвитель детектора
    d.add(_c0g("C35", "1,5 пФ*", "GRM0335C1E1R5BA01", note="Подбирают при настройке"), **{"1": "PA_OUT", "2": "GND"})
    d.add(_c0g("C36", "22 пФ", "GRM0335C1E220JA01"), **{"1": "PA_OUT", "2": "LPF1"})
    d.add(_c0g("C37", "1,8 пФ", "GRM0335C1E1R8BA01"), **{"1": "LPF1", "2": "GND"})
    d.add(L("L10", "5,6 нГн", "0402", mpn="LQW15AN5N6C10", mfr=M), **{"1": "LPF1", "2": "LPF2"})
    d.add(_c0g("C38", "3,3 пФ", "GRM0335C1E3R3BA01"), **{"1": "LPF2", "2": "GND"})
    d.add(L("L11", "5,6 нГн", "0402", mpn="LQW15AN5N6C10", mfr=M), **{"1": "LPF2", "2": "TX_ANT"})
    d.add(_c0g("C39", "1,8 пФ", "GRM0335C1E1R8BA01"), **{"1": "TX_ANT", "2": "GND"})
    d.add(_c0g("C40", "0,2 пФ*", "GRM0335C1ER20BA01", note="Подбирают при настройке"), **{"1": "TX_ANT", "2": "DET_IN"})
    d.add(R("R12", "51 Ом", "0201", mpn="RC0201FR-0751RL", mfr=Y), **{"1": "DET_IN", "2": "GND"})
    d.add(ic("DA8", "ADL5501AKSZ-R7", "Package_TO_SOT_SMD:SOT-363_SC-70-6",
             "1:VPOS:L:power_in, 2:FLTR:L:passive, 3:RFIN:L:input, 4:COMM:B:power_in, 5:ENBL:R:input, 6:VRMS:R:output",
             "Микросхема ADL5501AKSZ-R7", mfr="Analog Devices", pos=(9.4, 10.9, 0), body=(2.0, 1.25), height=1.0,
             mass=0.006, group="A2"),
          **{"1": "V3RF", "2": "DET_FLT", "3": "DET_IN", "4": "GND", "5": "PA_EN", "6": "DET_OUT"})
    cap("C41", "0,1 мкФ", "V3RF")
    d.add(C("C42", "4700 пФ", "0201", "25 В X7R", mpn="GRM033R71E472KA01", mfr=M), **{"1": "DET_FLT", "2": "V3RF"})
    d.add(R("R13", "1 кОм", "0201", mpn="RC0201FR-071KL", mfr=Y), **{"1": "DET_OUT", "2": "ADC_PDET"})
    cap("C43", "0,01 мкФ", "ADC_PDET")

    # ------------------------------------------------------------ A1: коммутатор, перестраиваемое согласование, XW1
    d.add(ic("DA1", "BGS12P2L6E6327XTSA1", "TENSH:Infineon_PG-TSLP-6-4_0.7x1.1mm",
             "1:RF2:R:passive, 2:GND:B:power_in, 3:RF1:R:passive, 4:VDD:L:power_in, 5:RFIN:L:passive, 6:CTRL:L:input",
             "Микросхема BGS12P2L6E6327XTSA1", mfr="Infineon", pos=(6.4, 12.0, 0), body=(0.7, 1.1), height=0.31,
             mass=0.001, group="A1"),
          **{"1": "TX_ANT", "2": "GND", "3": "RX_SW", "4": "V3RF", "5": "ANT_SW", "6": "TRX_SEL"})
    cap("C44", "100 пФ", "V3RF")
    d.add(ic("DA9", "PE64906B-Z", "TENSH:pSemi_QFN-10-1EP_2x2mm_P0.5mm_EP0.95mm",
             "1:RF-:L:passive, 2:RF-:L:passive, 3:GND:B:power_in, 4:VDD:L:power_in, 5:SCL:L:input, 6:SEN:R:input, "
             "7:SDA:R:input, 8:RF+:R:passive, 9:RF+:R:passive, 10:GND:B:power_in, 11:GND:B:power_in",
             "Микросхема PE64906B-Z", mfr="pSemi", pos=(6.0, 15.6, 0), body=(2.0, 2.0), height=0.55, mass=0.004,
             group="A1"),
          **{"1": "GND", "2": "GND", "3": "GND", "4": "V3RF", "5": "SCK", "6": "DTC_SEN", "7": "MOSI", "8": "ANT",
             "9": "ANT", "10": "GND", "11": "GND"})
    cap("C45", "0,1 мкФ", "V3RF")
    d.add(L("L12", "3,3 нГн*", "0402", mpn="LQW15AN3N3B80", mfr=M, note="Подбирают при настройке"),
          **{"1": "ANT", "2": "ANT_SW"})
    d.add(Part("XW1", "COAX", "U.FL-R-SMT-1(10)", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
               [Pin("1", "SIG", "R"), Pin("2", "GND", "B")], name_ru="Розетка U.FL-R-SMT-1(10)",
               mpn="U.FL-R-SMT-1(10)", mfr="Hirose", pos=(2.3, 12.0, 180), body=(3.0, 3.0), height=1.25, mass_g=0.02,
               group="XW1"),
          **{"1": "ANT", "2": "GND"})

    # ------------------------------------------------------------ A3, Z2: МШУ и фильтр ПР
    d.add(_c0g("C46", "100 пФ", "GRM0335C1E101JA01"), **{"1": "RX_SW", "2": "LNA_IN"})
    d.add(L("L13", "9,1 нГн*", "0402", mpn="LQW15AN9N1G00", mfr=M, note="Подбирают при настройке"),
          **{"1": "LNA_IN", "2": "LNA_AI"})
    d.add(ic("DA3", "BGA524N6E6327XTSA1", "TENSH:Infineon_PG-TSNP-6-2_0.7x1.1mm",
             "1:GND:B:power_in, 2:VCC:L:power_in, 3:AO:R:output, 4:GND:B:power_in, 5:AI:L:input, 6:PON:L:input",
             "Микросхема BGA524N6E6327XTSA1", mfr="Infineon", pos=(9.0, 15.2, 0), body=(1.1, 0.7), height=0.38,
             mass=0.001, group="A3"),
          **{"1": "GND", "2": "V3RF", "3": "LNA_AO", "4": "GND", "5": "LNA_AI", "6": "LNA_ON"})
    cap("C47", "0,01 мкФ", "V3RF")
    d.add(ic("Z2", "TA1926A", SAW_FP, saw, "Фильтр ПАВ TA1926A 1542 МГц", mfr="TST", pos=(11.6, 17.2, 0),
             body=(3.0, 3.0), height=1.0, kind="SAW", mass=0.03, group="Z2"),
          **{"1": "GND", "2": "LNA_AO", "3": "GND", "4": "GND", "5": "RX_Z2", "6": "GND"})

    # ------------------------------------------------------------ экран и крепёжные отверстия
    d.add(Part("SH1", "SHIELD", "Рамка экрана", SH_FP, [Pin("1", "GND", "B", "power_in")], name_ru="Рамка экрана",
               pos=(SHIELD["x"] + SHIELD["l"] / 2, SHIELD["y"] + SHIELD["w"] / 2, 0),
               body=(SHIELD["l"], SHIELD["w"]), height=SHIELD["h"]),
          **{"1": "GND"})
    for i, (x, y) in enumerate(D.HOLES, 1):
        d.add(Part(f"MH{i}", "MH", "1,1", f"TENSH:MountingHole_{D.HOLE_D}mm_NPTH", [], name_ru="Отверстие крепёжное",
                   pos=(x, y, 0), body=(1.1, 1.1), height=0))
    rf = ["ANT", "ANT_SW", "TX_ANT", "LPF1", "LPF2", "PA_OUT", "PA_IN", "TX_Z1", "TX_LR", "RX_SW", "LNA_IN",
          "LNA_AI", "LNA_AO", "RX_Z2", "LR_RFO", "LR_RFO1", "LR_RFI", "LR_RFI1"]
    d.net_class.update({n: "RF" for n in rf})
    d.net_class.update({"VPA": "PA", "VBAT": "PWR", "V3": "PWR", "V3RF": "PWR", "GND": "PWR"})
    return d


# ---------------------------------------------------------------- плата
def shield_box():
    s = SHIELD
    return (s["x"], s["y"], s["x"] + s["l"], s["y"] + s["w"])


def place(b):
    return b.autoplace(near=NEAR, regions=[shield_box()])


def pcb_extra(b):
    import pcbnew
    W, H = BOARD
    b.b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    box = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]
    b.zone("GND", pcbnew.In1_Cu, box, priority=0, clearance=0.15, min_w=0.15)
    for lay in (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        b.zone("GND", lay, box, priority=0, clearance=0.15, min_w=0.15)
    # переходные отверстия по рамке экрана (между ними проходят дорожки внутренних слоёв)
    for x, y in D.fence_points():
        b.via("GND", x, y, b.via_d, b.via_drill)
    b.text(PCB_CODE, W / 2, H / 2, layer=pcbnew.B_SilkS, h=0.8)


def pre_route(b):
    return b.pad_vias("GND", refs=[r for r in b.fps if r not in ("X1", "SH1")], clearance=0.12, track=0.2)


def post_route(b):
    n = b.stitch("GND", pitch=1.0, clearance=0.15, keepout=[(0, 0, BOARD[0], 1.9), (0, BOARD[1] - 1.9, *BOARD)])
    return n + b.fix_islands("GND")
