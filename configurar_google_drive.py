#!/usr/bin/env python3
"""
Script para ayudar a configurar el ID de Google Drive en el archivo de procesamiento
"""

import os
import re

def configurar_google_drive_id():
    """Configura el ID de Google Drive en el archivo de procesamiento"""
    
    # Ruta al archivo de procesamiento
    archivo_procesamiento = 'procesamiento.py'
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_procesamiento):
        print(f"❌ Error: No se encontró el archivo {archivo_procesamiento}")
        return False
    
    # Pedir el ID de Google Drive al usuario
    print("=== Configuración de Google Drive ===")
    print()
    print("Para obtener el ID de Google Drive:")
    print("1. Sube el archivo 'Casos_positivos_de_COVID-19_en_Colombia.csv' a Google Drive")
    print("2. Haz clic derecho sobre el archivo y selecciona 'Compartir' o 'Obtener enlace'")
    print("3. Cambia la configuración de acceso a 'Cualquier persona con el enlace puede ver'")
    print("4. Copia el enlace compartido")
    print()
    print("Ejemplo de enlace:")
    print("https://drive.google.com/file/d/1A2B3C4D5E6F7G8H9I0J/view?usp=sharing")
    print("El ID sería: 1A2B3C4D5E6F7G8H9I0J")
    print()
    
    file_id = input("Ingresa el ID del archivo de Google Drive: ").strip()
    
    if not file_id:
        print("❌ Error: Debes ingresar un ID válido")
        return False
    
    # Leer el contenido del archivo
    try:
        with open(archivo_procesamiento, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return False
    
    # Buscar y reemplazar el ID en el código
    patron = r"def descargar_dataset\(self, file_id='([^']*)'\):"
    reemplazo = f"def descargar_dataset(self, file_id='{file_id}'):"
    
    if re.search(patron, contenido):
        nuevo_contenido = re.sub(patron, reemplazo, contenido)
        
        # Guardar el archivo modificado
        try:
            with open(archivo_procesamiento, 'w', encoding='utf-8') as f:
                f.write(nuevo_contenido)
            
            print()
            print("✅ ¡Configuración completada!")
            print(f"El ID '{file_id}' ha sido configurado correctamente.")
            print()
            print("Ahora puedes ejecutar la aplicación con:")
            print("python run_app.py")
            return True
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")
            return False
    else:
        print("❌ Error: No se encontró la función descargar_dataset en el archivo")
        return False

if __name__ == "__main__":
    configurar_google_drive_id()