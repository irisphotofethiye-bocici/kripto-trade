#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PORTFOY ASAMASI — uc asamali siranin UCUNCUSU (ham -> mekanik -> PORTFOY).

CLAUDE.md sirasi: ham getiri -> ticaret mekanigi -> portfoy simulasyonu.
Ilk ikisi yapildi (24_rejim_kararliligi · 37_pos_mekanik). Bu, ucuncusu.

PORTFOY ASAMASI NE SORAR — per-islem kenar, PORTFOY KISITLARI altinda kaliyor mu?
   1) POZISYON SINIRI bagliyor mu? (maks_pozisyon dolu iken kac aday reddedildi)
   2) KUYRUK SIRASI isabetli mi? Bot skora gore siraliyor (testbot.py:1444).
      Skor sonucu ONGORUYOR mu — yoksa sira keyfi mi?
   3) BOYUTLANDIRMA ne yapiyor? risk sabit -> stop genisligi POZISYON BUYUKLUGUNU
      belirliyor. Genis stoplu (oynak) coinlerde notional kuculuyor mu?
   4) `pos` girişte kaydediliyor (`range_pos_giriste`) — botun KENDI islemlerinde
      olculen 5/5 iliski goruluyor mu?

⚠️ TANIMLAYICI OLCUM. HUKUM YAZILMAZ. Ileri sinav icin ayri on-kayit gerekir
   (`ON_KAYIT_pos_suzgec.md` bunun bir parcasini kapsiyor).

⚠️ KAZANMA ORANI POZISYON basina sayilir, KAYIT basina degil (CLAUDE.md).
   P&L TOPLARKEN suzgec UYGULANMAZ — kayitlar `id` ile birlestirilir.

SALT OKUMA.
"""
# [2026-08-25] cp1254 TUZAGI — kalici kapatma.
#   Windows konsolu cp1254; print() icindeki emoji/varyasyon secici CIKTI
#   YONLENDIRILDIGINDE UnicodeEncodeError firlatiyor ve betik COKUYOR.
#   Bu sinif bu projede BES kez isirdi. Emoji ayiklamak yerine stdout
#   guvenli hale getirilir; hata sinifi disiplinle degil ARACLA kapanir.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, collections, statistics as sx, math

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
F = "%Y-%m-%d %H:%M:%S"


def jl(ad):
    y = os.path.join(PROJE, ad)
    out = []
    if os.path.exists(y):
        with open(y, encoding="utf-8") as f:
            for s in f:
                if s.strip():
                    try:
                        out.append(json.loads(s))
                    except Exception:
                        pass
    return out


def pozisyonlar():
    """id ile birlestirilmis KAPANMIS pozisyonlar."""
    g = collections.defaultdict(list)
    for x in jl("testbot_islemler.jsonl"):
        g[x["id"]].append(x)
    out = []
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        son = v[-1]
        out.append({
            "id": i, "sym": son["sym"], "yon": son["yon"],
            "net": sum((t.get("sonuc_usdt") or 0) for t in v),
            "gun": son["ts"][:10], "ts": son["ts"],
            "skor": son.get("skor_giriste"),
            "pos": son.get("range_pos_giriste"),
            "chg24": son.get("chg24_giriste"),
            "rejim": son.get("rejim_giriste"),
            "kapi": (son.get("sebep_giris") or "?").split(":")[0],
            "tut": max((t.get("tutma_saat") or 0) for t in v),
            "kismi": any(t.get("kismi") for t in v)})
    return out


def gun_kumeli_t(ciftler):
    """[(gun, deger)] -> gun ortalamalarinin t'si."""
    g = collections.defaultdict(list)
    for gun, d in ciftler:
        g[gun].append(d)
    gunluk = [sx.mean(v) for v in g.values() if len(v) >= 2]
    if len(gunluk) < 5:
        return None, len(gunluk)
    m, sd = sx.mean(gunluk), sx.pstdev(gunluk)
    return (m / (sd / math.sqrt(len(gunluk))) if sd > 0 else None), len(gunluk)


def dilim_raporu(P, alan, ad, n=4):
    w = [p for p in P if isinstance(p.get(alan), (int, float))]
    if len(w) < 40:
        print("  %-18s N=%d yetersiz" % (ad, len(w)))
        return
    w.sort(key=lambda z: z[alan])
    k = len(w) // n
    print("  %s  (N=%d)" % (ad, len(w)))
    print("     %-14s %5s %10s %9s %8s" % ("dilim", "N", "ort net $", "kazanma", "medyan"))
    for i in range(n):
        d = w[i * k:(i + 1) * k] if i < n - 1 else w[i * k:]
        if not d:
            continue
        kz = sum(1 for z in d if z["net"] > 0)
        print("     %-14s %5d %+10.2f %8.0f%% %+8.2f"
              % ("%.2f-%.2f" % (d[0][alan], d[-1][alan]), len(d),
                 sx.mean(z["net"] for z in d), 100.0 * kz / len(d),
                 sx.median(z["net"] for z in d)))
    alt = w[:k]
    ust = w[-k:]
    fark = sx.mean(z["net"] for z in ust) - sx.mean(z["net"] for z in alt)
    # gun-kumeli: her gun icin ust-alt farki
    g = collections.defaultdict(lambda: [[], []])
    esik_alt, esik_ust = w[k - 1][alan], w[-k][alan]
    for z in w:
        if z[alan] <= esik_alt:
            g[z["gun"]][0].append(z["net"])
        elif z[alan] >= esik_ust:
            g[z["gun"]][1].append(z["net"])
    gunluk = [sx.mean(b) - sx.mean(a) for a, b in g.values() if a and b]
    t = None
    if len(gunluk) >= 5:
        m, sd = sx.mean(gunluk), sx.pstdev(gunluk)
        t = m / (sd / math.sqrt(len(gunluk))) if sd > 0 else None
    print("     UST - ALT ceyrek: %+.2f $   gun-kumeli t: %s  (%d gun)"
          % (fark, ("%+.2f" % t) if t is not None else "-", len(gunluk)))
    print()


if __name__ == "__main__":
    P = pozisyonlar()
    print("PORTFOY ASAMASI — botun KENDI islemleri")
    print("=" * 88)
    print("kapanmis pozisyon: %d   (kismi kayit iceren: %d)"
          % (len(P), sum(1 for p in P if p["kismi"])))
    print("toplam net: %+.2f $" % sum(p["net"] for p in P))
    print()

    # --- 1) POZISYON SINIRI BAGLIYOR MU
    print("1) POZISYON SINIRI")
    cfg = {}
    try:
        with open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8") as f:
            # ⚠️ testbot ayarlari "esikler" degil "testbot" bolumunde
            #    (testbot.py:53 -> evren.cfg().get("testbot")). Ilk surumde
            #    "esikler"den okundu, varsayilan 4 sanildi ve TASMA VAR gibi
            #    gorundu. Gercek deger 8; dagilim tam 8'de duruyor, tasma YOK.
            cfg = (json.load(f).get("testbot") or {})
    except Exception:
        pass
    maks = int(cfg.get("maks_pozisyon", 4))
    eq = jl("testbot_equity.jsonl")
    dolu = sum(1 for x in eq if (x.get("acik_sayisi") or 0) >= maks)
    var = sum(1 for x in eq if x.get("acik_sayisi") is not None)
    print("   maks_pozisyon (config): %d" % maks)
    if var:
        print("   tur sayisi: %d   sinir DOLU olan tur: %d  (%%%.1f)"
              % (var, dolu, 100.0 * dolu / var))
        dag = collections.Counter(x.get("acik_sayisi") for x in eq if x.get("acik_sayisi") is not None)
        print("   acik sayisi dagilimi: %s" % dict(sorted(dag.items())))
    else:
        print("   equity kaydinda acik_sayisi alani YOK -> sinir baglama orani olculemedi")
    print()

    # --- 2) KUYRUK SIRASI: SKOR sonucu ongoruyor mu
    print("2) KUYRUK SIRASI — bot skora gore siraliyor (testbot.py:1444)")
    dilim_raporu(P, "skor", "skor_giriste")

    # --- 3) pos: botun KENDI islemlerinde
    print("3) GIRISTEKI pos — 5/5 rejim bulgusu botun kendi islemlerinde goruluyor mu")
    dilim_raporu(P, "pos", "range_pos_giriste")

    # --- 4) BOYUTLANDIRMA
    print("4) BOYUTLANDIRMA — risk sabit, stop genisligi boyutu belirliyor")
    kay = [x for x in jl("testbot_islemler.jsonl") if x.get("marjin")]
    if kay:
        mar = [x["marjin"] for x in kay]
        print("   marjin $: medyan %.0f  %%25 %.0f  %%75 %.0f  min %.0f  max %.0f"
              % (sx.median(mar), sorted(mar)[len(mar)//4], sorted(mar)[3*len(mar)//4],
                 min(mar), max(mar)))
        kal = collections.Counter(x.get("kaldirac") for x in kay if x.get("kaldirac"))
        print("   kaldirac dagilimi: %s" % dict(sorted(kal.items())))
    print()

    # --- 5) KAPI x SONUC
    print("5) KAPI KARNESI (botun kendi islemleri)")
    for k, n in collections.Counter(p["kapi"] for p in P).most_common(6):
        w = [p for p in P if p["kapi"] == k]
        kz = sum(1 for z in w if z["net"] > 0)
        print("   %-22s N=%3d  toplam %+9.2f  ort %+7.2f  kazanma %%%.0f"
              % (k[:22], n, sum(z["net"] for z in w), sx.mean(z["net"] for z in w),
                 100.0 * kz / len(w)))
    print()
    print("TANIMLAYICI OLCUM — HUKUM YAZILMADI. Bot dosyalarina yazim: YOK")
