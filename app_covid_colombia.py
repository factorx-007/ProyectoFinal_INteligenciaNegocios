import pandas as pd
import requests
import plotly.express as px
import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Análisis COVID-19 Colombia",
    page_icon="📊",
    layout="wide"
)

def obtener_datos():
    """Obtiene los datos de la API de Datos Abiertos de Colombia"""
    url = "https://www.datos.gov.co/resource/gt2j-8ykr.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        datos = response.json()
        return pd.DataFrame(datos)
    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")
        return pd.DataFrame()

def limpiar_datos(df):
    """Limpia y formatea los datos"""
    if df.empty:
        return df
    
    # Convertir columnas de fechas
    fechas = ['fecha_reporte_web', 'fecha_de_notificaci_n', 'fecha_inicio_sintomas', 
              'fecha_diagnostico', 'fecha_recuperado', 'fecha_muerte']
    
    for col in fechas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convertir columnas numéricas
    if 'edad' in df.columns:
        df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    
    return df

def mostrar_estadisticas(df):
    """Muestra estadísticas generales"""
    st.subheader("📊 Estadísticas Generales")
    
    if df.empty:
        st.warning("No hay datos disponibles")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de casos", len(df))
    
    with col2:
        recuperados = df[df['recuperado'] == 'Recuperado'].shape[0]
        st.metric("Casos recuperados", recuperados)
    
    with col3:
        fallecidos = df[df['estado'] == 'Fallecido'].shape[0]
        st.metric("Fallecidos", fallecidos)
    
    with col4:
        if 'fecha_reporte_web' in df.columns and pd.api.types.is_datetime64_any_dtype(df['fecha_reporte_web']):
            ultima_actualizacion = df['fecha_reporte_web'].max()
            if pd.notna(ultima_actualizacion):
                st.metric("Última actualización", ultima_actualizacion.strftime('%Y-%m-%d'))

def mostrar_graficos(df):
    """Muestra gráficos de análisis"""
    if df.empty:
        return
    
    st.subheader("📈 Análisis de Datos")
    
    # Gráfico de casos por departamento
    if 'departamento_nom' in df.columns:
        casos_por_depto = df['departamento_nom'].value_counts().reset_index()
        casos_por_depto.columns = ['Departamento', 'Casos']
        
        fig1 = px.bar(
            casos_por_depto.head(10),
            x='Departamento',
            y='Casos',
            title='Top 10 Departamentos con más casos',
            color='Casos',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico de evolución temporal
    if 'fecha_reporte_web' in df.columns and pd.api.types.is_datetime64_any_dtype(df['fecha_reporte_web']):
        df_fecha = df.groupby(df['fecha_reporte_web'].dt.date).size().reset_index()
        df_fecha.columns = ['Fecha', 'Casos']
        
        fig2 = px.line(
            df_fecha,
            x='Fecha',
            y='Casos',
            title='Evolución de casos por fecha de reporte',
            labels={'Casos': 'Número de casos', 'Fecha': 'Fecha de reporte'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Distribución por edad y sexo
    if 'edad' in df.columns and 'sexo' in df.columns:
        fig3 = px.histogram(
            df,
            x='edad',
            color='sexo',
            title='Distribución de casos por edad y sexo',
            labels={'edad': 'Edad', 'sexo': 'Sexo', 'count': 'Número de casos'},
            barmode='overlay',
            opacity=0.7
        )
        st.plotly_chart(fig3, use_container_width=True)

def main():
    st.title("📊 Análisis de Casos de COVID-19 en Colombia")
    st.markdown("Datos obtenidos de [Datos Abiertos Colombia](https://www.datos.gov.co/)")
    
    # Mostrar indicador de carga mientras se obtienen los datos
    with st.spinner('Cargando datos...'):
        datos = obtener_datos()
        datos_limpios = limpiar_datos(datos)
    
    if not datos_limpios.empty:
        mostrar_estadisticas(datos_limpios)
        mostrar_graficos(datos_limpios)
        
        # Mostrar datos en una tabla expandible
        with st.expander("🔍 Ver datos completos"):
            st.dataframe(datos_limpios)
    else:
        st.error("No se pudieron cargar los datos. Por favor, intente más tarde.")

if __name__ == "__main__":
    main()
