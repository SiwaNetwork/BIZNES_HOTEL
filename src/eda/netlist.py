"""Модель изделия для электрической схемы, перечня элементов и платы KiCad.

Один источник: элементы (позиционное обозначение, тип, номинал, корпус, распиновка, размещение)
и цепи (имя цепи -> выводы). Из него строятся Э3/ПЭ3/спецификация (reportlab) и проект KiCad.
"""
from collections import OrderedDict
from dataclasses import dataclass, field


@dataclass
class Pin:
    num: str
    name: str
    side: str = "L"          # сторона УГО: L, R, T (питание), B (общий)
    etype: str = "passive"   # тип вывода KiCad: input, output, bidirectional, power_in, power_out, passive, no_connect


@dataclass
class Part:
    ref: str                  # позиционное обозначение по ГОСТ 2.710 (DA1, R5, C12, ...)
    kind: str                 # R, C, L, FB, IC, XTAL, OSC, SAW, CONN, COAX, TP, MH, SHIELD
    value: str                # номинал или тип (для ПЭ3: «Наименование»)
    footprint: str            # KiCad «библиотека:посадочное место»
    pins: list                # [Pin]
    name_ru: str = ""         # наименование для ПЭ3/спецификации (без номинала)
    mpn: str = ""             # обозначение изготовителя
    mfr: str = ""
    note: str = ""            # графа «Примечание» ПЭ3
    pos: tuple = (0.0, 0.0, 0.0)   # размещение на плате: x, y (мм, от левого нижнего угла, вид сверху), поворот
    height: float = 0.5
    body: tuple = (1.0, 0.5)  # габарит корпуса по x, y (мм) — для 3D и сборочного чертежа
    sch: tuple = None         # размещение на схеме (x, y) в мм; None — автоматически
    group: str = ""           # функциональная группа (A1...A7 по Э1)
    dnp: bool = False
    mass_g: float = 0.0

    def pin(self, num):
        for p in self.pins:
            if p.num == str(num):
                return p
        raise KeyError(f"{self.ref}: нет вывода {num}")


class Design:
    def __init__(self, code, title):
        self.code = code
        self.title = title
        self.parts = OrderedDict()
        self.nets = OrderedDict()      # имя цепи -> [(ref, pin)]
        self.net_class = {}            # имя цепи -> класс (RF, PWR, ...)

    # ---------------------------------------------------------------- построение
    def add(self, part, **conn):
        """conn: номер_вывода=цепь; номера с буквами передаются как p_A1=... ."""
        if part.ref in self.parts:
            raise ValueError(f"повтор {part.ref}")
        self.parts[part.ref] = part
        for k, net in conn.items():
            self.connect(net, part.ref, k[2:] if k.startswith("p_") else k)
        return part

    def connect(self, net, ref, pin):
        pin = str(pin)
        part = self.parts[ref]
        part.pin(pin)                   # проверка существования вывода
        lst = self.nets.setdefault(net, [])
        for n, items in self.nets.items():
            if (ref, pin) in items and n != net:
                raise ValueError(f"{ref}.{pin} уже в цепи {n}, попытка подключить к {net}")
        if (ref, pin) not in lst:
            lst.append((ref, pin))

    def pins_of(self, ref):
        """{вывод: цепь} элемента."""
        out = {}
        for net, items in self.nets.items():
            for r, p in items:
                if r == ref:
                    out[p] = net
        return out

    def net_of(self, ref, pin):
        for net, items in self.nets.items():
            if (ref, str(pin)) in items:
                return net
        return None

    # ---------------------------------------------------------------- проверки
    def check(self, allow_nc=()):
        """Возвращает список замечаний: неподключённые выводы, цепи из одного вывода."""
        problems = []
        for ref, part in self.parts.items():
            conn = self.pins_of(ref)
            for p in part.pins:
                if p.num not in conn and p.etype != "no_connect" and (ref, p.num) not in allow_nc:
                    problems.append(f"{ref}.{p.num} ({p.name}) не подключён")
        for net, items in self.nets.items():
            if len(items) < 2 and not net.startswith("NC"):
                problems.append(f"цепь {net} содержит один вывод {items}")
        return problems

    # ---------------------------------------------------------------- перечень
    def bom_groups(self):
        """Группировка для ПЭ3: (префикс, [(refs, part)]) с объединением одинаковых соседних позиций."""
        import re
        key = lambda r: (re.match(r"[A-Z]+", r).group(0), int(re.search(r"\d+", r).group(0)))
        refs = sorted(self.parts, key=key)
        rows = []
        for r in refs:
            p = self.parts[r]
            ident = (p.name_ru, p.value, p.mpn, p.note)
            if rows and rows[-1][0] == ident and key(rows[-1][1][-1])[0] == key(r)[0] \
                    and key(rows[-1][1][-1])[1] + 1 == key(r)[1]:
                rows[-1][1].append(r)
            else:
                rows.append((ident, [r], p))
                continue
        return [(refs_, part) for _, refs_, part in rows]
