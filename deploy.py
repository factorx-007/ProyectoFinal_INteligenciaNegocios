#!/usr/bin/env python3
"""
Script de despliegue para la aplicación de análisis de COVID-19
"""

import os
import sys
import subprocess

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    try:
        import streamlit
        import pandas
        import dask
        import plotly
        import pyarrow
        import numpy
        import requests
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Error: Falta una dependencia: {e}")
        return False

def install_dependencies():
    """Instala las dependencias desde requirements.txt"""
    print("📥 Instalando dependencias...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False

def check_data_file():
    """Verifica si el archivo de datos existe o puede ser descargado"""
    data_file = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
    
    if os.path.exists(data_file):
        print(f"✅ Archivo de datos encontrado: {data_file}")
        return True
    else:
        print(f"⚠️  Archivo de datos no encontrado: {data_file}")
        print("El sistema intentará descargarlo automáticamente al iniciar la aplicación")
        return True

def main():
    """Función principal de despliegue"""
    print("🚀 Script de Despliegue - Análisis de COVID-19 Colombia")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("🔄 Intentando instalar dependencias...")
        if not install_dependencies():
            print("❌ No se pudieron instalar las dependencias")
            return 1
    
    # Verificar archivo de datos
    if not check_data_file():
        print("❌ No se puede continuar sin el archivo de datos")
        return 1
    
    print("\n✅ ¡Todo listo para el despliegue!")
    print("Para ejecutar la aplicación, usa:")
    print("   python run_app.py")
    print("o")
    print("   streamlit run app_analisis_covid.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())