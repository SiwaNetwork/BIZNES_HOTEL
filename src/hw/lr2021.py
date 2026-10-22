"""Узел A4/G1: приёмопередатчик Semtech LR2021 и опорный генератор TCXO 32 МГц.

Распиновка LR2021 (QFN-32 5×5 мм, шаг 0,5 мм) сверена по трём независимым библиотекам KiCad
(teletype7/IRIS, leorosenbaum11-ui/RFM-LoRa, busterbn/lr2021_kicad — перенос эталонного проекта Semtech E788V01A)
и по переписанной таблице 2-1 технического описания LR20xx Rev 2.1. Номиналы обвязки питания и SIMO-преобразователя
повторяют эталонный проект Semtech (2,2 мкГн; 10/4,7/1 мкФ + 100 нФ по VBAT; ферритовые фильтры VDCC1→VDCC2 и
VPAX1→VPAX2). Согласующие цепи ВЧ-входа и ВЧ-выхода для L-диапазона подбираются при настройке (отмечены «*»).
"""
from eda.netlist import Pin

from .common import C, FB, L, R, ic

LR2021_PINS = [
    Pin("1", "VR_PA", "R", "power_out"), Pin("2", "VPAX2", "L", "power_in"), Pin("3", "NTC", "L", "no_connect"),
    Pin("4", "XTA", "L", "input"), Pin("5", "XTB", "L", "no_connect"), Pin("6", "VTCXO", "L", "power_out"),
    Pin("7", "DIO11", "R", "no_connect"), Pin("8", "DIO10", "R", "no_connect"), Pin("9", "DIO9", "R", "no_connect"),
    Pin("10", "DIO8", "R", "no_connect"), Pin("11", "DIO7", "R", "bidirectional"), Pin("12", "VDCC1", "L", "power_out"),
    Pin("13", "VPAX1", "L", "power_out"), Pin("14", "LXB", "L", "passive"), Pin("15", "GND_DCC", "B", "power_in"),
    Pin("16", "LXA", "L", "passive"), Pin("17", "VBAT", "L", "power_in"), Pin("18", "DIO6", "R", "bidirectional"),
    Pin("19", "DIO5", "R", "bidirectional"), Pin("20", "NRESET", "R", "input"), Pin("21", "MISO", "R", "output"),
    Pin("22", "MOSI", "R", "input"), Pin("23", "SCK", "R", "input"), Pin("24", "NSS", "R", "input"),
    Pin("25", "BUSY", "R", "output"), Pin("26", "VDCC2", "L", "power_in"), Pin("27", "RFO_LF2", "R", "no_connect"),
    Pin("28", "RFO_LF1", "R", "no_connect"), Pin("29", "RFI_LF", "R", "no_connect"), Pin("30", "GND", "B", "power_in"),
    Pin("31", "RFI_HF", "R", "input"), Pin("32", "RFO_HF", "R", "output"), Pin("33", "GND", "B", "power_in"),
]
# площадка 33 — открытая контактная площадка (EP, вывод 0 по документации Semtech)
# G1: выводы 1 и 2 — общий, 3 — выход, 4 — питание (три независимых символа серии ECS-TXO-20CSMV4)

TCXO_PINS = [Pin("1", "GND", "B", "power_in"), Pin("2", "GND", "B", "power_in"),
             Pin("3", "OUT", "R", "output"), Pin("4", "VDD", "L", "power_in")]


def add(d, xy, nets):
    """xy: словарь размещения {поз: (x, y, поворот)}; nets: имена цепей интерфейса:
    V3 (питание 3,0 В), NSS, SCK, MOSI, MISO, BUSY, NRST, IRQ, TXEN, RXEN, RFI (вход ПР 50 Ом), RFO (выход ПД 50 Ом)."""
    P = lambda r: xy.get(r, (0, 0, 0))
    n = nets
    d.add(ic("DA4", "LR2021IMLTRT", "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.7x3.7mm_ThermalVias", LR2021_PINS,
             "Микросхема LR2021IMLTRT", mfr="Semtech", pos=P("DA4"), body=(5.0, 5.0), height=0.9, mass=0.07,
             group="A4"))
    conn = {"1": "LR_VRPA", "2": "LR_VPAX", "4": "LR_XTA", "6": "LR_VTCXO",
            "12": "LR_VDCC1", "13": "LR_VPAX1", "14": "LR_LXB", "15": "GND", "16": "LR_LXA", "17": "LR_VBAT",
            "19": n["IRQ"], "18": n["TXEN"], "11": n["RXEN"], "20": n["NRST"], "21": n["MISO"], "22": n["MOSI"],
            "23": n["SCK"], "24": n["NSS"], "25": n["BUSY"], "26": "LR_VDCC", "30": "GND", "33": "GND",
            "31": "LR_RFI", "32": "LR_RFO"}
    for pin, net in conn.items():
        d.connect(net, "DA4", pin)
    # питание VBAT 3,0 В через ферритовый фильтр
    d.add(FB("L1", "600 Ом", "0402", mpn="BLM15AG601SN1D", mfr="Murata", pos=P("L1")), **{"1": n["V3"], "2": "LR_VBAT"})
    d.add(C("C10", "10 мкФ", "0603", "6,3 В X5R", mpn="GRM188R60J106ME47", mfr="Murata", pos=P("C10")),
          **{"1": "LR_VBAT", "2": "GND"})
    d.add(C("C11", "1 мкФ", "0402", "10 В X5R", mpn="GRM155R61A105KE15", mfr="Murata", pos=P("C11")),
          **{"1": "LR_VBAT", "2": "GND"})
    d.add(C("C12", "0,1 мкФ", "0201", "10 В X5R", mpn="GRM033R61A104KE15", mfr="Murata", pos=P("C12")),
          **{"1": "LR_VBAT", "2": "GND"})
    # SIMO-преобразователь
    d.add(L("L2", "2,2 мкГн", "0603", "±20 %", mpn="LQM18PN2R2MFRL", mfr="Murata", pos=P("L2"), height=0.9,
            name_ru="Катушка индуктивности LQM18PN2R2MFRL 2,2 мкГн ±20 %"),
          **{"1": "LR_LXA", "2": "LR_LXB"})
    d.add(C("C13", "4,7 мкФ", "0402", "6,3 В X5R", mpn="GRM155R60J475ME47", mfr="Murata", pos=P("C13")),
          **{"1": "LR_VDCC1", "2": "GND"})
    d.add(FB("L3", "600 Ом", "0402", mpn="BLM15AG601SN1D", mfr="Murata", pos=P("L3")), **{"1": "LR_VDCC1", "2": "LR_VDCC"})
    d.add(C("C14", "1 мкФ", "0402", "10 В X5R", mpn="GRM155R61A105KE15", mfr="Murata", pos=P("C14")),
          **{"1": "LR_VDCC", "2": "GND"})
    d.add(C("C15", "4,7 мкФ", "0402", "6,3 В X5R", mpn="GRM155R60J475ME47", mfr="Murata", pos=P("C15")),
          **{"1": "LR_VPAX1", "2": "GND"})
    d.add(FB("L4", "600 Ом", "0402", mpn="BLM15AG601SN1D", mfr="Murata", pos=P("L4")), **{"1": "LR_VPAX1", "2": "LR_VPAX"})
    d.add(C("C16", "2,2 мкФ", "0402", "6,3 В X5R", mpn="GRM155R60J225ME15", mfr="Murata", pos=P("C16")),
          **{"1": "LR_VPAX", "2": "GND"})
    d.add(C("C17", "47 пФ", "0201", "25 В C0G", mpn="GRM0335C1E470JA01", mfr="Murata", pos=P("C17")),
          **{"1": "LR_VRPA", "2": "GND"})
    # опорный генератор G1: питание от вывода VTCXO, выход на XTA через 220 Ом + 10 пФ
    d.add(ic("G1", "ECS-TXO-20CSMV4-320-AY-TR", "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm", TCXO_PINS,
             "Генератор кварцевый термокомпенсированный ECS-TXO-20CSMV4-320-AY-TR 32 МГц ±0,5 ppm",
             mfr="ECS", pos=P("G1"), body=(2.0, 1.6), height=0.8, kind="OSC", mass=0.01, group="G1"),
          **{"1": "GND", "2": "GND", "3": "TCXO_OUT", "4": "LR_VTCXO"})
    d.add(C("C18", "0,1 мкФ", "0201", "10 В X5R", mpn="GRM033R61A104KE15", mfr="Murata", pos=P("C18")),
          **{"1": "LR_VTCXO", "2": "GND"})
    d.add(R("R4", "220 Ом", "0201", mpn="RC0201FR-07220RL", mfr="Yageo", pos=P("R4")), **{"1": "TCXO_OUT", "2": "TCXO_AC"})
    d.add(C("C19", "10 пФ", "0201", "25 В C0G", mpn="GRM0335C1E100JA01", mfr="Murata", pos=P("C19")),
          **{"1": "TCXO_AC", "2": "LR_XTA"})
    # ВЧ-выход: питание выходного каскада от VR_PA через дроссель, последовательное согласование 50 Ом
    d.add(L("L5", "27 нГн*", "0201", mpn="LQP03TN27NJ02", mfr="Murata", pos=P("L5"), note="Подбирают при настройке"),
          **{"1": "LR_VRPA", "2": "LR_RFO"})
    d.add(L("L6", "2,2 нГн*", "0201", mpn="LQP03TN2N2B02", mfr="Murata", pos=P("L6"), note="Подбирают при настройке"),
          **{"1": "LR_RFO", "2": "LR_RFO1"})
    d.add(C("C20", "1,5 пФ*", "0201", "25 В C0G", mpn="GRM0335C1E1R5BA01", mfr="Murata", pos=P("C20"),
            note="Подбирают при настройке"), **{"1": "LR_RFO1", "2": "GND"})
    d.add(C("C21", "10 пФ", "0201", "25 В C0G", mpn="GRM0335C1E100JA01", mfr="Murata", pos=P("C21")),
          **{"1": "LR_RFO1", "2": n["RFO"]})
    # ВЧ-вход: Г-образное согласование 50 Ом
    d.add(C("C22", "10 пФ", "0201", "25 В C0G", mpn="GRM0335C1E100JA01", mfr="Murata", pos=P("C22")),
          **{"1": n["RFI"], "2": "LR_RFI1"})
    d.add(L("L7", "3,3 нГн*", "0201", mpn="LQP03TN3N3B02", mfr="Murata", pos=P("L7"), note="Подбирают при настройке"),
          **{"1": "LR_RFI1", "2": "LR_RFI"})
    d.add(C("C23", "1,2 пФ*", "0201", "25 В C0G", mpn="GRM0335C1E1R2BA01", mfr="Murata", pos=P("C23"),
            note="Подбирают при настройке"), **{"1": "LR_RFI", "2": "GND"})
