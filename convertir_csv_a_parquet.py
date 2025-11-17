#!/usr/bin/env python3
"""
Script para convertir el archivo CSV grande a formato Parquet para mejor rendimiento
"""

import pandas as pd
import os
import time

def convertir_csv_a_parquet():
    """Convierte el archivo CSV a Parquet para mejor rendimiento"""
    csv_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    parquet_file = 'Casos_positivos_de_COVID-19_en_Colombia.parquet'
    
    if not os.path.exists(csv_file):
        print(f"❌ No se encontró el archivo: {csv_file}")
        return False
    
    file_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
    print(f"📁 Archivo CSV encontrado: {file_size:.1f} MB")
    
    if file_size < 1000:
        print("⚠️  El archivo parece ser una muestra, no el dataset completo")
        return False
    
    # Verificar si ya existe el archivo Parquet
    if os.path.exists(parquet_file):
        parquet_size = os.path.getsize(parquet_file) / (1024 * 1024)  # MB
        print(f"✅ Archivo Parquet ya existe: {parquet_size:.1f} MB")
        return True
    
    print("🔄 Iniciando conversión a formato Parquet...")
    print("⏰ Esto puede tomar varios minutos...")
    
    start_time = time.time()
    
    try:
        # Procesar en chunks para manejar mejor la memoria
        print("📥 Leyendo archivo CSV en chunks...")
        chunk_size = 50000
        chunks = []
        total_rows = 0
        
        for chunk in pd.read_csv(csv_file, 
                                delimiter=',',
                                on_bad_lines='skip',
                                low_memory=False,
                                dtype=str,
                                chunksize=chunk_size):
            chunks.append(chunk)
            total_rows += len(chunk)
            
            if total_rows % (chunk_size * 10) == 0:
                print(f"📊 Procesadas {total_rows:,} filas...")
        
        print(f"✅ Lectura completada: {total_rows:,} filas en total")
        
        # Combinar chunks
        print("🔗 Combinando chunks...")
        df = pd.concat(chunks, ignore_index=True)
        print(f"📊 DataFrame final: {len(df):,} filas, {len(df.columns)} columnas")
        
        # Convertir columnas de fecha
        print("📅 Convirtiendo columnas de fecha...")
        columnas_fecha = ['fecha_de_notificación', 'fecha_reporte_web', 'fecha_inicio_sintomas', 'fecha_muerte', 'fecha_diagnostico', 'fecha_recuperado']
        for col in columnas_fecha:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convertir columnas numéricas
        print("🔢 Convirtiendo columnas numéricas...")
        columnas_numericas = ['edad']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Guardar en formato Parquet
        print("💾 Guardando en formato Parquet...")
        df.to_parquet(parquet_file, index=False)
        
        # Verificar el archivo creado
        final_size = os.path.getsize(parquet_file) / (1024 * 1024)  # MB
        compression_ratio = file_size / final_size if final_size > 0 else 0
        
        tiempo_total = time.time() - start_time
        
        print(f"✅ Conversión completada exitosamente!")
        print(f"   Archivo Parquet: {final_size:.1f} MB")
        print(f"   Compresión: {compression_ratio:.1f}x más pequeño")
        print(f"   Tiempo total: {tiempo_total:.1f} segundos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    convertir_csv_a_parquet()