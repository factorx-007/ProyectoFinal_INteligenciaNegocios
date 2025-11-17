#!/usr/bin/env python3
"""
Script para convertir el archivo CSV de casos COVID-19 a formato Parquet
Esto reduce significativamente el tamaño del archivo y mejora el rendimiento de carga
"""

import pandas as pd
import os
from pathlib import Path

def convert_csv_to_parquet(csv_file_path, parquet_file_path):
    """
    Convierte un archivo CSV a formato Parquet
    
    Args:
        csv_file_path (str): Ruta al archivo CSV de entrada
        parquet_file_path (str): Ruta donde se guardará el archivo Parquet
    """
    print(f"📊 Convirtiendo {csv_file_path} a formato Parquet...")
    print("⏳ Este proceso puede tomar varios minutos debido al tamaño del archivo...")
    
    try:
        # Verificar que el archivo CSV existe
        if not os.path.exists(csv_file_path):
            print(f"❌ Error: No se encontró el archivo {csv_file_path}")
            return False
            
        # Obtener tamaño del archivo CSV
        csv_size_mb = os.path.getsize(csv_file_path) / (1024 * 1024)
        print(f"📁 Tamaño del archivo CSV: {csv_size_mb:.1f} MB")
        
        # Leer el archivo CSV
        print("📥 Leyendo archivo CSV...")
        df = pd.read_csv(
            csv_file_path,
            delimiter=',',
            on_bad_lines='skip',
            low_memory=False,
            dtype=str  # Leer todo como string para evitar problemas de tipos
        )
        
        print(f"✅ CSV leído exitosamente. Total de registros: {len(df):,}")
        
        # Convertir columnas de fecha si existen
        date_columns = ['fecha_de_notificación', 'fecha_reporte_web', 'fecha_inicio_sintomas', 
                       'fecha_muerte', 'fecha_diagnostico', 'fecha_recuperado']
        
        for col in date_columns:
            if col in df.columns:
                print(f"📅 Convirtiendo columna {col} a formato de fecha...")
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convertir columnas numéricas
        numeric_columns = ['edad']
        for col in numeric_columns:
            if col in df.columns:
                print(f"🔢 Convirtiendo columna {col} a formato numérico...")
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Guardar como archivo Parquet
        print("💾 Guardando como archivo Parquet...")
        df.to_parquet(parquet_file_path, index=False, engine='pyarrow')
        
        # Verificar tamaño del archivo Parquet
        parquet_size_mb = os.path.getsize(parquet_file_path) / (1024 * 1024)
        compression_ratio = csv_size_mb / parquet_size_mb if parquet_size_mb > 0 else 0
        
        print(f"✅ Conversión completada!")
        print(f"📄 Archivo Parquet guardado en: {parquet_file_path}")
        print(f"📊 Tamaño Parquet: {parquet_size_mb:.1f} MB")
        print(f"📈 Compresión alcanzada: {compression_ratio:.1f}x menor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        return False

if __name__ == "__main__":
    # Definir rutas de archivos
    csv_file = "Casos_positivos_de_COVID-19_en_Colombia._20251116.csv"
    parquet_file = "Casos_positivos_de_COVID-19_en_Colombia.parquet"
    
    # Ejecutar conversión
    success = convert_csv_to_parquet(csv_file, parquet_file)
    
    if success:
        print("\n🎉 ¡Archivo convertido exitosamente!")
        print("💡 Ahora puedes usar el archivo Parquet para mejorar el rendimiento de tu aplicación")
    else:
        print("\n💥 La conversión falló. Por favor revisa los mensajes de error anteriores.")