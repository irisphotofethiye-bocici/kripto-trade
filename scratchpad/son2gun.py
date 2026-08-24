#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SON 2 GUN — bes defterin durumu. SALT OKUMA, bota DOKUNMAZ.

CLAUDE.md kurallari uygulanir:
  - kazanma orani POZISYON basina (kismi kayitlar HARIC sayilir)
  - P&L TOPLARKEN suzgec UYGULANMAZ (id ile birlestirilir)
  - pencere sonucu EQUITY uzerinden turetilir, defter toplamindan DEGIL
  - funding_usdt: dolar, dilim, id ile toplanir; None = BILINMIYOR
  - canli rakam .md dosyasindan DEGIL state/jsonl dosyasindan okunur
"""
import os, json, datetime, collections, statistics as sx

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
SIMDI = datetime.datetime.now()
BAS = SIMDI - datetime.timedelta(days=2)

DEFTER = [("testbot", "testbot_state.json", "testbot_islemler.jsonl", "testbot_equity.jsonl"),
          ("golge", "golge_state.json", "golge_islemler.jsonl", "golge_equity.jsonl"),
          ("benim", "benim_state.json", "benim_islemler.jsonl", "benim_equity.jsonl"),
          ("ayna", "ayna_state.json", "ayna_islemler.jsonl", "ayna_equity.jsonl"),
          ("defter2", "defter2_state.json", "defter2_islemler.jsonl", "defter2_equity.jsonl")]


def oku_jsonl(y):
    out = []
    if not os.path.exists(y):
        return out
    with open(y, encoding="utf-8") as f:
        for s in f:
            s = s.strip()
            if s:
                try:
                    out.append(json.loads(s))
                except Exception:
                    pass
    return out


def ts(x):
    try:
        return datetime.datetime.strptime(x["ts"], F)
    except Exception:
        return None


print("SON 2 GUN — %s .. %s" % (BAS.strftime("%m-%d %H:%M"), SIMDI.strftime("%m-%d %H:%M")))
print("=" * 92)

for ad, sy, iy, ey in DEFTER:
    sp, ip, ep = (os.path.join(PROJE, z) for z in (sy, iy, ey))
    if not os.path.exists(sp):
        print("\n%-9s durum dosyasi YOK" % ad)
        continue
    with open(sp, encoding="utf-8") as f:
        st = json.load(f)
    eq = oku_jsonl(ep)
    pen_eq = [x for x in eq if ts(x) and ts(x) >= BAS]
    kay = oku_jsonl(ip)
    pen = [x for x in kay if ts(x) and ts(x) >= BAS]

    # POZISYON bazli: id ile birlestir (P&L toplarken suzgec YOK)
    grup = collections.defaultdict(list)
    for x in pen:
        grup[x.get("id")].append(x)
    kapanan = len(grup)
    pnl = sum((t.get("sonuc_usdt") or 0) for x in grup.values() for t in x)
    poz_sonuc = [sum((t.get("sonuc_usdt") or 0) for t in v) for v in grup.values()]
    kazanan = sum(1 for z in poz_sonuc if z > 0)
    fon = [t.get("funding_usdt") for v in grup.values() for t in v
           if t.get("funding_usdt") is not None]

    acik = st.get("acik_pozisyonlar") or []
    yon = collections.Counter(p.get("yon") for p in acik)
    e0 = pen_eq[0].get("equity") if pen_eq else None
    e1 = st.get("equity")

    print("\n%-9s equity %10.2f   acik %d (%dL/%dS)   durum %s"
          % (ad, e1 or 0, len(acik), yon.get("LONG", 0), yon.get("SHORT", 0),
             st.get("durum", "?")))
    if e0 is not None and e1 is not None:
        print("          2 gun equity farki  %+10.2f   (%.2f -> %.2f)" % (e1 - e0, e0, e1))
    print("          kapanan pozisyon %3d   kazanan %3d   (%s)"
          % (kapanan, kazanan,
             ("%%%.0f" % (100.0 * kazanan / kapanan)) if kapanan else "-"))
    print("          defter P&L toplami %+10.2f   kayit %d" % (pnl, len(pen)))
    if fon:
        print("          fonlama (id bazli, dolar) %+9.4f   (%d kayitta bilinen)"
              % (sum(fon), len(fon)))
    if acik:
        print("          ACIK POZISYONLAR:")
        for p in sorted(acik, key=lambda z: z.get("giris_ts", "")):
            g = p.get("giris_ts", "?")
            print("            %-10s %-5s giris %s  kapi %s"
                  % (p.get("sym"), p.get("yon"), g[5:16], p.get("sebep_giris", "?")))

# --- tur sagligi: son equity damgalari ---
print("\n" + "=" * 92)
print("ZAMANLAYICI SAGLIGI (testbot_equity.jsonl son kayitlar)")
eq = oku_jsonl(os.path.join(PROJE, "testbot_equity.jsonl"))
son = [x for x in eq if ts(x)][-6:]
for x in son:
    t = ts(x)
    sure = x.get("sure_sn")
    print("   %s   equity %10.2f   sure %s sn   tur basi %s"
          % (t.strftime("%m-%d %H:%M:%S"), x.get("equity") or 0,
             ("%6.1f" % sure) if sure else "   ?  ",
             (t - datetime.timedelta(seconds=sure)).strftime("%H:%M:%S") if sure else "?"))
if son:
    gecikme = (SIMDI - ts(son[-1])).total_seconds() / 60
    print("   son turdan bu yana: %.1f dakika  ->  %s"
          % (gecikme, "SAGLIKLI" if gecikme < 20 else "DIKKAT: tur gecikmis"))

# --- rejim etiketi ---
rd = os.path.join(PROJE, "radar_active.json")
if os.path.exists(rd):
    with open(rd, encoding="utf-8") as f:
        ra = json.load(f)
    print("\n   radar guncelleme: %s   rejim: %s"
          % (ra.get("guncelleme", "?"), (ra.get("rejim") or {}) if isinstance(ra.get("rejim"), dict) else ra.get("rejim")))

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
