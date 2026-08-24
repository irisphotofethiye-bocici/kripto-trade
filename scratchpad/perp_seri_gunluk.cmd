@echo off
REM ============================================================================
REM KriptoPerpSeri gunluk arsiv isi  (2026-08-24)
REM
REM NEDEN VAR: Binance /futures/data/* uclari (openInterestHist ·
REM   topLongShortPositionRatio · globalLongShortAccountRatio ·
REM   takerlongshortRatio) YALNIZ 30 GUN tutuyor. Bu seriler CEKILEMEZ,
REM   ancak ARSIVLENIR -> kosulmadigi her gun pencerenin kuyrugundan bir gun
REM   KALICI olarak duser. (klines ve fundingRate KALICI, bu kapsamda degil.)
REM
REM NEDEN .CMD: gorev dogrudan "cmd /c ..." ile kurulmustu ve cmd bas/son
REM   tirnaklari yutup CALISMADI (LastTaskResult=1, log hic olusmadi).
REM   Toplu is dosyasi tirnak sorununu tamamen ortadan kaldirir.
REM
REM Bota DOKUNMAZ: yalniz scratchpad\perp_seri\ altina yazar.
REM ============================================================================
setlocal
set PY=C:\Users\alper\AppData\Local\Programs\Python\Python312\python.exe
set KOK=C:\Users\alper\Desktop\kripto trade\scratchpad
set LOG=%KOK%\perp_seri_indir.log

cd /d "%KOK%"
if not exist "%PY%" (
    echo [%DATE% %TIME%] HATA: python bulunamadi: %PY% >> "%LOG%"
    exit /b 9
)

echo. >> "%LOG%"
echo ================ %DATE% %TIME%  BASLADI ================ >> "%LOG%"
"%PY%" perp_seri_indir.py --bot >> "%LOG%" 2>&1
set RC=%ERRORLEVEL%
"%PY%" perp_seri_indir.py --rapor >> "%LOG%" 2>&1
echo ================ %DATE% %TIME%  BITTI (indirici cikis=%RC%) ================ >> "%LOG%"
exit /b %RC%
