import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Soya Insights - Dashboard Principal",
    page_icon="🌱",
    layout="wide"
)

# Título principal
st.title("🌱 Soya Insights: Calidad y Degradación del Grano")

# Información sobre las páginas disponibles
st.info("""
📚 **Páginas Disponibles:**
- **📊 Dashboard Principal** (actual): Vista general
- **📉 Modelo de Degradación**: Detalle científico del modelo de degradación del grano en el tiempo
- **🧪 Modelo de Acidez**: Análisis del cambio de acidez en función de los tipos de daño
- **🥜 Modelo de Proteína**: Estudio del cambio de proteína soluble por degradación
""")

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

# Función para calcular acidez
def calcular_acidez(degradacion):
    # Acidez base (mg KOH/g) + incremento por degradación
    acidez_base = 0.5
    incremento_acidez = degradacion * 2.0  # Máximo 2.0 mg KOH/g adicional
    return acidez_base + incremento_acidez

# Función para calcular porcentaje de proteína
def calcular_proteina(degradacion):
    # Proteína base (%) - pérdida por degradación
    proteina_base = 40.0  # 40% proteína típica en soya
    perdida_proteina = degradacion * 15.0  # Máximo 15% de pérdida
    return max(proteina_base - perdida_proteina, 25.0)  # Mínimo 25%

# Calcular métricas
degradacion_actual = calcular_degradacion(temperatura, humedad, tiempo_almacenamiento)
impacto_productos = calcular_impacto_productos(degradacion_actual)
acidez_actual = calcular_acidez(degradacion_actual)
proteina_actual = calcular_proteina(degradacion_actual)

# ===== SECCIÓN PRINCIPAL: CALCULADORA Y RESULTADOS =====
st.markdown("---")
st.header("📊 Calculadora de Degradación y Resultados")

# Métricas principales en tarjetas
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
        label="Acidez (mg KOH/g)",
        value=f"{acidez_actual:.2f}",
        delta=f"+{acidez_actual - 0.5:.2f}" if acidez_actual > 0.5 else None
    )

with col4:
    st.metric(
        label="Proteína (%)",
        value=f"{proteina_actual:.1f}%",
        delta=f"-{40.0 - proteina_actual:.1f}%" if proteina_actual < 40.0 else None
    )

# Resumen textual de resultados
st.subheader("📋 Resumen de Resultados")

meses_transcurridos = tiempo_almacenamiento / 30.0

if degradacion_actual < 0.1:
    st.success(f"""
    **✅ Condiciones Óptimas**
    
    Después de {meses_transcurridos:.1f} meses de almacenamiento, los granos de soya mantienen excelente calidad:
    - **Degradación mínima:** {degradacion_actual:.1%}
    - **Acidez controlada:** {acidez_actual:.2f} mg KOH/g (dentro de límites normales)
    - **Proteína preservada:** {proteina_actual:.1f}% (cercano al valor original)
    
    **Recomendación:** Continuar con las condiciones actuales de almacenamiento.
    """)
elif degradacion_actual < 0.3:
    st.warning(f"""
    **⚠️ Degradación Moderada**
    
    Después de {meses_transcurridos:.1f} meses de almacenamiento, se observa degradación moderada:
    - **Degradación:** {degradacion_actual:.1%}
    - **Acidez aumentando:** {acidez_actual:.2f} mg KOH/g (requiere monitoreo)
    - **Proteína reducida:** {proteina_actual:.1f}% (pérdida de {40.0 - proteina_actual:.1f}%)
    
    **Recomendación:** Optimizar condiciones de almacenamiento y considerar rotación de inventario.
    """)
else:
    st.error(f"""
    **🚨 Degradación Crítica**
    
    Después de {meses_transcurridos:.1f} meses de almacenamiento, la degradación es crítica:
    - **Degradación alta:** {degradacion_actual:.1%}
    - **Acidez elevada:** {acidez_actual:.2f} mg KOH/g (fuera de especificaciones)
    - **Proteína significativamente reducida:** {proteina_actual:.1f}% (pérdida de {40.0 - proteina_actual:.1f}%)
    
    **Recomendación:** Venta inmediata o procesamiento urgente. Revisar condiciones de almacenamiento.
    """)

# ===== CALCULADORA DE DEGRADACIÓN POR MESES =====
st.subheader("🧮 Calculadora de Degradación por Meses")

# Input para meses
meses_calculo = st.number_input(
    "Ingrese el número de meses para calcular degradación:",
    min_value=0.0,
    max_value=12.0,
    value=3.0,
    step=0.5,
    help="Calcula la degradación esperada para un período específico"
)

# Calcular degradación para el período especificado
dias_calculo = meses_calculo * 30
degradacion_calculada = calcular_degradacion(temperatura, humedad, dias_calculo)
acidez_calculada = calcular_acidez(degradacion_calculada)
proteina_calculada = calcular_proteina(degradacion_calculada)

# Mostrar resultados de la calculadora
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Degradación Esperada**
    - **Período:** {meses_calculo:.1f} meses
    - **Degradación:** {degradacion_calculada:.1%}
    - **Calidad:** {(1-degradacion_calculada):.1%}
    """)

with col2:
    st.info(f"""
    **Acidez Esperada**
    - **Valor:** {acidez_calculada:.2f} mg KOH/g
    - **Incremento:** +{acidez_calculada - 0.5:.2f} mg KOH/g
    - **Estado:** {'Normal' if acidez_calculada < 1.0 else 'Elevada' if acidez_calculada < 2.0 else 'Crítica'}
    """)

with col3:
    st.info(f"""
    **Proteína Esperada**
    - **Valor:** {proteina_calculada:.1f}%
    - **Pérdida:** -{40.0 - proteina_calculada:.1f}%
    - **Estado:** {'Excelente' if proteina_calculada > 35 else 'Buena' if proteina_calculada > 30 else 'Reducida'}
    """)

# ===== GRÁFICOS DE EVOLUCIÓN =====
st.subheader("📈 Evolución de Parámetros por Meses")

# Datos para gráficos
meses_grafico = np.arange(0, 12.1, 0.5)
dias_grafico = meses_grafico * 30
degradaciones = [calcular_degradacion(temperatura, humedad, dia) for dia in dias_grafico]
acideces = [calcular_acidez(deg) for deg in degradaciones]
proteinas = [calcular_proteina(deg) for deg in degradaciones]

# Gráfico de evolución múltiple
fig_evolucion = go.Figure()

# Degradación
fig_evolucion.add_trace(go.Scatter(
    x=meses_grafico,
    y=degradaciones,
    mode='lines+markers',
    name='Degradación (%)',
    line=dict(color='red', width=3),
    yaxis='y'
))

# Acidez
fig_evolucion.add_trace(go.Scatter(
    x=meses_grafico,
    y=acideces,
    mode='lines+markers',
    name='Acidez (mg KOH/g)',
    line=dict(color='orange', width=3),
    yaxis='y2'
))

# Proteína
fig_evolucion.add_trace(go.Scatter(
    x=meses_grafico,
    y=proteinas,
    mode='lines+markers',
    name='Proteína (%)',
    line=dict(color='green', width=3),
    yaxis='y3'
))

fig_evolucion.update_layout(
    title="Evolución de Degradación, Acidez y Proteína por Meses",
    xaxis_title="Meses de Almacenamiento",
    yaxis=dict(title="Degradación (%)", side="left"),
    yaxis2=dict(title="Acidez (mg KOH/g)", side="right", overlaying="y"),
    yaxis3=dict(title="Proteína (%)", side="right", position=0.95),
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_evolucion, use_container_width=True)

# ===== TABLA DE RESULTADOS DETALLADOS =====
st.subheader("📋 Tabla de Resultados Detallados")

# Crear DataFrame con resultados
resultados_data = []
for mes in [0, 1, 2, 3, 6, 9, 12]:
    dias = mes * 30
    deg = calcular_degradacion(temperatura, humedad, dias)
    ac = calcular_acidez(deg)
    prot = calcular_proteina(deg)
    
    resultados_data.append({
        'Meses': mes,
        'Días': dias,
        'Degradación (%)': f"{deg:.1%}",
        'Acidez (mg KOH/g)': f"{ac:.2f}",
        'Proteína (%)': f"{prot:.1f}%",
        'Calidad': 'Excelente' if deg < 0.1 else 'Buena' if deg < 0.2 else 'Moderada' if deg < 0.4 else 'Crítica'
    })

df_resultados = pd.DataFrame(resultados_data)
st.dataframe(df_resultados, use_container_width=True)

# ===== SECCIÓN ORIGINAL (MANTENER PARA COMPATIBILIDAD) =====
st.markdown("---")
st.header("📊 Análisis de Impacto en Productos Derivados")

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

# Footer
st.markdown("---")
st.markdown("*Soya Insights - Análisis de Degradación de Granos*") 