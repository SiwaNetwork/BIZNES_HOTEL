"""Плата KiCad 7 из модели Design: контур, слои, посадочные места, цепи, полигоны,
автотрассировка Freerouting, проверка DRC и выпуск производственных файлов (Gerber, сверловка, координаты, BOM).
"""
import csv
import json
import math
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pcbnew

from . import ses
from .netlist import Design

FP_ROOT = Path("/usr/share/kicad/footprints")
FREEROUTING = Path(os.environ.get("FREEROUTING_JAR", "/opt/tools/freerouting.jar"))
mm = pcbnew.FromMM


OX, OY = 40.0, 160.0      # положение левого нижнего угла платы на листе KiCad, мм


def V(x, y):
    """Координаты изделия (Y вверх, от левого нижнего угла) -> координаты KiCad (Y вниз)."""
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


def U(p):
    """Координаты KiCad -> координаты изделия, мм."""
    return pcbnew.ToMM(p.x) - OX, OY - pcbnew.ToMM(p.y)


def UB(bb):
    """Прямоугольник KiCad -> (x0, y0, x1, y1) изделия."""
    return (pcbnew.ToMM(bb.GetLeft()) - OX, OY - pcbnew.ToMM(bb.GetBottom()),
            pcbnew.ToMM(bb.GetRight()) - OX, OY - pcbnew.ToMM(bb.GetTop()))


class Builder:
    def __init__(self, design: Design, outdir, name, board_w, board_h, thickness=0.6, layers=4, local_lib=None):
        self.d = design
        self.out = Path(outdir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.name = name
        self.W, self.H = board_w, board_h
        self.local_lib = Path(local_lib) if local_lib else None
        b = self.b = pcbnew.BOARD()
        b.SetCopperLayerCount(layers)
        ds = b.GetDesignSettings()
        ds.SetBoardThickness(mm(thickness))
        ds.SetAuxOrigin(V(0, 0))
        ds.SetGridOrigin(V(0, 0))
        self.nets = {}
        self.fps = {}

    # ---------------------------------------------------------------- правила
    def rules(self, track=0.1, clearance=0.1, via=0.45, drill=0.2, classes=None):
        ds = self.b.GetDesignSettings()
        self.via_d, self.via_drill = via, drill
        ds.m_TrackMinWidth = mm(track)
        ds.m_MinClearance = mm(clearance)
        ds.m_ViasMinSize = mm(via)
        ds.m_MinThroughDrill = mm(drill)
        ds.m_ViasMinAnnularWidth = mm(0.1)
        ds.m_HoleToHoleMin = mm(0.2)
        ds.m_CopperEdgeClearance = mm(0.2)
        ns = ds.m_NetSettings
        nc = ns.m_DefaultNetClass
        nc.SetTrackWidth(mm(track)); nc.SetClearance(mm(clearance))
        nc.SetViaDiameter(mm(via)); nc.SetViaDrill(mm(drill))
        self.classes = classes or {}
        for cname, prm in self.classes.items():
            c = pcbnew.NETCLASS(cname)
            c.SetTrackWidth(mm(prm["track"])); c.SetClearance(mm(prm.get("clearance", clearance)))
            c.SetViaDiameter(mm(prm.get("via", via))); c.SetViaDrill(mm(prm.get("drill", drill)))
            ns.m_NetClasses[cname] = c

    # ---------------------------------------------------------------- контур
    def outline(self, r=1.0, w=0.1):
        W, H = self.W, self.H
        segs = [((r, 0), (W - r, 0)), ((W, r), (W, H - r)), ((W - r, H), (r, H)), ((0, H - r), (0, r))]
        for a, bb in segs:
            s = pcbnew.PCB_SHAPE(self.b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
            s.SetStart(V(*a)); s.SetEnd(V(*bb)); s.SetWidth(mm(w)); self.b.Add(s)
        for cx, cy, a0 in ((r, r, 180), (W - r, r, 270), (W - r, H - r, 0), (r, H - r, 90)):
            s = pcbnew.PCB_SHAPE(self.b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
            s.SetCenter(V(cx, cy))
            s.SetStart(V(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))))
            s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(-90, pcbnew.DEGREES_T), True)
            s.SetWidth(mm(w)); self.b.Add(s)

    def reload(self):
        """Плата, собранная в памяти, не заливается (сбой ZONE_FILLER в KiCad 7) — сохраняем и загружаем заново."""
        pcb = self.out / f"{self.name}.kicad_pcb"
        pcbnew.SaveBoard(str(pcb), self.b)
        self.b = pcbnew.LoadBoard(str(pcb))
        self.nets = {n: self.b.FindNet(n) for n in self.nets}
        self.fps = {fp.GetReference(): fp for fp in self.b.GetFootprints()}
        return self.b

    def net(self, name):
        if name not in self.nets:
            ni = pcbnew.NETINFO_ITEM(self.b, name)
            self.b.Add(ni)
            self.nets[name] = ni
        return self.nets[name]

    # ---------------------------------------------------------------- элементы
    def load_fp(self, fpid):
        lib, name = fpid.split(":", 1)
        if lib == "TENSH" and self.local_lib:
            fp = pcbnew.FootprintLoad(str(self.local_lib), name)
        else:
            fp = pcbnew.FootprintLoad(str(FP_ROOT / f"{lib}.pretty"), name)
        if fp is None:
            raise FileNotFoundError(fpid)
        fp.SetFPIDAsString(fpid)
        return fp

    def place_all(self):
        for ref, part in self.d.parts.items():
            if not part.footprint:
                continue
            fp = self.load_fp(part.footprint)
            fp.SetReference(ref)
            fp.SetValue(part.value)
            x, y, rot = part.pos
            fp.SetPosition(V(x, y))
            if rot:
                fp.SetOrientationDegrees(rot)
            self.b.Add(fp)
            conn = self.d.pins_of(ref)
            pads_seen = set()
            for pad in fp.Pads():
                num = pad.GetNumber()
                if num in conn:
                    pad.SetNet(self.net(conn[num]))
                    pads_seen.add(num)
            missing = set(conn) - pads_seen
            if missing:
                raise ValueError(f"{ref} ({part.footprint}): нет контактных площадок {sorted(missing)}")
            fp.SetLocked(True)
            fp.Reference().SetVisible(False)        # позиционные обозначения — на сборочном чертеже
            fp.Value().SetVisible(False)
            self.fps[ref] = fp
        for name, cls in self.d.net_class.items():
            if name in self.nets:
                self.nets[name].SetNetClass(self.b.GetDesignSettings().m_NetSettings.m_NetClasses[cls])

    def hole(self, x, y, d):
        fp = self.load_fp(f"MountingHole:MountingHole_{d:.1f}mm".replace(".", "."))
        fp.SetPosition(V(x, y))
        self.b.Add(fp)

    # ---------------------------------------------------------------- полигоны
    def zone(self, net, layer, poly, priority=0, clearance=0.15, min_w=0.15, thermal=False):
        z = pcbnew.ZONE(self.b)
        z.SetLayer(layer)
        z.SetNet(self.net(net))
        ol = z.Outline()
        ol.NewOutline()
        for x, y in poly:
            ol.Append(mm(OX + x), mm(OY - y))
        z.SetAssignedPriority(priority)
        z.SetLocalClearance(mm(clearance))
        z.SetMinThickness(mm(min_w))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(mm(0.2)); z.SetThermalReliefSpokeWidth(mm(0.25))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        self.b.Add(z)
        return z

    def keepout(self, layer_set, poly, tracks=True, vias=True, pour=False):
        z = pcbnew.ZONE(self.b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowCopperPour(pour)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET()
        for l in layer_set:
            ls.AddLayer(l)
        z.SetLayerSet(ls)
        ol = z.Outline(); ol.NewOutline()
        for x, y in poly:
            ol.Append(mm(OX + x), mm(OY - y))
        self.b.Add(z)

    def track(self, net, pts, width, layer=pcbnew.F_Cu, locked=True):
        for a, bb in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(V(*a)); t.SetEnd(V(*bb)); t.SetWidth(mm(width)); t.SetLayer(layer)
            t.SetNet(self.net(net)); t.SetLocked(locked)
            self.b.Add(t)

    def via(self, net, x, y, d=0.45, drill=0.2, locked=True):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(V(x, y)); v.SetWidth(mm(d)); v.SetDrill(mm(drill))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(self.net(net)); v.SetLocked(locked)
        self.b.Add(v)

    def text(self, s, x, y, layer=pcbnew.F_SilkS, h=0.6, rot=0):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s); t.SetLayer(layer); t.SetPosition(V(x, y))
        t.SetTextSize(pcbnew.VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(h * 0.15))
        if rot:
            t.SetTextAngleDegrees(rot)
        if layer in (pcbnew.B_SilkS, pcbnew.B_Cu):
            t.SetMirrored(True)
        self.b.Add(t)

    def _obstacles(self):
        obst = []   # (тип, геометрия, код цепи)
        for t in self.b.GetTracks():
            if t.GetClass() == "PCB_VIA":
                obst.append(("c", (*U(t.GetPosition()), pcbnew.ToMM(t.GetWidth()) / 2), t.GetNetCode()))
            else:
                obst.append(("s", (*U(t.GetStart()), *U(t.GetEnd()), pcbnew.ToMM(t.GetWidth()) / 2), t.GetNetCode()))
        for fp in self.b.GetFootprints():
            for pad in fp.Pads():
                bb = pad.GetBoundingBox()
                nc = pad.GetNetCode() if pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH else -1
                if pad.GetDrillSize().x > 0 and pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                    nc = -2 if nc == -1 else nc      # отверстие: зазор до отверстий учитывается отдельно
                obst.append(("r", UB(bb), nc))
        return obst

    @staticmethod
    def _free(x, y, obst, code, r_via, clearance, hole_gap=0.6):
        import math as _m

        def dist_seg(px, py, ax, ay, bx, by):
            vx, vy = bx - ax, by - ay
            L2 = vx * vx + vy * vy
            t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / L2))
            return _m.hypot(px - ax - t * vx, py - ay - t * vy)
        for kind, g, nc in obst:
            if kind == "c":
                if nc == code:
                    if _m.hypot(x - g[0], y - g[1]) < hole_gap:      # своё отверстие: зазор между отверстиями
                        return False
                    continue
                dd = _m.hypot(x - g[0], y - g[1]) - g[2]
            elif kind == "s":
                if nc == code:
                    continue
                dd = dist_seg(x, y, *g[:4]) - g[4]
            else:
                dx = max(g[0] - x, 0, x - g[2]); dy = max(g[1] - y, 0, y - g[3])
                dd = _m.hypot(dx, dy)
                if nc == code:
                    dd += 0.05
                elif nc == -2:
                    dd -= 0.12          # неметаллизированное отверстие: зазор медь — отверстие 0,25 мм
            if dd < r_via + clearance:
                return False
        return True

    def _seg_free(self, x0, y0, x1, y1, obst, code, need, own_pad):
        """Отвод от площадки к отверстию не должен подходить к чужой меди ближе need (проверка по точкам)."""
        import math as _m
        L = _m.hypot(x1 - x0, y1 - y0)
        n = max(2, int(L / 0.05))
        own = UB(own_pad.GetBoundingBox())
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n; y = y0 + (y1 - y0) * i / n
            for kind, g, nc in obst:
                if nc == code or (kind == "r" and all(abs(a - b) < 1e-6 for a, b in zip(g, own))):
                    continue
                if kind == "r":
                    dx = max(g[0] - x, 0, x - g[2]); dy = max(g[1] - y, 0, y - g[3])
                    dd = _m.hypot(dx, dy)
                elif kind == "c":
                    dd = _m.hypot(x - g[0], y - g[1]) - g[2]
                else:
                    ax, ay, bx, by, w = g
                    vx, vy = bx - ax, by - ay
                    L2 = vx * vx + vy * vy
                    t = 0 if L2 == 0 else max(0, min(1, ((x - ax) * vx + (y - ay) * vy) / L2))
                    dd = _m.hypot(x - ax - t * vx, y - ay - t * vy) - w
                if dd < need:
                    return False
        return True

    def stitch(self, net, pitch=1.5, region=None, d=None, drill=None, clearance=0.15, keepout=(), edge=0.6):
        """Сшивка полигонов цепи net переходными отверстиями по сетке там, где до чужой меди не меньше clearance.
        region — (x0, y0, x1, y1) в мм (Y вверх); keepout — список таких прямоугольников."""
        import math as _m
        d, drill = d or self.via_d, drill or self.via_drill
        x0, y0, x1, y1 = region or (edge, edge, self.W - edge, self.H - edge)
        code = self.b.FindNet(net).GetNetCode()
        obst = self._obstacles()
        placed = 0
        y = y0
        while y <= y1 + 1e-6:
            x = x0
            while x <= x1 + 1e-6:
                if not any(kx0 <= x <= kx1 and ky0 <= y <= ky1 for kx0, ky0, kx1, ky1 in keepout) and \
                        self._free(x, y, obst, code, d / 2, clearance, hole_gap=max(pitch * 0.9, d + 0.3)):
                    self.via(net, x, y, d, drill, locked=False)
                    obst.append(("c", (x, y, d / 2), code))
                    placed += 1
                x += pitch
            y += pitch
        return placed

    def fix_islands(self, net, rounds=3, step=0.2):
        """Каждому изолированному куску полигона цепи net — переходное отверстие в свободной точке куска."""
        added = 0
        code = self.b.FindNet(net).GetNetCode()
        d = self.via_d
        for _ in range(rounds):
            self.fill()
            obst = self._obstacles()
            new = 0
            for z in self.b.Zones():
                if z.GetNetCode() != code or z.GetIsRuleArea():
                    continue
                lay = z.GetLayer()
                ps = z.GetFilledPolysList(lay)
                n = ps.OutlineCount()
                if n < 2:
                    continue
                areas = [abs(ps.Outline(i).Area()) for i in range(n)]
                main = areas.index(max(areas))
                for i in range(n):
                    if i == main:
                        continue
                    o = ps.Outline(i)
                    # уже есть отверстие своей цепи внутри куска?
                    if any(k == "c" and nc == code and o.PointInside(V(g[0], g[1])) for k, g, nc in obst):
                        continue
                    x0, yb, x1, yt = UB(o.BBox())
                    done = False
                    y = yb + step
                    while y < yt and not done:
                        x = x0 + step
                        while x < x1 and not done:
                            # отверстие целиком внутри куска (проверка по центру и 4 точкам на окружности)
                            pts = [(x, y)] + [(x + dx, y + dy) for dx, dy in ((d / 2, 0), (-d / 2, 0), (0, d / 2), (0, -d / 2))]
                            if all(o.PointInside(V(px, py)) for px, py in pts) and \
                                    self._free(x, y, obst, code, d / 2, 0.15):
                                self.via(net, x, y, d, self.via_drill, locked=False)
                                obst.append(("c", (x, y, d / 2), code))
                                new += 1
                                done = True
                            x += step
                        y += step
            added += new
            if not new:
                break
        self.fill()
        return added

    def pad_vias(self, net, refs=None, d=None, drill=None, clearance=0.15, track=0.25, locked=True):
        """Отдельное переходное отверстие к каждой SMD-площадке цепи net (связь с полигоном другого слоя)."""
        import math as _m
        d, drill = d or self.via_d, drill or self.via_drill
        code = self.b.FindNet(net).GetNetCode()
        obst = self._obstacles()
        n = 0
        for fp in self.b.GetFootprints():
            if refs and fp.GetReference() not in refs:
                continue
            for pad in fp.Pads():
                if pad.GetNetCode() != code or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                    continue
                cx, cy = U(pad.GetPosition())
                bb = pad.GetBoundingBox()
                biggest = max(fp.Pads(), key=lambda q: q.GetSize().x * q.GetSize().y)
                is_ep = len(fp.Pads()) > 4 and pad is biggest or pad.GetNumber() == biggest.GetNumber() and len(fp.Pads()) > 4
                if is_ep and min(pcbnew.ToMM(pad.GetSize().x), pcbnew.ToMM(pad.GetSize().y)) >= d + 0.1 and \
                        not any(k == "c" and nc == code and _m.hypot(cx - g[0], cy - g[1]) < 0.3 for k, g, nc in obst):
                    self.via(net, cx, cy, d, drill, locked=locked)    # отверстие в теплоотводящей площадке
                    obst.append(("c", (cx, cy, d / 2), code))
                    n += 1
                    continue
                half = max(pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())) / 2
                if any(k == "c" and nc == code and _m.hypot(cx - g[0], cy - g[1]) < half + 0.8 for k, g, nc in obst):
                    continue                                   # рядом уже есть своё отверстие
                done = False
                for r in (half + d / 2 + 0.2, half + d / 2 + 0.45, half + d / 2 + 0.8):
                    for ang in range(0, 360, 30):
                        x = cx + r * _m.cos(_m.radians(ang)); y = cy + r * _m.sin(_m.radians(ang))
                        if 0.6 < x < self.W - 0.6 and 0.6 < y < self.H - 0.6 and \
                                self._free(x, y, obst, code, d / 2, clearance) and \
                                self._seg_free(cx, cy, x, y, obst, code, track / 2 + clearance, pad):
                            self.via(net, x, y, d, drill, locked=locked)
                            self.track(net, [(cx, cy), (x, y)], track, locked=locked)
                            obst.append(("c", (x, y, d / 2), code))
                            n += 1
                            done = True
                            break
                    if done:
                        break
        return n

    # ---------------------------------------------------------------- трассировка
    def fill(self):
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())

    def route(self, passes=40, timeout=1800, extra=()):
        """Freerouting не принимает не-ASCII имена (кириллицу в пути к файлу) — работаем во временном каталоге."""
        import tempfile
        pcb = self.out / f"{self.name}.kicad_pcb"
        pcbnew.SaveBoard(str(pcb), self.b)
        with tempfile.TemporaryDirectory(prefix="fr_") as tmp:
            dsn, sesf = Path(tmp) / "board.dsn", Path(tmp) / "board.ses"
            assert pcbnew.ExportSpecctraDSN(self.b, str(dsn))
            cmd = ["xvfb-run", "-a", "java", "-jar", str(FREEROUTING), "-de", str(dsn), "-do", str(sesf),
                   "-mp", str(passes), "-dct", "0", *extra]
            try:
                log = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=tmp)
                text = log.stdout[-20000:] + log.stderr[-20000:]
            except subprocess.TimeoutExpired as e:
                text = f"timeout {timeout} s"
            (self.out / "freerouting.log").write_text(
                "\n".join(l for l in text.splitlines() if "INFO" in l or "WARN" in l or "ERROR" in l or "timeout" in l))
            if not sesf.exists():
                raise RuntimeError("Freerouting не создал SES: см. freerouting.log")
            return ses.import_ses(self.b, str(sesf))

    def drc(self):
        """Возвращает (ошибки, неразведённые, текст); предупреждения (шелкография и т. п.) не считаются ошибками."""
        import re
        rpt = self.out / "drc.rpt"
        self.fill()
        pcbnew.WriteDRCReport(self.b, str(rpt), pcbnew.EDA_UNITS_MILLIMETRES, True)
        txt = rpt.read_text()
        errors = len(re.findall(r"Severity: error", txt))
        unc = int(re.search(r"Found (\d+) unconnected pads", txt).group(1))
        return errors, unc, txt

    def unrouted(self):
        conn = self.b.GetConnectivity()
        conn.RecalculateRatsnest()
        return conn.GetUnconnectedCount(False)

    def save(self):
        pcb = self.out / f"{self.name}.kicad_pcb"
        pcbnew.SaveBoard(str(pcb), self.b)
        return pcb

    # ---------------------------------------------------------------- выпуск
    def fab_outputs(self, fab_dir, prefix):
        pcb = self.save()
        fab = Path(fab_dir)
        if fab.exists():
            shutil.rmtree(fab)
        (fab / "gerber").mkdir(parents=True)
        n = self.b.GetCopperLayerCount()
        cu = ["F.Cu"] + [f"In{i}.Cu" for i in range(1, n - 1)] + ["B.Cu"]
        layers = ",".join(cu + ["F.Mask", "B.Mask", "F.Paste", "B.Paste", "F.Silkscreen", "B.Silkscreen", "Edge.Cuts"])
        run = lambda *a: subprocess.run(["kicad-cli", *a], check=True, capture_output=True, text=True)
        run("pcb", "export", "gerbers", "--no-x2", "--subtract-soldermask", "--use-drill-file-origin", "-o", str(fab / "gerber") + "/", "--layers", layers, str(pcb))
        run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th",
            "--generate-map", "--map-format", "gerberx2", "--drill-origin", "plot", "-o", str(fab / "gerber") + "/", str(pcb))
        run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "--smd-only", "--use-drill-file-origin",
            "-o", str(fab / f"{prefix}_pos.csv"), str(pcb))
        # BOM — из модели (с обозначениями изготовителей)
        with open(fab / f"{prefix}_bom.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Designator", "Qty", "Value", "Manufacturer", "MPN", "Footprint", "Description"])
            groups = {}
            for ref, p in self.d.parts.items():
                if not p.footprint or p.kind in ("MH", "TP", "PAD"):
                    continue
                groups.setdefault((p.value, p.mfr, p.mpn, p.footprint, p.name_ru), []).append(ref)
            for (val, mfr, mpn, fpid, desc), refs in groups.items():
                w.writerow([" ".join(refs), len(refs), val, mfr, mpn, fpid.split(":")[1], desc])
        zpath = fab / f"{prefix}_gerber.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for fpath in sorted((fab / "gerber").iterdir()):
                z.write(fpath, fpath.name)
        return fab

    def project_file(self, sch_name=None):
        """Минимальный .kicad_pro с классами цепей и библиотеками проекта."""
        pro = {"board": {"design_settings": {"defaults": {"board_outline_line_width": 0.1}}},
               "meta": {"filename": f"{self.name}.kicad_pro", "version": 1},
               "net_settings": {"classes": [{"name": "Default", "track_width": 0.1, "clearance": 0.1,
                                             "via_diameter": 0.45, "via_drill": 0.2}] +
                                [{"name": k, "track_width": v["track"], "clearance": v.get("clearance", 0.1),
                                  "via_diameter": v.get("via", 0.45), "via_drill": v.get("drill", 0.2)}
                                 for k, v in self.classes.items()],
                                "meta": {"version": 3},
                                "netclass_patterns": [{"netclass": c, "pattern": n} for n, c in self.d.net_class.items()]},
               "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
               "sheets": [], "text_variables": {}}
        (self.out / f"{self.name}.kicad_pro").write_text(json.dumps(pro, indent=2, ensure_ascii=False))
        (self.out / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "TENSH")(type "KiCad")'
                                               '(uri "${KIPRJMOD}/TENSH.pretty")(options "")(descr "Посадочные места проекта"))\n)\n')
        (self.out / "sym-lib-table").write_text('(sym_lib_table\n  (version 7)\n  (lib (name "TENSH")(type "KiCad")'
                                                '(uri "${KIPRJMOD}/TENSH.kicad_sym")(options "")(descr "Символы проекта"))\n)\n')
