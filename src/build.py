"""Сборка комплекта: python3 src/build.py  (3D-рендер требует дисплей; без него — xvfb-run).

Порядок: 3D-модель и рендеры → Э1 → чертёж платы → ГЧ → ПЗ (с включением рисунков).
"""
import subprocess
import sys
from pathlib import Path

import gost

ROOT = gost.ROOT
DOCS = ROOT / "docs"
TMP = ROOT / "build"


def main():
    DOCS.mkdir(exist_ok=True)
    TMP.mkdir(exist_ok=True)
    gost.register_fonts()
    if "--no-3d" not in sys.argv:
        import model3d
        model3d.main()
    import gen_e1, gen_gch, gen_pcb, gen_pz
    e1 = DOCS / "ТЕНШ.464512.001_Э1.pdf"
    gen_e1.build(e1)
    gen_pcb.build(DOCS / "ТЕНШ.758726.001.pdf")
    gen_gch.build(DOCS / "ТЕНШ.464512.001_ГЧ.pdf", ROOT / "cad" / "renders" / "assembly_iso.png")
    subprocess.run(["pdftoppm", "-r", "220", "-png", "-singlefile", str(e1), str(TMP / "e1")], check=True)
    gen_pz.build(DOCS / "ТЕНШ.464512.001_ПЗ.pdf", TMP / "e1.png")
    print("Готово:", *sorted(p.name for p in DOCS.glob("*.pdf")), sep="\n  ")


if __name__ == "__main__":
    main()
