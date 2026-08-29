#!/usr/bin/env python3
"""Generates translations.csv (names + descriptions per fg/fn/dp key) from Hoval's
official datapoint list, seeded with the DE/EN text columns Hoval ships in the xlsx.

Usage:
  python3 generate_translations.py <datapoint-list.xlsx> <datapoints.csv> [out.csv]

Hoval only maintains English descriptions patchily -- where they are missing,
consumers should fall back to the German description.
"""
import csv
import re
import sys


def harvest(wb, sheetname, wanted):
    ws = wb[sheetname]
    hdr, out = None, {}
    for row in ws.iter_rows(values_only=True):
        if hdr is None:
            hdr = [str(h or "").strip() for h in row]
            idx = {h.lower(): i for i, h in enumerate(hdr)}
            c_reg, c_name = idx["register address"], idx["datapointname"]
            c_com, c_type = idx["commentary"], idx["typename"]
            texts = sorted((int(re.match(r"text (\d+)$", h.lower()).group(1)), i)
                           for i, h in enumerate(hdr) if re.match(r"text \d+$", h.lower()))
            continue
        try:
            reg = int(row[c_reg])
        except (TypeError, ValueError):
            continue
        if reg not in wanted or reg in out:
            continue
        name = str(row[c_name] or "").strip()
        com = str(row[c_com] or "").strip()
        enum = []
        if str(row[c_type] or "").strip().upper() == "LIST":
            for num, i in texts:
                if row[i] not in (None, ""):
                    enum.append(f"{num}={row[i]}")
        desc = com + ((" " if com else "") + "[" + ", ".join(enum) + "]" if enum else "")
        out[reg] = (name, desc)
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    import openpyxl
    wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)

    regs = {}
    with open(sys.argv[2], encoding="utf-8") as f:
        for row in csv.DictReader(f):
            regs[int(row["reg"])] = row
    wanted = set(regs)
    out_path = sys.argv[3] if len(sys.argv) > 3 else "translations.csv"

    de = harvest(wb, "Deutsch", wanted) if "Deutsch" in wb.sheetnames else {}
    en_sheet = next((s for s in wb.sheetnames if s.lower().startswith("eng")), None)
    en = harvest(wb, en_sheet, wanted) if en_sheet else {}

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fg", "fn", "dp", "name_de", "desc_de", "name_en", "desc_en"])
        for reg in sorted(wanted):
            r = regs[reg]
            nd, dd = de.get(reg, ("", ""))
            ne, ed = en.get(reg, ("", ""))
            w.writerow([r["fg"], r["fn"], r["dp"], nd, dd, ne, ed])

    print(f"{out_path}: {len(wanted)} datapoints translated")


if __name__ == "__main__":
    main()
