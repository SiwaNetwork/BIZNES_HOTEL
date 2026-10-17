"""Импорт результатов трассировки Freerouting (Specctra SES) в плату KiCad без GUI."""
import re

import pcbnew


def sexpr(text):
    tokens = re.findall(r'\(|\)|"[^"]*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t.strip('"'))
    return stack[0][0]


def find(node, key):
    return [n for n in node if isinstance(n, list) and n and n[0] == key]


def import_ses(board, path):
    tree = sexpr(open(path, encoding="utf-8").read())
    routes = find(tree, "routes")[0]
    res = find(routes, "resolution")[0]
    per_mm = {"um": 1000.0, "mm": 1.0, "mil": 1 / 0.0254}[res[1]] * float(res[2])
    to_iu = lambda v: pcbnew.FromMM(float(v) / per_mm)
    layers = {board.GetLayerName(l): l for l in range(pcbnew.PCB_LAYER_ID_COUNT)}
    vias_def = {}
    for ps in find(find(routes, "library_out")[0], "padstack") if find(routes, "library_out") else []:
        m = re.search(r"_(\d+):(\d+)_um", ps[1])
        if m:
            vias_def[ps[1]] = (int(m.group(1)) / 1000.0, int(m.group(2)) / 1000.0)
    n_tr = n_via = 0
    for net in find(find(routes, "network_out")[0], "net"):
        ni = board.FindNet(net[1])
        for w in find(net, "wire"):
            p = find(w, "path")[0]
            layer, width = layers[p[1]], to_iu(p[2])
            xy = p[3:]
            pts = [(to_iu(xy[i]), -to_iu(xy[i + 1])) for i in range(0, len(xy) - 1, 2)]
            for a, b in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(*a)); t.SetEnd(pcbnew.VECTOR2I(*b))
                t.SetWidth(width); t.SetLayer(layer); t.SetNet(ni)
                board.Add(t); n_tr += 1
        for v in find(net, "via"):
            d, drill = vias_def.get(v[1], (0.45, 0.2))
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(to_iu(v[2]), -to_iu(v[3])))
            via.SetWidth(pcbnew.FromMM(d)); via.SetDrill(pcbnew.FromMM(drill))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(ni)
            board.Add(via); n_via += 1
    return n_tr, n_via
