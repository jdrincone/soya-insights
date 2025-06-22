import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Modelo de Acidez - Soya Insights",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Modelo de Cambio de Acidez en Función del Daño del Grano")
st.markdown("---")

# Sidebar para parámetros del modelo
st.sidebar.header("🔧 Parámetros del Modelo")
st.sidebar.subheader("Condiciones de Degradación")

degradacion_max = st.sidebar.slider("Degradación Máxima (%)", 0, 100, 95, help="Degradación máxima a simular")
acidez_base = st.sidebar.slider("Acidez Base (mg KOH/g)", 0.1, 1.0, 0.5, step=0.1, 
                               help="Acidez inicial del grano fresco")
factor_acidez = st.sidebar.slider("Factor de Incremento de Acidez", 1.0, 5.0, 2.0, step=0.1,
                                 help="Sensibilidad del incremento de acidez a la degradación")

# Parámetros adicionales del modelo
st.sidebar.subheader("Parámetros Avanzados")
temperatura_acidez = st.sidebar.slider("Temperatura (°C)", 15, 40, 25, help="Temperatura que afecta la acidez")
factor_temp_acidez = st.sidebar.slider("Factor de Temperatura para Acidez", 0.1, 1.0, 0.3, step=0.1,
                                      help="Efecto de la temperatura en la acidez")

# Función del modelo científico de acidez
def modelo_acidez_cientifico(degradacion, acidez_base, factor_acidez, temperatura, factor_temp):
    """
    Modelo científico de cambio de acidez en función de la degradación del grano
    
    Parámetros:
    - degradacion: porcentaje de degradación (0-1)
    - acidez_base: acidez inicial en mg KOH/g
    - factor_acidez: sensibilidad del incremento de acidez
    - temperatura: temperatura en °C
    - factor_temp: efecto de la temperatura en la acidez
    
    Retorna: acidez en mg KOH/g
    """
    # Temperatura de referencia
    temp_ref = 20
    
    # Factor de temperatura (efecto Arrhenius simplificado para acidez)
    factor_temp_efecto = 1 + (temperatura - temp_ref) * factor_temp * 0.01
    
    # Incremento de acidez por degradación (modelo exponencial)
    incremento_acidez = degradacion * factor_acidez * factor_temp_efecto
    
    # Acidez total
    acidez_total = acidez_base + incremento_acidez
    
    # Límite máximo de acidez (5.0 mg KOH/g)
    return min(acidez_total, 5.0)

# Calcular datos para gráficos
degradaciones = np.arange(0, degradacion_max/100 + 0.01, 0.01)
acideces = [modelo_acidez_cientifico(deg, acidez_base, factor_acidez, temperatura_acidez, factor_temp_acidez) 
           for deg in degradaciones]

# Crear DataFrame para análisis
df_acidez = pd.DataFrame({
    'Degradación (%)': [d * 100 for d in degradaciones],
    'Acidez (mg KOH/g)': acideces,
    'Incremento Acidez': [a - acidez_base for a in acideces]
})

# ===== SECCIÓN 1: EXPLICACIÓN DEL MODELO =====
st.header("🔬 Explicación del Modelo de Acidez")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Ecuación del Modelo de Acidez
    
    El modelo de acidez considera la relación entre degradación y formación de ácidos libres:
    
    **A(D) = A₀ + ΔA(D) × Fₜ**
    
    Donde:
    - **A(D)**: Acidez total en función de la degradación
    - **A₀**: Acidez base del grano fresco (mg KOH/g)
    - **ΔA(D)**: Incremento de acidez = D × α × Fₜ
    - **D**: Porcentaje de degradación (0-1)
    - **α**: Factor de sensibilidad de acidez
    - **Fₜ**: Factor de temperatura = 1 + (T - T₀) × β
    - **T₀**: Temperatura de referencia (20°C)
    - **β**: Sensibilidad a temperatura
    """)

with col2:
    st.info(f"""
    **Parámetros Actuales:**
    
    - **Acidez Base:** {acidez_base} mg KOH/g
    - **Factor Acidez:** {factor_acidez}
    - **Temperatura:** {temperatura_acidez}°C
    - **Factor Temp:** {factor_temp_acidez}
    - **Acidez Máx:** 5.0 mg KOH/g
    """)

# ===== SECCIÓN 2: GRÁFICOS DE ACIDEZ =====
st.header("📈 Visualización del Modelo de Acidez")

# Gráfico principal de acidez
fig_acidez = go.Figure()

fig_acidez.add_trace(go.Scatter(
    x=df_acidez['Degradación (%)'],
    y=df_acidez['Acidez (mg KOH/g)'],
    mode='lines+markers',
    name='Acidez Total',
    line=dict(color='orange', width=3),
    fill='tonexty'
))

# Agregar línea de acidez base
fig_acidez.add_hline(
    y=acidez_base, 
    line_dash="dash", 
    line_color="red",
    annotation_text=f"Acidez Base: {acidez_base} mg KOH/g"
)

# Agregar zonas de calidad
fig_acidez.add_hrect(
    y0=0, y1=1.0, 
    fillcolor="green", opacity=0.2,
    annotation_text="Calidad Excelente"
)
fig_acidez.add_hrect(
    y0=1.0, y1=2.0, 
    fillcolor="yellow", opacity=0.2,
    annotation_text="Calidad Buena"
)
fig_acidez.add_hrect(
    y0=2.0, y1=5.0, 
    fillcolor="red", opacity=0.2,
    annotation_text="Calidad Crítica"
)

fig_acidez.update_layout(
    title="Cambio de Acidez en Función de la Degradación del Grano",
    xaxis_title="Degradación (%)",
    yaxis_title="Acidez (mg KOH/g)",
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_acidez, use_container_width=True)

# ===== SECCIÓN 3: ANÁLISIS DE SENSIBILIDAD =====
st.header("🔍 Análisis de Sensibilidad")

col1, col2 = st.columns(2)

with col1:
    # Sensibilidad a temperatura
    temps = np.arange(15, 41, 5)
    acidez_temp = [modelo_acidez_cientifico(0.5, acidez_base, factor_acidez, t, factor_temp_acidez) 
                  for t in temps]
    
    fig_temp = px.line(
        x=temps,
        y=acidez_temp,
        title="Sensibilidad a la Temperatura (50% degradación)",
        labels={'x': 'Temperatura (°C)', 'y': 'Acidez (mg KOH/g)'}
    )
    fig_temp.update_traces(line_color='red', line_width=3)
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    # Sensibilidad al factor de acidez
    factores = np.arange(1.0, 5.1, 0.5)
    acidez_factor = [modelo_acidez_cientifico(0.5, acidez_base, f, temperatura_acidez, factor_temp_acidez) 
                    for f in factores]
    
    fig_factor = px.line(
        x=factores,
        y=acidez_factor,
        title="Sensibilidad al Factor de Acidez (50% degradación)",
        labels={'x': 'Factor de Acidez', 'y': 'Acidez (mg KOH/g)'}
    )
    fig_factor.update_traces(line_color='purple', line_width=3)
    st.plotly_chart(fig_factor, use_container_width=True)

# ===== SECCIÓN 4: TABLA DE RESULTADOS =====
st.header("📋 Resultados Detallados")

# Crear tabla con puntos clave de degradación
puntos_degradacion = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
resultados_acidez = []

for deg in puntos_degradacion:
    acidez = modelo_acidez_cientifico(deg, acidez_base, factor_acidez, temperatura_acidez, factor_temp_acidez)
    incremento = acidez - acidez_base
    
    # Determinar calidad basada en acidez
    if acidez < 1.0:
        calidad = "Excelente"
        color = "🟢"
    elif acidez < 2.0:
        calidad = "Buena"
        color = "🟡"
    elif acidez < 3.0:
        calidad = "Moderada"
        color = "🟠"
    else:
        calidad = "Crítica"
        color = "🔴"
    
    resultados_acidez.append({
        'Degradación (%)': f"{deg * 100:.0f}%",
        'Acidez (mg KOH/g)': f"{acidez:.2f}",
        'Incremento (mg KOH/g)': f"+{incremento:.2f}",
        'Calidad': f"{color} {calidad}"
    })

df_resultados = pd.DataFrame(resultados_acidez)
st.dataframe(df_resultados, use_container_width=True)

# ===== SECCIÓN 5: INTERPRETACIÓN CIENTÍFICA =====
st.header("🧪 Interpretación Científica")

st.markdown("""
### Mecanismos de Formación de Acidez

1. **Hidrólisis de Triglicéridos**: Los lípidos se descomponen liberando ácidos grasos libres
2. **Oxidación Lipídica**: Los ácidos grasos se oxidan formando peróxidos y ácidos
3. **Actividad Enzimática**: Las lipasas naturales hidrolizan los triglicéridos
4. **Actividad Microbiana**: Hongos y bacterias producen ácidos orgánicos

### Factores que Afectan la Acidez

- **Temperatura elevada**: Acelera reacciones de hidrólisis y oxidación
- **Humedad alta**: Favorece actividad enzimática y microbiana
- **Tiempo de almacenamiento**: Acumulación de productos de degradación
- **Daño mecánico**: Facilita acceso de enzimas y microorganismos

### Estándares de Calidad por Acidez

- **< 1.0 mg KOH/g**: Calidad excelente, apto para aceite comestible
- **1.0 - 2.0 mg KOH/g**: Calidad buena, requiere monitoreo
- **2.0 - 3.0 mg KOH/g**: Calidad moderada, uso limitado
- **> 3.0 mg KOH/g**: Calidad crítica, no apto para consumo humano

### Impacto en Productos Derivados

- **Aceite de soya**: Acidez alta reduce estabilidad oxidativa
- **Harina de soya**: Afecta palatabilidad y digestibilidad
- **Proteína de soya**: Puede afectar funcionalidad tecnológica
- **Biodiesel**: Acidez alta puede causar problemas en motores
""")

# ===== SECCIÓN 6: CALCULADORA INTERACTIVA =====
st.header("🧮 Calculadora de Acidez")

col1, col2 = st.columns(2)

with col1:
    degradacion_calc = st.slider(
        "Degradación del grano (%)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=5.0,
        help="Selecciona el nivel de degradación para calcular la acidez"
    )
    
    acidez_calculada = modelo_acidez_cientifico(
        degradacion_calc/100, 
        acidez_base, 
        factor_acidez, 
        temperatura_acidez, 
        factor_temp_acidez
    )
    
    st.metric(
        label="Acidez Calculada",
        value=f"{acidez_calculada:.2f} mg KOH/g",
        delta=f"+{acidez_calculada - acidez_base:.2f} mg KOH/g"
    )

with col2:
    # Mostrar interpretación de la acidez calculada
    if acidez_calculada < 1.0:
        st.success("✅ **Calidad Excelente** - Apto para aceite comestible")
    elif acidez_calculada < 2.0:
        st.warning("⚠️ **Calidad Buena** - Requiere monitoreo")
    elif acidez_calculada < 3.0:
        st.error("🚨 **Calidad Moderada** - Uso limitado")
    else:
        st.error("🚨 **Calidad Crítica** - No apto para consumo humano")

# Footer
st.markdown("---")
st.markdown("*Modelo de Acidez - Soya Insights*") 