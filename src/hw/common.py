"""Типовые элементы (резисторы, конденсаторы, дроссели) с наименованиями для перечня элементов."""
import re

from eda.netlist import Part, Pin

SIZES = {  # типоразмер -> (посадочное место KiCad R/C/L, габарит x, y, высота, масса г)
    "0201": ("0201_0603Metric", 0.6, 0.3, 0.3, 0.0002),
    "0402": ("0402_1005Metric", 1.0, 0.5, 0.5, 0.0006),
    "0603": ("0603_1608Metric", 1.6, 0.8, 0.8, 0.003),
    "0805": ("0805_2012Metric", 2.0, 1.25, 1.25, 0.01),
}


def two(kind, ref, value, size="0402", mpn="", mfr="", name_ru="", note="", pos=(0, 0, 0), fp=None, body=None, height=None, mass=None):
    lib = {"R": "Resistor_SMD:R_", "C": "Capacitor_SMD:C_", "L": "Inductor_SMD:L_", "FB": "Inductor_SMD:L_"}[kind]
    f, bx, by, bh, m = SIZES[size]
    return Part(ref, kind, value, fp or (lib + f), [Pin("1", "1"), Pin("2", "2")], name_ru=name_ru, mpn=mpn, mfr=mfr,
                note=note, pos=pos, body=body or (bx, by), height=height or bh, mass_g=m if mass is None else mass)


def R(ref, value, size="0402", tol="1 %", mpn="", mfr="", **kw):
    nm = kw.pop("name_ru", f"Резистор {mpn} {value} ±{tol}".replace("  ", " ").strip() if mpn else
                f"Резистор {size} {value} ±{tol}")
    return two("R", ref, value, size, mpn, mfr, nm, **kw)


def C(ref, value, size="0402", spec="", mpn="", mfr="", **kw):
    nm = kw.pop("name_ru", f"Конденсатор {mpn} {value}{(' ' + spec) if spec else ''}".strip())
    return two("C", ref, value, size, mpn, mfr, nm, **kw)


def L(ref, value, size="0402", spec="", mpn="", mfr="", **kw):
    nm = kw.pop("name_ru", f"Катушка индуктивности {mpn} {value}{(' ' + spec) if spec else ''}".strip())
    return two("L", ref, value, size, mpn, mfr, nm, **kw)


def FB(ref, value, size="0402", mpn="", mfr="", **kw):
    nm = kw.pop("name_ru", f"Фильтр помехоподавляющий {mpn} {value}".strip())
    return two("FB", ref, value, size, mpn, mfr, nm, **kw)


def ic(ref, value, footprint, pins, name_ru, mpn="", mfr="", note="", pos=(0, 0, 0), body=(1, 1), height=0.8,
       kind="IC", mass=0.0, group=""):
    """pins: строка 'num:NAME:side:etype, ...' или список Pin."""
    if isinstance(pins, str):
        lst = []
        for item in re.split(r",\s*", pins.strip()):
            f = item.split(":")
            lst.append(Pin(f[0], f[1], f[2] if len(f) > 2 and f[2] else "L", f[3] if len(f) > 3 else "passive"))
        pins = lst
    return Part(ref, kind, value, footprint, pins, name_ru=name_ru, mpn=mpn or value, mfr=mfr, note=note, pos=pos,
                body=body, height=height, mass_g=mass, group=group)
