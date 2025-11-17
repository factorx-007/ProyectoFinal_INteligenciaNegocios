#!/usr/bin/env python3
"""
Script para probar la descarga rápida con gdown
"""

import os

def test_gdown_download():
    """Prueba la descarga con gdown"""
    file_id = '1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r'  # ID del archivo de COVID-19
    output_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    
    # Verificar si gdown está disponible
    try:
        import gdown
        print("✅ gdown está disponible")
    except ImportError:
        print("❌ gdown no está instalado")
        print("💡 Instálalo con: pip install gdown")
        return False
    
    # Verificar si el archivo ya existe
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ El archivo ya existe: {file_size:.1f} MB")
        return True
    
    # Intentar descargar
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        print(f"📥 Descargando desde: {url}")
        print("⏳ Esto puede tomar varios minutos...")
        
        gdown.download(url, output_file, quiet=False)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"✅ Descarga completada: {file_size:.1f} MB")
            return True
        else:
            print("❌ La descarga falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en la descarga: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Prueba de descarga rápida con gdown")
    print("=====================================")
    
    success = test_gdown_download()
    
    if success:
        print("\n🎉 ¡Prueba completada exitosamente!")
    else:
        print("\n💥 La prueba falló. Revisa los mensajes de error.")