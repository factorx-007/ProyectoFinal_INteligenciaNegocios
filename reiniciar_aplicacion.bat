@echo off
echo Reiniciando aplicaci¢n COVID-19...
echo.

echo Limpiando cach‚ de datos...
python limpiar_cache.py
echo.

echo Iniciando aplicaci¢n...
python run_app.py