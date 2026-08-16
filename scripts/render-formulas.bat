@echo off
cd /d "%~dp0.."
echo [1/3] 正在用 KaTeX 渲染公式...
node scripts/render-questions-html.mjs
if %ERRORLEVEL% NEQ 0 (
    echo [×] 渲染失败，请确认 Node.js 已安装
    pause
    exit /b 1
)
echo [2/3] 复制到小程序数据目录...
copy /Y "mini-program\miniprogram\data\questions_with_html.js" "mini-program\miniprogram\data\questions_with_html.js" >nul
echo [3/3] 完成！
echo.
echo 现在打开微信开发者工具，题库就会显示漂亮的数学公式！
pause