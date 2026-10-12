"""Расчёты для ТЕНШ.464512.001 ПЗ: энергетика радиолинии «борт — КА на ГСО»,
масса и энергопотребление. Все исходные значения — проектные оценки стадии
технического проекта; ПЗ берёт числа только отсюда и из design.py.
Запуск: python3 src/calc.py — печатает сводку расчётов.
"""
import math

import design as D

K_DBW = -228.6          # 10·lg k, дБВт/(К·Гц)
RE_KM = 6378.137        # экваториальный радиус Земли, км
H_GEO_KM = 35786.0      # высота ГСО, км
C = 299_792_458.0
F_UP_MHZ = 1643.5       # середина полосы ПД 1626,5–1660,5 МГц
F_DN_MHZ = 1542.0       # середина полосы ПР 1525–1559 МГц


def slant_range_km(elev_deg: float, h_km: float = H_GEO_KM) -> float:
    """Наклонная дальность до КА на высоте h_km при угле места elev_deg."""
    e = math.radians(elev_deg)
    r = RE_KM + h_km
    return math.sqrt(r**2 - (RE_KM * math.cos(e))**2) - RE_KM * math.sin(e)


def max_elevation_deg(lat_deg: float) -> float:
    """Максимальный угол места КА на ГСО (КА на меридиане точки)."""
    phi = math.radians(lat_deg)
    k = RE_KM / (RE_KM + H_GEO_KM)
    return math.degrees(math.atan((math.cos(phi) - k) / math.sin(phi))) if lat_deg else 90.0


def latitude_for_elevation(elev_deg: float) -> float:
    """Широта, на которой максимальный угол места КА на ГСО равен elev_deg (бисекция)."""
    lo, hi = 0.1, 89.9
    for _ in range(60):
        mid = (lo + hi) / 2
        if max_elevation_deg(mid) > elev_deg:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def wavelength_cm(f_mhz: float) -> float:
    return C / (f_mhz * 1e6) * 100


def fspl_db(d_km: float, f_mhz: float) -> float:
    lam = C / (f_mhz * 1e6)
    return 20 * math.log10(4 * math.pi * d_km * 1e3 / lam)


def db(x: float) -> float:
    return 10 * math.log10(x)


# ---------------------------------------------------------------- исходные данные линии
ELEV_DEG = 20.0      # расчётный угол места (широты 55–60° с. ш. при смещении КА по долготе)
P_TX_DBM = 30.0      # выходная мощность УМ
L_PATH = 1.2         # ПАВ-фильтр, антенный коммутатор, кабель 60 мм с разъёмами, дБ
L_TUNE = 0.5         # перестройка согласования антенны (5.4.2 а), дБ
G_ANT = -3.0         # усиление антенны WA1 (базовый вариант) при угле места 20°, нижняя оценка, дБи
G_ANT_QHA = -1.0     # то же для спиральной антенны (облегчённый вариант)
L_POL_ATM = 0.8      # поляризационные и атмосферные потери, дБ
L_BODY = 3.0         # затенение телом птицы, крен, разброс ДН, дБ
T_ANT = 200.0        # шумовая температура антенны (видит тело птицы и подстилающую поверхность), К
NF_LNA = 1.0         # коэффициент шума МШУ, дБ
EBN0_REQ = 4.0       # π/2-BPSK + LDPC 1/2, вероятность ошибки 1e-5, с учётом потерь реализации, дБ
MARGIN = 3.0         # запас на замирания, дБ
MODEM_MAX_BPS = 2400
MODEM_MIN_BPS = 100

GT_CASES = [(-10.0, "глобальный луч"), (0.0, "региональный луч"), (10.0, "узкий луч")]
EIRP_CASES = [20.0, 30.0]


def l_feed() -> float:
    return L_PATH + L_TUNE


def uplink(gt_sat_dbk: float, g_ant: float = G_ANT, p_tx_dbm: float = P_TX_DBM):
    """Линия «борт → КА». Возвращает строки таблицы и C/N0."""
    d = slant_range_km(ELEV_DEG)
    eirp = p_tx_dbm - 30 - L_PATH - L_TUNE + g_ant
    lfs = fspl_db(d, F_UP_MHZ)
    cn0 = eirp - lfs - L_POL_ATM - L_BODY + gt_sat_dbk - K_DBW
    rows = [
        ("Выходная мощность УМ", p_tx_dbm - 30, "дБВт"),
        ("Потери в тракте (ПАВ-фильтр, коммутатор, кабель)", -L_PATH, "дБ"),
        ("Потери перестройки согласования антенны", -L_TUNE, "дБ"),
        (f"Усиление антенны при угле места {ELEV_DEG:.0f}°", g_ant, "дБи"),
        ("ЭИИМ борта", eirp, "дБВт"),
        ("Наклонная дальность", d, "км"),
        ("Потери в свободном пространстве", -lfs, "дБ"),
        ("Поляризационные и атмосферные потери", -L_POL_ATM, "дБ"),
        ("Затенение телом птицы, крен, разброс ДН", -L_BODY, "дБ"),
        ("Добротность КА G/T", gt_sat_dbk, "дБ/К"),
        ("Отношение C/N<sub>0</sub>", cn0, "дБГц"),
    ]
    return rows, cn0


def board_noise():
    """Шумовая температура системы (на входе МШУ) и добротность борта G/T."""
    a = 10 ** (-l_feed() / 10)
    t_lna = 290 * (10 ** (NF_LNA / 10) - 1)
    t_sys = T_ANT * a + 290 * (1 - a) + t_lna     # приведено ко входу МШУ
    gt = G_ANT - l_feed() - db(t_sys)
    return t_sys, gt


def downlink(eirp_sat_dbw: float):
    """Линия «КА → борт». Возвращает строки таблицы и C/N0."""
    d = slant_range_km(ELEV_DEG)
    t_sys, gt = board_noise()
    lfs = fspl_db(d, F_DN_MHZ)
    cn0 = eirp_sat_dbw - lfs - L_POL_ATM - L_BODY + gt - K_DBW
    rows = [
        ("ЭИИМ КА на несущую", eirp_sat_dbw, "дБВт"),
        ("Наклонная дальность", d, "км"),
        ("Потери в свободном пространстве", -lfs, "дБ"),
        ("Поляризационные и атмосферные потери", -L_POL_ATM, "дБ"),
        ("Затенение телом птицы, крен, разброс ДН", -L_BODY, "дБ"),
        (f"Усиление антенны при угле места {ELEV_DEG:.0f}°", G_ANT, "дБи"),
        ("Потери в тракте до МШУ (с перестройкой)", -l_feed(), "дБ"),
        ("Шумовая температура антенны", T_ANT, "К"),
        ("Коэффициент шума МШУ", NF_LNA, "дБ"),
        ("Шумовая температура системы (на входе МШУ)", t_sys, "К"),
        ("Добротность борта G/T", gt, "дБ/К"),
        ("Отношение C/N<sub>0</sub>", cn0, "дБГц"),
    ]
    return rows, cn0


def max_rate_bps(cn0: float) -> float:
    """Максимальная скорость по энергетике (с запасом MARGIN)."""
    return 10 ** ((cn0 - EBN0_REQ - MARGIN) / 10)


def cn0_threshold(rate_bps: float, with_margin: bool = False) -> float:
    return db(rate_bps) + EBN0_REQ + (MARGIN if with_margin else 0.0)


def gt_required(rate_bps: float) -> float:
    """G/T КА, необходимая для скорости rate_bps на линии «борт → КА» (с запасом)."""
    _, cn0_at_0 = uplink(0.0)
    return cn0_threshold(rate_bps, True) - cn0_at_0


def eirp_required(rate_bps: float) -> float:
    """ЭИИМ КА, необходимая для скорости rate_bps на линии «КА → борт» (с запасом)."""
    _, cn0_at_0 = downlink(0.0)
    return cn0_threshold(rate_bps, True) - cn0_at_0


def packet_tx_time(payload_bytes: int, rate_bps: float, overhead_s: float = 0.4) -> float:
    """Время передачи пакета: преамбула и синхронизация + данные со служебными 16 байт."""
    return overhead_s + (payload_bytes + 16) * 8 / rate_bps


# ---------------------------------------------------------------- энергопотребление
V_BAT = 3.7
V_BAT_MIN = 3.3
P_SLEEP = 0.0002
P_RX = 0.085
P_TX_1W = 2.6
P_TX_05W = 1.5
MODES = [  # режим, мощность потребления, Вт
    ("Сон (часы реального времени, пробуждение)", P_SLEEP),
    ("Приём (дежурный, синхронизация)", P_RX),
    ("Передача, Pвых = 30 дБм (1 Вт)", P_TX_1W),
    ("Передача, Pвых = 27 дБм (0,5 Вт)", P_TX_05W),
]
SCEN_RATE = 250      # бит/с — достижимо при G/T КА не хуже региональной оценки (таблица линии «борт → КА»)


def scenario(tx_s_per_h: float, tx_w: float, rx_s_per_h: float):
    """Энергия за час: полудуплекс — время приёма не пересекается со временем передачи."""
    rx = min(rx_s_per_h, 3600 - tx_s_per_h)
    sleep = max(0.0, 3600 - tx_s_per_h - rx)
    wh = (tx_s_per_h * tx_w + rx * P_RX + sleep * P_SLEEP) / 3600
    return wh, wh / V_BAT * 1000


SCENARIOS_DEF = [
    # имя, пакетов телеметрии в час, байт, кадров-превью 2 кБ в час, секунд приёма в час
    ("А — телеметрия раз в 5 мин, приём команд 10 % времени", 12, 64, 0, 360),
    ("Б — телеметрия раз в 1 мин, приём команд 10 % времени", 60, 64, 0, 360),
    ("В — телеметрия раз в 1 мин, непрерывный приём", 60, 64, 0, 3600),
    ("Г — как Б, плюс кадр-превью 2 кБ раз в 10 мин", 60, 64, 6, 360),
]


def scenarios(rate_bps: float = SCEN_RATE):
    out = []
    for name, n, nbytes, n_prev, rx in SCENARIOS_DEF:
        t = n * packet_tx_time(nbytes, rate_bps) + n_prev * packet_tx_time(2048, rate_bps)
        wh, mah = scenario(t, P_TX_1W, rx)
        out.append((name, wh, mah, t))
    return out


def summary():
    """Ключевые числа для текста ПЗ (единый источник)."""
    up = {gt: uplink(gt)[1] for gt, _ in GT_CASES}
    dn = {e: downlink(e)[1] for e in EIRP_CASES}
    t_sys, gt_board = board_noise()
    sc = scenarios()
    r_up = {gt: max_rate_bps(c) for gt, c in up.items()}
    r_dn = {e: max_rate_bps(c) for e, c in dn.items()}
    e_pkt_1w = P_TX_1W * packet_tx_time(64, r_up[10.0] if r_up[10.0] < MODEM_MAX_BPS else MODEM_MAX_BPS)
    return dict(
        up=up, dn=dn, r_up=r_up, r_dn=r_dn, t_sys=t_sys, gt_board=gt_board, scenarios=sc,
        gt_req_100=gt_required(MODEM_MIN_BPS), gt_req_scen=gt_required(SCEN_RATE),
        eirp_req_cmd_1s=None,
        thr_100=cn0_threshold(MODEM_MIN_BPS), thr_100_m=cn0_threshold(MODEM_MIN_BPS, True),
        i_peak=(P_TX_1W / V_BAT, P_TX_1W / V_BAT_MIN),
        lat_el5=latitude_for_elevation(5.0), lat_el0=math.degrees(math.acos(RE_KM / (RE_KM + H_GEO_KM))),
        lam_cm=wavelength_cm(1600.0), lam_band=(wavelength_cm(1660.5), wavelength_cm(1525.0)),
        e_pkt_1w=e_pkt_1w,
    )


if __name__ == "__main__":
    s = summary()
    for lat in (45, 55, 60, 65, 70, 75):
        print(f"широта {lat}° — макс. угол места {max_elevation_deg(lat):.1f}°")
    print(f"угол места 5° на широте {s['lat_el5']:.1f}°, КА под горизонтом выше {s['lat_el0']:.1f}°")
    for gt, name in GT_CASES:
        print(f"UP G/T={gt:+.0f} ({name}): C/N0={s['up'][gt]:.1f} дБГц, Rmax={s['r_up'][gt]:.0f} бит/с")
    for e in EIRP_CASES:
        print(f"DOWN EIRP={e:.0f}: C/N0={s['dn'][e]:.1f} дБГц, Rmax={s['r_dn'][e]:.0f} бит/с")
    print(f"Tsys={s['t_sys']:.0f} К, G/T борта={s['gt_board']:.1f} дБ/К")
    print(f"G/T КА для 100 бит/с: {s['gt_req_100']:+.1f} дБ/К; для {SCEN_RATE} бит/с: {s['gt_req_scen']:+.1f} дБ/К")
    print(f"ЭИИМ КА для 100 бит/с на борт: {eirp_required(100):.1f} дБВт")
    print(f"масса модуля {D.MASS_MODULE} г, комплект {D.MASS_KIT} г, облегчённый {D.MASS_KIT_LIGHT} г")
    for name, wh, mah, t in s["scenarios"]:
        print(f"{name}: ПД {t:.0f} с/ч, {wh:.3f} Вт·ч, {mah:.1f} мА·ч")
