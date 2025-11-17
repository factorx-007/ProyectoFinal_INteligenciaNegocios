#!/usr/bin/env python3
"""
Script de prueba para verificar el procesamiento del dataset completo
"""

import os
import time
from procesamiento import ProcesadorCOVID

def test_procesamiento_completo():
    """Prueba el procesamiento completo del dataset"""
    print("🔍 Verificando archivo CSV...")
    csv_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ No se encontró el archivo: {csv_file}")
        return False
    
    file_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
    print(f"✅ Archivo encontrado: {file_size:.1f} MB")
    
    if file_size < 1000:
        print("⚠️  El archivo parece ser una muestra, no el dataset completo")
        return False
    
    print("\n🔄 Iniciando procesamiento...")
    start_time = time.time()
    
    try:
        procesador = ProcesadorCOVID(csv_file)
        resultado = procesador.cargar_datos(forzar_analisis=True)
        
        tiempo_total = time.time() - start_time
        registros = len(resultado['datos'])
        
        print(f"✅ Procesamiento completado exitosamente!")
        print(f"📊 Registros procesados: {registros:,}")
        print(f"⏱️  Tiempo de procesamiento: {tiempo_total:.1f} segundos")
        
        # Guardar estadísticas
        os.makedirs('datos_procesados', exist_ok=True)
        import json
        with open('datos_procesados/estadisticas.json', 'w') as f:
            json.dump(resultado['analisis'], f, indent=2, default=str)
        
        print(f"💾 Estadísticas guardadas en datos_procesados/estadisticas.json")
        
        # Mostrar algunas estadísticas
        analisis = resultado['analisis']
        print(f"\n📈 Estadísticas generales:")
        print(f"   Total registros: {analisis.get('total_registros', 'N/A'):,}")
        if 'rango_fechas' in analisis:
            print(f"   Rango de fechas: {analisis['rango_fechas']['min']} a {analisis['rango_fechas']['max']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_procesamiento_completo()