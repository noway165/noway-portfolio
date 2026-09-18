@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Dang cai thu vien (lan dau hoi lau)...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check
start "" cmd /c "timeout /t 2 >nul & start http://127.0.0.1:5000"
python app.py
pause
