#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[:10] KIRPMASI uygun adayi disarida birakiyor mu? SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections

BONUS = 8.0          # hazirlaniyor_sira_bonus (notrlong ile ayni)
tur = collections.defaultdict(list)
for l in open("radar_archive.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    d = json.loads(l)
    if d.get("ts", "") >= "2026-08-20" and (d.get("score") or 0) >= 30:
        tur[d["ts"]].append(d)


def uygun(d):
    st, sk = d.get("stage"), (d.get("score") or 0)
    if st not in ("BASLIYOR", "HAZIRLANIYOR"):
        return False
    if sk < (40.0 if st == "HAZIRLANIYOR" else 45.0):
        return False
    return d.get("smart") == "LONG"


var = ic = dis = 0
dis_ornek = []
for ts, rows in tur.items():
    u = [d for d in rows if uygun(d)]
    if not u:
        continue
    var += 1
    rows.sort(key=lambda x: -((x.get("score") or 0)
                              + (BONUS if x.get("stage") == "HAZIRLANIYOR" else 0.0)))
    ilk10 = rows[:10]
    if any(uygun(d) for d in ilk10):
        ic += 1
    else:
        dis += 1
        if len(dis_ornek) < 6:
            b = u[0]
            sira = rows.index(b) + 1
            dis_ornek.append((ts, b["sym"], b.get("stage"), b.get("score"), sira, len(rows)))

print("=" * 92)
print("[:10] KIRPMASI — uygun aday VARKEN kac kez ilk 10'un DISINDA kaldi")
print("=" * 92)
print("  uygun adayin BULUNDUGU tur : %d" % var)
print("    ilk 10'a GIRDI            : %d  (%%%.1f)" % (ic, 100 * ic / max(var, 1)))
print("    ilk 10'un DISINDA kaldi   : %d  (%%%.1f)  <- KAYIP FIRSAT"
      % (dis, 100 * dis / max(var, 1)))
print("")
print("  ornekler (en iyi uygun aday nerede siralandi):")
print("  %-20s %-10s %-13s %6s %7s %7s" % ("ts", "sym", "stage", "skor", "sira", "havuz"))
for ts, s, st, sk, si, n in dis_ornek:
    print("  %-20s %-10s %-13s %6.1f %6d. %7d" % (ts, s, st, sk, si, n))

print("")
print("=" * 92)
print("SEBEP — siralama bonusu YALNIZ HAZIRLANIYOR'a veriliyor")
print("=" * 92)
c = collections.Counter()
for ts, rows in tur.items():
    for d in rows:
        if uygun(d):
            c[d.get("stage")] += 1
print("  uygun adaylarin stage'i:", dict(c))
print("  sira bonusu: HAZIRLANIYOR +%.1f · BASLIYOR +0,0" % BONUS)
print("  -> BASLIYOR adaylari bonussuz yarisiyor ve yuksek skorlu 'izle'lere yeniliyor.")
