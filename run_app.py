#!/usr/bin/env python3
"""
Script para ejecutar la aplicación de análisis de COVID-19
"""

import subprocess
import sys
import os

# Function to download dataset using gdown
def download_dataset_with_gdown():
    """Download dataset using gdown if file doesn't exist"""
    data_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    
    # Check if file already exists
    if os.path.exists(data_file):
        file_size = os.path.getsize(data_file) / (1024 * 1024)  # MB
        print(f"✅ El archivo de datos ya existe: {file_size:.1f} MB")
        return True
    
    # Try to download with gdown
    try:
        import gdown
        print("✅ gdown está disponible")
        
        file_id = '1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r'  # COVID-19 dataset ID
        url = f'https://drive.google.com/uc?id={file_id}'
        print(f"📥 Descargando dataset desde Google Drive...")
        print("⏳ Esto puede tomar varios minutos debido al tamaño del archivo (~1.4GB)...")
        
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
        print("💡 Para descargar automáticamente el dataset, instala gdown:")
        print("   pip install gdown")
        return False
    except Exception as e:
        print(f"❌ Error en la descarga: {e}")
        return False

def main():
    """Ejecuta la aplicación Streamlit"""
    try:
        # Verificar que los archivos requeridos existen
        required_files = [
            'app_analisis_covid.py',
            'procesamiento.py',
            'analisis.py',
            'requirements.txt'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Error: No se encontró el archivo requerido: {file}")
                return 1
        
        # Verificar que el archivo de datos existe y descargar si es necesario
        data_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
        if not os.path.exists(data_file):
            print(f"⚠️  Advertencia: No se encontró el archivo de datos: {data_file}")
            print(".Intentando descargar automáticamente el dataset usando gdown...")
            
            if not download_dataset_with_gdown():
                print("\n❌ No se pudo descargar el dataset automáticamente.")
                print("Por favor, descarga manualmente el archivo desde:")
                print("🔗 https://drive.google.com/file/d/1agwpqQa_Yv7GD5Gzu7RJuG0HqpOk2c0r/view?usp=sharing")
                print("y colócalo en el directorio del proyecto.")
                print()
                return 1
        
        # Ejecutar la aplicación Streamlit
        print("\n🚀 Iniciando aplicación de análisis de COVID-19...")
        print("La aplicación estará disponible en http://localhost:8501")
        print()
        
        # Construir comando de Streamlit con configuración adecuada
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app_analisis_covid.py",
            "--server.port=8501",
            "--server.headless=true",
            "--global.developmentMode=false",
            "--logger.level=warning"
        ]
        
        # Usar subprocess para ejecutar Streamlit
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
        return 0
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())