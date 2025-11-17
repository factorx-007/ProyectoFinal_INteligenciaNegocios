# Proyecto Final Inteligencia de Negocios - Análisis de COVID-19 en Colombia

## Descripción
Esta aplicación realiza un análisis exhaustivo de los casos positivos de COVID-19 en Colombia utilizando datos del gobierno colombiano.

## Novedades Importantes
- ✅ **Descarga Rápida**: Ahora puedes usar `gdown` para descargar el archivo directamente desde Google Drive
- ✅ **Formato Parquet**: Conversión automática a formato Parquet para mejor rendimiento (hasta 90% menos espacio)

## Requisitos
- Python 3.8 o superior
- Las dependencias listadas en `requirements.txt`

## Instalación
1. Clonar el repositorio
2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. (Opcional) Para descarga rápida:
   ```
   pip install gdown
   ```

## Ejecución
### Opción 1: Ejecución normal
```
streamlit run app_analisis_covid.py
```

### Opción 2: Configuración automática
Ejecuta `setup_and_convert.bat` para instalar dependencias y convertir datos automáticamente

## Uso
1. Al iniciar la aplicación, haz clic en "Cargar Datos" en la barra lateral
2. La aplicación intentará descargar el dataset automáticamente (si tienes `gdown`)
3. Los datos se cargarán desde el archivo CSV o Parquet y se guardarán en caché
4. Utiliza los filtros en la barra lateral para explorar los datos
5. Navega entre las diferentes pestañas para ver distintos análisis

## Estructura del Proyecto
- `app_analisis_covid.py`: Aplicación principal de Streamlit
- `procesamiento.py`: Procesamiento y limpieza de datos
- `analisis.py`: Generación de gráficos y análisis estadísticos
- `Casos_positivos_de_COVID-19_en_Colombia.csv`: Datos fuente
- `Casos_positivos_de_COVID-19_en_Colombia.parquet`: Datos en formato comprimido (más rápido)
- `datos_procesados/`: Directorio con datos procesados y en caché
- `convert_to_parquet.py`: Script para convertir CSV a Parquet
- `setup_and_convert.bat`: Script de configuración automática

## Notas
- La primera ejecución puede tardar varios minutos debido al tamaño del archivo de datos
- Los datos se almacenan en caché para mejorar el rendimiento en ejecuciones posteriores
- El formato Parquet reduce el tiempo de carga en un 80-90%

## Deployment
Para instrucciones detalladas de deployment, consulta el archivo `DEPLOYMENT.md`.