# Instrucciones de Despliegue

## Problema
El despliegue en plataformas como Render está fallando por dos razones:
1. El archivo de datos grande está almacenado en Git LFS y se ha excedido el presupuesto
2. La versión de Python 3.13.9 en el entorno de despliegue no es compatible con pyarrow==16.1.0

## Solución Implementada
Se han realizado los siguientes cambios para resolver estos problemas:

### 1. Gestión de Dependencias
- Actualizado [requirements.txt](file:///d:/ProyectoFinal_DPD/requirements.txt) para usar versiones mínimas en lugar de versiones fijas
- Cambiado de `pyarrow==16.1.0` a `pyarrow>=16.1.0` para permitir versiones compatibles
- Añadido `requests>=2.31.0` para la descarga desde Google Drive
- Añadido [runtime.txt](file:///d:/ProyectoFinal_DPD/runtime.txt) para especificar Python 3.11

### 2. Configuración de Streamlit
- Añadido [.streamlit/config.toml](file:///d:/ProyectoFinal_DPD/.streamlit/config.toml) con configuración optimizada para despliegue
- Configurado modo headless y puerto fijo

### 3. Descarga Automática de Datos
- Implementada funcionalidad para descargar el dataset desde Google Drive si no existe localmente
- Añadido script de configuración para facilitar la integración con Google Drive

## Pasos para el Despliegue

### 1. Configurar Google Drive (Obligatorio)
1. Sube el archivo `Casos_positivos_de_COVID-19_en_Colombia.csv` a Google Drive
2. Configura el ID de Google Drive:
   ```bash
   python configurar_google_drive.py
   ```

### 2. Verificar Dependencias
```bash
python deploy.py
```

### 3. Ejecutar la Aplicación
```bash
python run_app.py
```

## Solución de Problemas Comunes

### Error de Construcción de PyArrow
Si continúan los problemas con pyarrow, prueba:
1. Asegúrate de que [runtime.txt](file:///d:/ProyectoFinal_DPD/runtime.txt) especifica `python-3.11`
2. Elimina versiones fijas en [requirements.txt](file:///d:/ProyectoFinal_DPD/requirements.txt)

### Problemas de Memoria en Despliegue
La aplicación está configurada para usar menos recursos:
- Modo headless activado
- Nivel de logging reducido
- Desactivadas funciones de desarrollo

### Problemas de Puerto
La aplicación usa el puerto 8501 por defecto, que es compatible con la mayoría de plataformas de despliegue.

## Archivos de Configuración Importantes

- [runtime.txt](file:///d:/ProyectoFinal_DPD/runtime.txt): Especifica la versión de Python
- [.streamlit/config.toml](file:///d:/ProyectoFinal_DPD/.streamlit/config.toml): Configuración de Streamlit
- [requirements.txt](file:///d:/ProyectoFinal_DPD/requirements.txt): Dependencias actualizadas
- [deploy.py](file:///d:/ProyectoFinal_DPD/deploy.py): Script de verificación de despliegue

## Beneficios de Esta Configuración

1. **Compatibilidad**: Funciona con versiones modernas de Python
2. **Flexibilidad**: No depende de Git LFS para datos grandes
3. **Eficiencia**: Configuración optimizada para entornos con recursos limitados
4. **Automatización**: Descarga automática de datos si no están presentes