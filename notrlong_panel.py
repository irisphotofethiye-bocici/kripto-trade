#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NOTR-LONG PANELI — TEK KOL (2026-09-06, kullanici karari)

KULLANICI: "paneli duzenle, panelde sadece bu bot olsun, temiz bir sayfa olsun."
           "skor kapisini kaldir."  -> iki kol yerine TEK KOL.

NEDEN YENI DOSYA (eski panel_sunucu.py'ye DOKUNULMADI):
   Eski panel 9 sekmelik ve tamami testbot'a ozel — "Bot'un Kafasi", "Bot vs Ben",
   "Defterim", "Coin Ara"... Bu botta o sekmelerin cogunun karsiligi YOK.

NE GOSTERIR:
   - kasa · acik pozisyonlar (canli PnL) · kapanmis pozisyonlar
   - PENCERE ILERLEMESI: gun X/30 ve kapanmis pozisyon X/80
     (on-kayit bolum 5: IKISI BIRDEN dolmadan hukum YOK)
   - SKOR DAGILIMI: kapi kaldirildi ama defter skor_giriste'yi yaziyor;
     skor sorusu SONRADAN buradan olculecek (on-kayit bolum 11)
   - son kapanislar · log kuyrugu

SALT-OKUNUR: hicbir state/defter dosyasina YAZMAZ. Islem acma/kapama YOK.
   (Eski panelde 'ayna_kapat' gibi eylem uclari vardi; burada BILEREK yok —
   CLAUDE.md: "olcum penceresine elle mudahale girerse hakem kalmaz".)

Kullanim: python notrlong_panel.py [--port 8787]
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, time, argparse, datetime, urllib.request, urllib.parse, subprocess, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "notrlong_state.json")
ISLEMLERF = os.path.join(HERE, "notrlong_islemler.jsonl")
LOGF = os.path.join(HERE, "notrlong_log.txt")

# ON-KAYIT bolum 5: pencere. Panelden degistirilemez.
PENCERE_GUN = 30
PENCERE_N = 80

_fiyat = {"ts": 0.0, "d": {}}


def _oku_json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _oku_jsonl(p):
    out = []
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            for l in f:
                l = l.strip()
                if l:
                    try:
                        out.append(json.loads(l))
                    except Exception:
                        pass
    except Exception:
        pass
    return out


def fiyatlar():
    """TEK cagrida tum perp fiyatlari, 20 sn cache."""
    if time.time() - _fiyat["ts"] < 20 and _fiyat["d"]:
        return _fiyat["d"]
    try:
        r = urllib.request.urlopen(
            "https://fapi.binance.com/fapi/v1/ticker/price", timeout=12).read()
        _fiyat["d"] = dict((x["symbol"], float(x["price"])) for x in json.loads(r))
        _fiyat["ts"] = time.time()
    except Exception:
        pass
    return _fiyat["d"]


def karne(kayitlar):
    """id ile birlestirilmis pozisyon karnesi.
    CLAUDE.md: P&L TOPLARKEN kismi kayitlar DAHIL (yoksa TP1'de realize edilen
    kar kaybolur); POZISYON SAYARKEN haric (TP1 pozisyonu ikiye boluyor)."""
    poz = {}
    for t in kayitlar:
        poz.setdefault(t.get("id"), []).append(t)
    out = []
    for i, v in poz.items():
        v.sort(key=lambda z: z.get("ts") or "")
        s = v[-1]
        ilk = v[0]
        net = sum(t.get("sonuc_usdt") or 0 for t in v)
        marjin = ilk.get("marjin") or 0
        out.append({
            "id": i, "sym": s.get("sym"), "sebep": s.get("sebep"), "ts": s.get("ts"),
            "net": net,
            "fon": sum(t["funding_usdt"] for t in v
                       if t.get("funding_usdt") is not None),
            "tutma": max((t.get("tutma_saat") or 0) for t in v),
            "skor": s.get("skor_giriste"),
            # --- detay (2026-09-06)
            "yon": ilk.get("yon"), "giris": ilk.get("giris"), "cikis": s.get("cikis"),
            "kaldirac": ilk.get("kaldirac"), "marjin": marjin,
            "notional": ilk.get("notional"),
            "roi": (net / marjin * 100.0) if marjin else None,
            "r": s.get("r"),
            "stage": ilk.get("stage_giriste"), "smart": ilk.get("smart_giriste"),
            "kismi": len(v) > 1,
        })
    out.sort(key=lambda x: x["ts"] or "")
    return out


def liqmap_bedava_calistir(sym):
    """liqmap_bedava.py'yi ALT SUREC olarak kosar ve seviyeleri doner.

    🔴 UCRETSIZ: Binance aggTrades. Apify/CoinGlass CAGRILMAZ.
    Panel salt-okunurlugu KORUNUR — betik de hicbir dosyaya yazmaz.
    """
    if not sym or not sym.isalnum():
        return {"hata": "gecersiz sembol"}
    yol = os.path.join(HERE, "liqmap_bedava.py")
    if not os.path.exists(yol):
        return {"hata": "liqmap_bedava.py yok"}
    try:
        r = subprocess.run([sys.executable, yol, "--symbol", sym,
                            "--pay", "1", "--poz", "--n", "5"],
                           capture_output=True, text=True, timeout=300,
                           encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"hata": "zaman asimi (300 sn)"}
    if r.returncode != 0:
        return {"hata": (r.stderr or "")[-200:]}
    sat = []
    for l in (r.stdout or "").splitlines():
        l = l.rstrip()
        if "ANLIK" in l or ("%" in l and l.strip().startswith(("0", "1", "2", "3",
                                                               "4", "5", "6", "7",
                                                               "8", "9"))):
            sat.append(l.strip())
    bilgi = [l.strip() for l in (r.stdout or "").splitlines()
             if "efektif esik" in l or "secilen" in l]
    return {"sym": sym, "satirlar": sat, "bilgi": bilgi, "maliyet_usd": 0.0}


def durum():
    st = _oku_json(STATEF)
    if not st:
        return {"var": False, "simdi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    kap = karne(_oku_jsonl(ISLEMLERF))
    fy = fiyatlar()
    acik, acik_pnl = [], 0.0
    for p in st.get("acik_pozisyonlar") or []:
        # 🔴 HATA DUZELTMESI 2026-09-06: ticker anahtarlari 'ARXUSDT' bicimindedir,
        #   pozisyon kaydinda ise sembol 'ARX'. Eskiden fy.get("ARX") araniyordu ->
        #   HER ZAMAN None -> acik PnL ve acik_pnl toplami HEP 0 gorunuyordu.
        _s = p["sym"]
        px = fy.get(_s) or fy.get(_s + "USDT")
        yi = 1 if p.get("yon") == "LONG" else -1
        pnl = ((px - p["giris"]) * p["miktar"] * yi) if px else None
        if pnl:
            acik_pnl += pnl
        g = p.get("giris") or 0
        marjin = p.get("marjin") or 0
        notional = (p.get("miktar") or 0) * g
        stop = p.get("stop")
        hedef = p.get("tp2")
        # 🔴 tp1_alindi bu botta "TP1 ALINDI" DEMEK DEGIL: sabit_hedef_kur()
        #    kismi kari KAPATMAK icin True yapiyor ve tp1=tp2 atiyor.
        #    Dogru etiket: kismi kar acik mi kapali mi.
        kismi_kapali = (p.get("cikis_modu") == "sabit_hedef")
        tp1_gercek = (bool(p.get("tp1_alindi")) and not kismi_kapali)
        acik.append({
            "sym": p.get("sym"), "yon": p.get("yon"), "giris": g,
            "anlik": px, "pnl": pnl,
            "pnl_pct": ((pnl / marjin * 100.0) if (pnl is not None and marjin) else None),
            "stop": stop, "hedef": hedef,
            "stop_pct": (abs(stop - g) / g * 100.0) if (stop and g) else None,
            "hedef_pct": (abs(hedef - g) / g * 100.0) if (hedef and g) else None,
            "kaldirac": p.get("kaldirac"), "marjin": marjin, "notional": notional,
            "risk": p.get("risk_usdt"), "likidasyon": p.get("likidasyon"),
            "skor": p.get("skor_giriste"), "stage": p.get("stage_giriste"),
            "giris_ts": (p.get("giris_ts") or "")[:16],
            "kismi_kapali": kismi_kapali, "tp1_alindi": tp1_gercek,
            "stop_tasindi": (p.get("stop") != p.get("stop_orijinal")),
            # --- GEOMETRI (2026-09-06): hedef SABIT %, stop ATR'ye bagli ->
            #     R:R pozisyondan pozisyona degisir, basabas isabet de oyle.
            "kald_hedef_roi": ((abs(hedef - g) / g * 100.0 * (p.get("kaldirac") or 1))
                               if (hedef and g) else None),
            "kald_stop_roi": ((abs(stop - g) / g * 100.0 * (p.get("kaldirac") or 1))
                              if (stop and g) else None),
            "rr": ((abs(hedef - g) / abs(stop - g))
                   if (hedef and stop and abs(stop - g) > 0) else None),
            "basabas": ((100.0 / (1.0 + abs(hedef - g) / abs(stop - g)))
                        if (hedef and stop and abs(stop - g) > 0) else None),
            # --- KAR KILIDI (2026-09-07, kullanici karari) ---
            #   Kullanici bu kurali KENDI actigi pozlarda da elle uygulayacak;
            #   seviyeler burada okunabilsin diye tasiniyor.
            #   Seviyeler notrlong.kilit_kur() tarafindan pozisyona YAZILIR;
            #   panel formulu KOPYALAMAZ (tek kaynak = notrlong.kilit_seviyeleri).
            "kilit_tetik": p.get("kilit_tetik"),
            "kilit_stop": p.get("kilit_stop"),
            "kilit_alindi": bool(p.get("kilit_alindi")),
            "kilit_uzak_pct": ((p.get("kilit_tetik") / px - 1) * 100.0
                               if (px and p.get("kilit_tetik")) else None),
        })
    # --- FUNDING ve MUHASEBE (2026-09-06)
    # CLAUDE.md: sonuc_usdt FONLAMAYI ICERMEZ; funding dogrudan equity'den duser.
    fon_acik = sum((p.get("funding_toplam") or 0)
                   for p in (st.get("acik_pozisyonlar") or []))
    fon_kapali = sum(k["fon"] for k in kap)
    ucret = st.get("kumulatif_giris_ucret") or 0
    realize = sum(k["net"] for k in kap)
    bas = st.get("baslangic_bakiye") or 0
    beklenen = bas + realize + fon_kapali + fon_acik - ucret
    muh = {"baslangic": bas, "realize": realize,
           "funding_kapali": fon_kapali, "funding_acik": fon_acik,
           "giris_ucret": ucret, "beklenen": beklenen,
           "sapma": (st.get("equity") or 0) - beklenen}

    gun = 0.0
    try:
        b = datetime.datetime.strptime((st.get("baslangic_ts") or "")[:19],
                                       "%Y-%m-%d %H:%M:%S")
        gun = (datetime.datetime.now() - b).total_seconds() / 86400.0
    except Exception:
        pass
    kaz = sum(1 for p in kap if p["net"] > 0)

    # SKOR DAGILIMI — kapi kaldirildi, soru SONRADAN buradan olculecek
    skor_kova = {}
    for p in kap:
        if p["skor"] is None:
            continue
        k = int(p["skor"] // 10) * 10
        d = skor_kova.setdefault(k, {"n": 0, "net": 0.0, "kaz": 0})
        d["n"] += 1
        d["net"] += p["net"]
        if p["net"] > 0:
            d["kaz"] += 1
    skor = [{"bant": "%d-%d" % (k, k + 9), "n": v["n"], "net": v["net"],
             "kaz": 100.0 * v["kaz"] / v["n"]} for k, v in sorted(skor_kova.items())]

    log = []
    try:
        with open(LOGF, encoding="utf-8", errors="replace") as f:
            log = f.read().splitlines()[-40:]
    except Exception:
        pass

    return {"var": True, "durum": st.get("durum"), "equity": st.get("equity", 0),
            "baslangic": st.get("baslangic_bakiye", 0),
            "baslangic_ts": st.get("baslangic_ts") or "",
            "son_cycle": st.get("son_cycle_ts"),
            "acik": acik, "acik_pnl": acik_pnl,
            "muh": muh,
            "kapanan": len(kap), "net": sum(p["net"] for p in kap),
            "kazanan_pct": (100.0 * kaz / len(kap)) if kap else None,
            "fonlama": sum(p["fon"] for p in kap),
            "son": list(reversed(kap[-20:])), "skor": skor,
            "gun": gun, "gun_hedef": PENCERE_GUN, "n_hedef": PENCERE_N,
            "log": log,
            "simdi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


SAYFA = r"""<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NOTR-LONG</title><style>
:root{--bg:#0d1117;--k:#161b22;--cz:#21262d;--y:#e6edf3;--y2:#9198a1;--y3:#6e7681;
      --iyi:#3fb950;--kotu:#f85149;--uyari:#d29922;--vurgu:#58a6ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--y);
     font:14px/1.5 ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif}
.ust{position:sticky;top:0;z-index:9;background:var(--k);border-bottom:1px solid var(--cz);
     padding:12px 20px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
h1{margin:0;font-size:16px;font-weight:650;letter-spacing:.2px}
.rozet{font-size:11px;padding:3px 9px;border-radius:99px;background:var(--cz);color:var(--y2)}
.rozet.iyi{background:#12261a;color:var(--iyi)} .rozet.kotu{background:#2d1214;color:var(--kotu)}
.rozet.uyari{background:#2b2412;color:var(--uyari)}
main{padding:20px;max-width:1080px;margin:0 auto}
.izgara{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.kart{background:var(--k);border:1px solid var(--cz);border-radius:10px;padding:16px}
.kart h2{margin:0 0 3px;font-size:14px;font-weight:600}
.alt{color:var(--y3);font-size:11px;margin-bottom:12px}
.buyuk{font-size:30px;font-weight:650;font-variant-numeric:tabular-nums;margin:2px 0 12px}
.satir{display:flex;justify-content:space-between;padding:5px 0;
       border-bottom:1px solid var(--cz);font-size:13px}
.satir:last-child{border-bottom:none}
.satir span:first-child{color:var(--y2)}
.satir b{font-variant-numeric:tabular-nums;font-weight:600}
.iyi{color:var(--iyi)} .kotu{color:var(--kotu)} .sonuk{color:var(--y3)}
.cubuk{height:6px;background:var(--cz);border-radius:99px;overflow:hidden;margin:6px 0 3px}
.cubuk i{display:block;height:100%;background:var(--vurgu)}
.cubuk i.tam{background:var(--iyi)}
table{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums}
th{text-align:left;color:var(--y3);font-weight:500;padding:6px 8px;
   border-bottom:1px solid var(--cz);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
td{padding:6px 8px;border-bottom:1px solid var(--cz)}
tr:last-child td{border-bottom:none}
.sar{overflow-x:auto}
.bos{color:var(--y3);padding:14px 0;font-size:13px}
pre{background:var(--bg);border:1px solid var(--cz);border-radius:8px;padding:12px;
    font-size:11.5px;color:var(--y2);overflow-x:auto;max-height:260px;margin:0}
.not{background:#161b22;border-left:3px solid var(--uyari);padding:10px 14px;
     border-radius:0 8px 8px 0;font-size:12.5px;color:var(--y2);margin:16px 0}
h3{font-size:13px;margin:22px 0 10px;font-weight:600;color:var(--y2)}
</style></head><body>
<div class="ust"><h1>NOTR-LONG</h1><span class="rozet" id="rz">-</span>
  <span class="sonuk" style="font-size:11px">tek kol · skor kapisi yok</span>
  <span class="sonuk" style="margin-left:auto;font-size:11px" id="zaman"></span></div>
<main>
  <div class="izgara" id="kartlar"></div>
  <h3>Açık pozisyonlar</h3><div class="bos" style="margin:0 0 6px"><b>Hedef %10 = FİYAT hareketi</b>, marjinin %10&apos;u değil — marjine göre getiri = fiyat%% &times; kaldıraç. Dolar riski her pozisyonda sabit ($150); kaldıraç R:R&apos;yi <b>değiştirmez</b>. &#9888; Hedef sabit %10, stop ATR&apos;ye bağlı &rarr; <b>R:R ve başabaş pozisyondan pozisyona değişir</b>; başabaş &gt;%35 olan pozisyon kırmızı gösterilir (ölçülen isabet ~%25). PnL % = marjine göre (kaldıraçlı). <b>Çıkış modu:</b> hedef <b>sabit %10 AKTİF</b> (tp2 = giriş &times; 1,10). <b>KÂR KİLİDİ AKTİF (2026-09-07, kullanıcı kararı):</b> koyulan paranın <b>%20&apos;si kadar kâr</b> olunca pozisyonun <b>%20&apos;si kapanır</b> ve stop <b>%15 kâra</b> çekilir. Fiyat karşılığı: tetik = giriş &times; (1 + 0,20/kaldıraç), stop = giriş &times; (1 + 0,15/kaldıraç) &mdash; <b>kaldıraçtan bağımsız</b>. &#9888; Bu, ön-kayıt bölüm 2&apos;deki <b>&quot;kısmi kâr kapalı&quot;</b> kararını <b>DEĞİŞTİRİR</b> (D/8: ölçüm penceresi sıfırlandı).</div><div class="sar" id="acik"></div>
  <h3>Skor bandına göre sonuç <span class="sonuk" style="font-weight:400">— kapı yok, ölçüm sonradan</span></h3>
  <div class="sar" id="skor"></div>
  <h3>Kapanan pozisyonlar</h3><div class="bos" style="margin:0 0 6px">ROI % = marjine göre &middot; R = kapanış kaydının R degeri (&#9888; kısmi kâr alınmışsa R yalnız <b>kalan yarıyı</b> gösterir, net $ ise tümünü) &middot; funding ayrı sütunda, net $ içinde <b>değildir</b>.</div><div class="sar" id="son"></div>
  <h3>Log</h3><pre id="log">-</pre>
</main>
<script>
const $=s=>document.querySelector(s);
const p2=v=>(v==null?'-':v.toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2}));
const isr=v=>v==null?'':(v>=0?'+':'');
const snf=v=>v==null?'':(v>0?'iyi':(v<0?'kotu':'sonuk'));
function cubuk(o,h){const y=Math.min(100,100*o/h);
  return '<div class="cubuk"><i class="'+(o>=h?'tam':'')+'" style="width:'+y+'%"></i></div>';}

async function yenile(){
  let d; try{ d=await (await fetch('/api/durum')).json(); }catch(e){ return; }
  $('#zaman').textContent='yenilendi '+d.simdi;
  if(!d.var){ $('#kartlar').innerHTML='<div class="kart"><div class="bos">Başlatılmamış.</div></div>'; return; }

  const e=$('#rz'); e.textContent=d.durum;
  e.className='rozet '+(d.durum==='AKTIF'?'iyi':(d.durum==='DURDU'?'kotu':'uyari'));

  const f=d.equity-d.baslangic; const m=d.muh||{};
  $('#kartlar').innerHTML =
   '<div class="kart"><h2>Kasa</h2><div class="alt">başlangıç '+d.baslangic_ts.slice(0,16)+
     ' · son tur '+(d.son_cycle||'-').slice(11,16)+'</div>'+
   '<div class="buyuk">'+p2(d.equity)+' $ <span style="font-size:16px" class="'+snf(f)+'">'+
     isr(f)+p2(f)+'</span></div>'+
   '<div class="satir"><span>Realize P&amp;L</span><b class="'+snf(d.net)+'">'+isr(d.net)+p2(d.net)+' $</b></div>'+
   '<div class="satir"><span>Açık pozisyon</span><b>'+d.acik.length+' / 8'+
     (d.acik.length?' <span class="'+snf(d.acik_pnl)+'">('+isr(d.acik_pnl)+p2(d.acik_pnl)+' $)</span>':'')+'</b></div>'+
   '<div class="satir"><span>Kazanan oranı</span><b>'+(d.kazanan_pct==null?'-':d.kazanan_pct.toFixed(0)+'%')+'</b></div>'+
   '<div class="satir"><span>Fonlama</span><b class="'+snf(d.fonlama)+'">'+isr(d.fonlama)+p2(d.fonlama)+' $</b></div>'+
   '</div>'+
   '<div class="kart"><h2>Kasa muhasebesi</h2>'+
   '<div class="alt">CLAUDE.md: <b>sonuc_usdt fonlamayı İÇERMEZ</b> — funding doğrudan kasadan düşer.</div>'+
   '<table style="margin-top:6px">'+
   '<tr><td>başlangıç</td><td style="text-align:right">'+p2(m.baslangic)+' $</td></tr>'+
   '<tr><td>realize P&amp;L (kapanan)</td><td style="text-align:right" class="'+snf(m.realize)+'">'+isr(m.realize)+p2(m.realize)+' $</td></tr>'+
   '<tr><td>funding — kapanan</td><td style="text-align:right" class="'+snf(m.funding_kapali)+'">'+isr(m.funding_kapali)+p2(m.funding_kapali)+' $</td></tr>'+
   '<tr><td>funding — açık</td><td style="text-align:right" class="'+snf(m.funding_acik)+'">'+isr(m.funding_acik)+p2(m.funding_acik)+' $</td></tr>'+
   '<tr><td>giriş ücreti (taker)</td><td style="text-align:right" class="kotu">-'+p2(m.giris_ucret)+' $</td></tr>'+
   '<tr style="border-top:1px solid #444"><td><b>kasa (equity)</b></td><td style="text-align:right"><b>'+p2(d.equity)+' $</b></td></tr>'+
   '<tr><td class="sonuk">mutabakat sapması</td><td style="text-align:right" class="sonuk">'+isr(m.sapma)+p2(m.sapma)+' $</td></tr>'+
   '</table>'+
   '<div class="alt" style="margin-top:6px">Açık pozisyonların kâr/zararı kasaya <b>henüz yazılmadı</b>.</div></div>'+
  '<div class="kart"><h2>Ölçüm penceresi</h2>'+
   '<div class="alt">ikisi birden dolmadan hüküm yok</div>'+
   '<div class="satir"><span>Kapanan pozisyon</span><b>'+d.kapanan+' / '+d.n_hedef+'</b></div>'+
   cubuk(d.kapanan,d.n_hedef)+
   '<div class="satir"><span>Gün</span><b>'+d.gun.toFixed(2)+' / '+d.gun_hedef+'</b></div>'+
   cubuk(d.gun,d.gun_hedef)+
   '<div class="not">Ön-kayıt bölüm 7: <b>N 30 günde 80\'e ulaşmazsa</b> sonuç '+
   '<b>"ölçülemedi"</b> olur ve pencere <b>uzatılmaz</b>.</div></div>';

  const n0=(v,d0)=>(v===null||v===undefined)?'-':Number(v).toFixed(d0??2);
  window.liqmap=async function(sym){
    const btn=document.getElementById('lqb_'+sym), out=document.getElementById('lq_'+sym);
    if(!btn||!out) return;
    btn.disabled=true; btn.textContent='çekiliyor…'; out.textContent='';
    try{
      const r=await (await fetch('/api/liqmap?sym='+encodeURIComponent(sym))).json();
      if(r.hata){ out.innerHTML='<span class="kotu">'+r.hata+'</span>'; }
      else{
        let h='<div class="sonuk">'+(r.bilgi||[]).join(' · ')+'</div>';
        for(const l of (r.satirlar||[])){
          const anlik=l.indexOf('ANLIK')>=0, stop=l.indexOf('STOP')>=0;
          h+='<div style="font-family:monospace'+(anlik?';font-weight:700':'')+
             (stop?';color:#c0392b':'')+'">'+l.replace(/</g,'&lt;')+'</div>';
        }
        h+='<div class="sonuk">maliyet 0 USD · bağlam katmanı, sinyal değil</div>';
        out.innerHTML=h;
      }
    }catch(e){ out.innerHTML='<span class="kotu">hata</span>'; }
    btn.disabled=false; btn.textContent='harita çek';
  };
  let ah='<table><tr><th>sembol</th><th>yön</th><th>kald.</th><th>marjin $</th>'+
         '<th>büyüklük $</th><th>risk $</th><th>giriş</th><th>anlık</th>'+
         '<th>PnL $</th><th>PnL %</th><th>stop</th><th>hedef</th>'+
         '<th>R:R</th><th>başabaş</th><th>kâr kilidi</th><th>liqmap</th><th>çıkış modu</th></tr>';
  for(const p of d.acik)
    ah+='<tr><td><b>'+p.sym+'</b><div class="sonuk" style="font-size:11px">'+
          (p.giris_ts??'')+' · skor '+(p.skor??'-')+' · '+(p.stage??'-')+'</div></td>'+
        '<td>'+p.yon+'</td>'+
        '<td><b>'+(p.kaldirac??'-')+'x</b></td>'+
        '<td>'+n0(p.marjin)+'</td>'+
        '<td>'+n0(p.notional)+'</td>'+
        '<td class="sonuk">'+n0(p.risk)+'</td>'+
        '<td>'+(p.giris??'-')+'</td><td>'+(p.anlik??'-')+'</td>'+
        '<td class="'+snf(p.pnl)+'"><b>'+isr(p.pnl)+p2(p.pnl)+'</b></td>'+
        '<td class="'+snf(p.pnl_pct)+'">'+isr(p.pnl_pct)+n0(p.pnl_pct,1)+'%</td>'+
        '<td class="sonuk">'+(p.stop??'-')+'<div style="font-size:11px">-'+n0(p.stop_pct,2)+'% fiyat / -'+n0(p.kald_stop_roi,1)+'% ROI'+
          (p.stop_tasindi?' <span title="stop tasindi">↑</span>':'')+
          '<br>liq '+(p.likidasyon??'-')+'</div></td>'+
        '<td class="sonuk">'+(p.hedef??'-')+'<div style="font-size:11px">+'+n0(p.hedef_pct,2)+'% fiyat'+
          '<br><b>+'+n0(p.kald_hedef_roi,1)+'% ROI</b></div></td>'+
        '<td><b>'+n0(p.rr,2)+'</b></td>'+
        '<td class="'+((p.basabas??0)>35?'kotu':'sonuk')+'">'+n0(p.basabas,1)+'%'+
          '<div style="font-size:11px">ölçülen ~%25</div></td>'+
        // --- KAR KILIDI (2026-09-07): tetik / kilitlenen stop / durum
        '<td class="'+(p.kilit_alindi?'iyi':'sonuk')+'">'+
          (p.kilit_tetik?('tetik <b>'+p.kilit_tetik+'</b>'+
            (p.kilit_uzak_pct!==null&&p.kilit_uzak_pct!==undefined
               ? '<div style="font-size:11px">'+(p.kilit_uzak_pct>0?'+':'')+n0(p.kilit_uzak_pct,2)+'% uzak</div>'
               : '')+
            '<div style="font-size:11px">stop &rarr; '+(p.kilit_stop??'-')+'</div>'+
            (p.kilit_alindi?'<div style="font-size:11px"><b>ALINDI ✓</b></div>':''))
            : '<span style="font-size:11px">kurulmadı</span>')+'</td>'+
        // --- LIQMAP dugmesi (UCRETSIZ surum; Apify CAGRILMAZ)
        '<td><button onclick="liqmap(''+p.sym+'')" id="lqb_'+p.sym+'" '+
          'style="font-size:11px;padding:3px 7px;cursor:pointer">harita çek</button>'+
          '<div id="lq_'+p.sym+'" style="font-size:10px;line-height:1.5;margin-top:4px"></div></td>'+
        '<td class="sonuk">'+(p.kismi_kapali
            ? '<b>sabit %10 hedef</b><div style="font-size:11px">kısmi kâr (TP1) kapalı</div>'
            : (p.tp1_alindi?'<b>TP1 alındı</b><div style="font-size:11px">kısmi kâr açık</div>'
                           :'kısmi kâr açık<div style="font-size:11px">TP1 alınmadı</div>'))+'</td></tr>';
  $('#acik').innerHTML = d.acik.length? ah+'</table>' : '<div class="bos">Açık pozisyon yok.</div>';

  let kh='<table><tr><th>skor bandı</th><th>N</th><th>net $</th><th>kazanan</th></tr>';
  for(const s of d.skor)
    kh+='<tr><td>'+s.bant+'</td><td>'+s.n+'</td>'+
        '<td class="'+snf(s.net)+'">'+isr(s.net)+p2(s.net)+'</td>'+
        '<td>'+s.kaz.toFixed(0)+'%</td></tr>';
  $('#skor').innerHTML = d.skor.length? kh+'</table>' :
    '<div class="bos">Henüz kapanan pozisyon yok — skor bandı ölçümü doldukça oluşacak.</div>';

  const nn=(v,k)=>(v===null||v===undefined)?'-':Number(v).toFixed(k??2);
  let sh='<table><tr><th>zaman</th><th>sembol</th><th>yön</th><th>kald.</th><th>marjin $</th>'+
         '<th>giriş</th><th>çıkış</th><th>net $</th><th>ROI %</th><th>R</th>'+
         '<th>funding $</th><th>sebep</th><th>tutma</th></tr>';
  for(const p of d.son)
    sh+='<tr><td class="sonuk">'+(p.ts||'').slice(5,16)+'</td>'+
        '<td><b>'+p.sym+'</b><div class="sonuk" style="font-size:11px">skor '+(p.skor??'-')+
          ' · '+(p.stage??'-')+(p.kismi?' · <b>kısmi</b>':'')+'</div></td>'+
        '<td>'+(p.yon??'-')+'</td>'+
        '<td>'+(p.kaldirac??'-')+'x</td>'+
        '<td>'+nn(p.marjin)+'</td>'+
        '<td>'+(p.giris??'-')+'</td><td>'+(p.cikis??'-')+'</td>'+
        '<td class="'+snf(p.net)+'"><b>'+isr(p.net)+p2(p.net)+'</b></td>'+
        '<td class="'+snf(p.roi)+'">'+isr(p.roi)+nn(p.roi,1)+'%</td>'+
        '<td class="'+snf(p.r)+'">'+isr(p.r)+nn(p.r,2)+'</td>'+
        '<td class="'+snf(p.fon)+'">'+isr(p.fon)+nn(p.fon,3)+'</td>'+
        '<td class="sonuk">'+p.sebep+'</td>'+
        '<td class="sonuk">'+(p.tutma||0).toFixed(1)+' sa</td></tr>';
  $('#son').innerHTML = d.son.length? sh+'</table>' : '<div class="bos">Henüz kapanan pozisyon yok.</div>';

  $('#log').textContent = d.log.length? d.log.join('\n') : '(log henüz yok)';
}
yenile(); setInterval(yenile, 20000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _gonder(self, kod, tip, govde):
        self.send_response(kod)
        self.send_header("Content-Type", tip)
        self.send_header("Content-Length", str(len(govde)))
        self.end_headers()
        self.wfile.write(govde)

    def do_GET(self):
        try:
            if self.path.startswith("/api/durum"):
                self._gonder(200, "application/json; charset=utf-8",
                             json.dumps(durum(), ensure_ascii=False).encode("utf-8"))
            elif self.path.startswith("/api/liqmap"):
                # 🔴 YALNIZ UCRETSIZ SURUM. Apify/CoinGlass'a BU UCTAN ASLA
                #    gidilmez (ucretli cagri onay ister — CLAUDE.md).
                q = urllib.parse.urlparse(self.path).query
                sym = (urllib.parse.parse_qs(q).get("sym") or [""])[0].upper()
                self._gonder(200, "application/json; charset=utf-8",
                             json.dumps(liqmap_bedava_calistir(sym),
                                        ensure_ascii=False).encode("utf-8"))
            elif self.path in ("/", "/index.html"):
                self._gonder(200, "text/html; charset=utf-8", SAYFA.encode("utf-8"))
            else:
                self._gonder(404, "text/plain; charset=utf-8", b"yok")
        except Exception as e:
            self._gonder(500, "text/plain; charset=utf-8", str(e)[:200].encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print("NOTR-LONG paneli: http://127.0.0.1:%d" % a.port)
    print("SALT-OKUNUR - hicbir dosyaya yazmaz.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
