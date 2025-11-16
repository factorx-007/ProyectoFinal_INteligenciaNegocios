# Instrucciones para Configurar la Descarga desde Google Drive

## Problema
El archivo de datos `Casos_positivos_de_COVID-19_en_Colombia.csv` es muy grande (1.4 GB) y está almacenado en Git LFS. Cuando se excede el presupuesto de LFS, la aplicación falla al clonar el repositorio.

## Solución
Se ha implementado una funcionalidad para descargar automáticamente el dataset desde Google Drive si no existe localmente.

## Pasos para Configurar la Descarga desde Google Drive

### 1. Subir el Archivo a Google Drive
1. Ve a [Google Drive](https://drive.google.com)
2. Sube el archivo `Casos_positivos_de_COVID-19_en_Colombia.csv` a tu Google Drive
3. Una vez subido, haz clic derecho sobre el archivo
4. Selecciona "Obtener enlace" o "Compartir"
5. Cambia la configuración de acceso a "Cualquier persona con el enlace puede ver"
6. Copia el enlace compartido

### 2. Obtener el ID del Archivo
Del enlace compartido, extrae el ID del archivo:
- Enlace de ejemplo: `https://drive.google.com/file/d/1A2B3C4D5E6F7G8H9I0J/view?usp=sharing`
- El ID es: `1A2B3C4D5E6F7G8H9I0J`

### 3. Configurar el ID en el Código
Tienes dos opciones para configurar el ID:

#### Opción 1: Usar el Script de Configuración (Recomendado)
1. Ejecuta el script de configuración:
   ```bash
   python configurar_google_drive.py
   ```
2. Sigue las instrucciones en pantalla para ingresar el ID

#### Opción 2: Editar Manualmente
1. Abre el archivo `procesamiento.py`
2. Busca la función `descargar_dataset`
3. Reemplaza `'YOUR_GOOGLE_DRIVE_FILE_ID'` con el ID real del archivo

```python
def descargar_dataset(self, file_id='TU_ID_DE_GOOGLE_DRIVE_AQUI'):
```

### 4. Verificar la Configuración
1. Asegúrate de que el archivo `Casos_positivos_de_COVID-19_en_Colombia.csv` NO existe en el directorio del proyecto
2. Ejecuta la aplicación:
   ```bash
   python run_app.py
   ```
3. La aplicación debería mostrar un mensaje indicando que está descargando el dataset desde Google Drive

## Notas Importantes
- La descarga puede tomar varios minutos dependiendo de la velocidad de conexión a internet
- Una vez descargado, el archivo se guardará localmente y no se volverá a descargar en futuras ejecuciones
- El archivo descargado se procesará normalmente como si estuviera en el repositorio

## Solución Alternativa (Descarga Manual)
Si prefieres descargar el archivo manualmente:

1. Descarga el archivo desde [Datos Abiertos Colombia](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr)
2. Guarda el archivo como `Casos_positivos_de_COVID-19_en_Colombia.csv` en el directorio del proyecto
3. Ejecuta la aplicación normalmente

## Beneficios de Esta Solución
- Evita problemas de LFS en plataformas de deployment como Render
- Permite la ejecución de la aplicación sin necesidad de Git LFS
- Mantiene la funcionalidad completa de la aplicación
- Reduce los costos de almacenamiento en Git LFS