#  Importaciones principales 

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as pit
from datetime import datetime, timedelta

# Creamos datos sinteticos realistas
np.random.seed(42)
fechas = pd.date_range('2023-01-01', '2024-12-31', freq='D')
n_productos = ['Laptop', 'mouse', 'Teclado', 'Monitor', 'Auriculares']
Regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']

#Generamos un dataset
data = []
for fecha in fechas:
    for _ in range(np.random.poisson(10)): #ventas por promedio por dia
        data.append({
            'fecha': fecha,
            'producto': np.random.choice(n_productos),
            'region': np.random.choice(Regiones),
            'cantidad': np.random.randint(1, 16),
            'precio_unitario': np.random.uniform(50, 1500),
            'vendedor': f'Vendedor_{np.random.randint(1, 21)}'

        })

df = pd.DataFrame(data)
df['total_venta'] = df['cantidad'] * df['precio_unitario']

print("shape del dataset:", df.shape)
print("nprimeras filas:")
print(df.head())
print("\nInformacion general:")
print(df.info())
print("\nEstadisticas descriptivas:")
print(df.describe())

# 1. Ventas por mes 

df_monthly = df.groupby(df['fecha'].dt.to_period('M'))['total_venta'].sum().reset_index()
df_monthly['fecha'] = df_monthly['fecha'].astype(str)

fig_monthly = px.line(
    df_monthly,
    x='fecha',
    y='total_venta',
    title='Tendencia de Ventas Mensuales',
    labels={'total_venta': 'Ventas ($)', 'fecha': 'Mes'}
)

fig_monthly.update_traces(line=dict(width=3))
#fig_monthly.show()

# 2. Top productos

df_productos = df.groupby('producto')['total_venta'].sum().sort_values(ascending=False)

fig_productos = px.bar(
    x=df_productos.values,
    y=df_productos.index,
    orientation='h',
    title='Ventas por Producto',
    labels={'x': 'Ventas Totales ($)', 'y': 'Producto'}
)
#fig_monthly.show()

# 3. Análisis geográficos

df_regiones = df.groupby('region')['total_venta'].sum().reset_index()

fig_regiones = px.pie(
    df_regiones,
    values='total_venta',
    names='region',
    title='Distribución de Ventas por Región'
)

#fig_regiones.show()  

# 4 Correlacion entre variables

df_corr = df[['cantidad', 'precio_unitario', 'total_venta']].corr()

fig_heatmap = px.imshow(
    df_corr,
    text_auto=True,
    aspect='auto',
    title='Correlación entre Variables Numéricas'
)

#fig_heatmap.show()

# 5 Distribucion de ventas 

fig_dist = px.histogram(
    df,
    x='total_venta',   # ← Asegúrate de que esté correctamente nombrado
    nbins=50,
    title='Distribución de Ventas Individuales'
)

#fig_dist.show()

# Configuracion de la pagina

st.set_page_config(page_title="Dashboard de Ventas", 
                     page_icon="📊", layout="wide")

# Titulo  principal
st.title("📊 Dashboard de Analisis de Ventas")
st.markdown("___")

# Sidebar para filtros 

st.sidebar.header("Filtros")
productos_seleccionados = st.sidebar.multiselect(
    "Selecciona Productos",
    options=df['producto'].unique(),
    default=df['producto'].unique()
)

regiones_seleccionadas = st.sidebar.multiselect(
    "Selecciona Regiones",
    options=df['region'].unique(),
    default=df['region'].unique()
)

# Filtrar datos basado en seleccion

df_filtrado = df[
    (df['producto'].isin(productos_seleccionados)) &
    (df['region'].isin(regiones_seleccionadas))
]



# Metrica principales

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Ventas Totales", f"${df_filtrado['total_venta'].sum():,.0f}")

with col2:
    st.metric("Promedio de Ventas", f"${df_filtrado['total_venta'].mean():,.0f}")

with col3:
    st.metric("Número de Ventas", f"{len(df_filtrado):,}")

with col4:
    ventas_2024 = df_filtrado[df_filtrado['fecha'] >= '2024-01-01']['total_venta'].sum()
    ventas_antes_2024 = df_filtrado[df_filtrado['fecha'] < '2024-01-01']['total_venta'].sum()
    
    # Evita división por cero
    if ventas_antes_2024 > 0:
        crecimiento = ((ventas_2024 / ventas_antes_2024) - 1) * 100
    else:
        crecimiento = 0.0  # o puedes poner None

    st.metric("Crecimiento 2024", f"{crecimiento:.1f}%")

# Layout con dos columnas
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.plotly_chart(fig_productos, use_container_width=True)
with col2:
    st.plotly_chart(fig_regiones, use_container_width=True)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Grafico completo en la parte inferior

st.plotly_chart(fig_dist, use_container_width=True)