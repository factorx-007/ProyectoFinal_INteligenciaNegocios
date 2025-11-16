@echo off
title Análisis COVID-19 Colombia
echo ========================================
echo Proyecto Final Inteligencia de Negocios
echo Análisis de COVID-19 en Colombia
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.8 o superior
    pause
    exit /b 1
)

REM Verificar si pip está disponible
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip no está disponible
    echo Por favor, asegúrate de tener pip instalado
    pause
    exit /b 1
)

REM Instalar dependencias si no están instaladas
echo 📦 Verificando dependencias...
pip install -r requirements.txt

REM Verificar si Streamlit está instalado
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Instalando Streamlit...
    pip install streamlit
)

echo.
echo 🚀 Iniciando aplicación...
echo La aplicación estará disponible en http://localhost:8501
echo.
echo Presiona CTRL+C para detener la aplicación
echo.

REM Ejecutar la aplicación
python -m streamlit run app_analisis_covid.py --server.port 8501

pause