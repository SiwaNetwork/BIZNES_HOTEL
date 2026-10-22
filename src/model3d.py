"""3D-модель модуля ТЕНШ.464512.001 и антенны WA1 (CadQuery).

Выход (каталог cad/):
  module.step           — модуль (плата + элементы + экран), сборка с цветами
  antenna.step          — антенна WA1 на плате-носителе
  assembly.step         — модуль + антенна + кабель (массогабаритный макет)
  mockup_module.stl,
  mockup_antenna.stl    — для печати массогабаритного макета
  renders/*.png         — изометрические виды
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

import design as D

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cad"

PALETTE = {
    "board": (0.05, 0.35, 0.18),
    "pad": (0.85, 0.7, 0.3),
    "gold": (0.9, 0.75, 0.35),
    "ic": (0.12, 0.12, 0.13),
    "metal": (0.75, 0.75, 0.78),
    "ferrite": (0.3, 0.3, 0.32),
    "tant": (0.15, 0.15, 0.15),
    "shield": (0.82, 0.83, 0.86),
    "passive": (0.55, 0.45, 0.35),
    "ceramic": (0.93, 0.92, 0.88),
    "silver": (0.8, 0.8, 0.82),
    "cable": (0.25, 0.25, 0.28),
    "antpcb": (0.08, 0.3, 0.16),
}


def board():
    b = (cq.Workplane("XY").box(D.BOARD_L, D.BOARD_W, D.BOARD_T, centered=False)
         .edges("|Z").fillet(D.CORNER_R))
    # полуотверстия
    pts = [(x, y) for _, x, y, _ in D.pad_positions()]
    b = b.faces(">Z").workplane(origin=(0, 0, D.BOARD_T)).pushPoints(pts).hole(D.PAD_HOLE_D)
    b = b.faces(">Z").workplane(origin=(0, 0, D.BOARD_T)).pushPoints(D.HOLES).hole(D.HOLE_D)
    return b


def pads():
    w = cq.Workplane("XY")
    res = None
    for _, x, y, side in D.pad_positions():
        yc = D.PAD_L / 2 if side == "bottom" else D.BOARD_W - D.PAD_L / 2
        p = (cq.Workplane("XY").box(D.PAD_W, D.PAD_L, 0.04).translate((x, yc, D.BOARD_T + 0.02))
             .cut(cq.Workplane("XY").cylinder(1, D.PAD_HOLE_D / 2).translate((x, y, D.BOARD_T))))
        res = p if res is None else res.union(p)
    return res


def comp_solid(name, x, y, l, w, h, kind):
    z0 = D.BOARD_T
    if kind == "gold":   # розетка U.FL: основание + цилиндр
        s = cq.Workplane("XY").box(l, w, 0.5, centered=(True, True, False)).translate((x, y, z0))
        s = s.union(cq.Workplane("XY").circle(1.0).circle(0.6).extrude(h - 0.5).translate((x, y, z0 + 0.5)))
        return s
    if kind == "tant":
        s = cq.Workplane("XY").box(l, w, h, centered=(True, True, False)).translate((x, y, z0))
        return s.edges("|X").fillet(0.15)
    s = cq.Workplane("XY").box(l, w, h, centered=(True, True, False)).translate((x, y, z0))
    return s


def shield():
    sh = D.SHIELD
    outer = cq.Workplane("XY").box(sh["l"], sh["w"], sh["h"], centered=False)
    inner = cq.Workplane("XY").box(sh["l"] - 0.2, sh["w"] - 0.2, sh["h"] - 0.1, centered=False).translate((0.1, 0.1, 0))
    s = outer.cut(inner).translate((sh["x"], sh["y"], D.BOARD_T))
    # отверстия для пайки/контроля в крышке
    pts = [(sh["x"] + 2 + i * 3.2, sh["y"] + 2 + j * 3.2) for i in range(4) for j in range(5)]
    s = s.faces(">Z").workplane(origin=(0, 0, D.BOARD_T + sh["h"])).pushPoints(pts).hole(0.6)
    return s


def module_parts(with_shield=True, include_hidden=False):
    """Детали модуля. include_hidden=True — с элементами под экраном (для STEP)."""
    parts = [("board", board(), "board"), ("pads", pads(), "pad")]
    sh = D.SHIELD
    skip = with_shield and not include_hidden
    for name, x, y, l, w, h, _, kind in D.COMPONENTS:
        inside = sh["x"] < x < sh["x"] + sh["l"] and sh["y"] < y < sh["y"] + sh["w"]
        if inside and skip:
            continue   # под экраном — на изображениях не видны
        parts.append((name, comp_solid(name, x, y, l, w, h, kind), kind))
    for i, (x, y, r, l, w, h) in enumerate(D.PASSIVES):
        if skip and sh["x"] < x < sh["x"] + sh["l"] and sh["y"] < y < sh["y"] + sh["w"]:
            continue
        parts.append((f"P{i}", cq.Workplane("XY").box(l, w, h, centered=(True, True, False))
                      .translate((x, y, D.BOARD_T)), "passive"))
    if with_shield:
        parts.append(("shield", shield(), "shield"))
    return parts


def antenna_parts(origin=(0.0, 0.0, 0.0)):
    ox, oy, oz = origin
    L, T, P = D.ANT_L, D.ANT_T, D.ANT_PATCH
    pcb = (cq.Workplane("XY").box(D.ANT_PCB_L, D.ANT_PCB_L, D.ANT_PCB_T, centered=(True, True, False))
           .edges("|Z").fillet(1.5))
    cer = cq.Workplane("XY").box(L, L, T, centered=(True, True, False)).translate((0, 0, D.ANT_PCB_T))
    cer = cer.edges("|Z").chamfer(1.0)
    patch = (cq.Workplane("XY").rect(P, P).extrude(0.03).translate((0, 0, D.ANT_PCB_T + T)))
    # два возбуждающих штыря (круговая поляризация, квадратурное питание)
    feeds = (cq.Workplane("XY").pushPoints([(-3.6, 0), (0, -3.6)]).circle(0.7).extrude(0.05)
             .translate((0, 0, D.ANT_PCB_T + T + 0.03)))
    conn = (cq.Workplane("XY").box(3, 3, 0.5, centered=(True, True, False))
            .union(cq.Workplane("XY").circle(1.0).circle(0.6).extrude(0.75).translate((0, 0, 0.5)))
            .rotate((0, 0, 0), (1, 0, 0), 180).translate((-10.5, -10.5, 0)))
    parts = [("ant_pcb", pcb, "antpcb"), ("ant_ceramic", cer, "ceramic"),
             ("ant_patch", patch, "silver"), ("ant_feeds", feeds, "silver"), ("ant_conn", conn, "gold")]
    return [(n, s.translate((ox, oy, oz)), k) for n, s, k in parts]


def cable_parts(p0, p1, sag=6.0):
    """Кабель ⌀1,13 мм между разъёмами — сплайн."""
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    mid = (min(x0, x1) - 2.5, (y0 + y1) / 2, (z0 + z1) / 2 + 1.0)
    path = cq.Workplane("XY").spline([p0, mid, p1], includeCurrent=False)
    prof = cq.Workplane(cq.Plane(origin=p0, xDir=(1, 0, 0) if abs(x1 - x0) < 1e-3 else (0, 1, 0),
                                 normal=(0, 0, -1) if z1 < z0 else (0, 0, 1))).circle(D.CABLE_D / 2)
    try:
        s = prof.sweep(path, isFrenet=True)
    except Exception:
        s = cq.Workplane("XY")
    return [("cable", s, "cable")]


def to_assembly(parts, name):
    asm = cq.Assembly(name=name)
    for n, s, k in parts:
        r, g, b = PALETTE[k]
        asm.add(s, name=n, color=cq.Color(r, g, b))
    return asm


def union(parts):
    res = None
    for _, s, _ in parts:
        try:
            res = s if res is None else res.union(s)
        except Exception:
            pass
    return res


# ---------------------------------------------------------------- рендер
def _tess_unused(parts, tol=0.05):
    tris, cols = [], []
    for _, s, k in parts:
        for solid in s.vals():
            try:
                vs, fs = solid.tessellate(tol, 0.3)
            except Exception:
                continue
            v = np.array([(p.x, p.y, p.z) for p in vs])
            for f in fs:
                tris.append(v[list(f)])
                cols.append(PALETTE[k])
    return np.array(tris), np.array(cols)


def render(parts, path, elev=28, azim=-58, size=(1600, 1200), zoom=1.0, edges=True):
    """Рендер средствами VTK (запуск под xvfb-run при отсутствии дисплея)."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    for _, s, k in parts:
        for solid in s.vals():
            try:
                vs, fs = solid.tessellate(0.02, 0.2)
            except Exception:
                continue
            if not fs:
                continue
            pts = vtk.vtkPoints()
            pts.SetData(numpy_to_vtk(np.array([(p.x, p.y, p.z) for p in vs], dtype=float), deep=True))
            f = np.array(fs, dtype=np.int64)
            cells = np.hstack([np.full((len(f), 1), 3, dtype=np.int64), f]).ravel()
            ca = vtk.vtkCellArray()
            ca.SetCells(len(f), numpy_to_vtkIdTypeArray(cells, deep=True))
            pd = vtk.vtkPolyData()
            pd.SetPoints(pts)
            pd.SetPolys(ca)
            m = vtk.vtkPolyDataMapper()
            m.SetInputData(pd)
            act = vtk.vtkActor()
            act.SetMapper(m)
            pr = act.GetProperty()
            pr.SetColor(*PALETTE[k])
            pr.SetAmbient(0.25)
            pr.SetDiffuse(0.75)
            pr.SetSpecular(0.35 if k in ("shield", "metal", "silver", "gold", "pad") else 0.08)
            pr.SetSpecularPower(30)
            ren.AddActor(act)
            if edges:
                fe = vtk.vtkFeatureEdges()
                fe.SetInputData(pd)
                fe.BoundaryEdgesOn(); fe.FeatureEdgesOn(); fe.SetFeatureAngle(35)
                fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff(); fe.ColoringOff()
                em = vtk.vtkPolyDataMapper()
                em.SetInputConnection(fe.GetOutputPort())
                ea = vtk.vtkActor()
                ea.SetMapper(em)
                ea.GetProperty().SetColor(0.1, 0.1, 0.1)
                ea.GetProperty().SetLineWidth(1.2)
                ea.GetProperty().SetOpacity(0.55)
                ren.AddActor(ea)
    cam = ren.GetActiveCamera()
    e, a = math.radians(elev), math.radians(azim)
    cam.SetFocalPoint(0, 0, 0)
    cam.SetPosition(math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))
    cam.SetViewUp(0, 0, 1)
    cam.ParallelProjectionOn()
    ren.ResetCamera()
    cam.Zoom(zoom)
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetMultiSamples(0)
    rw.AddRenderer(ren)
    rw.SetSize(*size)
    rw.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.ReadFrontBufferOff()
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(str(path))
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()


def main(render_only=False):
    OUT.mkdir(exist_ok=True)
    (OUT / "renders").mkdir(exist_ok=True)
    mod = module_parts(True)
    mod_full = module_parts(True, include_hidden=True)
    mod_open = module_parts(False)
    xw1 = next(c for c in D.COMPONENTS if c[0] == "XW1")
    p0 = (xw1[1], xw1[2], D.BOARD_T + 1.3)

    def geometry(dy):
        origin = (D.BOARD_L / 2, D.BOARD_W + dy, 0.0)
        p1 = (origin[0] - 10.5, origin[1] - 10.5, -0.8)
        return origin, p1

    def cable_length(dy):
        _, p1 = geometry(dy)
        (x0, y0, z0), (x1, y1, z1) = p0, p1
        mid = (min(x0, x1) - 2.5, (y0 + y1) / 2, (z0 + z1) / 2 + 1.0)
        return cq.Workplane("XY").spline([p0, mid, p1], includeCurrent=False).val().Length()

    lo, hi = 5.0, 80.0                      # подбор положения антенны под длину кабеля D.CABLE_LEN
    for _ in range(40):
        mid_dy = (lo + hi) / 2
        lo, hi = (mid_dy, hi) if cable_length(mid_dy) < D.CABLE_LEN else (lo, mid_dy)
    ant_origin, p1 = geometry((lo + hi) / 2)
    print(f"кабель: {cable_length((lo + hi) / 2):.1f} мм")
    ant = antenna_parts(ant_origin)
    cab = cable_parts(p0, p1)

    if not render_only:
        to_assembly(mod_full, "module").save(str(OUT / "module.step"))
        to_assembly(antenna_parts(), "antenna_WA1").save(str(OUT / "antenna.step"))
        to_assembly(mod_full + ant + cab, "assembly").save(str(OUT / "assembly.step"))
        cq.exporters.export(union(mod), str(OUT / "mockup_module.stl"), tolerance=0.02)
        cq.exporters.export(union(antenna_parts()), str(OUT / "mockup_antenna.stl"), tolerance=0.02)

    R = OUT / "renders"
    render(mod, R / "module_iso.png", zoom=1.25)
    render(mod_open, R / "module_no_shield.png", zoom=1.25)
    render(mod, R / "module_bottom.png", elev=-35, azim=-58, zoom=1.25)
    render(antenna_parts(), R / "antenna_iso.png", elev=32, azim=-50, zoom=1.2)
    render(mod + ant + cab, R / "assembly_iso.png", elev=38, azim=-62, size=(1600, 1400), zoom=1.15)
    print("ok")


if __name__ == "__main__":
    main("--render-only" in sys.argv)
