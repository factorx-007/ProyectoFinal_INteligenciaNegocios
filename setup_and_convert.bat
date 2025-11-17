@echo off
echo 🚀 Configurando entorno y convirtiendo datos COVID-19 a formato Parquet
echo ======================================================================

echo.
echo 1. Instalando dependencias necesarias...
echo ----------------------------------------
pip install gdown

echo.
echo 2. Instalando/actualizando otras dependencias...
echo -----------------------------------------------
pip install -r requirements.txt

echo.
echo 3. Convirtiendo archivo CSV a Parquet...
echo ---------------------------------------
python convert_to_parquet.py

echo.
echo 4. Verificando archivos generados...
echo ----------------------------------
dir "*.parquet"

echo.
echo ✅ Proceso completado!
echo.
echo 💡 Recomendaciones:
echo    - Usa el archivo Parquet para mejor rendimiento
echo    - Reinicia tu aplicación para usar el nuevo formato
echo.
pause