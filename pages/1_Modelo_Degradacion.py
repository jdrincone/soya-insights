import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Modelo de Degradación - Soya Insights",
    page_icon="📉",
    layout="wide"
)

st.title("📉 Modelo de Degradación del Grano en el Tiempo")
st.markdown("---")

# Sidebar para parámetros del modelo
st.sidebar.header("🔧 Parámetros del Modelo")
st.sidebar.subheader("Condiciones Ambientales")

temperatura = st.sidebar.slider("Temperatura (°C)", 15, 40, 25, help="Temperatura de almacenamiento")
humedad = st.sidebar.slider("Humedad Relativa (%)", 40, 90, 60, help="Humedad relativa del ambiente")
tiempo_max = st.sidebar.slider("Período de Análisis (meses)", 1, 24, 12, help="Meses a simular")

# Parámetros del modelo científico
st.sidebar.subheader("Parámetros del Modelo")
factor_temp = st.sidebar.slider("Factor de Temperatura", 0.01, 0.10, 0.05, step=0.01, 
                               help="Sensibilidad del grano a la temperatura")
factor_humedad = st.sidebar.slider("Factor de Humedad", 0.005, 0.05, 0.02, step=0.005,
                                  help="Sensibilidad del grano a la humedad")
constante_degradacion = st.sidebar.slider("Constante de Degradación Base", 0.0005, 0.002, 0.001, step=0.0001,
                                         help="Tasa base de degradación por día")

# Función del modelo científico de degradación
def modelo_degradacion_cientifico(temperatura, humedad, tiempo_dias, factor_temp, factor_humedad, constante_base):
    """
    Modelo científico de degradación de granos de soya
    
    Parámetros:
    - temperatura: temperatura en °C
    - humedad: humedad relativa en %
    - tiempo_dias: tiempo de almacenamiento en días
    - factor_temp: sensibilidad a temperatura
    - factor_humedad: sensibilidad a humedad
    - constante_base: tasa base de degradación
    
    Retorna: porcentaje de degradación (0-1)
    """
    # Temperatura de referencia (20°C)
    temp_ref = 20
    
    # Humedad de referencia (50%)
    hum_ref = 50
    
    # Factor de temperatura (efecto Arrhenius simplificado)
    factor_temp_efecto = 1 + (temperatura - temp_ref) * factor_temp
    
    # Factor de humedad (efecto exponencial)
    factor_humedad_efecto = 1 + (humedad - hum_ref) * factor_humedad
    
    # Degradación base (efecto del tiempo)
    degradacion_base = constante_base * tiempo_dias
    
    # Degradación total con efectos combinados
    degradacion_total = degradacion_base * factor_temp_efecto * factor_humedad_efecto
    
    # Límite máximo de degradación (95%)
    return min(degradacion_total, 0.95)

# Calcular datos para gráficos
dias = np.arange(0, tiempo_max * 30 + 1, 1)
degradaciones = [modelo_degradacion_cientifico(temperatura, humedad, dia, factor_temp, factor_humedad, constante_degradacion) 
                for dia in dias]

# Crear DataFrame para análisis
df_degradacion = pd.DataFrame({
    'Días': dias,
    'Meses': dias / 30,
    'Degradación (%)': [d * 100 for d in degradaciones],
    'Calidad Remanente (%)': [(1 - d) * 100 for d in degradaciones]
})

# ===== SECCIÓN 1: EXPLICACIÓN DEL MODELO =====
st.header("🔬 Explicación del Modelo Científico")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Ecuación del Modelo de Degradación
    
    El modelo utiliza una ecuación que combina múltiples factores ambientales:
    
    **D(t) = D₀ × Fₜ × Fₕ × t**
    
    Donde:
    - **D(t)**: Degradación total en el tiempo t
    - **D₀**: Constante de degradación base (por día)
    - **Fₜ**: Factor de temperatura = 1 + (T - T₀) × αₜ
    - **Fₕ**: Factor de humedad = 1 + (H - H₀) × αₕ
    - **t**: Tiempo en días
    - **T₀**: Temperatura de referencia (20°C)
    - **H₀**: Humedad de referencia (50%)
    - **αₜ**: Sensibilidad a temperatura
    - **αₕ**: Sensibilidad a humedad
    """)

with col2:
    st.info(f"""
    **Parámetros Actuales:**
    
    - **Temperatura:** {temperatura}°C
    - **Humedad:** {humedad}%
    - **Factor Temp:** {factor_temp}
    - **Factor Hum:** {factor_humedad}
    - **Constante Base:** {constante_degradacion}
    """)

# ===== SECCIÓN 2: GRÁFICOS DE DEGRADACIÓN =====
st.header("📈 Visualización del Modelo")

# Gráfico principal de degradación
fig_degradacion = go.Figure()

fig_degradacion.add_trace(go.Scatter(
    x=df_degradacion['Meses'],
    y=df_degradacion['Degradación (%)'],
    mode='lines+markers',
    name='Degradación (%)',
    line=dict(color='red', width=3),
    fill='tonexty'
))

fig_degradacion.add_trace(go.Scatter(
    x=df_degradacion['Meses'],
    y=df_degradacion['Calidad Remanente (%)'],
    mode='lines+markers',
    name='Calidad Remanente (%)',
    line=dict(color='green', width=3),
    fill='tonexty'
))

fig_degradacion.update_layout(
    title="Evolución de la Degradación del Grano en el Tiempo",
    xaxis_title="Meses de Almacenamiento",
    yaxis_title="Porcentaje (%)",
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_degradacion, use_container_width=True)

# ===== SECCIÓN 3: ANÁLISIS DE SENSIBILIDAD =====
st.header("🔍 Análisis de Sensibilidad")

col1, col2 = st.columns(2)

with col1:
    # Sensibilidad a temperatura
    temps = np.arange(15, 41, 5)
    degrad_temp = [modelo_degradacion_cientifico(t, humedad, 180, factor_temp, factor_humedad, constante_degradacion) * 100 
                  for t in temps]
    
    fig_temp = px.line(
        x=temps,
        y=degrad_temp,
        title="Sensibilidad a la Temperatura (6 meses)",
        labels={'x': 'Temperatura (°C)', 'y': 'Degradación (%)'}
    )
    fig_temp.update_traces(line_color='orange', line_width=3)
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    # Sensibilidad a humedad
    hums = np.arange(40, 91, 10)
    degrad_hum = [modelo_degradacion_cientifico(temperatura, h, 180, factor_temp, factor_humedad, constante_degradacion) * 100 
                 for h in hums]
    
    fig_hum = px.line(
        x=hums,
        y=degrad_hum,
        title="Sensibilidad a la Humedad (6 meses)",
        labels={'x': 'Humedad (%)', 'y': 'Degradación (%)'}
    )
    fig_hum.update_traces(line_color='blue', line_width=3)
    st.plotly_chart(fig_hum, use_container_width=True)

# ===== SECCIÓN 4: TABLA DE RESULTADOS =====
st.header("📋 Resultados Detallados")

# Crear tabla con puntos clave
puntos_clave = [0, 1, 2, 3, 6, 9, 12, 18, 24]
resultados_clave = []

for mes in puntos_clave:
    dias = mes * 30
    degrad = modelo_degradacion_cientifico(temperatura, humedad, dias, factor_temp, factor_humedad, constante_degradacion)
    calidad = 1 - degrad
    
    resultados_clave.append({
        'Meses': mes,
        'Días': dias,
        'Degradación (%)': f"{degrad * 100:.2f}%",
        'Calidad (%)': f"{calidad * 100:.2f}%",
        'Estado': 'Excelente' if degrad < 0.1 else 'Buena' if degrad < 0.2 else 'Moderada' if degrad < 0.4 else 'Crítica'
    })

df_resultados = pd.DataFrame(resultados_clave)
st.dataframe(df_resultados, use_container_width=True)

# ===== SECCIÓN 5: INTERPRETACIÓN CIENTÍFICA =====
st.header("🧪 Interpretación Científica")

st.markdown("""
### Mecanismos de Degradación

1. **Degradación Enzimática**: Las enzimas naturales del grano continúan activas durante el almacenamiento
2. **Oxidación Lipídica**: Los ácidos grasos se oxidan, especialmente a temperaturas elevadas
3. **Actividad Microbiana**: Hongos y bacterias proliferan en condiciones de alta humedad
4. **Respiración del Grano**: El grano continúa respirando, consumiendo nutrientes

### Factores que Aceleran la Degradación

- **Temperatura alta**: Acelera reacciones químicas y enzimáticas
- **Humedad elevada**: Favorece crecimiento microbiano y actividad enzimática
- **Tiempo prolongado**: Acumulación de efectos degradativos
- **Daño mecánico**: Facilita entrada de oxígeno y microorganismos

### Indicadores de Calidad

- **Degradación < 10%**: Calidad excelente, apto para cualquier uso
- **Degradación 10-20%**: Calidad buena, requiere monitoreo
- **Degradación 20-40%**: Calidad moderada, considerar procesamiento
- **Degradación > 40%**: Calidad crítica, uso limitado
""")

# Footer
st.markdown("---")
st.markdown("*Modelo de Degradación - Soya Insights*") 