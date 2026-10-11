"""Сборка комплекта: python3 src/build.py  (3D-рендер требует дисплей; без него — xvfb-run).

Порядок: 3D-модель и рендеры → Э1 → сборочный чертёж платы → ГЧ → ПЗ (с включением рисунков).
"""
import subprocess
import sys
from pathlib import Path

import gost

ROOT = gost.ROOT
DOCS = ROOT / "docs"
TMP = ROOT / "build"


def e1_figure():
    """Поле схемы Э1 без рамки и основной надписи — растр для рисунка ПЗ, обрезанный по содержимому."""
    import gen_e1
    from PIL import Image, ImageOps
    pdf = TMP / "e1_bare.pdf"
    gen_e1.build(pdf, bare=True)
    subprocess.run(["pdftoppm", "-r", "250", "-png", "-singlefile", str(pdf), str(TMP / "e1_bare")], check=True)
    png = TMP / "e1_bare.png"
    im = Image.open(png).convert("RGB")
    box = ImageOps.invert(im).getbbox()
    pad = 20
    im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width),
             min(box[3] + pad, im.height))).save(png)
    return png


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
    gen_pcb.build(DOCS / f"{gen_pcb.DESIGNATION}_СБ.pdf")
    for old in DOCS.glob("ТЕНШ.758726.001*.pdf"):    # прежнее обозначение платы
        old.unlink()
    gen_gch.build(DOCS / "ТЕНШ.464512.001_ГЧ.pdf", ROOT / "cad" / "renders" / "assembly_iso.png")
    gen_pz.build(DOCS / "ТЕНШ.464512.001_ПЗ.pdf", e1_figure())
    print("Готово:", *sorted(p.name for p in DOCS.glob("*.pdf")), sep="\n  ")


if __name__ == "__main__":
    main()
