import pandas as pd
import os
import requests
import json
from pathlib import Path
import re

# Import gdown con manejo de errores
GDOWN_AVAILABLE = False
gdown = None
try:
    import gdown
    GDOWN_AVAILABLE = True
except ImportError:
    print("⚠️  gdown no disponible. Instala con: pip install gdown")

class ProcesadorCOVID:
    def __init__(self, ruta_archivo='Casos_positivos_de_COVID-19_en_Colombia.csv'):
        self.ruta_archivo = ruta_archivo
        self.ruta_cache = 'datos_procesados/datos_covid.parquet'
        self.ruta_estadisticas = 'datos_procesados/estadisticas.json'
        
    def descargar_dataset(self, file_id='1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r'):
        """
        Maneja el dataset de COVID-19 con múltiples estrategias de descarga.
        Prioridad: 1. Archivo local, 2. Variable de entorno, 3. gdown (si disponible), 4. Instrucciones claras
        """
        # Verificar si el archivo ya existe localmente
        if os.path.exists(self.ruta_archivo):
            print(f"✅ El archivo {self.ruta_archivo} ya existe localmente.")
            return True
            
        # Verificar variable de entorno para deployment
        deploy_file_url = os.environ.get('COVID_DATA_URL')
        if deploy_file_url:
            print("🔄 Usando URL de datos desde variable de entorno")
            return self._descargar_desde_url_directa(deploy_file_url)
            
        # Intentar descargar con gdown si está disponible
        if GDOWN_AVAILABLE:
            print("🚀 Intentando descarga rápida con gdown...")
            if self._descargar_con_gdown(file_id):
                return True
        else:
            print("ℹ️  Para descarga rápida, instala gdown: pip install gdown")
            
        # Para archivos grandes, proporcionar instrucciones detalladas
        print("⚠️  PROBLEMA DETECTADO: Archivo grande (1.34GB) bloqueado por Google Drive")
        print("")
        print("📁 SOLUCIONES DISPONIBLES:")
        print("   1. DESCARGA CON GDOWN (recomendado):")
        print("      a) Instala gdown: pip install gdown")
        print("      b) Reinicia la aplicación")
        print("")
        print("   2. DESCARGA MANUAL RECOMENDADA:")
        print("      a) Abre en navegador:")
        print("         🔗 https://drive.google.com/file/d/1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r/view?usp=sharing")
        print("      b) Haz clic en 'Download' o 'Descargar'")
        print("      c) Si aparece advertencia, haz clic en 'Download anyway'")
        print("      d) Guarda como: Casos_positivos_de_COVID-19_en_Colombia.csv")
        print("      e) Coloca el archivo en: D:\\ProyectoFinal_DPD\\")
        print("")
        print("   3. USAR SERVICIO DE ALMACENAMIENTO DIRECTO:")
        print("      Sube el archivo a AWS S3, Dropbox, o similar y usa el enlace directo:")
        print("      💻 PowerShell: $env:COVID_DATA_URL='https://enlace-directo-al-archivo.csv'")
        print("      🐧 Linux/Mac: export COVID_DATA_URL='https://enlace-directo-al-archivo.csv'")
        print("")
        print("   4. USAR ARCHIVO DE MUESTRA (solo para pruebas):")
        print("      🔄 Reinicia la aplicación para crear datos de prueba")
        print("")
        print("▶️  Una vez descargado el archivo completo, reinicia la aplicación")
        
        # Crear archivo de muestra para pruebas iniciales
        self._crear_archivo_muestra()
        return True
        
    def _descargar_desde_url_directa(self, url):
        """Descarga desde URL directa con manejo de errores"""
        try:
            print(f"📥 Intentando descargar desde: {url}")
            print("⏳ Esto puede tardar varios minutos...")
            
            # Hacer una solicitud simple primero para verificar
            response = requests.get(url, timeout=30)
            
            # Verificar si es una página HTML (indicador de problema con Google Drive)
            if response.text.startswith('<!DOCTYPE html>') or '<title>Google Drive' in response.text:
                print("❌ BLOQUEADO: Google Drive requiere interacción manual para archivos grandes")
                print("   Solución: Descarga el archivo manualmente usando las instrucciones arriba")
                return False
            
            # Si llegamos aquí, intentar descarga completa
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = 0
            chunk_size = 8192
            with open(self.ruta_archivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
                        if total_size % (chunk_size * 6400) == 0:
                            print(f"📥 Descargados {total_size // (1024*1024)} MB...")
            
            print(f"✅ Descargado exitosamente: {total_size // (1024*1024)} MB")
            return True
        except Exception as e:
            print(f"❌ Error en descarga directa: {e}")
            print("⚠️  Google Drive bloquea descargas automáticas de archivos grandes")
            print("   Solución: Descarga el archivo manualmente")
            return False
            
    def _crear_archivo_muestra(self):
        """Crea un archivo de muestra para prueba inicial"""
        muestra_contenido = """fecha_de_notificación,ciudad_de_ubicación,departamento_nom,atención,edad,sexo,tipo,estado,pa_s_de_origen,pertenencia_etnica,fecha_inicio_sintomas,fecha_muerte,fecha_diagnostico,fecha_recuperado,tipo_recuperacion,ubicacion_del_caso
2020-03-01,Bogotá,Cundinamarca,Hospital,25,M,Importado,Leve,Italia,Otro,2020-02-25,,2020-03-01,,,Casa
2020-03-02,Medellín,Antioquia,Hospital,30,F,Relacionado,Grave,Colombia,Indígena,2020-02-28,,2020-03-02,,,Hospital
2020-03-03,Cali,Valle del Cauca,Casa,45,M,Importado,Leve,España,Afrodescendiente,2020-02-29,,2020-03-03,,,Casa
2020-03-04,Barranquilla,Atlántico,Hospital,35,F,Relacionado,Leve,Colombia,Indígena,2020-03-01,,2020-03-04,,,Hospital
2020-03-05,Cartagena,Bolívar,Casa,28,M,Importado,Grave,Estados Unidos,Raizal,2020-03-02,,2020-03-05,,,Casa
2020-03-06,Pereira,Risaralda,Hospital,52,M,Relacionado,Leve,Colombia,Otro,2020-03-03,,2020-03-06,,,Hospital
2020-03-07,Manizales,Caldas,Casa,29,F,Importado,Grave,Francia,Afrodescendiente,2020-03-04,,2020-03-07,,,Casa
2020-03-08,Villavicencio,Meta,Hospital,41,M,Relacionado,Leve,Colombia,Indígena,2020-03-05,,2020-03-08,,,Hospital
2020-03-09,Pasto,Nariño,Casa,33,F,Importado,Grave,Brasil,Raizal,2020-03-06,,2020-03-09,,,Casa
2020-03-10,Montería,Córdoba,Hospital,38,M,Relacionado,Leve,Colombia,Otro,2020-03-07,,2020-03-10,,,Hospital"""
        
        with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(muestra_contenido)
        print("✅ Archivo de muestra creado para prueba inicial (10 registros)")
        
    def _descargar_con_gdown(self, file_id):
        """Descarga archivo usando gdown si está disponible"""
        if not GDOWN_AVAILABLE or gdown is None:
            print("❌ gdown no está disponible")
            return False
            
        try:
            url = f'https://drive.google.com/uc?id={file_id}'
            print(f"📥 Descargando con gdown desde: {url}")
            gdown.download(url, self.ruta_archivo, quiet=False)
            print("✅ Descarga completada con gdown")
            return True
        except Exception as e:
            print(f"❌ Error en descarga con gdown: {e}")
            return False
            
    def cargar_datos(self, remuestrear=False, forzar_analisis=False):
        """Carga y procesa los datos del archivo CSV o Parquet"""
        try:
            # Verificar si existe caché y no se fuerza la recarga
            if not forzar_analisis and os.path.exists(self.ruta_cache) and os.path.exists(self.ruta_estadisticas):
                print("Cargando datos desde caché...")
                df = pd.read_parquet(self.ruta_cache)
                with open(self.ruta_estadisticas, 'r') as f:
                    estadisticas = json.load(f)
                return {'datos': df, 'analisis': estadisticas}
            
            # Verificar si existe un archivo Parquet
            parquet_file = self.ruta_archivo.replace('.csv', '.parquet')
            if os.path.exists(parquet_file):
                print("Cargando datos desde archivo Parquet...")
                df = pd.read_parquet(parquet_file)
            else:
                print("Cargando datos desde archivo CSV...")
                # Verificar si es un archivo grande y usar procesamiento por chunks
                file_size = os.path.getsize(self.ruta_archivo) / (1024 * 1024)  # MB
                if file_size > 1000:  # Archivo mayor a 1GB
                    print(f"📁 Archivo grande detectado ({file_size:.1f} MB). Usando procesamiento optimizado...")
                    df = self._cargar_csv_grande()
                else:
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
                
                # Guardar en formato Parquet para futuras cargas más rápidas
                print("Guardando datos en formato Parquet para cargas futuras más rápidas...")
                df.to_parquet(parquet_file, index=False)
            
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
            
    def _cargar_csv_grande(self):
        """Carga un archivo CSV grande usando chunks para evitar problemas de memoria"""
        print("🔄 Procesando archivo CSV grande en chunks...")
        
        # Leer solo las primeras filas para obtener la estructura
        chunk_sample = pd.read_csv(self.ruta_archivo, 
                                  delimiter=',',
                                  on_bad_lines='skip',
                                  low_memory=False,
                                  dtype=str,
                                  nrows=1000)
        
        print(f"📊 Columnas detectadas: {len(chunk_sample.columns)}")
        
        # Procesar en chunks
        chunks = []
        total_filas = 0
        chunk_size = 50000  # Ajustar según memoria disponible
        
        try:
            for chunk in pd.read_csv(self.ruta_archivo, 
                                   delimiter=',',
                                   on_bad_lines='skip',
                                   low_memory=False,
                                   dtype=str,
                                   chunksize=chunk_size):
                chunks.append(chunk)
                total_filas += len(chunk)
                if total_filas % (chunk_size * 10) == 0:  # Mostrar progreso cada 500k filas
                    print(f"📥 Procesadas {total_filas:,} filas...")
            
            print(f"✅ Lectura completada: {total_filas:,} filas en total")
            
            # Combinar todos los chunks
            print("🔗 Combinando chunks...")
            df = pd.concat(chunks, ignore_index=True)
            print(f"📊 DataFrame final: {len(df):,} filas, {len(df.columns)} columnas")
            
            return df
            
        except Exception as e:
            print(f"❌ Error procesando CSV grande: {e}")
            # Fallback: intentar cargar con configuración más permisiva
            print("🔄 Intentando método alternativo...")
            return pd.read_csv(self.ruta_archivo, 
                             delimiter=',',
                             on_bad_lines='skip',
                             low_memory=True,  # Menos memoria pero más lento
                             dtype=str,
                             engine='python')  # Engine más robusto
    
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