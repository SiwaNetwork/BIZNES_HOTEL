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


def V(x, y):
    """Координаты изделия (Y вверх, от левого нижнего угла) -> координаты KiCad (Y вниз)."""
    return pcbnew.VECTOR2I(mm(x), mm(-y))


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
        self.nets = {}
        self.fps = {}

    # ---------------------------------------------------------------- правила
    def rules(self, track=0.1, clearance=0.1, via=0.45, drill=0.2, classes=None):
        ds = self.b.GetDesignSettings()
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
            ol.Append(mm(x), mm(-y))
        z.SetAssignedPriority(priority)
        z.SetLocalClearance(mm(clearance))
        z.SetMinThickness(mm(min_w))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(mm(0.2)); z.SetThermalReliefSpokeWidth(mm(0.25))
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
            ol.Append(mm(x), mm(-y))
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

    # ---------------------------------------------------------------- трассировка
    def fill(self):
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())

    def route(self, passes=40, timeout=1800, extra=()):
        pcb = self.out / f"{self.name}.kicad_pcb"
        dsn, sesf = self.out / f"{self.name}.dsn", self.out / f"{self.name}.ses"
        pcbnew.SaveBoard(str(pcb), self.b)
        assert pcbnew.ExportSpecctraDSN(self.b, str(dsn))
        cmd = ["xvfb-run", "-a", "java", "-jar", str(FREEROUTING), "-de", str(dsn), "-do", str(sesf),
               "-mp", str(passes), "-dct", "0", *extra]
        log = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        (self.out / "freerouting.log").write_text(log.stdout[-20000:] + log.stderr[-20000:])
        if not sesf.exists():
            raise RuntimeError("Freerouting не создал SES: см. freerouting.log")
        n = ses.import_ses(self.b, str(sesf))
        dsn.unlink(); sesf.unlink()
        return n

    def drc(self):
        rpt = self.out / "drc.rpt"
        self.fill()
        pcbnew.WriteDRCReport(self.b, str(rpt), pcbnew.EDA_UNITS_MILLIMETRES, True)
        txt = rpt.read_text()
        import re
        viol = int(re.search(r"Found (\d+) DRC violations", txt).group(1))
        unc = int(re.search(r"Found (\d+) unconnected pads", txt).group(1))
        return viol, unc, txt

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
        run("pcb", "export", "gerbers", "--no-x2", "--subtract-soldermask", "-o", str(fab / "gerber") + "/", "--layers", layers, str(pcb))
        run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th",
            "--generate-map", "--map-format", "gerberx2", "-o", str(fab / "gerber") + "/", str(pcb))
        run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "--smd-only",
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
