#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NOTR-LONG PANELI — tek bot, iki kol (2026-09-06, kullanici karari)

KULLANICI: "paneli duzenle, panelde sadece bu bot olsun, temiz bir sayfa olsun."

NEDEN YENI DOSYA (eski panel_sunucu.py'ye DOKUNULMADI):
   Eski panel 9 sekmelik ve tamami testbot'a ozel — "Bot'un Kafasi", "Bot vs Ben",
   "Defterim", "Coin Ara"... Bu botta o sekmelerin cogunun karsiligi YOK.
   Eskisini notrlong'a cevirmek hem buyuk hem riskli bir ameliyat olurdu.
   Bu panel ON-KAYIDIN olctugu seyi gosterir, baska bir sey degil.

NE GOSTERIR:
   - iki kol YAN YANA (N1 skor kapisiz / N2 skor >= 45)
   - PENCERE ILERLEMESI: gun X/30 ve kol basina kapanmis pozisyon X/80
     (on-kayit: IKISI BIRDEN dolmadan hukum YOK)
   - N1 - N2 farki = olcumun kendisi (skor kapisi ne katiyor)
   - acik pozisyonlar (canli PnL) · son kapanislar · log kuyrugu

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

import json, os, time, argparse, datetime, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
KOLLAR = ("n1", "n2")
KOL_AD = {"n1": "N1 — skor kapisi YOK", "n2": "N2 — skor >= 45"}

# ON-KAYIT bolum 5: pencere. Burada SABIT, panelden degistirilemez.
PENCERE_GUN = 30
PENCERE_N = 80

_fiyat_cache = {"ts": 0.0, "d": {}}


def _yol(kol, ek):
    return os.path.join(HERE, "notrlong_%s_%s" % (kol, ek))


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
    if time.time() - _fiyat_cache["ts"] < 20 and _fiyat_cache["d"]:
        return _fiyat_cache["d"]
    try:
        r = urllib.request.urlopen(
            "https://fapi.binance.com/fapi/v1/ticker/price", timeout=12).read()
        _fiyat_cache["d"] = dict((x["symbol"], float(x["price"]))
                                 for x in json.loads(r))
        _fiyat_cache["ts"] = time.time()
    except Exception:
        pass
    return _fiyat_cache["d"]


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
        out.append({
            "id": i, "sym": s.get("sym"), "yon": s.get("yon"),
            "sebep": s.get("sebep"), "ts": s.get("ts"),
            "net": sum(t.get("sonuc_usdt") or 0 for t in v),
            "fon": sum(t["funding_usdt"] for t in v
                       if t.get("funding_usdt") is not None),
            "tutma": max((t.get("tutma_saat") or 0) for t in v),
        })
    out.sort(key=lambda x: x["ts"] or "")
    return out


def kol_ozet(kol):
    st = _oku_json(_yol(kol, "state.json"))
    if not st:
        return {"var": False, "ad": KOL_AD[kol]}
    kap = karne(_oku_jsonl(_yol(kol, "islemler.jsonl")))
    fy = fiyatlar()
    acik = []
    acik_pnl = 0.0
    for p in st.get("acik_pozisyonlar") or []:
        px = fy.get(p["sym"])
        yi = 1 if p.get("yon") == "LONG" else -1
        pnl = ((px - p["giris"]) * p["miktar"] * yi) if px else None
        if pnl:
            acik_pnl += pnl
        acik.append({"sym": p.get("sym"), "yon": p.get("yon"),
                     "giris": p.get("giris"), "anlik": px, "pnl": pnl,
                     "stop": p.get("stop"), "hedef": p.get("tp2"),
                     "kaldirac": p.get("kaldirac"), "ts": p.get("acilis_ts")})
    net = sum(p["net"] for p in kap)
    kaz = sum(1 for p in kap if p["net"] > 0)
    # pencere ilerlemesi
    bas = st.get("baslangic_ts") or ""
    gun = 0.0
    try:
        b = datetime.datetime.strptime(bas[:19], "%Y-%m-%d %H:%M:%S")
        gun = (datetime.datetime.now() - b).total_seconds() / 86400.0
    except Exception:
        pass
    return {
        "var": True, "kol": kol, "ad": KOL_AD[kol], "durum": st.get("durum"),
        "equity": st.get("equity", 0), "baslangic": st.get("baslangic_bakiye", 0),
        "acik": acik, "acik_pnl": acik_pnl,
        "kapanan": len(kap), "net": net,
        "kazanan_pct": (100.0 * kaz / len(kap)) if kap else None,
        "fonlama": sum(p["fon"] for p in kap),
        "son": list(reversed(kap[-12:])),
        "gun": gun, "gun_hedef": PENCERE_GUN, "n_hedef": PENCERE_N,
        "baslangic_ts": bas,
    }


def durum():
    d = dict((k, kol_ozet(k)) for k in KOLLAR)
    n1, n2 = d["n1"], d["n2"]
    fark = None
    if n1.get("var") and n2.get("var"):
        fark = {"net": n1["net"] - n2["net"],
                "kapanan": n1["kapanan"] - n2["kapanan"],
                "equity": n1["equity"] - n2["equity"]}
    log = []
    try:
        with open(os.path.join(HERE, "notrlong_log.txt"),
                  encoding="utf-8", errors="replace") as f:
            log = f.read().splitlines()[-40:]
    except Exception:
        pass
    return {"kollar": d, "fark": fark, "log": log,
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
main{padding:20px;max-width:1180px;margin:0 auto}
.izgara{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px}
.kart{background:var(--k);border:1px solid var(--cz);border-radius:10px;padding:16px}
.kart h2{margin:0 0 3px;font-size:14px;font-weight:600}
.alt{color:var(--y3);font-size:11px;margin-bottom:12px}
.buyuk{font-size:26px;font-weight:650;font-variant-numeric:tabular-nums;margin:2px 0 10px}
.satir{display:flex;justify-content:space-between;padding:5px 0;
       border-bottom:1px solid var(--cz);font-size:13px}
.satir:last-child{border-bottom:none}
.satir span:first-child{color:var(--y2)}
.satir b{font-variant-numeric:tabular-nums;font-weight:600}
.iyi{color:var(--iyi)} .kotu{color:var(--kotu)} .sonuk{color:var(--y3)}
.cubuk{height:6px;background:var(--cz);border-radius:99px;overflow:hidden;margin:6px 0 3px}
.cubuk i{display:block;height:100%;background:var(--vurgu)}
.cubuk i.tam{background:var(--iyi)}
table{width:100%;border-collapse:collapse;font-size:12.5px;
      font-variant-numeric:tabular-nums}
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
<div class="ust"><h1>NOTR-LONG</h1>
  <span class="rozet" id="rz1">-</span><span class="rozet" id="rz2">-</span>
  <span class="sonuk" style="margin-left:auto;font-size:11px" id="zaman"></span></div>
<main>
  <div class="izgara" id="kollar"></div>
  <div id="farkKutu"></div>
  <h3>Açık pozisyonlar</h3><div class="sar" id="acik"></div>
  <h3>Son kapanışlar</h3><div class="sar" id="son"></div>
  <h3>Log</h3><pre id="log">-</pre>
</main>
<script>
const $=s=>document.querySelector(s);
const p2=v=>(v==null?'-':v.toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2}));
const isr=v=>v==null?'':(v>=0?'+':'');
const snf=v=>v==null?'':(v>0?'iyi':(v<0?'kotu':'sonuk'));
function cubuk(o,h){const y=Math.min(100,100*o/h);
  return '<div class="cubuk"><i class="'+(o>=h?'tam':'')+'" style="width:'+y+'%"></i></div>';}

function kolKart(k){
  if(!k.var) return '<div class="kart"><h2>'+k.ad+'</h2><div class="bos">Başlatılmamış.</div></div>';
  const f=k.equity-k.baslangic;
  return '<div class="kart"><h2>'+k.ad+'</h2>'+
   '<div class="alt">'+k.durum+' · başlangıç '+k.baslangic_ts.slice(0,16)+'</div>'+
   '<div class="buyuk">'+p2(k.equity)+' $ <span style="font-size:15px" class="'+snf(f)+'">'+
     isr(f)+p2(f)+'</span></div>'+
   '<div class="satir"><span>Kapanan pozisyon</span><b>'+k.kapanan+' / '+k.n_hedef+'</b></div>'+
   cubuk(k.kapanan,k.n_hedef)+
   '<div class="satir"><span>Pencere günü</span><b>'+k.gun.toFixed(1)+' / '+k.gun_hedef+'</b></div>'+
   cubuk(k.gun,k.gun_hedef)+
   '<div class="satir"><span>Realize P&amp;L</span><b class="'+snf(k.net)+'">'+isr(k.net)+p2(k.net)+' $</b></div>'+
   '<div class="satir"><span>Açık pozisyon</span><b>'+k.acik.length+
     (k.acik.length?' <span class="'+snf(k.acik_pnl)+'">('+isr(k.acik_pnl)+p2(k.acik_pnl)+' $)</span>':'')+'</b></div>'+
   '<div class="satir"><span>Kazanan oranı</span><b>'+(k.kazanan_pct==null?'-':k.kazanan_pct.toFixed(0)+'%')+'</b></div>'+
   '<div class="satir"><span>Fonlama</span><b class="'+snf(k.fonlama)+'">'+isr(k.fonlama)+p2(k.fonlama)+' $</b></div>'+
   '</div>';
}

async function yenile(){
  let d; try{ d=await (await fetch('/api/durum')).json(); }catch(e){ return; }
  const n1=d.kollar.n1, n2=d.kollar.n2;
  $('#kollar').innerHTML = kolKart(n1)+kolKart(n2);
  for(const [id,k] of [['#rz1',n1],['#rz2',n2]]){
    const e=$(id); if(!k.var){e.textContent='-';continue;}
    e.textContent=k.kol.toUpperCase()+' '+k.durum;
    e.className='rozet '+(k.durum==='AKTIF'?'iyi':(k.durum==='DURDU'?'kotu':'uyari'));
  }
  $('#zaman').textContent='yenilendi '+d.simdi;

  $('#farkKutu').innerHTML = d.fark ?
   ('<div class="kart" style="margin-top:16px"><h2>Ölçüm: N1 − N2</h2>'+
    '<div class="alt">Tek değişken skor kapısı. Bu fark, kapının ne kattığının cevabı.</div>'+
    '<div class="satir"><span>Realize P&amp;L farkı</span><b class="'+snf(d.fark.net)+'">'+
      isr(d.fark.net)+p2(d.fark.net)+' $</b></div>'+
    '<div class="satir"><span>Kapanan pozisyon farkı</span><b>'+isr(d.fark.kapanan)+d.fark.kapanan+'</b></div>'+
    '<div class="not">Pencere <b>30 gün</b> VE kol başına <b>80 kapanmış pozisyon</b> — '+
    '<b>ikisi birden</b> dolmadan hüküm yok. Bu kutu ilerlemeyi gösterir, sonucu değil.</div></div>') : '';

  let ah='<table><tr><th>kol</th><th>sembol</th><th>yön</th><th>giriş</th><th>anlık</th>'+
         '<th>PnL $</th><th>stop</th><th>hedef</th></tr>';
  let n=0;
  for(const k of [n1,n2]) if(k.var) for(const p of k.acik){ n++;
    ah+='<tr><td class="sonuk">'+k.kol+'</td><td>'+p.sym+'</td><td>'+p.yon+'</td>'+
        '<td>'+(p.giris??'-')+'</td><td>'+(p.anlik??'-')+'</td>'+
        '<td class="'+snf(p.pnl)+'">'+isr(p.pnl)+p2(p.pnl)+'</td>'+
        '<td class="sonuk">'+(p.stop??'-')+'</td><td class="sonuk">'+(p.hedef??'-')+'</td></tr>';}
  $('#acik').innerHTML = n? ah+'</table>' : '<div class="bos">Açık pozisyon yok.</div>';

  let sh='<table><tr><th>kol</th><th>zaman</th><th>sembol</th><th>sebep</th>'+
         '<th>net $</th><th>tutma</th></tr>';
  let liste=[];
  for(const k of [n1,n2]) if(k.var) for(const p of k.son) liste.push([k.kol,p]);
  liste.sort((a,b)=>(b[1].ts||'').localeCompare(a[1].ts||''));
  for(const [kol,p] of liste.slice(0,20))
    sh+='<tr><td class="sonuk">'+kol+'</td><td class="sonuk">'+(p.ts||'').slice(5,16)+'</td>'+
        '<td>'+p.sym+'</td><td class="sonuk">'+p.sebep+'</td>'+
        '<td class="'+snf(p.net)+'">'+isr(p.net)+p2(p.net)+'</td>'+
        '<td class="sonuk">'+(p.tutma||0).toFixed(1)+' sa</td></tr>';
  $('#son').innerHTML = liste.length? sh+'</table>' : '<div class="bos">Henüz kapanan pozisyon yok.</div>';

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
    print("SALT-OKUNUR — hicbir dosyaya yazmaz.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
