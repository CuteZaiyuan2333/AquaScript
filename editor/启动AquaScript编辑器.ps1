# AquaScript Editor PowerShell 启动脚本
# 设置控制台编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    🌊 AquaScript Editor 启动器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本目录
Set-Location $PSScriptRoot

# 检查虚拟环境
$venvPath = Join-Path ".." ".venv" "Scripts" "Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "警告: 未找到虚拟环境，使用系统 Python" -ForegroundColor Yellow
}

Write-Host "启动 AquaScript 编辑器..." -ForegroundColor Green
Write-Host ""

try {
    python desktop_app.py
} catch {
    Write-Host ""
    Write-Host "启动失败！请检查以下问题：" -ForegroundColor Red
    Write-Host "1. 确保已安装 Python" -ForegroundColor Red
    Write-Host "2. 确保已安装必要的依赖包" -ForegroundColor Red
    Write-Host "3. 检查网络连接" -ForegroundColor Red
    Write-Host ""
    Read-Host "按回车键退出"
}