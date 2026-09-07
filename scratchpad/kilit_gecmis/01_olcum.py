#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAR KILIDI — BOTUN ESKI POZISYONLARINDA (KARSI-OLGU)

ON_KAYIT_kilit_gecmis.md · commit 737abf9 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 HUKUM YOK — cikti BETIMLEYICI (on-kayit bolum 2).
🔴 Kaybedene YANLI ornekleme (on-kayit bolum 3).
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, time, collections, datetime as dt, statistics as stx
import urllib.request, urllib.error

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)
MUMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mum")
os.makedirs(MUMD, exist_ok=True)

CFG = json.load(io.open(os.path.join(KOK, "kripto-config.json"), encoding="utf-8"))
MAL = CFG.get("maliyet", {})
TAKER = float(MAL.get("taker_fee_pct", 0.045)) / 100.0
SLIP = float(MAL.get("slippage_pct", 0.02)) / 100.0

TETIK_ROI, STOP_ROI, PAY = 20.0, 15.0, 0.20     # kullanici karari, SABIT
HEDEF_PCT = 10.0
TZ = 3
API = "https://fapi.binance.com/fapi/v1/klines"
TOL_DK, TOL_PNL = 10, 0.02                      # on-kayit bolum 4


def yerel_ms(s):
    t = dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return int((t - dt.timedelta(hours=TZ)).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def ms_str(ms):
    return (dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)
            + dt.timedelta(hours=TZ)).strftime("%m-%d %H:%M")


def mum_getir(sym, bas, bit):
    """1m mumlar. Disk onbellegi BIRLESTIRIR, EZMEZ (CLAUDE.md kurali)."""
    yol = os.path.join(MUMD, "%s.json" % sym)
    var = {}
    if os.path.exists(yol):
        try:
            for x in json.load(open(yol)):
                var[x[0]] = x
        except Exception:
            var = {}
    n0 = len(var)
    gerek = [t for t in range(bas - bas % 60000, bit + 60000, 60000) if t not in var]
    if gerek:
        cur = min(gerek)
        son = max(gerek)
        while cur <= son:
            u = "%s?symbol=%sUSDT&interval=1m&startTime=%d&endTime=%d&limit=1000" % (
                API, sym, cur, son)
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    d = json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 418:
                    raise RuntimeError("418 IP BAN — DUR")
                if e.code == 429:
                    time.sleep(5)
                    continue
                return None
            except Exception:
                return None
            if not d:
                break
            for k in d:
                var.setdefault(int(k[0]), [int(k[0]), float(k[2]), float(k[3]), float(k[4]),
                                           float(k[1])])
            if len(d) < 1000:
                break
            cur = int(d[-1][0]) + 60000
        if len(var) > n0:
            birlesik = sorted(var.values(), key=lambda z: z[0])
            if len(birlesik) < n0:
                raise RuntimeError("onbellek KISALDI: %s" % sym)
            tmp = yol + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(birlesik, fh, separators=(",", ":"))
            os.replace(tmp, yol)
    return [var[t] for t in sorted(var) if bas <= t <= bit]


def pnl_hesapla(giris, fiyat, miktar, yon):
    ce = fiyat * (1 - SLIP) if yon == "LONG" else fiyat * (1 + SLIP)
    yi = 1 if yon == "LONG" else -1
    return (ce - giris) * miktar * yi - miktar * ce * TAKER, ce


def yol_kos(bars, giris, stop, hedef, miktar, yon, kilit):
    """-> (net, sebep, ms, olaylar). kilit=True ise KAR KILIDI acik.

    Sira testbot bar dongusuyle AYNI: stop -> tetik -> hedef.
    """
    tetik = kstop = None
    if kilit:
        yi = 1 if yon == "LONG" else -1
        tetik = giris * (1 + yi * TETIK_ROI / 100.0 / K["k"])
        kstop = giris * (1 + yi * STOP_ROI / 100.0 / K["k"])
    kalan, st_ak, top = miktar, stop, 0.0
    alindi = False
    olay = []
    for b in bars:
        ts, hi, lo = b[0], b[1], b[2]
        vurdu_stop = (lo <= st_ak) if yon == "LONG" else (hi >= st_ak)
        if vurdu_stop:
            p, _ = pnl_hesapla(giris, st_ak, kalan, yon)
            top += p
            olay.append(("STOP_KILIT" if alindi else "STOP", ts, st_ak, kalan, p))
            return top, ("STOP_KILIT" if alindi else "STOP"), ts, olay
        if kilit and not alindi:
            vurdu_tetik = (hi >= tetik) if yon == "LONG" else (lo <= tetik)
            if vurdu_tetik:
                dilim = kalan * PAY
                p, _ = pnl_hesapla(giris, tetik, dilim, yon)
                top += p
                kalan -= dilim
                alindi = True
                st_ak = max(st_ak, kstop) if yon == "LONG" else min(st_ak, kstop)
                olay.append(("KILIT", ts, tetik, dilim, p))
        vurdu_hedef = (hi >= hedef) if yon == "LONG" else (lo <= hedef)
        if vurdu_hedef:
            p, _ = pnl_hesapla(giris, hedef, kalan, yon)
            top += p
            olay.append(("TP2", ts, hedef, kalan, p))
            return top, "TP2", ts, olay
    p, _ = pnl_hesapla(giris, bars[-1][3], kalan, yon)
    top += p
    olay.append(("ZAMAN", bars[-1][0], bars[-1][3], kalan, p))
    return top, "ZAMAN", bars[-1][0], olay


K = {"k": 1}          # yol_kos'un okudugu kaldirac (tek pozisyon islenirken set edilir)


def main():
    print("=" * 104)
    print("KAR KILIDI — BOTUN ESKI POZISYONLARINDA (KARSI-OLGU)")
    print("ON_KAYIT_kilit_gecmis.md (737abf9) · HUKUM YOK, BETIMLEYICI")
    print("=" * 104)

    rows = [json.loads(l) for l in io.open(os.path.join(KOK, "testbot_islemler.jsonl"),
                                           encoding="utf-8", errors="ignore") if l.strip()]
    g = collections.defaultdict(list)
    for r in rows:
        g[r.get("id")].append(r)
    tek = [v[0] for v in g.values() if len(v) == 1]
    cok = [v for v in g.values() if len(v) > 1]
    uygun = [x for x in tek if x.get("r") and x.get("kaldirac")
             and x.get("sebep") != "ELLE_KAPAT_TEMIZ_SAYFA"]
    print("pozisyon %d · tek kayitli %d · cok kayitli %d · islenecek %d"
          % (len(g), len(tek), len(cok), len(uygun)))
    print()

    tut, dis = [], collections.Counter()
    for i, r in enumerate(uygun, 1):
        sym, giris, cikis = r["sym"], r["giris"], r["cikis"]
        yon, k = r["yon"], r["kaldirac"]
        miktar = r["notional"] / giris
        yi = 1 if yon == "LONG" else -1
        if r["sebep"] == "STOP":
            stop = cikis / (1 - SLIP) if yon == "LONG" else cikis / (1 + SLIP)
        else:
            net_pct = (cikis / giris - 1) * 100.0 * yi
            risk_pct = net_pct / r["r"] if r["r"] else None
            if not risk_pct or risk_pct <= 0:
                dis["stop turetilemedi"] += 1
                continue
            stop = giris * (1 - yi * risk_pct / 100.0)
        hedef = giris * (1 + yi * HEDEF_PCT / 100.0)
        kapanis_ms = yerel_ms(r["ts"])
        giris_ms = kapanis_ms - int((r.get("tutma_saat") or 0) * 3600 * 1000)
        bars = mum_getir(sym, giris_ms - 5 * 60000, kapanis_ms + 20 * 60000)
        if not bars or len(bars) < 5:
            dis["mum yok"] += 1
            continue
        K["k"] = k
        # --- ZORUNLU SINAMA: gercek yolu yeniden uret
        net0, seb0, ms0, _ = yol_kos(bars, giris, stop, hedef, miktar, yon, False)
        if seb0 != r["sebep"]:
            dis["sebep uyusmadi (%s->%s)" % (r["sebep"], seb0)] += 1
            continue
        if abs(ms0 - kapanis_ms) > TOL_DK * 60000:
            dis["zaman uyusmadi"] += 1
            continue
        ger = r["sonuc_usdt"]
        if abs(net0 - ger) > max(abs(ger) * TOL_PNL, 0.5):
            dis["pnl uyusmadi"] += 1
            continue
        net1, seb1, ms1, olay1 = yol_kos(bars, giris, stop, hedef, miktar, yon, True)
        tut.append({"r": r, "net0": net0, "net1": net1, "seb1": seb1,
                    "tetikledi": any(o[0] == "KILIT" for o in olay1),
                    "k": k, "sym": sym, "ger": ger,
                    "sure0": (ms0 - giris_ms) / 3600000.0,
                    "sure1": (ms1 - giris_ms) / 3600000.0})
        if i % 40 == 0:
            print("   [%3d/%d] islendi %d · dislanan %d" % (i, len(uygun), len(tut), sum(dis.values())))

    N = len(uygun)
    dis_n = sum(dis.values())
    print()
    print("### 1) ZORUNLU SINAMA (on-kayit bolum 4)")
    print("   yeniden kuruldu %d / %d  (%%%.1f)" % (len(tut), N, 100.0 * len(tut) / N))
    print("   dislanan %d (%%%.1f):" % (dis_n, 100.0 * dis_n / N))
    for s, c in dis.most_common():
        print("      %-34s %d" % (s, c))
    if dis_n > 0.25 * N:
        print()
        print("   🔴 DISLANAN >%25 -> ON-KAYIT bolum 4: karsi-olgu YAYIMLANMAZ.")
        return
    print("   -> esik %25'in altinda, karsi-olgu yayimlanabilir")
    print()

    tetik = [x for x in tut if x["tetikledi"]]
    fark = [x["net1"] - x["net0"] for x in tut]
    print("### 2) TETIKLEME")
    print("   kilit tetikleyen %d / %d  (%%%.1f)"
          % (len(tetik), len(tut), 100.0 * len(tetik) / len(tut)))
    kald = collections.defaultdict(lambda: [0, 0])
    for x in tut:
        kald[x["k"]][0] += 1
        kald[x["k"]][1] += 1 if x["tetikledi"] else 0
    print("   %-8s %6s %8s %8s" % ("kaldirac", "N", "tetik", "%"))
    for k in sorted(kald):
        a, b = kald[k]
        print("   %-8s %6d %8d %7.1f%%" % ("%dx" % k, a, b, 100.0 * b / a))
    print()

    print("### 3) DOLAR ETKISI")
    print("   GERCEK toplam        %+10.2f $" % sum(x["net0"] for x in tut))
    print("   KARSI-OLGU toplam    %+10.2f $" % sum(x["net1"] for x in tut))
    print("   FARK                 %+10.2f $   (poz basina %+.2f · medyan %+.2f)"
          % (sum(fark), stx.mean(fark), stx.median(fark)))
    iy = sum(1 for f in fark if f > 0.01)
    ko = sum(1 for f in fark if f < -0.01)
    print("   iyilesen %d · kotulesen %d · degismeyen %d" % (iy, ko, len(fark) - iy - ko))
    if tetik:
        tf = [x["net1"] - x["net0"] for x in tetik]
        print("   YALNIZ tetikleyenlerde: fark %+.2f $ (poz basina %+.2f)"
              % (sum(tf), stx.mean(tf)))
    print()

    print("### 4) 🔴 KURALIN MALIYETI — kilit stopu ERKEN CIKARDI MI?")
    erken = [x for x in tetik if x["seb1"] == "STOP_KILIT" and x["r"]["sebep"] == "TP2"]
    kurtaran = [x for x in tetik if x["seb1"] == "STOP_KILIT" and x["r"]["sebep"] == "STOP"]
    print("   kilit stopu ile kapanan %d" % sum(1 for x in tetik if x["seb1"] == "STOP_KILIT"))
    print("      bunlardan GERCEKTE hedefe varan (kural KAYBETTIRDI) : %d" % len(erken))
    print("      bunlardan GERCEKTE stop olan   (kural KURTARDI)     : %d" % len(kurtaran))
    if kurtaran:
        print("      kurtarilan toplam: %+.2f $" % sum(x["net1"] - x["net0"] for x in kurtaran))
    if erken:
        print("      kaybedilen toplam: %+.2f $" % sum(x["net1"] - x["net0"] for x in erken))
    print()

    print("### 5) 🔴 DISARIDA KALAN 153 (on-kayit bolum 3) — KAZANANLAR")
    ted = 0
    for v in cok:
        ilk = sorted(v, key=lambda z: z.get("ts") or "")[0]
        kk = ilk.get("kaldirac")
        if not kk:
            continue
        # TP1'e ulasmis: TP1 ROI'si tetik ROI'sinden BUYUKSE kilit ONCE gelirdi
        gg, cc = ilk.get("giris"), ilk.get("cikis")
        if not gg or not cc:
            continue
        tp1_roi = abs(cc / gg - 1) * 100.0 * kk
        if tp1_roi >= TETIK_ROI:
            ted += 1
    print("   kismi kar alan pozisyon: %d" % len(cok))
    print("   bunlarin %d'inde TP1 ROI'si >= %%%.0f  ->  kilit TP1'DEN ONCE tetiklerdi"
          % (ted, TETIK_ROI))
    print("   ⚠️ Bu kume karsi-olguda YOK. Kilit onlarda da %20 alip stopu +%15'e")
    print("      cekerdi; net etkisi OLCULMEDI. Yani asagidaki hukum EKSIK bilgiyle.")
    print()

    print("=" * 104)
    print("OKUMA — ON_KAYIT bolum 2: HUKUM YOK")
    print("=" * 104)
    print("   Bu bir karsi-olgudur, ornek disi kanit DEGILDIR: karar veriyi")
    print("   ureten veriyle sinandi. Ayrica ornek KAYBEDENE YANLI (%d'inin"
          % len(tut))
    print("   %.0f%%'i STOP) cunku kazananlarin cogu kismi kar aldigi icin"
          % (100.0 * sum(1 for x in tut if x["r"]["sebep"] == "STOP") / len(tut)))
    print("   yeniden kurulamadi. Kural DEGISTIRILMEZ; hakem PENCERE-3.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
