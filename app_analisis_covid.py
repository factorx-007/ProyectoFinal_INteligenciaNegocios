import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time

# Configuración inicial para entornos de deployment
st.set_page_config(
    page_title="Análisis COVID-19 Colombia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
import numpy as np
import json
from pathlib import Path
from procesamiento import ProcesadorCOVID
from analisis import AnalizadorCOVID

# La configuración de la página se hace al inicio del archivo
# para evitar problemas en entornos de deployment

# Título y descripción
st.title("📊 Proyecto Final Inteligencia De Negocios")


# Inicialización de variables de sesión
if 'datos_cargados' not in st.session_state:
    st.session_state.datos_cargados = False
    st.session_state.datos_completos = None
    st.session_state.analisis = None
    st.session_state.procesador = None
    st.session_state.df_muestra = None
    st.session_state.filtros_activos = {
        'fecha_inicio': None,
        'fecha_fin': None,
        'departamentos': [],
        'estados': []
    }

def get_memory_usage():
    """Obtiene el uso de memoria actual en MB (simulado para evitar problemas de deployment)"""
    return 0

def verificar_archivos_cache():
    """Verifica si existen los archivos de caché necesarios"""
    return os.path.exists('datos_procesados/datos_covid.parquet') and \
           os.path.exists('datos_procesados/estadisticas.json')

def cargar_datos(forzar_actualizacion=False):
    """Carga los datos con monitoreo de recursos y análisis en caché"""
    try:
        if not forzar_actualizacion and st.session_state.get('datos_cargados', False):
            st.info("Usando datos cargados previamente. Usa 'Forzar Actualización' si necesitas recargar los datos.")
            return True

        cache_existente = verificar_archivos_cache()
        
        start_time = time.time()
        mem_before = get_memory_usage()
        
        # Verificar si los archivos de datos existen antes de intentar cargarlos
        ruta_archivo = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
        
        # Crear procesador
        st.session_state.procesador = ProcesadorCOVID(ruta_archivo)
        
        # Intentar descargar el dataset si no existe localmente
        if not os.path.exists(ruta_archivo):
            st.info("Descargando dataset desde Google Drive...")
            # Reemplaza 'YOUR_GOOGLE_DRIVE_FILE_ID' con el ID real del archivo en Google Drive
            if not st.session_state.procesador.descargar_dataset():
                st.error(f"No se encontró el archivo de datos: {ruta_archivo}")
                st.info("Por favor, asegúrate de que el archivo Casos_positivos_de_COVID-19_en_Colombia.csv está en el directorio del proyecto o se puede descargar desde Google Drive.")
                return False
        
        with st.spinner('Cargando y procesando datos (esto puede tomar varios minutos la primera vez)...'):
            ruta_archivo = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
            
            if cache_existente and not forzar_actualizacion:
                try:
                    # Intentar cargar desde caché con manejo de errores mejorado
                    st.session_state.datos_completos = st.session_state.procesador.cargar_desde_cache()
                    st.session_state.analisis = st.session_state.procesador.cargar_analisis_cache()
                    
                    # Verificar que los datos se cargaron correctamente
                    if st.session_state.analisis is None or len(st.session_state.analisis) == 0:
                        raise Exception("Los datos de análisis del caché están vacíos")
                    
                    st.session_state.df_muestra = st.session_state.procesador.obtener_muestreo_aleatorio(
                        st.session_state.datos_completos, 
                        tamaño_muestra=50000
                    )
                    
                    mem_after = get_memory_usage()
                    tiempo_ejecucion = time.time() - start_time
                    
                    st.session_state.datos_cargados = True
                    st.session_state.metrics = {
                        'tiempo_carga': tiempo_ejecucion,
                        'memoria_usada': mem_after - mem_before,
                        'total_registros': len(st.session_state.datos_completos) if st.session_state.datos_completos is not None else 0,
                        'ultima_actualizacion': st.session_state.analisis.get('ultima_actualizacion', 'N/A') if st.session_state.analisis else 'N/A',
                        'cargado_desde_cache': True
                    }
                    
                    st.success(
                        f"¡Datos cargados desde caché! • "
                        f"{st.session_state.metrics['total_registros']:,} registros • "
                        f"Tiempo: {tiempo_ejecucion:.2f}s"
                    )
                    return True
                except Exception as e:
                    st.warning(f"Error al cargar desde caché: {str(e)}. Procediendo a cargar desde el archivo CSV...")
            
            resultado = st.session_state.procesador.cargar_datos(
                remuestrear=forzar_actualizacion,
                forzar_analisis=forzar_actualizacion
            )
            
            st.session_state.datos_completos = resultado['datos']
            st.session_state.analisis = resultado['analisis']
            
            st.session_state.df_muestra = st.session_state.procesador.obtener_muestreo_aleatorio(
                st.session_state.datos_completos, 
                tamaño_muestra=50000
            )
            
            mem_after = get_memory_usage()
            tiempo_ejecucion = time.time() - start_time
            
            st.session_state.datos_cargados = True
            st.session_state.metrics = {
                'tiempo_carga': tiempo_ejecucion,
                'memoria_usada': mem_after - mem_before,
                'total_registros': len(st.session_state.datos_completos),
                'ultima_actualizacion': st.session_state.analisis.get('ultima_actualizacion', 'N/A'),
                'cargado_desde_cache': False
            }
            
            st.success(
                f"¡Datos cargados correctamente! • "
                f"{st.session_state.metrics['total_registros']:,} registros • "
                f"Tiempo: {tiempo_ejecucion:.2f}s • "
                f"Memoria: {mem_after - mem_before:.2f}MB"
            )
            return True
            
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

# Sidebar para controles
with st.sidebar:
    st.header("⚙️ Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Cargar Datos", use_container_width=True, 
                    help="Cargar datos desde el archivo CSV"):
            cargar_datos()
    
    with col2:
        if st.button("🔄 Forzar Actualización", 
                    help="Forzar la actualización de los datos y análisis",
                    use_container_width=True):
            cargar_datos(forzar_actualizacion=True)
    
    st.markdown("---")
    
    if st.session_state.datos_cargados and st.session_state.analisis:
        st.subheader("📅 Filtros")
        
        try:
            fecha_min = datetime.strptime(st.session_state.analisis['rango_fechas']['min'], '%Y-%m-%d').date()
            fecha_max = datetime.strptime(st.session_state.analisis['rango_fechas']['max'], '%Y-%m-%d').date()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fecha_inicio = st.date_input(
                    "Fecha de inicio",
                    value=fecha_max - timedelta(days=30),
                    min_value=fecha_min,
                    max_value=fecha_max,
                    key='filtro_fecha_inicio'
                )
            
            with col2:
                fecha_fin = st.date_input(
                    "Fecha de fin",
                    value=fecha_max,
                    min_value=fecha_min,
                    max_value=fecha_max,
                    key='filtro_fecha_fin'
                )
            
            departamentos = sorted(st.session_state.analisis.get('top_departamentos', {}).keys())
            departamento_seleccionado = st.multiselect(
                "Departamentos (Top 10)",
                options=departamentos,
                default=st.session_state.filtros_activos['departamentos'],
                key='filtro_departamentos'
            )
            
            estados = list(st.session_state.analisis.get('conteo_por_estado', {}).keys())
            estado_seleccionado = st.multiselect(
                "Estado del caso",
                options=estados,
                default=st.session_state.filtros_activos['estados'],
                key='filtro_estados'
            )
            
            st.session_state.filtros_activos = {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'departamentos': departamento_seleccionado,
                'estados': estado_seleccionado
            }
            
            # Verificar que df_muestra no sea None antes de copiar
            if st.session_state.df_muestra is not None:
                df_filtrado = st.session_state.df_muestra.copy()
                
                # Aplicar filtros solo si el procesador está disponible
                if st.session_state.procesador is not None:
                    if fecha_inicio or fecha_fin:
                        df_filtrado = st.session_state.procesador.filtrar_por_fecha(
                            df_filtrado, 
                            fecha_inicio=fecha_inicio, 
                            fecha_fin=fecha_fin
                        )
                
                if departamento_seleccionado:
                    df_filtrado = df_filtrado[df_filtrado['departamento'].isin(departamento_seleccionado)]
                
                if estado_seleccionado:
                    df_filtrado = df_filtrado[df_filtrado['estado'].isin(estado_seleccionado)]
                
                st.session_state.df_filtrado = df_filtrado
                
                st.caption(f"📊 Mostrando {len(df_filtrado):,} de {len(st.session_state.df_muestra):,} registros")
            else:
                st.warning("No hay datos cargados para filtrar")
            
        except Exception as e:
            st.error(f"Error en filtros: {str(e)}")

def mostrar_estadisticas_generales():
    """Muestra un resumen de estadísticas generales"""
    st.subheader("📊 Estadísticas Generales")
    
    if not st.session_state.analisis:
        st.warning("Por favor carga los datos primero")
        return
    
    try:
        if 'estadisticas_edad' in st.session_state.analisis:
            st.markdown("### 📏 Distribución por Edad")
            edad = st.session_state.analisis['estadisticas_edad']
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Edad promedio", f"{edad.get('promedio', 0):.1f} años")
            col2.metric("Edad mediana", f"{edad.get('mediana', 0):.0f} años")
            col3.metric("Edad mínima", f"{edad.get('min', 0)} años")
            col4.metric("Edad máxima", f"{edad.get('max', 0)} años")
            
            if 'distribucion_por_edad' in st.session_state.analisis:
                dist_edad = st.session_state.analisis['distribucion_por_edad']
                if dist_edad:
                    df_edades = pd.DataFrame(
                        [(str(k), v) for k, v in dist_edad.items()],
                        columns=['Grupo de Edad', 'Cantidad']
                    ).sort_values('Cantidad', ascending=False)
                    
                    fig = px.bar(
                        df_edades, 
                        x='Grupo de Edad', 
                        y='Cantidad',
                        title='Distribución de casos por grupo de edad',
                        color='Cantidad',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error en estadísticas de edad: {str(e)}")
    
    try:
        if 'conteo_por_sexo' in st.session_state.analisis:
            st.markdown("### 👥 Distribución por Sexo")
            conteo_sexo = st.session_state.analisis['conteo_por_sexo']
            if conteo_sexo:
                df_sexo = pd.DataFrame(
                    list(conteo_sexo.items()),
                    columns=['Sexo', 'Cantidad']
                )
                
                fig = px.pie(
                    df_sexo, 
                    values='Cantidad', 
                    names='Sexo',
                    title='Distribución de casos por sexo'
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error en distribución por sexo: {str(e)}")

def mostrar_evolucion_temporal():
    """Muestra la evolución temporal de los casos"""
    st.subheader("📈 Evolución Temporal de Casos")
    
    if not st.session_state.analisis:
        st.warning("Por favor carga los datos primero")
        return
    
    try:
        if 'casos_por_mes' in st.session_state.analisis:
            df_evolucion = pd.DataFrame(
                [(k, v) for k, v in st.session_state.analisis['casos_por_mes'].items()],
                columns=['Fecha', 'Casos']
            )
            df_evolucion['Fecha'] = pd.to_datetime(df_evolucion['Fecha'])
            df_evolucion = df_evolucion.sort_values('Fecha')
            
            fig = px.line(
                df_evolucion,
                x='Fecha',
                y='Casos',
                title='Evolución mensual de casos de COVID-19',
                labels={'Casos': 'Número de casos', 'Fecha': 'Mes'},
                markers=True
            )
            
            df_evolucion['Media Móvil (3 meses)'] = df_evolucion['Casos'].rolling(window=3).mean()
            
            fig.add_scatter(
                x=df_evolucion['Fecha'],
                y=df_evolucion['Media Móvil (3 meses)'],
                name='Media Móvil (3 meses)',
                line=dict(color='red', dash='dash')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error en evolución temporal: {str(e)}")

def mostrar_distribucion_departamentos():
    """Muestra la distribución de casos por departamento"""
    st.subheader("🗺️ Distribución por Departamento")
    
    if not st.session_state.analisis:
        st.warning("⚠️ Por favor carga los datos primero")
        return
    
    try:
        if 'top_departamentos' in st.session_state.analisis:
            # Debug info
            with st.expander("🔍 Información de Depuración"):
                st.write(f"Total departamentos: {len(st.session_state.analisis['top_departamentos'])}")
                st.json(list(st.session_state.analisis['top_departamentos'].keys()))
            
            df_deptos = pd.DataFrame(
                list(st.session_state.analisis['top_departamentos'].items()),
                columns=['Departamento', 'Casos']
            ).sort_values('Casos', ascending=False)
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Departamentos", len(df_deptos))
            with col2:
                st.metric("Casos Máximos", f"{df_deptos['Casos'].max():,}")
            with col3:
                st.metric("Casos Mínimos", f"{df_deptos['Casos'].min():,}")
            with col4:
                st.metric("Promedio", f"{df_deptos['Casos'].mean():.0f}")
            
            # Gráfico de barras horizontal
            st.markdown("### 📊 Top 10 Departamentos")
            fig = px.bar(
                df_deptos.head(10).sort_values('Casos', ascending=True),
                x='Casos',
                y='Departamento',
                orientation='h',
                title='Departamentos con Mayor Número de Casos',
                color='Casos',
                color_continuous_scale='Viridis',
                text='Casos'
            )
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de torta
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🥧 Proporción de Casos")
                fig_pie = px.pie(
                    df_deptos.head(10),
                    values='Casos',
                    names='Departamento',
                    title='Distribución Porcentual'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Comparación")
                fig_funnel = px.funnel(
                    df_deptos.head(10),
                    x='Casos',
                    y='Departamento',
                    title='Embudo de Casos'
                )
                st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Tabla de datos
            st.markdown("### 📋 Datos Detallados")
            df_deptos['Porcentaje'] = (df_deptos['Casos'] / df_deptos['Casos'].sum() * 100).round(2)
            st.dataframe(
                df_deptos,
                use_container_width=True,
                column_config={
                    'Casos': st.column_config.NumberColumn(format='%d'),
                    'Porcentaje': st.column_config.NumberColumn(format='%.2f%%')
                }
            )
        else:
            st.info("📊 No hay datos de departamentos disponibles")
    except Exception as e:
        st.error(f"❌ Error en distribución de departamentos: {str(e)}")
        with st.expander("Ver detalles del error"):
            import traceback
            st.code(traceback.format_exc())

def mostrar_piramide_edades():
    """Muestra la pirámide de edades por sexo"""
    st.subheader("👥 Pirámide de Edades")
    
    if not st.session_state.analisis:
        st.warning("⚠️ Por favor carga los datos primero")
        return
    
    try:
        if 'distribucion_por_edad_y_sexo' in st.session_state.analisis:
            piramide_data = st.session_state.analisis['distribucion_por_edad_y_sexo']
            
            # Debug info
            with st.expander("🔍 Información de Depuración"):
                st.write("Tipo de datos:", type(piramide_data))
                st.write("Claves disponibles:", list(piramide_data.keys()) if isinstance(piramide_data, dict) else "No es dict")
            
            if isinstance(piramide_data, dict):
                df_piramide = pd.DataFrame(piramide_data)
            else:
                df_piramide = piramide_data
            
            if df_piramide.empty:
                st.info("📊 No hay datos disponibles para la pirámide de edades")
                return
            
            # Métricas por sexo
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'F' in df_piramide.columns:
                    total_f = df_piramide['F'].sum()
                    st.metric("👩 Mujeres", f"{total_f:,.0f}")
            with col2:
                if 'M' in df_piramide.columns:
                    total_m = df_piramide['M'].sum()
                    st.metric("👨 Hombres", f"{total_m:,.0f}")
            with col3:
                total = df_piramide.sum().sum()
                st.metric("👥 Total", f"{total:,.0f}")
            
            # Pirámide de edades
            st.markdown("### 📊 Pirámide Poblacional")
            fig = go.Figure()
            
            if 'F' in df_piramide.columns:
                fig.add_trace(go.Bar(
                    y=df_piramide.index,
                    x=-df_piramide['F'].fillna(0),
                    name='Mujeres',
                    orientation='h',
                    marker_color='#FF69B4',
                    text=df_piramide['F'].fillna(0).astype(int),
                    textposition='inside'
                ))
            
            if 'M' in df_piramide.columns:
                fig.add_trace(go.Bar(
                    y=df_piramide.index,
                    x=df_piramide['M'].fillna(0),
                    name='Hombres',
                    orientation='h',
                    marker_color='#4169E1',
                    text=df_piramide['M'].fillna(0).astype(int),
                    textposition='inside'
                ))
            
            fig.update_layout(
                title='Distribución de Casos por Edad y Sexo',
                barmode='overlay',
                xaxis=dict(
                    title='Número de casos',
                    tickformat='.0f',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='black'
                ),
                yaxis_title='Grupo de Edad',
                showlegend=True,
                height=600,
                hovermode='y unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de distribución porcentual
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📈 Distribución por Edad")
                df_total_edad = pd.DataFrame({
                    'Grupo': df_piramide.index,
                    'Total': df_piramide.sum(axis=1)
                })
                fig_edad = px.bar(
                    df_total_edad,
                    x='Grupo',
                    y='Total',
                    title='Total de Casos por Grupo de Edad',
                    color='Total',
                    color_continuous_scale='Blues'
                )
                fig_edad.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_edad, use_container_width=True)
            
            with col2:
                st.markdown("### 🥧 Proporción por Sexo")
                if 'F' in df_piramide.columns and 'M' in df_piramide.columns:
                    sexo_total = pd.DataFrame({
                        'Sexo': ['Mujeres', 'Hombres'],
                        'Casos': [df_piramide['F'].sum(), df_piramide['M'].sum()]
                    })
                    fig_sexo = px.pie(
                        sexo_total,
                        values='Casos',
                        names='Sexo',
                        title='Distribución por Sexo',
                        color='Sexo',
                        color_discrete_map={'Mujeres': '#FF69B4', 'Hombres': '#4169E1'}
                    )
                    st.plotly_chart(fig_sexo, use_container_width=True)
            
            # Tabla detallada
            st.markdown("### 📋 Datos Detallados por Edad y Sexo")
            df_display = df_piramide.copy()
            df_display['Total'] = df_display.sum(axis=1)
            if 'F' in df_display.columns and 'M' in df_display.columns:
                df_display['% Mujeres'] = (df_display['F'] / df_display['Total'] * 100).round(2)
                df_display['% Hombres'] = (df_display['M'] / df_display['Total'] * 100).round(2)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("📊 Datos de pirámide de edades no disponibles")
    except Exception as e:
        st.error(f"❌ Error en pirámide de edades: {str(e)}")
        with st.expander("Ver detalles del error"):
            import traceback
            st.code(traceback.format_exc())

def mostrar_tendencias_temporales():
    """Muestra tendencias temporales avanzadas"""
    st.subheader("📅 Tendencias Temporales")
    
    if not st.session_state.analisis:
        st.warning("⚠️ Por favor carga los datos primero")
        return
    
    try:
        # Debug info
        with st.expander("🔍 Información de Depuración"):
            st.write("Claves disponibles:", list(st.session_state.analisis.keys()))
            if 'casos_por_semana' in st.session_state.analisis:
                st.write(f"Total semanas: {len(st.session_state.analisis['casos_por_semana'])}")
        
        if 'casos_por_semana' in st.session_state.analisis:
            df_semanal = pd.DataFrame(
                [(k, v) for k, v in st.session_state.analisis['casos_por_semana'].items()],
                columns=['Fecha', 'Casos']
            )
            df_semanal['Fecha'] = pd.to_datetime(df_semanal['Fecha'])
            df_semanal = df_semanal.sort_values('Fecha')
            
            # Métricas de tendencia
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📈 Pico Máximo", f"{df_semanal['Casos'].max():,.0f}")
            with col2:
                pico_fecha = df_semanal[df_semanal['Casos'] == df_semanal['Casos'].max()]['Fecha'].iloc[0]
                st.metric("📅 Fecha Pico", pico_fecha.strftime('%Y-%m-%d'))
            with col3:
                st.metric("📊 Promedio Semanal", f"{df_semanal['Casos'].mean():,.0f}")
            with col4:
                st.metric("📉 Mínimo", f"{df_semanal['Casos'].min():,.0f}")
            
            # Agregar año y semana para agrupación
            df_semanal['Año'] = df_semanal['Fecha'].dt.year
            df_semanal['Semana'] = df_semanal['Fecha'].dt.isocalendar().week
            
            # Gráfico de tendencia general
            st.markdown("### 📊 Evolución Semanal Completa")
            fig_linea = go.Figure()
            fig_linea.add_trace(go.Scatter(
                x=df_semanal['Fecha'],
                y=df_semanal['Casos'],
                mode='lines',
                name='Casos Semanales',
                line=dict(color='#1f77b4', width=2),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.3)'
            ))
            
            # Media móvil de 4 semanas
            df_semanal['Media_Movil'] = df_semanal['Casos'].rolling(window=4).mean()
            fig_linea.add_trace(go.Scatter(
                x=df_semanal['Fecha'],
                y=df_semanal['Media_Movil'],
                mode='lines',
                name='Media Móvil (4 semanas)',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            fig_linea.update_layout(
                title='Evolución Semanal de Casos',
                xaxis_title='Fecha',
                yaxis_title='Número de Casos',
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig_linea, use_container_width=True)
            
            # Comparación por año
            st.markdown("### 📈 Comparación Anual por Semana")
            df_agrupado = df_semanal.groupby(['Año', 'Semana'])['Casos'].sum().reset_index()
            df_pivot = df_agrupado.pivot(index='Semana', columns='Año', values='Casos')
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set2
            for idx, col in enumerate(df_pivot.columns):
                fig.add_trace(go.Scatter(
                    x=df_pivot.index,
                    y=df_pivot[col].fillna(0),
                    mode='lines+markers',
                    name=f'Año {col}',
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
            
            fig.update_layout(
                title='Comparación de Casos Semanales por Año',
                xaxis_title='Semana del Año',
                yaxis_title='Número de Casos',
                legend_title='Año',
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Mapa de calor por año y semana
            st.markdown("### 🔥 Mapa de Calor - Intensidad por Semana")
            fig_heatmap = px.imshow(
                df_pivot.fillna(0).T,
                labels=dict(x="Semana", y="Año", color="Casos"),
                x=df_pivot.index,
                y=df_pivot.columns,
                color_continuous_scale='YlOrRd',
                aspect="auto"
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Métricas de casos por estado
            if 'conteo_por_estado' in st.session_state.analisis:
                st.markdown("### 📊 Métricas por Estado del Caso")
                col1, col2, col3, col4 = st.columns(4)
                
                conteo_por_estado = st.session_state.analisis.get('conteo_por_estado', {})
                
                with col1:
                    confirmados = conteo_por_estado.get('Confirmado', 0)
                    st.metric("✅ Confirmados", f"{confirmados:,}".replace(",", "."))
                
                with col2:
                    recuperados = conteo_por_estado.get('Recuperado', 0)
                    st.metric("💚 Recuperados", f"{recuperados:,}".replace(",", "."))
                
                with col3:
                    fallecidos = conteo_por_estado.get('Fallecido', 0)
                    st.metric("⚰️ Fallecidos", f"{fallecidos:,}".replace(",", "."))
                
                with col4:
                    activos = conteo_por_estado.get('Activo', 0)
                    st.metric("🟡 Activos", f"{activos:,}".replace(",", "."))
                
                # Gráfico de distribución de estados
                df_estados = pd.DataFrame(
                    list(conteo_por_estado.items()),
                    columns=['Estado', 'Casos']
                )
                fig_estados = px.bar(
                    df_estados,
                    x='Estado',
                    y='Casos',
                    title='Distribución de Casos por Estado',
                    color='Estado',
                    text='Casos'
                )
                fig_estados.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_estados, use_container_width=True)
        else:
            st.info("📊 No hay datos de tendencias semanales disponibles")
    except Exception as e:
        st.error(f"❌ Error en tendencias temporales: {str(e)}")
        with st.expander("Ver detalles del error"):
            import traceback
            st.code(traceback.format_exc())

def mostrar_analisis_avanzado():
    """Muestra análisis avanzados y gráficos adicionales"""
    st.subheader("🔬 Análisis Avanzado")
    
    if not st.session_state.analisis:
        st.warning("⚠️ Por favor carga los datos primero")
        return
    
    # Debug expandible
    with st.expander("🔍 Información de Depuración - Datos Disponibles"):
        st.write("Claves en análisis:", list(st.session_state.analisis.keys()))
        for key in ['conteo_por_tipo_de_contagio', 'conteo_por_recuperado', 'conteo_por_ubicacion_del_caso', 'conteo_por_pertenencia_etnica']:
            if key in st.session_state.analisis:
                st.write(f"✅ {key}: {len(st.session_state.analisis[key])} categorías")
            else:
                st.write(f"❌ {key}: No disponible")
    
    tab_tipo_contagio, tab_recuperacion, tab_ubicacion, tab_etnia = st.tabs([
        "🦠 Tipo de Contagio", "✅ Recuperación", "📍 Ubicación", "👨‍👩‍👧 Etnia"
    ])
    
    with tab_tipo_contagio:
        try:
            if 'conteo_por_tipo_de_contagio' in st.session_state.analisis:
                st.markdown("### 🦠 Distribución por Tipo de Contagio")
                df_contagio = pd.DataFrame(
                    list(st.session_state.analisis['conteo_por_tipo_de_contagio'].items()),
                    columns=['Tipo', 'Cantidad']
                ).sort_values('Cantidad', ascending=False)
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Categorías", len(df_contagio))
                with col2:
                    st.metric("Categoría Principal", df_contagio.iloc[0]['Tipo'])
                with col3:
                    st.metric("Casos Principales", f"{df_contagio.iloc[0]['Cantidad']:,.0f}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = px.pie(
                        df_contagio.head(10),
                        values='Cantidad',
                        names='Tipo',
                        title='Distribución de Casos por Tipo de Contagio (Top 10)',
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig_bar = px.bar(
                        df_contagio.head(10).sort_values('Cantidad', ascending=True),
                        x='Cantidad',
                        y='Tipo',
                        orientation='h',
                        title='Casos por Tipo',
                        color='Cantidad',
                        color_continuous_scale='Reds',
                        text='Cantidad'
                    )
                    fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Tabla detallada
                st.markdown("#### 📋 Datos Completos")
                df_contagio['Porcentaje'] = (df_contagio['Cantidad'] / df_contagio['Cantidad'].sum() * 100).round(2)
                st.dataframe(df_contagio, use_container_width=True)
            else:
                st.info("📊 No hay datos de tipo de contagio disponibles")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver detalles"):
                import traceback
                st.code(traceback.format_exc())
    
    with tab_recuperacion:
        try:
            if 'conteo_por_recuperado' in st.session_state.analisis:
                st.markdown("### ✅ Distribución por Estado de Recuperación")
                df_recuperacion = pd.DataFrame(
                    list(st.session_state.analisis['conteo_por_recuperado'].items()),
                    columns=['Estado', 'Cantidad']
                ).sort_values('Cantidad', ascending=False)
                
                # Métricas
                col1, col2 = st.columns(2)
                with col1:
                    total = df_recuperacion['Cantidad'].sum()
                    st.metric("👥 Total de Casos", f"{total:,.0f}")
                with col2:
                    if len(df_recuperacion) > 0:
                        principal = df_recuperacion.iloc[0]
                        st.metric(f"👉 {principal['Estado']}", f"{principal['Cantidad']:,.0f}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = px.sunburst(
                        df_recuperacion,
                        path=['Estado'],
                        values='Cantidad',
                        title='Jerarquía de Estados de Recuperación'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📋 Resumen")
                    df_recuperacion['Porcentaje'] = (df_recuperacion['Cantidad'] / df_recuperacion['Cantidad'].sum() * 100).round(2)
                    st.dataframe(df_recuperacion, use_container_width=True)
            else:
                st.info("📊 No hay datos de recuperación disponibles")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver detalles"):
                import traceback
                st.code(traceback.format_exc())
    
    with tab_ubicacion:
        try:
            if 'conteo_por_ubicacion_del_caso' in st.session_state.analisis:
                st.markdown("### 📍 Distribución por Ubicación del Caso")
                df_ubicacion = pd.DataFrame(
                    list(st.session_state.analisis['conteo_por_ubicacion_del_caso'].items()),
                    columns=['Ubicación', 'Cantidad']
                ).sort_values('Cantidad', ascending=False)
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Ubicaciones", len(df_ubicacion))
                with col2:
                    st.metric("Ubicación Principal", df_ubicacion.iloc[0]['Ubicación'])
                with col3:
                    porcentaje = (df_ubicacion.iloc[0]['Cantidad'] / df_ubicacion['Cantidad'].sum() * 100)
                    st.metric("% Principal", f"{porcentaje:.1f}%")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = px.bar(
                        df_ubicacion.head(10),
                        x='Cantidad',
                        y='Ubicación',
                        orientation='h',
                        color='Cantidad',
                        color_continuous_scale='Blues',
                        title='Top 10 Ubicaciones con Más Casos',
                        text='Cantidad'
                    )
                    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Gráfico de dona
                    fig_pie = px.pie(
                        df_ubicacion.head(5),
                        values='Cantidad',
                        names='Ubicación',
                        title='Top 5 Ubicaciones',
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                st.markdown("#### 📋 Datos Completos")
                df_ubicacion['Porcentaje'] = (df_ubicacion['Cantidad'] / df_ubicacion['Cantidad'].sum() * 100).round(2)
                st.dataframe(df_ubicacion, use_container_width=True)
            else:
                st.info("📊 No hay datos de ubicación disponibles")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver detalles"):
                import traceback
                st.code(traceback.format_exc())
    
    with tab_etnia:
        try:
            if 'conteo_por_pertenencia_etnica' in st.session_state.analisis:
                st.markdown("### 👨‍👩‍👧 Distribución por Pertenencia Étnica")
                df_etnia = pd.DataFrame(
                    list(st.session_state.analisis['conteo_por_pertenencia_etnica'].items()),
                    columns=['Etnia', 'Cantidad']
                ).sort_values('Cantidad', ascending=False)
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Etnias", len(df_etnia))
                with col2:
                    st.metric("Etnia Principal", df_etnia.iloc[0]['Etnia'])
                with col3:
                    st.metric("Casos Principales", f"{df_etnia.iloc[0]['Cantidad']:,.0f}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = px.bar(
                        df_etnia.head(15),
                        x='Cantidad',
                        y='Etnia',
                        orientation='h',
                        color='Cantidad',
                        color_continuous_scale='Viridis',
                        title='Top 15 Etnias con Más Casos',
                        text='Cantidad'
                    )
                    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Tabla top 10
                    st.markdown("#### 🎯 Top 10 Etnias")
                    df_top = df_etnia.head(10).copy()
                    df_top['%'] = (df_top['Cantidad'] / df_etnia['Cantidad'].sum() * 100).round(2)
                    st.dataframe(df_top, use_container_width=True)
                
                # Gráfico de treemap
                st.markdown("#### 🌳 Vista Jerárquica")
                fig_tree = px.treemap(
                    df_etnia.head(20),
                    path=['Etnia'],
                    values='Cantidad',
                    title='Distribución Jerárquica de Etnias (Top 20)'
                )
                st.plotly_chart(fig_tree, use_container_width=True)
            else:
                st.info("📊 No hay datos de etnia disponibles")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver detalles"):
                import traceback
                st.code(traceback.format_exc())

def mostrar_comparativas_geographicas():
    """Muestra análisis comparativos y geográficos"""
    st.subheader("🗺️ Análisis Comparativos y Geográficos")
    
    if not st.session_state.analisis:
        st.warning("⚠️ Por favor carga los datos primero")
        return
    
    # Debug info
    with st.expander("🔍 Información de Depuración"):
        st.write("Datos disponibles:")
        if 'top_municipios' in st.session_state.analisis:
            st.write(f"✅ Municipios: {len(st.session_state.analisis['top_municipios'])}")
        if 'top_departamentos' in st.session_state.analisis:
            st.write(f"✅ Departamentos: {len(st.session_state.analisis['top_departamentos'])}")
        st.write(f"Muestra cargada: {st.session_state.datos_cargados}")
    
    tab_municipios, tab_evolucion_dpto, tab_comparacion = st.tabs([
        "🏘️ Top Municipios", "📊 Evolución por Departamento", "🔍 Comparación"
    ])
    
    with tab_municipios:
        try:
            if 'top_municipios' in st.session_state.analisis:
                st.markdown("### 🏘️ Top Municipios con Más Casos")
                df_municipios = pd.DataFrame(
                    list(st.session_state.analisis['top_municipios'].items()),
                    columns=['Municipio', 'Casos']
                ).sort_values('Casos', ascending=False)
                
                # Métricas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🎯 Total Municipios", len(df_municipios))
                with col2:
                    st.metric("🥇 Municipio #1", df_municipios.iloc[0]['Municipio'])
                with col3:
                    st.metric("📈 Casos Máximos", f"{df_municipios.iloc[0]['Casos']:,.0f}")
                with col4:
                    porcentaje_top = (df_municipios.head(10)['Casos'].sum() / df_municipios['Casos'].sum() * 100)
                    st.metric("📊 % Top 10", f"{porcentaje_top:.1f}%")
                
                # Gráfico de barras
                fig = px.bar(
                    df_municipios.head(20),
                    x='Casos',
                    y='Municipio',
                    orientation='h',
                    title='Top 20 Municipios con Más Casos',
                    color='Casos',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabla detallada
                st.markdown("#### 📋 Datos Completos")
                df_municipios['Porcentaje'] = (df_municipios['Casos'] / df_municipios['Casos'].sum() * 100).round(2)
                st.dataframe(df_municipios, use_container_width=True)
            else:
                st.info("📊 No hay datos de municipios disponibles")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver detalles"):
                import traceback
                st.code(traceback.format_exc())
    
    with tab_evolucion_dpto:
        st.info("📊 Funcionalidad en desarrollo")
    
    with tab_comparacion:
        st.info("📊 Funcionalidad en desarrollo")

def main():
    """Función principal de la aplicación"""
    # Cargar datos automáticamente al iniciar si no están cargados
    if not st.session_state.get('datos_cargados', False):
        cargar_datos()
    
    # Mostrar métricas si los datos están cargados
    if st.session_state.datos_cargados and st.session_state.metrics:
        metrics = st.session_state.metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("💾 Registros", f"{metrics['total_registros']:,}")
        col2.metric("⏱️ Tiempo de carga", f"{metrics['tiempo_carga']:.2f}s")
        col3.metric("🔄 Fuente", "Caché" if metrics['cargado_desde_cache'] else "CSV")
    
    # Crear pestañas para diferentes secciones
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Estadísticas Generales", 
        "📅 Evolución Temporal", 
        "🗺️ Departamentos", 
        "👥 Pirámide de Edades",
        "🔬 Análisis Avanzado",
        "🏘️ Comparativas Geográficas"
    ])
    
    with tab1:
        mostrar_estadisticas_generales()
    
    with tab2:
        mostrar_evolucion_temporal()
    
    with tab3:
        mostrar_distribucion_departamentos()
    
    with tab4:
        mostrar_piramide_edades()
    
    with tab5:
        mostrar_analisis_avanzado()
    
    with tab6:
        mostrar_comparativas_geographicas()

if __name__ == "__main__":
    main()