"""Э3, ПЭ3 и спецификация изделия из модели соединений (hw.<модуль>.design()).

  python3 src/gen_hw_docs.py lband|iridium

ПЭ3 (ГОСТ 2.701-2008): элементы — группами в алфавитном порядке буквенных позиционных обозначений,
в группе — по возрастанию номера; одинаковые элементы с последовательными номерами объединены в одну строку.
Спецификация (ГОСТ 2.106-2019): разделы «Документация», «Сборочные единицы», «Детали», «Прочие изделия»,
«Материалы»; покупные элементы — в разделе «Прочие изделия» со ссылкой на позиционные обозначения.
"""
import importlib
import re
import sys

import gen_e3
import gen_lists
import gost

DOCS = gost.ROOT / "docs"
PASSIVE = ("R", "C", "L", "FB")
# буквенный код -> (заголовок группы, слово в начале наименования, которое опускается под заголовком)
GROUPS = {"BQ": ("Резонаторы кварцевые", "Резонатор кварцевый"), "C": ("Конденсаторы", "Конденсатор"), "DA": ("Микросхемы", "Микросхема"),
          "DD": ("Микросхемы", "Микросхема"), "G": ("Генераторы кварцевые", "Генератор кварцевый"),
          "L": ("Катушки индуктивности", "Катушка индуктивности"), "R": ("Резисторы", "Резистор"),
          "X": ("Соединители", ""), "XW": ("Соединители", ""), "Z": ("Фильтры", "Фильтр")}
NOT_LISTED = ("MH", "SHIELD")


def letters(ref):
    return re.match(r"[A-Z]+", ref).group(0)


def number(ref):
    return int(re.search(r"\d+", ref).group(0))


def is_star(part):
    return "*" in part.value


def listed(d):
    return [(r, p) for r, p in d.parts.items() if p.kind not in NOT_LISTED]


def _merge_refs(refs):
    """['C3','C4'] -> 'C3, C4'; ['C25','C26','C27'] -> 'C25–C27'."""
    if len(refs) == 1:
        return refs[0]
    if len(refs) == 2:
        return ",".join(refs)       # без пробела — помещается в графу «Поз. обозначение» шириной 20 мм
    return f"{refs[0]}–{refs[-1]}"


def pe3_groups(d, pcb_code):
    by_letter = {}
    for ref, p in listed(d):
        by_letter.setdefault(letters(ref), []).append((ref, p))
    groups, last_head = [], None
    for let in sorted(by_letter):
        items = sorted(by_letter[let], key=lambda rp: number(rp[0]))
        head, word = GROUPS.get(let, ("", ""))
        rows = []
        i = 0
        while i < len(items):
            ref, p = items[i]
            j = i
            # объединяем подряд идущие одинаковые элементы с последовательными номерами
            while j + 1 < len(items) and items[j + 1][1].name_ru == p.name_ru and \
                    number(items[j + 1][0]) == number(items[j][0]) + 1 and is_star(items[j + 1][1]) == is_star(p):
                j += 1
            refs = [r + ("*" if is_star(q) else "") for r, q in items[i:j + 1]]
            name = p.name_ru
            if word and name.startswith(word + " "):
                name = name[len(word) + 1:]
            if p.kind == "PAD":
                name, note = f"{p.name_ru}", f"Элемент платы {pcb_code}"
            else:
                note = "Подбирают при настройке" if is_star(p) else p.mfr
            rows.append((_merge_refs(refs), name, j - i + 1, note))
            i = j + 1
        if head == last_head and groups:
            groups[-1][1].extend(rows)
        else:
            groups.append((head, rows))
        last_head = head
    return groups


def purchased(d):
    """Покупные изделия для спецификации: одинаковые наименования — одной строкой со списком позиций."""
    rows = {}
    for ref, p in listed(d):
        if p.kind == "PAD":
            continue
        rows.setdefault(p.name_ru, []).append(ref)
    out = []
    for name, refs in sorted(rows.items(), key=lambda kv: (letters(kv[1][0]), kv[0])):
        refs = sorted(refs, key=lambda r: (letters(r), number(r)))
        # последовательные номера сворачиваем в диапазоны
        parts, run = [], [refs[0]]
        for r in refs[1:]:
            if letters(r) == letters(run[-1]) and number(r) == number(run[-1]) + 1:
                run.append(r)
            else:
                parts.append(_merge_refs(run)); run = [r]
        parts.append(_merge_refs(run))
        out.append((name, len(refs), ", ".join(parts)))
    return out


def sp_sections(mod, d):
    code = mod.CODE
    docs = list(getattr(mod, "SP_DOCS", [])) + [
        ("A3", "", "", f"{code} Э3", "Схема электрическая принципиальная", "", ""),
        ("A4", "", "", f"{code} ПЭ3", "Перечень элементов", "", "")]
    # порядок документов — по ГОСТ 2.102: чертежи, схемы, перечни, текстовые документы
    order = ["ГЧ", "Э1", "Э3", "ПЭ3", "ПЗ"]
    docs.sort(key=lambda r: order.index(r[3].split()[-1]) if r[3].split()[-1] in order else 99)
    sec = [("Документация", docs)]
    pos = 1
    asm, det = [], []
    for kind, fmt, des, name, qty, note in getattr(mod, "SP_PARTS", []):
        (asm if kind == "asm" else det).append((fmt, "", pos, des, name, qty, note))
        pos += 1
    if asm:
        sec.append(("Сборочные единицы", asm))
    if det:
        sec.append(("Детали", det))
    other = []
    for name, qty, refs in purchased(d):
        other.append(("", "", pos, "", name, qty, refs))
        pos += 1
    for name, qty, note in getattr(mod, "SP_OTHER", []):
        other.append(("", "", pos, "", name, qty, note))
        pos += 1
    sec.append(("Прочие изделия", other))
    sec.append(("Материалы", [("", "", pos + i, "", n, "", "по ТП") for i, n in enumerate(mod.SP_MATERIALS)]))
    return sec


def owners(mod, d, mains):
    """Ячейка Э3 для каждого двухвыводного элемента: явная привязка (NEAR), иначе — ИС на цепи
    с наименьшим числом выводов (так же, как при расстановке на плате)."""
    near = getattr(mod, "NEAR", {})
    alias = getattr(mod, "E3_ALIAS", {})
    own, pending = {}, [r for r, p in d.parts.items() if p.kind in PASSIVE]
    while pending:
        progress = False
        for ref in list(pending):
            if ref in near:
                m = near[ref][0]
            else:
                best = None
                for net in d.pins_of(ref).values():
                    if net == "GND":
                        continue
                    ics = [r for r, _ in d.nets[net] if r != ref and d.parts[r].kind not in PASSIVE + ("PAD",)]
                    if ics and (best is None or len(d.nets[net]) < best[0]):
                        best = (len(d.nets[net]), ics[0])
                m = best[1] if best else None
                if m is None:       # цепочки пассивных элементов — владелец соседнего элемента
                    m = next((own[r] for net in d.pins_of(ref).values() if net != "GND"
                              for r, _ in d.nets.get(net, []) if r in own), None)
                    if m is None:
                        continue
            m = alias.get(m, m)
            own[ref] = m if m in mains else mains[0]
            pending.remove(ref)
            progress = True
        if not progress:
            for ref in pending:
                own[ref] = mains[0]
            break
    return own


def e3_sheets(mod, d):
    sheets = []
    mains = [m for sheet in mod.E3_SHEETS for m, _ in sheet]
    own = owners(mod, d, mains)
    key = lambda r: (letters(r), number(r))
    for sheet in mod.E3_SHEETS:
        cells = []
        for m, title in sheet:
            ps = sorted([r for r, o in own.items() if o == m], key=key)
            cells.append(gen_e3.Cell(d, m, ps, title))
        sheets.append(cells)
    return sheets


def build(which):
    mod = importlib.import_module(f"hw.{which}")
    d = mod.design()
    DOCS.mkdir(exist_ok=True)
    code = mod.CODE
    out = {}
    out["Э3"] = DOCS / f"{code}_Э3.pdf"
    gen_e3.build(out["Э3"], d, e3_sheets(mod, d), mod.PRODUCT, code, notes=mod.E3_NOTES)
    out["ПЭ3"] = DOCS / f"{code}_ПЭ3.pdf"
    gen_lists.build_pe3(out["ПЭ3"], code, mod.PRODUCT, pe3_groups(d, mod.PCB_CODE))
    out["СП"] = DOCS / f"{code}_СП.pdf"
    gen_lists.build_sp(out["СП"], code, mod.PRODUCT, sp_sections(mod, d))
    return out


if __name__ == "__main__":
    gost.register_fonts()
    for w in sys.argv[1:]:
        for k, v in build(w).items():
            print(k, v.name)
