import os
import dask.dataframe as dd
import pandas as pd
from datetime import datetime, timedelta
import pyarrow.parquet as pq
import pyarrow as pa
import numpy as np
import json
import requests
from pathlib import Path

class ProcesadorCOVID:
    def __init__(self, ruta_archivo, directorio_temporal='datos_procesados'):
        self.ruta_archivo = ruta_archivo
        self.directorio_temporal = directorio_temporal
        self.ruta_parquet = os.path.join(directorio_temporal, 'datos_covid.parquet')
        self.ruta_analisis = os.path.join(directorio_temporal, 'estadisticas.json')
        self.dtypes = {
            'ID de caso': 'str',
            'Código DIVIPOLA departamento': 'str',
            'Código DIVIPOLA municipio': 'str',
            'Edad': 'float32',
            'Unidad de medida de edad': 'category',
            'Sexo': 'category',
            'Tipo de contagio': 'category',
            'Ubicación del caso': 'category',
            'Estado': 'category',
            'Código ISO del país': 'category',
            'Recuperado': 'category',
            'Tipo de recuperación': 'category',
            'Pertenencia étnica': 'category',
            'Nombre del grupo étnico': 'category'
        }
        
        # Crear directorios necesarios
        os.makedirs(self.directorio_temporal, exist_ok=True)
        
    def descargar_dataset(self, file_id='1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r'):
        """
        Descarga el dataset desde Google Drive si no existe localmente.
        Reemplaza 'YOUR_GOOGLE_DRIVE_FILE_ID' con el ID real del archivo en Google Drive.
        """
        if os.path.exists(self.ruta_archivo):
            print(f"El archivo {self.ruta_archivo} ya existe localmente.")
            return True
            
        try:
            print("Descargando dataset desde Google Drive...")
            # URL para descargar archivo de Google Drive
            url = f"https://drive.google.com/uc?id={file_id}&export=download"
            
            # Realizar la descarga
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Guardar el archivo
            with open(self.ruta_archivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Dataset descargado exitosamente a {self.ruta_archivo}")
            return True
        except Exception as e:
            print(f"Error al descargar el dataset: {e}")
            return False
    
    def cargar_desde_cache(self):
        """Carga los datos desde el archivo parquet de caché"""
        try:
            return dd.read_parquet(self.ruta_parquet)
        except Exception as e:
            print(f"Error al cargar desde caché: {e}")
            raise e
    
    def cargar_analisis_cache(self):
        """Carga el análisis desde el archivo JSON de caché"""
        with open(self.ruta_analisis, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def cargar_datos(self, remuestrear=False, forzar_analisis=False):
        """
        Carga los datos desde el CSV o el archivo parquet si existe.
        Si forzar_analisis es True, recalcula todos los análisis.
        """
        # Verificar si ya se han generado los análisis
        analisis_completo = self._verificar_analisis_existente()
        
        if not remuestrear and os.path.exists(self.ruta_parquet) and analisis_completo and not forzar_analisis:
            print("Cargando datos desde archivos preprocesados...")
            return {
                'datos': dd.read_parquet(self.ruta_parquet),
                'analisis': self._cargar_analisis_existente()
            }
        
        print("Procesando archivo CSV (esto puede tomar varios minutos)...")
        
        # Leer el archivo en fragmentos
        chunks = pd.read_csv(
            self.ruta_archivo,
            chunksize=100000,
            dtype=self.dtypes,
            parse_dates=[
                'Fecha de notificación',
                'Fecha de inicio de síntomas',
                'Fecha de diagnóstico',
                'Fecha de recuperación',
                'fecha reporte web',
                'Fecha de muerte'
            ],
            infer_datetime_format=True,
            low_memory=False
        )
        
        # Lista para almacenar DataFrames procesados
        dfs_procesados = []
        
        for i, chunk in enumerate(chunks):
            # Limpieza de datos
            chunk = self._limpiar_datos(chunk)
            dfs_procesados.append(chunk)
            print(f"Procesados {(i+1)*100000} registros...")
        
        # Combinar todos los chunks
        df_completo = pd.concat(dfs_procesados, ignore_index=True)
        
        # Guardar el archivo parquet completo
        tabla = pa.Table.from_pandas(df_completo, preserve_index=False)
        pq.write_table(tabla, self.ruta_parquet)
        
        # Generar análisis
        print("Generando análisis...")
        analisis = self._generar_analisis_completo(df_completo)
        
        # Guardar análisis para uso futuro
        self._guardar_analisis(analisis)
        
        return {
            'datos': dd.from_pandas(df_completo, npartitions=4),
            'analisis': analisis
        }
    
    def _limpiar_datos(self, df):
        """Limpia y formatea los datos"""
        # Convertir a minúsculas los nombres de las columnas
        df.columns = df.columns.str.lower().str.normalize('NFKD')\
            .str.encode('ascii', errors='ignore')\
            .str.decode('utf-8')\
            .str.lower()\
            .str.replace(r'[^a-z0-9_]+', '_', regex=True)
        
        # Manejo de valores faltantes
        df['edad'] = df['edad'].fillna(-1).astype('int32')
        
        # Normalizar categorías
        for col in df.select_dtypes(include=['object']).columns:
            # Convertir a string y manejar nulos
            df[col] = df[col].astype(str).replace('nan', pd.NA)
            
            # Si tiene pocos valores únicos, convertir a categoría
            if df[col].nunique() < 100:
                df[col] = pd.Categorical(df[col])
        
        # Asegurar que las fechas estén en formato datetime
        columnas_fecha = [
            'fecha_de_notificacion',
            'fecha_de_inicio_de_sintomas',
            'fecha_de_diagnostico',
            'fecha_de_recuperacion',
            'fecha_reporte_web',
            'fecha_de_muerte'
        ]
        
        for col in columnas_fecha:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _generar_analisis_completo(self, df):
        """Genera un análisis completo de los datos"""
        print("Generando análisis completo de los datos...")
        
        # Estadísticas básicas
        stats = {
            'total_registros': len(df),
            'rango_fechas': {
                'min': df['fecha_de_notificacion'].min().strftime('%Y-%m-%d'),
                'max': df['fecha_de_notificacion'].max().strftime('%Y-%m-%d')
            },
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Análisis por categorías
        categorias = [
            'estado', 'sexo', 'tipo_de_contagio', 'ubicacion_del_caso',
            'recuperado', 'tipo_de_recuperacion', 'pertenencia_etnica'
        ]
        
        for categoria in categorias:
            if categoria in df.columns:
                stats[f'conteo_por_{categoria}'] = df[categoria].value_counts().to_dict()
        
        # Análisis temporal
        if 'fecha_de_notificacion' in df.columns:
            df_fecha = df.set_index('fecha_de_notificacion')
            # Convertir fechas a string para evitar problemas de serialización
            stats['casos_por_mes'] = {str(k.date()): int(v) for k, v in df_fecha.resample('ME').size().items()}
            stats['casos_por_semana'] = {str(k.date()): int(v) for k, v in df_fecha.resample('W').size().items()}
            stats['casos_por_dia'] = {str(k.date()): int(v) for k, v in df_fecha.resample('D').size().items()}
        
        # Análisis por ubicación
        if 'departamento' in df.columns and 'municipio' in df.columns:
            stats['top_departamentos'] = df['departamento'].value_counts().head(10).to_dict()
            stats['top_municipios'] = df['municipio'].value_counts().head(10).to_dict()
        
        # Análisis de edades
        if 'edad' in df.columns:
            edad_valida = df[df['edad'] > 0]['edad']
            stats['estadisticas_edad'] = {
                'promedio': float(edad_valida.mean()),
                'mediana': float(edad_valida.median()),
                'min': int(edad_valida.min()),
                'max': int(edad_valida.max()),
                'desviacion_estandar': float(edad_valida.std())
            }
            
            # Distribución por grupos de edad
            bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120]
            labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99', '100+']
            df_edad = df[df['edad'] > 0].copy()
            df_edad['grupo_edad'] = pd.cut(df_edad['edad'], bins=bins, labels=labels, right=False)
            stats['distribucion_por_edad'] = df_edad['grupo_edad'].value_counts().to_dict()
            
            # Distribución por edad y sexo
            if 'sexo' in df.columns:
                piramide = df_edad.groupby(['grupo_edad', 'sexo']).size().unstack(fill_value=0)
                stats['distribucion_por_edad_y_sexo'] = piramide.to_dict()
        
        # Estadísticas por sexo
        if 'sexo' in df.columns:
            stats['conteo_por_sexo'] = df['sexo'].value_counts().to_dict()
        
        return stats
    
    def _verificar_analisis_existente(self):
        """Verifica si ya existen análisis guardados"""
        # Verificar solo los archivos que realmente existen
        archivos_requeridos = [
            'estadisticas.json'
        ]
        
        return all(os.path.exists(os.path.join(self.directorio_temporal, f)) for f in archivos_requeridos)
    
    def _cargar_analisis_existente(self):
        """Carga los análisis previamente guardados"""
        try:
            with open(os.path.join(self.directorio_temporal, 'estadisticas.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar análisis existente: {e}")
            return {}
    
    def _guardar_analisis(self, analisis):
        """Guarda el análisis en archivos para uso futuro"""
        try:
            # Guardar estadísticas generales
            with open(os.path.join(self.directorio_temporal, 'estadisticas.json'), 'w', encoding='utf-8') as f:
                json.dump(analisis, f, ensure_ascii=False, indent=2)
                
            print("Análisis guardado exitosamente")
            return True
        except Exception as e:
            print(f"Error al guardar análisis: {e}")
            return False
    
    def obtener_estadisticas(self, df=None):
        """Obtiene estadísticas básicas del conjunto de datos"""
        if df is None:
            # Verificar si existe el atributo analisis
            if hasattr(self, 'analisis') and self.analisis is not None:
                return self.analisis
            return {}
            
        return self._generar_analisis_completo(df)
    
    def filtrar_por_fecha(self, df, fecha_inicio=None, fecha_fin=None, columna_fecha='fecha_de_notificacion'):
        """
        Filtra los datos por rango de fechas
        
        Args:
            df: DataFrame a filtrar
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            columna_fecha: Nombre de la columna de fecha a usar
            
        Returns:
            DataFrame filtrado
        """
        if columna_fecha not in df.columns:
            print(f"Advertencia: La columna de fecha '{columna_fecha}' no existe en el DataFrame")
            return df
            
        if fecha_inicio:
            df = df[df[columna_fecha] >= pd.to_datetime(fecha_inicio)]
        if fecha_fin:
            # Ajustar la fecha fin para incluir todo el día
            fecha_fin_ajustada = pd.to_datetime(fecha_fin) + timedelta(days=1)
            df = df[df[columna_fecha] < fecha_fin_ajustada]
            
        return df
    
    def obtener_muestreo_aleatorio(self, df, tamaño_muestra=10000, random_state=42):
        """
        Obtiene una muestra aleatoria de los datos para visualización
        
        Args:
            df: DataFrame de entrada (pandas o dask)
            tamaño_muestra: Número de registros a incluir en la muestra
            random_state: Semilla para reproducibilidad
            
        Returns:
            Muestra aleatoria como DataFrame de pandas
        """
        if hasattr(df, 'compute'):  # Es un DataFrame de dask
            if len(df) <= tamaño_muestra:
                return df.compute()
            return df.sample(frac=tamaño_muestra/len(df), random_state=random_state).compute()
        else:  # Es un DataFrame de pandas
            if len(df) <= tamaño_muestra:
                return df
            return df.sample(n=tamaño_muestra, random_state=random_state)
    
    def obtener_datos_agrupados(self, df, grupo, metrica='size', columna_metrica=None):
        """
        Agrupa los datos por una o más columnas y calcula una métrica
        
        Args:
            df: DataFrame de entrada
            grupo: Lista de columnas para agrupar
            metrica: Métrica a calcular ('size', 'sum', 'mean', 'count', 'nunique')
            columna_metrica: Columna sobre la que calcular la métrica (requerido para algunas métricas)
            
        Returns:
            DataFrame agrupado
        """
        if not isinstance(grupo, list):
            grupo = [grupo]
            
        # Verificar que las columnas existan
        for col in grupo:
            if col not in df.columns:
                raise ValueError(f"La columna '{col}' no existe en el DataFrame")
                
        if metrica in ['sum', 'mean', 'count'] and not columna_metrica:
            raise ValueError(f"Se requiere 'columna_metrica' para la métrica '{metrica}'")
            
        # Realizar la agrupación
        if hasattr(df, 'compute'):  # DataFrame de dask
            if metrica == 'size':
                return df.groupby(grupo).size().compute().reset_index(name='conteo')
            elif metrica == 'sum':
                return df.groupby(grupo)[columna_metrica].sum().compute().reset_index()
            elif metrica == 'mean':
                return df.groupby(grupo)[columna_metrica].mean().compute().reset_index()
            elif metrica == 'count':
                return df.groupby(grupo)[columna_metrica].count().compute().reset_index()
            elif metrica == 'nunique':
                return df.groupby(grupo)[columna_metrica].nunique().compute().reset_index()
        else:  # DataFrame de pandas
            if metrica == 'size':
                return df.groupby(grupo).size().reset_index(name='conteo')
            elif metrica == 'sum':
                return df.groupby(grupo)[columna_metrica].sum().reset_index()
            elif metrica == 'mean':
                return df.groupby(grupo)[columna_metrica].mean().reset_index()
            elif metrica == 'count':
                return df.groupby(grupo)[columna_metrica].count().reset_index()
            elif metrica == 'nunique':
                return df.groupby(grupo)[columna_metrica].nunique().reset_index()
                
        raise ValueError(f"Métrica no soportada: {metrica}")