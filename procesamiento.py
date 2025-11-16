import pandas as pd
import os
import requests
import json
from pathlib import Path

class ProcesadorCOVID:
    def __init__(self, ruta_archivo='Casos_positivos_de_COVID-19_en_Colombia.csv'):
        self.ruta_archivo = ruta_archivo
        self.ruta_cache = 'datos_procesados/datos_covid.parquet'
        self.ruta_estadisticas = 'datos_procesados/estadisticas.json'
        
    def descargar_dataset(self, file_id='1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r'):
        """
        Descarga el dataset desde Google Drive si no existe localmente.
        Reemplaza 'YOUR_GOOGLE_DRIVE_FILE_ID' con el ID real del archivo en Google Drive.
        """
        if os.path.exists(self.ruta_archivo):
            print(f"El archivo {self.ruta_archivo} ya existe localmente.")
            return True
            
        try:
            print(f"Descargando dataset desde Google Drive con ID: {file_id}")
            # URL para descargar archivo de Google Drive
            url = f"https://drive.google.com/uc?id={file_id}&export=download"
            print(f"URL de descarga: {url}")
            
            # Realizar la descarga
            response = requests.get(url, stream=True)
            print(f"Código de estado HTTP: {response.status_code}")
            response.raise_for_status()
            
            # Guardar el archivo
            with open(self.ruta_archivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Dataset descargado exitosamente a {self.ruta_archivo}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error de red al descargar el dataset: {e}")
            return False
        except Exception as e:
            print(f"Error al descargar el dataset: {e}")
            return False
            
    def cargar_datos(self, remuestrear=False, forzar_analisis=False):
        """Carga y procesa los datos del archivo CSV"""
        try:
            # Verificar si existe caché y no se fuerza la recarga
            if not forzar_analisis and os.path.exists(self.ruta_cache) and os.path.exists(self.ruta_estadisticas):
                print("Cargando datos desde caché...")
                df = pd.read_parquet(self.ruta_cache)
                with open(self.ruta_estadisticas, 'r') as f:
                    estadisticas = json.load(f)
                return {'datos': df, 'analisis': estadisticas}
            
            print("Cargando datos desde archivo CSV...")
            # Cargar datos con manejo de errores
            df = pd.read_csv(self.ruta_archivo, 
                           delimiter=',',
                           on_bad_lines='skip',
                           low_memory=False,
                           dtype=str)
            
            # Convertir columnas de fecha
            columnas_fecha = ['fecha_de_notificación', 'fecha_reporte_web', 'fecha_inicio_sintomas', 'fecha_muerte', 'fecha_diagnostico', 'fecha_recuperado']
            for col in columnas_fecha:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convertir columnas numéricas
            columnas_numericas = ['edad']
            for col in columnas_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Guardar en caché
            os.makedirs('datos_procesados', exist_ok=True)
            df.to_parquet(self.ruta_cache, index=False)
            
            # Generar estadísticas
            estadisticas = self._generar_estadisticas(df)
            with open(self.ruta_estadisticas, 'w') as f:
                json.dump(estadisticas, f, indent=2, default=str)
            
            return {'datos': df, 'analisis': estadisticas}
            
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            raise
            
    def _generar_estadisticas(self, df):
        """Genera estadísticas básicas del dataset"""
        estadisticas = {
            'total_registros': len(df),
            'ultima_actualizacion': pd.Timestamp.now().isoformat(),
            'rango_fechas': {},
            'conteo_por_departamento': {},
            'conteo_por_sexo': {},
            'conteo_por_estado': {},
            'estadisticas_edad': {}
        }
        
        # Rango de fechas
        if 'fecha_de_notificación' in df.columns:
            estadisticas['rango_fechas'] = {
                'min': str(df['fecha_de_notificación'].min()),
                'max': str(df['fecha_de_notificación'].max())
            }
        
        # Conteo por departamento
        if 'departamento_nom' in df.columns:
            estadisticas['conteo_por_departamento'] = df['departamento_nom'].value_counts().to_dict()
        
        # Conteo por sexo
        if 'sexo' in df.columns:
            estadisticas['conteo_por_sexo'] = df['sexo'].value_counts().to_dict()
        
        # Conteo por estado
        if 'estado' in df.columns:
            estadisticas['conteo_por_estado'] = df['estado'].value_counts().to_dict()
        
        # Estadísticas de edad
        if 'edad' in df.columns:
            edad_series = pd.to_numeric(df['edad'], errors='coerce').dropna()
            if not edad_series.empty:
                estadisticas['estadisticas_edad'] = {
                    'promedio': float(edad_series.mean()),
                    'mediana': float(edad_series.median()),
                    'min': int(edad_series.min()),
                    'max': int(edad_series.max())
                }
        
        return estadisticas
        
    def cargar_desde_cache(self):
        """Carga datos desde el archivo de caché"""
        if os.path.exists(self.ruta_cache):
            return pd.read_parquet(self.ruta_cache)
        return None
        
    def cargar_analisis_cache(self):
        """Carga análisis desde el archivo de caché"""
        if os.path.exists(self.ruta_estadisticas):
            with open(self.ruta_estadisticas, 'r') as f:
                return json.load(f)
        return None
        
    def obtener_muestreo_aleatorio(self, df, tamaño_muestra=50000):
        """Obtiene un muestreo aleatorio del dataset para visualización"""
        if df is not None and len(df) > tamaño_muestra:
            return df.sample(n=tamaño_muestra, random_state=42)
        return df
        
    def filtrar_por_fecha(self, df, fecha_inicio=None, fecha_fin=None):
        """Filtra el dataframe por rango de fechas"""
        if df is None or 'fecha_de_notificación' not in df.columns:
            return df
            
        mask = pd.Series([True] * len(df), index=df.index)
        
        if fecha_inicio:
            mask &= (df['fecha_de_notificación'] >= pd.Timestamp(fecha_inicio))
            
        if fecha_fin:
            mask &= (df['fecha_de_notificación'] <= pd.Timestamp(fecha_fin))
            
        return df[mask]