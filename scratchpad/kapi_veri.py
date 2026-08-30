#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAPI DENETIMI — BIRLESTIRME. On-kayit: ON_KAYIT_kapi_dengesi.md (commit bd327a6).

Aday arsivi x 5 defter x pozisyon_izleme -> pozisyon basina TEK satir.
Cikti: scratchpad/poz_yol/kapi_veri.json  (context'e YUKLENMEZ)

🔴 TASARIM KORUMASI — bugunku artefaktin tekrarini KOD DUZEYINDE engeller:
   Sonuc turetilmis her alan `_kontrol_` onekiyle yazilir. Yordayici tarama
   fonksiyonlari bu oneki tasiyan alanlari GORMEZ. Kontrol katmani olarak
   bilerek cagrilir, yanlislikla yordayici olamaz.

Birim POZISYON: kayitlar id ile birlestirilir, P&L toplarken SUZGEC YOK.
Sonuc = (sum sonuc_usdt + sum funding_usdt) / notional * 100.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections, bisect, statistics

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(PROJE, "scratchpad", "poz_yol", "kapi_veri.json")
F = "%Y-%m-%d %H:%M:%S"
ESLESME_DK = 30
DEFTERLER = [("testbot", "testbot_islemler.jsonl"), ("golge", "golge_islemler.jsonl"),
             ("ayna", "ayna_islemler.jsonl"), ("defter2", "defter2_islemler.jsonl"),
             ("defter3", "defter3_islemler.jsonl")]

# on-kayit s.5 — aday arsivinden alinacak YORDAYICI alanlar (A kolu + baglam)
ADAY_ALAN = ["score", "stage", "comp", "vol_x", "oi3", "oi24", "funding", "pos",
             "last1", "last3", "chg24", "dip_yakit", "ayrisma", "rel3", "btc_chg3",
             "rejim", "top_ls", "glob_ls", "taker", "smart", "ma50_mesafe",
             "dusuk_float", "price", "karar", "red_kapi"]


def satirlar(yol):
    p = os.path.join(PROJE, yol)
    if not os.path.exists(p):
        return
    with open(p, encoding="utf-8") as f:
        for s in f:
            s = s.strip()
            if s:
                try:
                    yield json.loads(s)
                except Exception:
                    continue


# ---------------------------------------------------------------- aday arsivi
print("KAPI DENETIMI — BIRLESTIRME")
print("=" * 100)
aday = collections.defaultdict(list)
n_aday = 0
for x in satirlar("testbot_aday_arsiv.jsonl"):
    t, sy = x.get("ts"), x.get("sym")
    if not t or not sy:
        continue
    try:
        d = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M")
    except Exception:
        continue
    aday[sy].append((d, x))
    n_aday += 1
for k in aday:
    aday[k].sort(key=lambda z: z[0])
print("aday arsivi: %d satir · %d sembol" % (n_aday, len(aday)))

# ---------------------------------------------------------------- izleme (ilk 30 dk)
izl = collections.defaultdict(list)
for x in satirlar("pozisyon_izleme.jsonl"):
    i = x.get("id")
    if i is not None:
        izl[i].append(x)
for i in izl:
    izl[i].sort(key=lambda z: z.get("ts") or "")
print("izleme: %d tekil pozisyon (yalniz testbot)" % len(izl))


def erken_ozellikler(i):
    """C kolu — ILK 30 DAKIKA. Karar penceresi ICINDE oldugu icin serbest."""
    sn = izl.get(i)
    if not sn:
        return {}
    ilk = sn[0]
    erk = [s for s in sn if (s.get("yas_saat") or 0) <= 0.5] or sn[:1]
    son = erk[-1]
    ag, ac = ilk.get("atr_giriste"), son.get("atr_canli")
    tp = son.get("toplam_dakika") or 0
    return {
        "e_ilk_pnl": ilk.get("pnl_pct"),
        "e30_pnl": son.get("pnl_pct"),
        "e30_mae": son.get("mae_pct"),
        "e30_arti_oran": (100.0 * (son.get("arti_dakika") or 0) / tp) if tp > 0 else None,
        "e30_atr_genis": (ac / ag) if (ag and ac) else None,
        "e30_stopa_uzaklik": son.get("stopa_uzaklik_pct"),
        "giris_stop_mesafe": ilk.get("stop_mesafe_pct"),
        "e_kare": len(erk),
    }


# ---------------------------------------------------------------- defterler
cikti = []
sayim = collections.Counter()
eslesme_gecikme = []
defter_dolar = collections.Counter()
for ad, f in DEFTERLER:
    g = collections.defaultdict(list)
    for x in satirlar(f):
        g[x.get("id")].append(x)
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        no = ilk.get("notional") or 0
        if no <= 0:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)          # SUZGEC YOK
        fon = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        dolar = net + (sum(fon) if fon else 0.0)
        kap = datetime.datetime.strptime(son["ts"], F)
        tut = max((t.get("tutma_saat") or 0) for t in v)
        gir = kap - datetime.timedelta(hours=tut)
        sayim[ad] += 1
        defter_dolar[ad] += dolar
        d = ilk.get("derinlik_giriste") or {}
        r = {
            "defter": ad, "id": i, "sym": son["sym"], "yon": son["yon"],
            "giris_ts": gir.strftime(F), "gun": gir.date().isoformat(),
            "notional": no, "marjin": ilk.get("marjin") or 0,
            "kaldirac": ilk.get("kaldirac") or 0,
            "ret": 100.0 * dolar / no, "dolar": dolar,
            # --- giris ani, deftere yazilmis (yordayici, serbest)
            "l_skor": ilk.get("skor_giriste"), "l_chg24": ilk.get("chg24_giriste"),
            "l_pos": ilk.get("range_pos_giriste"), "l_smart": ilk.get("smart_giriste"),
            "l_stage": ilk.get("stage_giriste"), "l_rejim": ilk.get("rejim_giriste"),
            "l_kaynak": son.get("kaynak"),
            "l_slipaj": d.get("slipaj_pct"),
            "l_defter_usdt": d.get("defter_usdt_20"),
            # --- 🔴 SONUC TURETILMIS — YALNIZ kontrol katmani, yordayici DEGIL
            "_kontrol_tp1": bool(any(t.get("kismi") for t in v)),
            "_kontrol_sebep": son.get("sebep"),
            "_kontrol_tutma_saat": tut,
            "_kontrol_kaz": dolar > 0,
        }
        # aday arsivi eslesmesi
        L = aday.get(son["sym"])
        if L:
            ts = [z[0] for z in L]
            j = bisect.bisect_right(ts, gir) - 1
            if j >= 0:
                dk = (gir - ts[j]).total_seconds() / 60.0
                if 0 <= dk <= ESLESME_DK:
                    a = L[j][1]
                    for k in ADAY_ALAN:
                        r["a_" + k] = a.get(k)
                    r["a_gecikme_dk"] = round(dk, 1)
                    eslesme_gecikme.append(dk)
        r.update(erken_ozellikler(i) if ad == "testbot" else {})
        cikti.append(r)

# ---------------------------------------------------------------- mutabakat
print()
print("MUTABAKAT — defter toplamlariyla tutuyor mu")
print("-" * 100)
esl = sum(1 for r in cikti if r.get("a_score") is not None)
print("  %-9s %8s %10s %14s" % ("defter", "poz", "eslesen", "dolar toplam"))
for ad, _ in DEFTERLER:
    w = [r for r in cikti if r["defter"] == ad]
    e = sum(1 for r in w if r.get("a_score") is not None)
    print("  %-9s %8d %9d%% %+13.2f" % (ad, len(w), (100 * e // len(w)) if w else 0,
                                        sum(r["dolar"] for r in w)))
print("  %-9s %8d %9d%% %+13.2f" % ("TOPLAM", len(cikti),
                                    100 * esl // len(cikti) if cikti else 0,
                                    sum(r["dolar"] for r in cikti)))
if eslesme_gecikme:
    print("  eslesme gecikmesi: medyan %.1f dk · %%90 %.1f dk"
          % (statistics.median(eslesme_gecikme),
             sorted(eslesme_gecikme)[int(0.9 * len(eslesme_gecikme))]))
erk = sum(1 for r in cikti if r.get("e30_pnl") is not None)
print("  ilk-30dk ozelligi olan (yalniz testbot): %d" % erk)

# on-kayit pencereleri
KESIF0, KESIF1 = "2026-08-04", "2026-08-16"
DOG0, DOG1 = "2026-08-17", "2026-08-30"
k = [r for r in cikti if KESIF0 <= r["gun"] <= KESIF1 and r.get("a_score") is not None]
d_ = [r for r in cikti if DOG0 <= r["gun"] <= DOG1 and r.get("a_score") is not None]
print()
print("ON-KAYIT PENCERELERI (yalniz eslesmis pozisyonlar)")
print("-" * 100)
print("  KESIF     %s..%s   N=%4d  gun %2d  dolar %+10.2f"
      % (KESIF0, KESIF1, len(k), len({r["gun"] for r in k}), sum(r["dolar"] for r in k)))
print("  DOGRULAMA %s..%s   N=%4d  gun %2d  dolar %+10.2f"
      % (DOG0, DOG1, len(d_), len({r["gun"] for r in d_}), sum(r["dolar"] for r in d_)))

os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
with open(CIKTI, "w", encoding="utf-8") as f:
    json.dump(cikti, f)
print()
print("yazildi: %s  (%d satir)" % (os.path.relpath(CIKTI, PROJE), len(cikti)))
print("bot dosyalarina yazim: YOK — yalniz scratchpad/poz_yol/ altina cikti")
