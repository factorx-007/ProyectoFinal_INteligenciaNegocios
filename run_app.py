#!/usr/bin/env python3
"""
Script para ejecutar la aplicación de análisis de COVID-19
"""

import subprocess
import sys
import os

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
        
        # Verificar que el archivo de datos existe
        data_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
        if not os.path.exists(data_file):
            print(f"⚠️  Advertencia: No se encontró el archivo de datos: {data_file}")
            print("El sistema intentará descargarlo automáticamente desde Google Drive.")
            print("Para configurar la descarga, debes:")
            print("1. Subir el archivo a Google Drive")
            print("2. Obtener el ID del archivo de Google Drive")
            print("3. Modificar el método 'descargar_dataset' en procesamiento.py con el ID correcto")
            print()
        
        # Ejecutar la aplicación Streamlit
        print("🚀 Iniciando aplicación de análisis de COVID-19...")
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