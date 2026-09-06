#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ortusme TOLERANSLI olculur (tur damgalari farkli ritimde). SALT OKUMA."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, bisect

A, B = "2026-08-21", "2026-09-03"
BONUS = 8.0
TOL = 600          # +-10 dk


def ts(s):
    s = str(s).strip().replace("T", " ")
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return dt.datetime.strptime(s[:19 if len(f) > 16 else 16], f)
        except ValueError:
            pass
    return None


def oku(f):
    out = []
    for l in open(f, encoding="utf-8", errors="replace"):
        l = l.strip()
        if not l:
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        t = ts(d.get("ts"))
        if t and A <= t.strftime("%Y-%m-%d") < B:
            d["_t"] = t
            out.append(d)
    return out


ADAY = oku("testbot_aday_arsiv.jsonl")
RAD = oku("radar_archive.jsonl")
tur = collections.defaultdict(list)
for d in RAD:
    if (d.get("score") or 0) >= 30:
        tur[d["_t"]].append(d)
NL = []
for t, rows in tur.items():
    rows.sort(key=lambda x: -((x.get("score") or 0)
                              + (BONUS if x.get("stage") == "HAZIRLANIYOR" else 0.0)))
    NL.extend(rows[:10])

# sembol bazli zaman indeksi
idx = collections.defaultdict(list)
for d in NL:
    idx[d["sym"]].append(d["_t"])
for s in idx:
    idx[s].sort()

es = 0
for d in ADAY:
    v = idx.get(d["sym"])
    if not v:
        continue
    i = bisect.bisect_left(v, d["_t"])
    for j in (i - 1, i):
        if 0 <= j < len(v) and abs((v[j] - d["_t"]).total_seconds()) <= TOL:
            es += 1
            break

print("=" * 92)
print("TOLERANSLI ORTUSME (+-10 dk, sembol bazli)")
print("=" * 92)
print("  aday_arsiv kaydi : %6d" % len(ADAY))
print("  notrlong kaydi   : %6d" % len(NL))
print("  aday_arsiv'den notrlong havuzunda KARSILIGI OLAN : %6d  (%%%.1f)"
      % (es, 100 * es / max(len(ADAY), 1)))
print("")
print("  KESIN eslesme %%1,7 idi -> tolerans acilinca %%%.1f" % (100 * es / max(len(ADAY), 1)))

print("")
print("=" * 92)
print("TUR BASINA KAYIT — havuz BUYUKLUGU farki")
print("=" * 92)
na, nn = len({d["_t"] for d in ADAY}), len(tur)
print("  aday_arsiv : %6d kayit / %4d tur = %.2f aday/tur" % (len(ADAY), na, len(ADAY) / na))
print("  notrlong   : %6d kayit / %4d tur = %.2f aday/tur" % (len(NL), nn, len(NL) / nn))
print("")
print("  -> notrlong ilk 10'u aliyor ama havuzda o kadar aday YOK.")
print("     radar arsivinde skor>=30 olan aday tur basina %.2f." % (len(NL) / nn))

print("")
print("=" * 92)
print("radar_archive BOSLUK kaydi (CLAUDE.md: bu dosya NOKTASAL)")
print("=" * 92)
try:
    n = 0
    ilk = son = None
    for l in open("radar_bosluk.jsonl", encoding="utf-8", errors="replace"):
        l = l.strip()
        if not l:
            continue
        d = json.loads(l)
        t = str(d.get("ts", ""))
        if A <= t[:10] < B:
            n += 1
            ilk = ilk or t
            son = t
    print("  pencerede isaretli bosluk: %d  (%s .. %s)" % (n, ilk, son))
except Exception as e:
    print("  okunamadi:", repr(e)[:80])
print("  aday_arsiv turu %d · radar turu %d · FARK %d tur" % (na, nn, na - nn))
