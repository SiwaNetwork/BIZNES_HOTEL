"""Расчёты для многорежимного модема ТЕНШ.464512.003: линия NTN NB-IoT через КА на ГСО (полоса n255,
L-диапазон ПСС), линия собственного протокола через тот же КА (A4 LR2021 + УМ 1 Вт, по calc.py),
mesh-линия LoRa 868 МГц между модемами (воздух — воздух, прямая видимость) и энергопотребление.

Методика линии «борт → КА» — та же, что в calc.py (раздел 6 ПЗ ТЕНШ.464512.001).
"""
import math

import calc

# ---------------------------------------------------------------- NTN NB-IoT (3GPP Rel. 17), полоса n255
NTN_P_TX = 23.0            # дБм — класс мощности 3 абонентского терминала, без внешнего УМ
NTN_SCS = 3750.0           # Гц — однотональная передача NPUSCH с разносом 3,75 кГц
NTN_SNR_REQ = -3.0         # дБ — требуемое ОСШ на тон с повторениями NB-IoT (оценка для 10 % BLER)
NTN_GT_CASES = [(-10.0, "глобальный луч"), (0.0, "региональный луч"), (10.0, "узкий луч")]

# ---------------------------------------------------------------- mesh LoRa 868 МГц
MESH_F_MHZ = 869.0
MESH_P_TX = 14.0           # дБм — 25 мВт ЭИИМ в полосе 868,7–869,2 МГц (без лицензии), с учётом антенны
MESH_G_ANT = -5.0          # дБи — малогабаритная антенна на птице (гибкая или штыревая укороченная)
MESH_L_BODY = 3.0          # дБ — затенение телом и крыльями, разброс ДН
MESH_MARGIN = 10.0         # дБ — запас на замирания при взаимном движении носителей
# чувствительность LoRa, полоса 125 кГц (по техописаниям SX126x/LR11xx, у LR2021 — не хуже), дБм
MESH_SENS = {7: -124.0, 8: -127.0, 9: -130.0, 10: -133.0, 11: -135.5, 12: -137.0}
MESH_BW = 125000.0


def fspl_db(d_km, f_mhz):
    return 20 * math.log10(d_km) + 20 * math.log10(f_mhz) + 32.44


def ntn_uplink(gt_sat_dbk, g_ant=calc.G_ANT):
    """C/N0 линии NTN «борт → КА» (те же потери, что для собственного протокола, без УМ)."""
    _, cn0 = calc.uplink(gt_sat_dbk, g_ant=g_ant, p_tx_dbm=NTN_P_TX)
    return cn0


def ntn_rate(cn0):
    """Оценка скорости NPUSCH: при ОСШ на тон 3,75 кГц ниже требуемого включаются повторения
    (до 128); скорость пропорциональна 1/повторения от пиковой ≈ 2,4 кбит/с на тон (π/4-QPSK, кодирование)."""
    snr_tone = cn0 - 10 * math.log10(NTN_SCS)
    if snr_tone >= NTN_SNR_REQ:
        return 2400.0, 1
    rep = 2 ** math.ceil(math.log2(10 ** ((NTN_SNR_REQ - snr_tone) / 10)))
    if rep > 128:
        return 0.0, rep
    return 2400.0 / rep, rep


def mesh_range_km(sf):
    """Дальность mesh-линии в прямой видимости (воздух — воздух) по потерям в свободном пространстве."""
    budget = MESH_P_TX + 2 * MESH_G_ANT - MESH_L_BODY * 2 - MESH_MARGIN - MESH_SENS[sf]
    return 10 ** ((budget - 20 * math.log10(MESH_F_MHZ) - 32.44) / 20)


def mesh_rate(sf):
    return sf * MESH_BW / 2 ** sf * 4 / 5


def summary():
    s = {"ntn": {}, "mesh": {}}
    for gt, name in NTN_GT_CASES:
        cn0 = ntn_uplink(gt)
        r, rep = ntn_rate(cn0)
        s["ntn"][gt] = dict(name=name, cn0=cn0, rate=r, rep=rep)
    for sf in MESH_SENS:
        s["mesh"][sf] = dict(range_km=mesh_range_km(sf), rate=mesh_rate(sf))
    return s


if __name__ == "__main__":
    s = summary()
    for gt, v in s["ntn"].items():
        print(f"NTN G/T={gt:+.0f} ({v['name']}): C/N0={v['cn0']:.1f} дБГц, "
              f"скорость {v['rate']:.0f} бит/с (повторений {v['rep']})")
    for sf, v in s["mesh"].items():
        print(f"mesh SF{sf}: {v['rate']:.0f} бит/с, дальность {v['range_km']:.1f} км")
