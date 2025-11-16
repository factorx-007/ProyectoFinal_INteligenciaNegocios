# Proyecto Final Inteligencia de Negocios - Análisis de COVID-19 en Colombia

## Descripción
Esta aplicación realiza un análisis exhaustivo de los casos positivos de COVID-19 en Colombia utilizando datos del gobierno colombiano.

## Requisitos
- Python 3.8 o superior
- Las dependencias listadas en `requirements.txt`

## Instalación
1. Clonar el repositorio
2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Ejecución
Para ejecutar la aplicación Streamlit:
```
streamlit run app_analisis_covid.py
```

## Uso
1. Al iniciar la aplicación, haz clic en "Cargar Datos" en la barra lateral
2. Los datos se cargarán desde el archivo CSV y se guardarán en caché para futuras ejecuciones
3. Utiliza los filtros en la barra lateral para explorar los datos
4. Navega entre las diferentes pestañas para ver distintos análisis

## Estructura del Proyecto
- `app_analisis_covid.py`: Aplicación principal de Streamlit
- `procesamiento.py`: Procesamiento y limpieza de datos
- `analisis.py`: Generación de gráficos y análisis estadísticos
- `Casos_positivos_de_COVID-19_en_Colombia.csv`: Datos fuente (debe ser descargado por separado)
- `datos_procesados/`: Directorio con datos procesados y en caché

## Notas
- La primera ejecución puede tardar varios minutos debido al tamaño del archivo de datos
- Los datos se almacenan en caché para mejorar el rendimiento en ejecuciones posteriores