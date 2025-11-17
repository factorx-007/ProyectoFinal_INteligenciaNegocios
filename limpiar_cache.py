#!/usr/bin/env python3
"""
Script para limpiar la caché de datos y forzar el reprocesamiento del dataset completo
"""

import os
import shutil

def limpiar_cache():
    """Elimina los archivos de caché para forzar el reprocesamiento"""
    cache_dir = 'datos_procesados'
    cache_files = [
        'datos_procesados/datos_covid.parquet',
        'datos_procesados/estadisticas.json'
    ]
    
    # Eliminar archivos de caché individuales
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                print(f"✅ Eliminado: {cache_file}")
            except Exception as e:
                print(f"❌ Error al eliminar {cache_file}: {e}")
    
    # Eliminar directorio de análisis si existe
    analisis_dir = os.path.join(cache_dir, 'analisis')
    if os.path.exists(analisis_dir):
        try:
            shutil.rmtree(analisis_dir)
            print(f"✅ Eliminado directorio: {analisis_dir}")
        except Exception as e:
            print(f"❌ Error al eliminar {analisis_dir}: {e}")
    
    # Verificar tamaño del archivo CSV
    csv_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    if os.path.exists(csv_file):
        file_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
        print(f"📁 Tamaño del archivo CSV: {file_size:.1f} MB")
        
        if file_size > 1000:  # Más de 1GB
            print("✅ El archivo CSV parece ser el dataset completo")
            print("🔄 Ahora puedes ejecutar la aplicación y usar 'Forzar Actualización' para procesar los datos")
        else:
            print("⚠️ El archivo CSV parece ser una muestra")
    else:
        print(f"❌ No se encontró el archivo: {csv_file}")

if __name__ == "__main__":
    limpiar_cache()