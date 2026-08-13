@echo off
title Sistema de Control de Proyectos - Windows
echo ==========================================================
echo   INICIANDO SISTEMA DE CONTROL DE PROYECTOS (WINDOWS)
echo ==========================================================

:: Comprobar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado o no se encuentra en el PATH de Windows.
    pause
    exit /b 1
)

echo Instalando dependencias necesarias (si faltan)...
python -m pip install eel pywebview PyQt6 qtpy PyQt6-WebEngine pandas openpyxl

echo.
echo Iniciando la aplicacion...
python eel_main.py

echo.
echo Aplicacion finalizada.
pause
