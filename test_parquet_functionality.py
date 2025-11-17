#!/usr/bin/env python3
"""
Script para probar la funcionalidad de carga de archivos Parquet
"""

import os
import sys
import pandas as pd

# Añadir el directorio actual al path para importar los módulos
sys.path.append('.')

from procesamiento import ProcesadorCOVID

def test_parquet_functionality():
    """Prueba la funcionalidad de Parquet"""
    print("🚀 Probando funcionalidad de Parquet")
    print("===================================")
    
    # Crear instancia del procesador
    procesador = ProcesadorCOVID()
    
    # Verificar si existe el archivo CSV
    csv_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    if os.path.exists(csv_file):
        csv_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
        print(f"✅ Archivo CSV encontrado: {csv_size:.1f} MB")
    else:
        print("❌ Archivo CSV no encontrado")
        return False
    
    # Verificar si existe el archivo Parquet
    parquet_file = 'Casos_positivos_de_COVID-19_en_Colombia.parquet'
    if os.path.exists(parquet_file):
        parquet_size = os.path.getsize(parquet_file) / (1024 * 1024)  # MB
        print(f"✅ Archivo Parquet encontrado: {parquet_size:.1f} MB")
        compression_ratio = csv_size / parquet_size if parquet_size > 0 else 0
        print(f"📈 Compresión: {compression_ratio:.1f}x menor")
    else:
        print("ℹ️  Archivo Parquet no encontrado, se creará al cargar los datos")
    
    # Probar la carga de datos
    print("\n📂 Probando carga de datos...")
    try:
        # Forzar análisis para probar la conversión a Parquet
        resultado = procesador.cargar_datos(forzar_analisis=True)
        
        if resultado and 'datos' in resultado:
            df = resultado['datos']
            print(f"✅ Datos cargados exitosamente")
            print(f"📊 Registros cargados: {len(df):,}")
            
            # Mostrar información básica del DataFrame
            print(f"📋 Columnas: {len(df.columns)}")
            print(f"🏷️  Primeras columnas: {list(df.columns[:5])}")
            
            # Verificar que se haya creado el archivo Parquet
            if os.path.exists(parquet_file):
                new_parquet_size = os.path.getsize(parquet_file) / (1024 * 1024)  # MB
                print(f"✅ Archivo Parquet creado: {new_parquet_size:.1f} MB")
            
            return True
        else:
            print("❌ Error al cargar los datos")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la carga de datos: {e}")
        return False

if __name__ == "__main__":
    success = test_parquet_functionality()
    
    if success:
        print("\n🎉 ¡Prueba completada exitosamente!")
        print("💡 La funcionalidad de Parquet está trabajando correctamente")
    else:
        print("\n💥 La prueba falló. Revisa los mensajes de error.")