import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class AnalizadorCOVID:
    def __init__(self, df):
        self.df = df
    
    def generar_grafico_evolucion(self, columna_fecha='fecha_de_notificación', frecuencia='M'):
        """Genera un gráfico de evolución temporal"""
        # Agrupar por fecha
        df_agrupado = self.df.groupby(
            pd.Grouper(key=columna_fecha, freq=frecuencia)
        ).size().reset_index(name='conteo')
        
        fig = px.line(
            df_agrupado,
            x=columna_fecha,
            y='conteo',
            title=f'Evolución de casos por {frecuencia}',
            labels={'conteo': 'Número de casos', columna_fecha: 'Fecha'}
        )
        
        return fig
    
    def generar_grafico_barras(self, columna, top_n=10, titulo=None):
        """Genera un gráfico de barras para una columna categórica"""
        if titulo is None:
            titulo = f'Distribución por {columna}'
        
        # Contar valores y tomar los top_n
        conteo = self.df[columna].value_counts().nlargest(top_n)
        
        fig = px.bar(
            x=conteo.index.astype(str),
            y=conteo.values,
            title=titulo,
            labels={'x': columna, 'y': 'Conteo'},
            color=conteo.values,
            color_continuous_scale='Viridis'
        )
        
        return fig
    
    def generar_grafico_piramide_edades(self):
        """Genera una pirámide de edades por sexo"""
        if 'edad' not in self.df.columns or 'sexo' not in self.df.columns:
            return None
        
        # Crear grupos de edad
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120]
        labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99', '100+']
        
        df = self.df.copy()
        df['grupo_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
        
        # Contar por grupo de edad y sexo
        piramide = df.groupby(['grupo_edad', 'sexo']).size().unstack().fillna(0)
        
        # Crear figura
        fig = go.Figure()
        
        # Agregar barras para cada sexo
        if 'F' in piramide.columns:
            fig.add_trace(go.Bar(
                y=piramide.index,
                x=-piramide['F'],
                name='Mujeres',
                orientation='h',
                marker_color='pink'
            ))
        
        if 'M' in piramide.columns:
            fig.add_trace(go.Bar(
                y=piramide.index,
                x=piramide.get('M', 0),
                name='Hombres',
                orientation='h',
                marker_color='lightblue'
            ))
        
        # Actualizar diseño
        fig.update_layout(
            title='Pirámide de Edades por Sexo',
            barmode='overlay',
            xaxis=dict(
                title='Número de casos',
                tickvals=[-50000, -25000, 0, 25000, 50000],
                ticktext=['50k', '25k', '0', '25k', '50k']
            ),
            yaxis_title='Grupo de Edad',
            showlegend=True
        )
        
        return fig
    
    def generar_mapa_calor(self, columna_x, columna_y):
        """Genera un mapa de calor entre dos variables categóricas"""
        if columna_x not in self.df.columns or columna_y not in self.df.columns:
            return None
        
        # Crear tabla de contingencia
        tabla = pd.crosstab(
            index=self.df[columna_y],
            columns=self.df[columna_x],
            normalize='index'  # Normalizar por fila
        )
        
        fig = px.imshow(
            tabla,
            labels=dict(x=columna_x, y=columna_y, color="Proporción"),
            x=tabla.columns,
            y=tabla.index,
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            title=f'Mapa de calor: {columna_y} vs {columna_x}',
            xaxis_title=columna_x,
            yaxis_title=columna_y
        )
        
        return fig
    
    def generar_resumen_estadistico(self):
        """Genera un resumen estadístico de las columnas numéricas"""
        return self.df.describe(include=[np.number])
    
    def generar_resumen_categorico(self, columnas=None):
        """Genera un resumen de las columnas categóricas"""
        if columnas is None:
            columnas = self.df.select_dtypes(include=['category', 'object']).columns
        
        resumen = {}
        for col in columnas:
            resumen[col] = self.df[col].value_counts(normalize=True).head(10).to_dict()
        
        return resumen
