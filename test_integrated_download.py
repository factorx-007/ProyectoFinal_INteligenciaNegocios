#!/usr/bin/env python3
"""
Script para probar la funcionalidad integrada de descarga con gdown
"""

import os
import sys

# Añadir el directorio actual al path
sys.path.append('.')

def test_integrated_download():
    """Prueba la descarga integrada con gdown"""
    print("🚀 Probando funcionalidad integrada de descarga con gdown")
    print("=====================================================")
    
    # Verificar si el archivo ya existe
    data_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    if os.path.exists(data_file):
        file_size = os.path.getsize(data_file) / (1024 * 1024)  # MB
        print(f"✅ El archivo ya existe: {file_size:.1f} MB")
        return True
    
    # Intentar descargar con gdown
    try:
        import gdown
        print("✅ gdown está disponible")
        
        file_id = '1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r'  # ID del archivo de COVID-19
        url = f'https://drive.google.com/uc?id={file_id}'
        print(f"📥 Descargando desde: {url}")
        print("⏳ Esto puede tomar varios minutos...")
        
        gdown.download(url, data_file, quiet=False)
        
        if os.path.exists(data_file):
            file_size = os.path.getsize(data_file) / (1024 * 1024)  # MB
            print(f"✅ Descarga completada: {file_size:.1f} MB")
            return True
        else:
            print("❌ La descarga falló")
            return False
            
    except ImportError:
        print("❌ gdown no está instalado")
        print("💡 Instálalo con: pip install gdown")
        return False
    except Exception as e:
        print(f"❌ Error en la descarga: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Prueba de descarga integrada con gdown")
    print("========================================")
    
    success = test_integrated_download()
    
    if success:
        print("\n🎉 ¡Prueba completada exitosamente!")
        print("💡 La funcionalidad de descarga integrada está trabajando correctamente")
    else:
        print("\n💥 La prueba falló. Revisa los mensajes de error.")