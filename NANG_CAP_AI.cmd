@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
  echo Chua co backend\.venv. Hay tao moi truong theo HUONG_DAN_CHAY.md truoc.
  pause
  exit /b 1
)
"backend\.venv\Scripts\python.exe" scripts\upgrade_ai_config.py
if errorlevel 1 goto failed
pushd backend
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed_pop
".venv\Scripts\python.exe" -m app.init_db
if errorlevel 1 goto failed_pop
popd
pushd frontend
call npm.cmd ci --no-audit --no-fund
if errorlevel 1 goto failed_pop
call npm.cmd run build
if errorlevel 1 goto failed_pop
popd
echo.
echo NANG CAP THANH CONG. Khoi dong lai backend va frontend nhu thuong le.
echo Mo file DOC_TRUOC_NANG_CAP_AI.md de xem cach chay va kiem thu.
pause
exit /b 0
:failed_pop
popd
:failed
echo.
echo Nang cap chua hoan tat. Doc thong bao loi phia tren.
pause
exit /b 1
