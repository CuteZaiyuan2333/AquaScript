@echo off
chcp 65001 >nul
title AquaScript Editor Launcher

echo.
echo ========================================
echo    🌊 AquaScript Editor 启动器
echo ========================================
echo.

cd /d "%~dp0"

REM 检查虚拟环境
if exist "..\\.venv\\Scripts\\activate.bat" (
    echo 激活虚拟环境...
    call "..\\.venv\\Scripts\\activate.bat"
) else (
    echo 警告: 未找到虚拟环境，使用系统 Python
)

echo 启动 AquaScript 编辑器...
echo.

python desktop_app.py

if errorlevel 1 (
    echo.
    echo 启动失败！请检查以下问题：
    echo 1. 确保已安装 Python
    echo 2. 确保已安装必要的依赖包
    echo 3. 检查网络连接
    echo.
    pause
)