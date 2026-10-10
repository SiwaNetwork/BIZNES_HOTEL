"""Расчёты для справки ТЕНШ.464512.001 ПЗ.

Энергетика радиолинии «борт — ГСО КА», массовый и энергетический бюджет.
Все исходные значения — проектные оценки стадии технического проекта.
Запуск: python3 src/calc.py — печатает таблицы, используемые в ПЗ.
"""
import math

K_DBW = -228.6          # постоянная Больцмана, дБВт/(К·Гц)
RE_KM = 6378.137        # экваториальный радиус Земли, км
H_GEO_KM = 35786.0      # высота ГСО, км
C = 299_792_458.0


def slant_range_km(elev_deg: float) -> float:
    """Наклонная дальность до КА на ГСО при угле места elev_deg."""
    e = math.radians(elev_deg)
    r = RE_KM + H_GEO_KM
    return math.sqrt(r**2 - (RE_KM * math.cos(e))**2) - RE_KM * math.sin(e)


def max_elevation_deg(lat_deg: float) -> float:
    """Максимальный угол места ГСО КА (КА на меридиане точки)."""
    phi = math.radians(lat_deg)
    k = RE_KM / (RE_KM + H_GEO_KM)
    return math.degrees(math.atan((math.cos(phi) - k) / math.sin(phi))) if lat_deg else 90.0


def fspl_db(d_km: float, f_mhz: float) -> float:
    lam = C / (f_mhz * 1e6)
    return 20 * math.log10(4 * math.pi * d_km * 1e3 / lam)


def db(x: float) -> float:
    return 10 * math.log10(x)


# ---------------------------------------------------------------- радиолиния
ELEV_DEG = 20.0  # расчётный угол места (широты ~55–60° с.ш., КА не на меридиане)


def uplink(gt_sat_dbk: float, p_tx_dbm: float = 30.0):
    """Линия «борт → КА» (1626,5–1660,5 МГц)."""
    d = slant_range_km(ELEV_DEG)
    rows = [
        ("Выходная мощность УМ", p_tx_dbm - 30, "дБВт"),
        ("Потери в тракте (фильтр, коммутатор, кабель)", -1.2, "дБ"),
        ("Усиление антенны при угле места 20°", -1.0, "дБи"),
    ]
    eirp = sum(r[1] for r in rows)
    rows.append(("ЭИИМ борта", eirp, "дБВт"))
    lfs = fspl_db(d, 1643.5)
    rows += [
        ("Наклонная дальность", d, "км"),
        ("Потери в свободном пространстве", -lfs, "дБ"),
        ("Поляризационные и атмосферные потери", -0.8, "дБ"),
        ("Затенение телом птицы, крен, разброс ДН", -3.0, "дБ"),
        ("Добротность КА G/T", gt_sat_dbk, "дБ/К"),
    ]
    cn0 = eirp - lfs - 0.8 - 3.0 + gt_sat_dbk - K_DBW
    rows.append(("Отношение C/N0", cn0, "дБГц"))
    return rows, cn0


def downlink(eirp_sat_dbw: float):
    """Линия «КА → борт» (1525–1559 МГц)."""
    d = slant_range_km(ELEV_DEG)
    l_feed = 1.2
    t_ant = 200.0       # видит тело птицы и подстилающую поверхность
    nf_lna = 1.0
    t_lna = 290 * (10 ** (nf_lna / 10) - 1)
    a = 10 ** (-l_feed / 10)
    t_sys = t_ant * a + 290 * (1 - a) + t_lna
    g_ant = -1.0
    gt = g_ant - l_feed - db(t_sys) + 0  # приведено ко входу антенны
    lfs = fspl_db(d, 1542.0)
    rows = [
        ("ЭИИМ КА на несущую", eirp_sat_dbw, "дБВт"),
        ("Наклонная дальность", d, "км"),
        ("Потери в свободном пространстве", -lfs, "дБ"),
        ("Поляризационные и атмосферные потери", -0.8, "дБ"),
        ("Затенение телом птицы, крен, разброс ДН", -3.0, "дБ"),
        ("Шумовая температура системы", t_sys, "К"),
        ("Добротность борта G/T", gt, "дБ/К"),
    ]
    cn0 = eirp_sat_dbw - lfs - 0.8 - 3.0 + gt - K_DBW
    rows.append(("Отношение C/N0", cn0, "дБГц"))
    return rows, cn0


EBN0_REQ = 4.0   # π/2-BPSK + LDPC 1/2, BER 1e-5, с учётом потерь реализации
MARGIN = 3.0     # запас на замирания


def max_rate_bps(cn0: float) -> float:
    return 10 ** ((cn0 - EBN0_REQ - MARGIN) / 10)


# ---------------------------------------------------------------- масса
MASS = [
    ("Плата печатная 32×22×0,6 мм, 4 слоя", 0.9),
    ("Электрорадиоэлементы (ИС, пассивные)", 1.6),
    ("Экран РЧ-тракта (луженая сталь 0,1 мм)", 0.9),
    ("Накопительные конденсаторы (2 шт.)", 0.4),
    ("Влагозащитное покрытие, припой", 0.2),
]
MASS_ANT = [
    ("Антенна WA1 двухслойная полосковая 42×42×6 мм", 4.8),
    ("Кабель коаксиальный ⌀1,13 мм, 60 мм, с разъёмами", 0.6),
    ("Элементы крепления, клей", 0.5),
]


# ---------------------------------------------------------------- энергетика
V_BAT = 3.7
MODES = [  # режим, мощность потребления, Вт
    ("Сон (часы реального времени, пробуждение)", 0.0002),
    ("Приём (дежурный, синхронизация)", 0.085),
    ("Передача, Pвых = 30 дБм (1 Вт)", 2.6),
    ("Передача, Pвых = 27 дБм (0,5 Вт)", 1.5),
]


def scenario(name, tx_s_per_h, tx_w, rx_s_per_h):
    sleep_s = 3600 - tx_s_per_h - rx_s_per_h
    wh = (tx_s_per_h * tx_w + rx_s_per_h * 0.085 + sleep_s * 0.0002) / 3600
    return name, wh, wh / V_BAT * 1000


def packet_tx_time(payload_bytes, rate_bps, overhead_s=0.4):
    """Время передачи пакета: преамбула/синхро + данные (кодовая скорость 1/2 учтена в rate)."""
    return overhead_s + (payload_bytes + 16) * 8 / rate_bps


SCENARIOS_DEF = [
    # имя, пакетов в час, байт, скорость, мощность ТХ, секунд приёма в час
    ("А — телеметрия раз в 5 мин, приём команд 10 %", 12, 64, 600, 2.6, 360),
    ("Б — телеметрия раз в 1 мин, приём команд 10 %", 60, 64, 600, 2.6, 360),
    ("В — телеметрия раз в 1 мин, непрерывный приём", 60, 64, 600, 2.6, 3600),
    ("Г — кадр-превью 2 кБ раз в 10 мин + Б", 60, 64, 600, 2.6, 360),
]


def scenarios():
    out = []
    for name, n, nbytes, rate, ptx, rx in SCENARIOS_DEF:
        t = n * packet_tx_time(nbytes, rate)
        if name.startswith("Г"):
            t += 6 * packet_tx_time(2048, 2400)
        out.append(scenario(name, t, ptx, rx) + (t,))
    return out


if __name__ == "__main__":
    for lat in (45, 55, 60, 65, 70, 75):
        print(f"широта {lat}° — макс. угол места {max_elevation_deg(lat):.1f}°")
    for gt in (0.0, 10.0):
        rows, cn0 = uplink(gt)
        print(f"\nUP G/T={gt}: C/N0={cn0:.1f} дБГц, Rmax={max_rate_bps(cn0):.0f} бит/с")
        for r in rows:
            print("   ", r)
    for e in (20.0, 30.0):
        rows, cn0 = downlink(e)
        print(f"\nDOWN EIRP={e}: C/N0={cn0:.1f}, Rmax={max_rate_bps(cn0):.0f}")
        for r in rows:
            print("   ", r)
    print("\nмасса модуля", sum(m for _, m in MASS), "антенный узел", sum(m for _, m in MASS_ANT))
    for s in scenarios():
        print(s)
