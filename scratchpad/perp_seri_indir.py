#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PERP SERI INDIRICI — 5 dakikalik OI / long-short / taker serileri.

NEDEN ACELE: Binance futures/data uclari SABIT 30 GUN tutuyor (olculdu:
  29 gun geriye N=500 geliyor, 31 gun geriye HTTP 400). Yani her gun bir gun
  kayboluyor. izleyici.py 2026-08-13 19:32'de basladi; ondan ONCEKI 46 pozisyonun
  (29 sembol) serisi SADECE bu pencerede kurtarilabilir. En eski giris
  2026-07-23 22:33, sinir 2026-07-22 -> pay yaklasik 1,5 gun.

NE YAPMAZ: bot dosyalarina yazmaz, state'e dokunmaz, ag disinda yan etkisi yoktur.
  Yalniz scratchpad/perp_seri/ altina yazar. Yeniden calistirilabilir: indirilmis
  dosyayi atlar, yarida kalirsa kaldigi yerden devam eder.

Kullanim:
  python perp_seri_indir.py --pozisyonlar     46 pozisyonun sembolleri (ACIL)
  python perp_seri_indir.py --evren --n 150   olay calismasi icin genis tarama
  python perp_seri_indir.py --rapor           indirilmis kapsami ozetle
"""
import json, os, sys, argparse, datetime, collections, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(HERE)
sys.path.insert(0, PROJE)
import evren                                                    # noqa: E402

CIKTI = os.path.join(HERE, "perp_seri")
os.makedirs(CIKTI, exist_ok=True)

FAPI = "https://fapi.binance.com"
ADIM_MS = 300000                     # 5 dakika
LIMIT = 500                          # ucun tek istekte verdigi azami
PENCERE_MS = LIMIT * ADIM_MS         # ~41,7 saat
TAMPON_SA = 6                        # giristen once / cikistan sonra

# ucun adi -> (yol, zaman alani)  — hepsi 5m
UCLAR = {
    "oi":      ("/futures/data/openInterestHist", "timestamp"),
    "top_ls":  ("/futures/data/topLongShortPositionRatio", "timestamp"),
    "glob_ls": ("/futures/data/globalLongShortAccountRatio", "timestamp"),
    "taker":   ("/futures/data/takerlongshortRatio", "timestamp"),
}


def _ms(dt):
    return int(dt.timestamp() * 1000)


def _cek(uc, sym, bas_ms, bit_ms):
    """Bir ucun [bas,bit] araligini 500'luk dilimlerle ceker. -> [kayit] (zamana gore tekil)"""
    yol, zaman = UCLAR[uc]
    out, gorulen, t0 = [], set(), bas_ms
    while t0 < bit_ms:
        t1 = min(t0 + PENCERE_MS, bit_ms)
        u = ("%s%s?symbol=%sUSDT&period=5m&limit=%d&startTime=%d&endTime=%d"
             % (FAPI, yol, sym, LIMIT, t0, t1))
        try:
            d = evren.get(u, timeout=25)
        except Exception:
            d = None
        if not d:
            t0 = t1                       # bos dilim: ilerle, seriyi kesme
            continue
        for x in d:
            t = int(x[zaman])
            if t not in gorulen:
                gorulen.add(t)
                out.append(x)
        son = int(d[-1][zaman])
        t0 = max(son + ADIM_MS, t0 + PENCERE_MS)
        time.sleep(random.uniform(0.05, 0.15))   # sicak dongu nezaketi (evren.py deseni)
    out.sort(key=lambda x: int(x[zaman]))
    return out


def _klines(sym, bas_ms, bit_ms):
    """5m mumlar — taker ALIS hacmi (tbv) dahil. Kalici veri, ama ayni pencerede alinir."""
    out, gorulen, t0 = [], set(), bas_ms
    while t0 < bit_ms:
        u = ("%s/fapi/v1/klines?symbol=%sUSDT&interval=5m&startTime=%d&limit=1500"
             % (FAPI, sym, t0))
        try:
            d = evren.get(u, timeout=25)
        except Exception:
            d = None
        if not d:
            break
        for k in d:
            t = int(k[0])
            if t > bit_ms:
                continue
            if t not in gorulen:
                gorulen.add(t)
                out.append({"t": t, "o": float(k[1]), "h": float(k[2]), "l": float(k[3]),
                            "c": float(k[4]), "v": float(k[5]), "qv": float(k[7]),
                            "n": int(k[8]), "tbv": float(k[9]), "tqv": float(k[10])})
        yeni = int(d[-1][0]) + ADIM_MS
        if yeni <= t0 or len(d) < 1500:
            break
        t0 = yeni
        time.sleep(random.uniform(0.05, 0.15))
    out.sort(key=lambda x: x["t"])
    return out


def _kapsiyor_mu(yol, uc, bas_ms, bit_ms):
    """Var olan dosya istenen araligi KAPSIYOR mu?

    Duz 'dosya varsa atla' yanlisti: ayni sembol once DAR pencereyle indirilip
    sonra GENIS pencereyle istendiginde eksik dosya sessizce kabul edilirdi."""
    try:
        with open(yol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return None
    if not d:
        return None
    zaman = "t" if uc == "kline" else UCLAR[uc][1]
    t0, t1 = int(d[0][zaman]), int(d[-1][zaman])
    # iki dilimlik pay: uc, istenen ucta veri tutmuyor olabilir
    if t0 <= bas_ms + 2 * ADIM_MS and t1 >= bit_ms - 2 * ADIM_MS:
        return len(d)
    return None


def sembol_indir(sym, bas_dt, bit_dt, yeniden=False):
    """Bir sembolun tum uclarini indirir. -> {uc: kayit_sayisi}"""
    bas_ms, bit_ms = _ms(bas_dt), _ms(bit_dt)
    sonuc = {}
    for uc in list(UCLAR) + ["kline"]:
        yol = os.path.join(CIKTI, "%s_%s.json" % (sym, uc))
        if os.path.exists(yol) and not yeniden:
            n = _kapsiyor_mu(yol, uc, bas_ms, bit_ms)
            if n is not None:
                sonuc[uc] = n
                continue
        d = _klines(sym, bas_ms, bit_ms) if uc == "kline" else _cek(uc, sym, bas_ms, bit_ms)
        if d:
            # [2026-08-24 ONARIM] ESKIDEN: os.replace ile UZERINE YAZIYORDU.
            #   Bu, dar pencereyle yeniden calistirildiginda ESKI VERIYI SILIYORDU ve
            #   futures/data uclari 30 GUN tuttugu icin silinen kisim GERI GETIRILEMIYORDU.
            #   Gercek kayip: 58 sembolde 07-23..07-26 arasi OI/long-short/taker.
            # SIMDI: var olan dosyayla ZAMAN DAMGASINA gore BIRLESTIR.
            zaman = "t" if uc == "kline" else UCLAR[uc][1]
            birlesik = {}
            if os.path.exists(yol):
                try:
                    with open(yol, encoding="utf-8") as f:
                        for x in json.load(f):
                            birlesik[int(x[zaman])] = x
                except Exception:
                    pass
            eski_n = len(birlesik)
            for x in d:
                birlesik[int(x[zaman])] = x
            d = [birlesik[k] for k in sorted(birlesik)]
            if eski_n and len(d) < eski_n:
                raise RuntimeError("BIRLESTIRME KAYIP URETTI: %s %s (%d -> %d)"
                                   % (sym, uc, eski_n, len(d)))
            tmp = yol + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(d, f)
            os.replace(tmp, yol)          # atomik — yarim dosya birakma
        sonuc[uc] = len(d)
    return sonuc


def pozisyon_pencereleri():
    """izleyici ONCESI kapanan pozisyonlarin sembol -> (en erken giris, en gec cikis).

    Giris damgasi defterde YOK; kapanis ts'inden tutma_saat cikarilarak kurulur
    (kapanis kaydinda ikisi de var)."""
    kes = "2026-08-13 19:32:15"
    f = "%Y-%m-%d %H:%M:%S"
    g = collections.defaultdict(list)
    with open(os.path.join(PROJE, "testbot_islemler.jsonl"), encoding="utf-8") as fh:
        for satir in fh:
            if satir.strip():
                x = json.loads(satir)
                g[x["id"]].append(x)
    pen = {}
    for v in g.values():
        kapanis = max(t["ts"] for t in v)
        if kapanis >= kes:
            continue
        tut = max(t.get("tutma_saat") or 0 for t in v)
        bit = datetime.datetime.strptime(kapanis, f)
        gir = bit - datetime.timedelta(hours=tut)
        sym = v[0]["sym"]
        a, b = pen.get(sym, (gir, bit))
        pen[sym] = (min(a, gir), max(b, bit))
    return pen


def bot_sembolleri():
    """Botun DOKUNDUGU tum semboller (kapanmis + acik).

    NEDEN TAMAMI: izleyici.py oi3/oi24/top_ls/glob_ls/vol_x/pos alanlarini radar
    kaydindan KOPYALIYOR (izleyici.py:355-362) -> pozisyon icinde ~%7-10 benzersiz,
    yani 5 dk degil radar temposunda tazeleniyor. Hacim ve taker_15/60 CANLI
    (%94-100 benzersiz), ama OI ve long/short DEGIL. O yuzden izleyici kapsamindaki
    104 pozisyon icin de 5 dakikalik OI/long-short serisi INDIRILMEK ZORUNDA."""
    syms = set()
    with open(os.path.join(PROJE, "testbot_islemler.jsonl"), encoding="utf-8") as fh:
        for satir in fh:
            if satir.strip():
                syms.add(json.loads(satir)["sym"])
    try:
        with open(os.path.join(PROJE, "testbot_state.json"), encoding="utf-8") as fh:
            for p in json.load(fh).get("acik_pozisyonlar", []):
                syms.add(p["sym"])
    except Exception:
        pass
    # [2026-08-24] BTC/ETH HER ZAMAN dahil. Bot bu ikisinde islem acmiyor, bu yuzden
    #   --bot listesine hic girmiyorlardi ve gunluk gorev onlari TAZELEMIYORDU.
    #   Ikisi de rejim referansi (btc_rejim · rel3 · ayrisma) -> serileri sart.
    #   Yakalandi: ETH dosyasi 08-21'de kalmisti, digerlerinin hepsi 08-24'teydi.
    syms.update(("BTC", "ETH"))
    return sorted(syms)


def evren_sembolleri(n):
    """Olay calismasi icin en likit n sembol (hacme gore)."""
    try:
        d = evren.get("%s/fapi/v1/ticker/24hr" % FAPI, timeout=25)
    except Exception:
        return []
    u = [(float(x["quoteVolume"]), x["symbol"][:-4]) for x in d
         if x["symbol"].endswith("USDT") and float(x["quoteVolume"]) > 2e6]
    u.sort(reverse=True)
    return [s for _, s in u[:n]]


def rapor():
    dosya = [f for f in os.listdir(CIKTI) if f.endswith(".json")]
    if not dosya:
        print("perp_seri/ bos — once --pozisyonlar veya --evren calistir.")
        return
    say = collections.defaultdict(lambda: collections.defaultdict(int))
    for f in dosya:
        sym, uc = f[:-5].rsplit("_", 1)
        try:
            with open(os.path.join(CIKTI, f), encoding="utf-8") as fh:
                say[sym][uc] = len(json.load(fh))
        except Exception:
            say[sym][uc] = -1
    print("PERP SERI KAPSAMI — %d sembol" % len(say))
    print("%-10s %8s %8s %8s %8s %8s" % ("sym", "oi", "top_ls", "glob_ls", "taker", "kline"))
    print("-" * 56)
    for sym in sorted(say):
        s = say[sym]
        print("%-10s %8d %8d %8d %8d %8d"
              % (sym, s["oi"], s["top_ls"], s["glob_ls"], s["taker"], s["kline"]))
    bos = [s for s in say if say[s]["oi"] == 0]
    if bos:
        print("\nOI verisi BOS (muhtemelen 30 gun disi veya sembol yok): %s" % ", ".join(sorted(bos)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pozisyonlar", action="store_true", help="izleyici oncesi 46 pozisyonun sembolleri")
    ap.add_argument("--bot", action="store_true", help="botun dokundugu TUM semboller, tam 29 gun")
    ap.add_argument("--evren", action="store_true", help="olay calismasi icin genis tarama")
    ap.add_argument("--n", type=int, default=150, help="--evren icin sembol sayisi")
    ap.add_argument("--gun", type=float, default=29.0, help="--evren icin kac gun geriye (30 SINIR)")
    ap.add_argument("--rapor", action="store_true")
    ap.add_argument("--yeniden", action="store_true", help="var olan dosyalari da yeniden indir")
    a = ap.parse_args()

    if a.rapor:
        rapor()
        sys.exit(0)

    if a.pozisyonlar:
        pen = pozisyon_pencereleri()
        print("izleyici oncesi %d sembol indirilecek" % len(pen))
        for i, (sym, (gir, bit)) in enumerate(sorted(pen.items()), 1):
            b = gir - datetime.timedelta(hours=TAMPON_SA)
            e = bit + datetime.timedelta(hours=TAMPON_SA)
            s = sembol_indir(sym, b, e, a.yeniden)
            print("  [%2d/%2d] %-10s %s -> %s   oi=%d top=%d glob=%d taker=%d kline=%d"
                  % (i, len(pen), sym, b.strftime("%m-%d %H:%M"), e.strftime("%m-%d %H:%M"),
                     s["oi"], s["top_ls"], s["glob_ls"], s["taker"], s["kline"]))
            sys.stdout.flush()

    if a.bot:
        syms = bot_sembolleri()
        bit = datetime.datetime.now()
        bas = bit - datetime.timedelta(days=min(a.gun, 29.0))
        print("bot sembolleri: %d · %s -> %s (tam pencere)" % (len(syms), bas.date(), bit.date()))
        for i, sym in enumerate(syms, 1):
            s = sembol_indir(sym, bas, bit, a.yeniden)
            print("  [%3d/%3d] %-10s oi=%d top=%d glob=%d taker=%d kline=%d"
                  % (i, len(syms), sym, s["oi"], s["top_ls"], s["glob_ls"], s["taker"], s["kline"]))
            sys.stdout.flush()

    if a.evren:
        syms = evren_sembolleri(a.n)
        bit = datetime.datetime.now()
        bas = bit - datetime.timedelta(days=min(a.gun, 29.0))
        print("evren taramasi: %d sembol · %s -> %s" % (len(syms), bas.date(), bit.date()))
        for i, sym in enumerate(syms, 1):
            s = sembol_indir(sym, bas, bit, a.yeniden)
            print("  [%3d/%3d] %-10s oi=%d top=%d glob=%d taker=%d kline=%d"
                  % (i, len(syms), sym, s["oi"], s["top_ls"], s["glob_ls"], s["taker"], s["kline"]))
            sys.stdout.flush()

    print("\nbot dosyalarina yazim: YOK (yalniz scratchpad/perp_seri/)")
