@echo off
cd /d "%~dp0"
echo Converting JSON to JS modules for WeChat mini-program...
echo.
python convert_to_js.py
echo.
pause