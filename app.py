import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Soya Insights - Degradación de Granos",
    page_icon="🌱",
    layout="wide"
)

# Título principal
st.title("🌱 Soya Insights")
st.subheader("Análisis de Degradación de Granos y su Impacto en Productos Derivados")

# Sidebar para controles
st.sidebar.header("Configuración de Análisis")

# Parámetros de degradación
st.sidebar.subheader("Parámetros de Degradación")
temperatura = st.sidebar.slider("Temperatura (°C)", 15, 40, 25)
humedad = st.sidebar.slider("Humedad Relativa (%)", 40, 90, 60)
tiempo_almacenamiento = st.sidebar.slider("Tiempo de Almacenamiento (días)", 0, 365, 30)

# Función para calcular degradación
def calcular_degradacion(temperatura, humedad, tiempo):
    # Modelo simplificado de degradación
    factor_temp = 1 + (temperatura - 20) * 0.05
    factor_humedad = 1 + (humedad - 50) * 0.02
    degradacion_base = tiempo * 0.001
    
    degradacion_total = degradacion_base * factor_temp * factor_humedad
    return min(degradacion_total, 0.95)  # Máximo 95% de degradación

# Función para calcular impacto en productos
def calcular_impacto_productos(degradacion):
    productos = {
        "Aceite de Soya": 1 - degradacion * 0.3,
        "Harina de Soya": 1 - degradacion * 0.5,
        "Proteína de Soya": 1 - degradacion * 0.7,
        "Lecitina": 1 - degradacion * 0.4,
        "Biodiesel": 1 - degradacion * 0.6
    }
    return productos

# Calcular métricas
degradacion_actual = calcular_degradacion(temperatura, humedad, tiempo_almacenamiento)
impacto_productos = calcular_impacto_productos(degradacion_actual)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Degradación Total",
        value=f"{degradacion_actual:.1%}",
        delta=f"{(degradacion_actual - 0.05):.1%}" if degradacion_actual > 0.05 else None
    )

with col2:
    st.metric(
        label="Calidad Remanente",
        value=f"{(1 - degradacion_actual):.1%}",
        delta=f"{(0.95 - degradacion_actual):.1%}" if degradacion_actual < 0.95 else None
    )

with col3:
    st.metric(
        label="Pérdida Económica Estimada",
        value=f"${degradacion_actual * 1000:.0f} USD/ton",
        delta=f"-${degradacion_actual * 100:.0f} USD/ton"
    )

with col4:
    st.metric(
        label="Vida Útil Restante",
        value=f"{max(0, 365 - tiempo_almacenamiento)} días",
        delta=f"-{tiempo_almacenamiento} días"
    )

# Gráficos
st.subheader("📊 Análisis de Impacto en Productos Derivados")

# Gráfico de barras para productos
fig_productos = px.bar(
    x=list(impacto_productos.keys()),
    y=list(impacto_productos.values()),
    title="Calidad de Productos Derivados",
    labels={'x': 'Producto', 'y': 'Factor de Calidad'},
    color=list(impacto_productos.values()),
    color_continuous_scale='RdYlGn'
)
fig_productos.update_layout(height=400)
st.plotly_chart(fig_productos, use_container_width=True)

# Gráfico de evolución temporal
st.subheader("📈 Evolución de la Degradación en el Tiempo")

dias = list(range(0, 366, 7))
degradaciones = [calcular_degradacion(temperatura, humedad, dia) for dia in dias]

fig_evolucion = go.Figure()
fig_evolucion.add_trace(go.Scatter(
    x=dias,
    y=degradaciones,
    mode='lines+markers',
    name='Degradación',
    line=dict(color='red', width=3)
))
fig_evolucion.add_trace(go.Scatter(
    x=dias,
    y=[1 - d for d in degradaciones],
    mode='lines+markers',
    name='Calidad Remanente',
    line=dict(color='green', width=3)
))

fig_evolucion.update_layout(
    title="Evolución de la Degradación vs Calidad",
    xaxis_title="Días de Almacenamiento",
    yaxis_title="Factor",
    height=400
)
st.plotly_chart(fig_evolucion, use_container_width=True)

# Análisis de sensibilidad
st.subheader("🔍 Análisis de Sensibilidad")

col1, col2 = st.columns(2)

with col1:
    # Sensibilidad a temperatura
    temps = list(range(15, 41, 5))
    degrad_temp = [calcular_degradacion(t, humedad, tiempo_almacenamiento) for t in temps]
    
    fig_temp = px.line(
        x=temps,
        y=degrad_temp,
        title="Sensibilidad a la Temperatura",
        labels={'x': 'Temperatura (°C)', 'y': 'Degradación'}
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    # Sensibilidad a humedad
    hums = list(range(40, 91, 10))
    degrad_hum = [calcular_degradacion(temperatura, h, tiempo_almacenamiento) for h in hums]
    
    fig_hum = px.line(
        x=hums,
        y=degrad_hum,
        title="Sensibilidad a la Humedad",
        labels={'x': 'Humedad (%)', 'y': 'Degradación'}
    )
    st.plotly_chart(fig_hum, use_container_width=True)

# Recomendaciones
st.subheader("💡 Recomendaciones")

if degradacion_actual > 0.3:
    st.warning("⚠️ **Alto nivel de degradación detectado**")
    st.write("- Considerar venta inmediata de inventario")
    st.write("- Revisar condiciones de almacenamiento")
    st.write("- Implementar sistema de monitoreo continuo")
elif degradacion_actual > 0.1:
    st.info("ℹ️ **Degradación moderada**")
    st.write("- Optimizar condiciones de almacenamiento")
    st.write("- Planificar rotación de inventario")
    st.write("- Monitorear parámetros ambientales")
else:
    st.success("✅ **Condiciones óptimas**")
    st.write("- Mantener condiciones actuales")
    st.write("- Continuar monitoreo regular")
    st.write("- Planificar almacenamiento a largo plazo")

# Footer
st.markdown("---")
st.markdown("*Soya Insights - Análisis de Degradación de Granos*") 