"""Сборка электрической части изделий: проверка соединений, проект KiCad (схема, плата, трассировка, DRC,
производственные файлы) и документы Э3, ПЭ3, спецификация.

  python3 src/build_hw.py iridium [--no-route]
  python3 src/build_hw.py lband   [--no-route]
"""
import importlib
import os
import sys

os.environ.setdefault("KICAD7_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
os.environ.setdefault("KICAD7_SYMBOL_DIR", "/usr/share/kicad/symbols")
os.environ.setdefault("KICAD7_3DMODEL_DIR", "/usr/share/kicad/3dmodels")
from pathlib import Path

import pcbnew

import gost
from eda import footprints as fpl
from eda import kicad_pcb, kicad_sch

ROOT = gost.ROOT
KICAD = ROOT / "kicad"


def make_footprints(lib):
    fpl.castellated_row(lib, 12)
    fpl.castellated_row(lib, 10)
    fpl.samtec_ss4_iridium(lib)
    fpl.supercap_horizontal(lib, side="L")
    fpl.supercap_horizontal(lib, side="R")
    fpl.bga524n6(lib)
    fpl.bgs12p2l6(lib)
    fpl.qfn10_2x2(lib)


def kicad_env():
    """Глобальные таблицы библиотек KiCad (в контейнере без GUI их нет)."""
    import shutil
    cfg = Path.home() / ".config/kicad/7.0"
    cfg.mkdir(parents=True, exist_ok=True)
    for t in ("fp-lib-table", "sym-lib-table"):
        src = Path("/usr/share/kicad/template") / t
        if src.exists() and not (cfg / t).exists():
            shutil.copy(src, cfg / t)


def build_kicad(mod, route=True):
    kicad_env()
    d = mod.design()
    problems = d.check()
    for s in problems:
        print("  [соединения]", s)
    name = mod.CODE.replace("ТЕНШ", "TENSH")       # латиница в именах файлов — для САПР и производства
    out = KICAD / name
    out.mkdir(parents=True, exist_ok=True)
    lib = out / "TENSH.pretty"
    make_footprints(lib)
    # схема
    kicad_sch.write(d, out / f"{name}.kicad_sch", name, paper="A1", sheet_w=841)
    kicad_sch.write_sym_lib(d, out / "TENSH.kicad_sym")
    # плата
    W, H = mod.BOARD
    b = kicad_pcb.Builder(d, out, name, W, H, thickness=mod.THICK, layers=mod.LAYERS, local_lib=lib)
    b.rules(**mod.RULES)
    b.outline(r=mod.CORNER_R)
    b.place_all()
    mod.pcb_extra(b)
    b.project_file()
    b.reload()
    if hasattr(mod, "pre_route"):
        print(f"  отверстия у площадок «земли»: {mod.pre_route(b)}")
    if route:
        n = b.route(passes=mod.ROUTE_PASSES)
        print(f"  трассировка: {n[0]} отрезков, {n[1]} переходных отверстий")
        if hasattr(mod, "post_route"):
            print(f"  сшивка земли: {mod.post_route(b)} переходных отверстий")
    b.fill()
    viol, unc, txt = b.drc()
    print(f"  DRC: нарушений {viol}, неразведённых {unc}")
    b.save()
    fab = b.fab_outputs(out / "fab", name)
    return d, b, viol, unc, fab


if __name__ == "__main__":
    which = sys.argv[1]
    mod = importlib.import_module(f"hw.{which}")
    gost.register_fonts()
    build_kicad(mod, route="--no-route" not in sys.argv)
