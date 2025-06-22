import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Modelo de Proteína - Soya Insights",
    page_icon="🥜",
    layout="wide"
)

st.title("🥜 Modelo de Cambio de Proteína Soluble en Función del Daño del Grano")
st.markdown("---")

# Sidebar para parámetros del modelo
st.sidebar.header("🔧 Parámetros del Modelo")
st.sidebar.subheader("Condiciones de Degradación")

degradacion_max = st.sidebar.slider("Degradación Máxima (%)", 0, 100, 95, help="Degradación máxima a simular")
proteina_base = st.sidebar.slider("Proteína Base (%)", 35.0, 45.0, 40.0, step=0.5, 
                                 help="Contenido inicial de proteína en el grano fresco")
factor_perdida_proteina = st.sidebar.slider("Factor de Pérdida de Proteína", 10.0, 25.0, 15.0, step=1.0,
                                           help="Sensibilidad de la pérdida de proteína a la degradación")

# Parámetros adicionales del modelo
st.sidebar.subheader("Parámetros Avanzados")
temperatura_proteina = st.sidebar.slider("Temperatura (°C)", 15, 40, 25, help="Temperatura que afecta la proteína")
factor_temp_proteina = st.sidebar.slider("Factor de Temperatura para Proteína", 0.1, 1.0, 0.5, step=0.1,
                                        help="Efecto de la temperatura en la proteína")
proteina_minima = st.sidebar.slider("Proteína Mínima (%)", 20.0, 30.0, 25.0, step=0.5,
                                   help="Contenido mínimo de proteína después de degradación")

# Función del modelo científico de proteína
def modelo_proteina_cientifico(degradacion, proteina_base, factor_perdida, temperatura, factor_temp, proteina_min):
    """
    Modelo científico de cambio de proteína soluble en función de la degradación del grano
    
    Parámetros:
    - degradacion: porcentaje de degradación (0-1)
    - proteina_base: contenido inicial de proteína (%)
    - factor_perdida: sensibilidad de la pérdida de proteína
    - temperatura: temperatura en °C
    - factor_temp: efecto de la temperatura en la proteína
    - proteina_min: contenido mínimo de proteína (%)
    
    Retorna: contenido de proteína (%)
    """
    # Temperatura de referencia
    temp_ref = 20
    
    # Factor de temperatura (efecto sobre la degradación de proteínas)
    factor_temp_efecto = 1 + (temperatura - temp_ref) * factor_temp * 0.01
    
    # Pérdida de proteína por degradación (modelo no lineal)
    # La pérdida es más rápida al inicio y se estabiliza
    perdida_proteina = degradacion * factor_perdida * factor_temp_efecto * (1 + degradacion * 0.5)
    
    # Proteína total
    proteina_total = proteina_base - perdida_proteina
    
    # Límite mínimo de proteína
    return max(proteina_total, proteina_min)

# Calcular datos para gráficos
degradaciones = np.arange(0, degradacion_max/100 + 0.01, 0.01)
proteinas = [modelo_proteina_cientifico(deg, proteina_base, factor_perdida_proteina, temperatura_proteina, factor_temp_proteina, proteina_minima) 
            for deg in degradaciones]

# Crear DataFrame para análisis
df_proteina = pd.DataFrame({
    'Degradación (%)': [d * 100 for d in degradaciones],
    'Proteína (%)': proteinas,
    'Pérdida Proteína (%)': [proteina_base - p for p in proteinas]
})

# ===== SECCIÓN 1: EXPLICACIÓN DEL MODELO =====
st.header("🔬 Explicación del Modelo de Proteína")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Ecuación del Modelo de Proteína
    
    El modelo de proteína considera la pérdida de proteína soluble por degradación:
    
    **P(D) = P₀ - ΔP(D) × Fₜ**
    
    Donde:
    - **P(D)**: Contenido de proteína en función de la degradación
    - **P₀**: Contenido inicial de proteína (%)
    - **ΔP(D)**: Pérdida de proteína = D × α × Fₜ × (1 + D × β)
    - **D**: Porcentaje de degradación (0-1)
    - **α**: Factor de sensibilidad de pérdida de proteína
    - **Fₜ**: Factor de temperatura = 1 + (T - T₀) × γ
    - **β**: Factor de aceleración no lineal (0.5)
    - **T₀**: Temperatura de referencia (20°C)
    - **γ**: Sensibilidad a temperatura
    """)

with col2:
    st.info(f"""
    **Parámetros Actuales:**
    
    - **Proteína Base:** {proteina_base}%
    - **Factor Pérdida:** {factor_perdida_proteina}
    - **Temperatura:** {temperatura_proteina}°C
    - **Factor Temp:** {factor_temp_proteina}
    - **Proteína Mín:** {proteina_minima}%
    """)

# ===== SECCIÓN 2: GRÁFICOS DE PROTEÍNA =====
st.header("📈 Visualización del Modelo de Proteína")

# Gráfico principal de proteína
fig_proteina = go.Figure()

fig_proteina.add_trace(go.Scatter(
    x=df_proteina['Degradación (%)'],
    y=df_proteina['Proteína (%)'],
    mode='lines+markers',
    name='Proteína Total',
    line=dict(color='green', width=3),
    fill='tonexty'
))

# Agregar línea de proteína base
fig_proteina.add_hline(
    y=proteina_base, 
    line_dash="dash", 
    line_color="blue",
    annotation_text=f"Proteína Base: {proteina_base}%"
)

# Agregar línea de proteína mínima
fig_proteina.add_hline(
    y=proteina_minima, 
    line_dash="dash", 
    line_color="red",
    annotation_text=f"Proteína Mínima: {proteina_minima}%"
)

# Agregar zonas de calidad
fig_proteina.add_hrect(
    y0=proteina_minima, y1=35, 
    fillcolor="red", opacity=0.2,
    annotation_text="Calidad Crítica"
)
fig_proteina.add_hrect(
    y0=35, y1=38, 
    fillcolor="orange", opacity=0.2,
    annotation_text="Calidad Moderada"
)
fig_proteina.add_hrect(
    y0=38, y1=proteina_base, 
    fillcolor="green", opacity=0.2,
    annotation_text="Calidad Excelente"
)

fig_proteina.update_layout(
    title="Cambio de Proteína Soluble en Función de la Degradación del Grano",
    xaxis_title="Degradación (%)",
    yaxis_title="Proteína (%)",
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_proteina, use_container_width=True)

# ===== SECCIÓN 3: ANÁLISIS DE SENSIBILIDAD =====
st.header("🔍 Análisis de Sensibilidad")

col1, col2 = st.columns(2)

with col1:
    # Sensibilidad a temperatura
    temps = np.arange(15, 41, 5)
    proteina_temp = [modelo_proteina_cientifico(0.5, proteina_base, factor_perdida_proteina, t, factor_temp_proteina, proteina_minima) 
                    for t in temps]
    
    fig_temp = px.line(
        x=temps,
        y=proteina_temp,
        title="Sensibilidad a la Temperatura (50% degradación)",
        labels={'x': 'Temperatura (°C)', 'y': 'Proteína (%)'}
    )
    fig_temp.update_traces(line_color='red', line_width=3)
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    # Sensibilidad al factor de pérdida
    factores = np.arange(10.0, 25.1, 2.0)
    proteina_factor = [modelo_proteina_cientifico(0.5, proteina_base, f, temperatura_proteina, factor_temp_proteina, proteina_minima) 
                      for f in factores]
    
    fig_factor = px.line(
        x=factores,
        y=proteina_factor,
        title="Sensibilidad al Factor de Pérdida (50% degradación)",
        labels={'x': 'Factor de Pérdida', 'y': 'Proteína (%)'}
    )
    fig_factor.update_traces(line_color='purple', line_width=3)
    st.plotly_chart(fig_factor, use_container_width=True)

# ===== SECCIÓN 4: TABLA DE RESULTADOS =====
st.header("📋 Resultados Detallados")

# Crear tabla con puntos clave de degradación
puntos_degradacion = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
resultados_proteina = []

for deg in puntos_degradacion:
    proteina = modelo_proteina_cientifico(deg, proteina_base, factor_perdida_proteina, temperatura_proteina, factor_temp_proteina, proteina_minima)
    perdida = proteina_base - proteina
    
    # Determinar calidad basada en proteína
    if proteina >= 38:
        calidad = "Excelente"
        color = "🟢"
    elif proteina >= 35:
        calidad = "Buena"
        color = "🟡"
    elif proteina >= 30:
        calidad = "Moderada"
        color = "🟠"
    else:
        calidad = "Crítica"
        color = "🔴"
    
    resultados_proteina.append({
        'Degradación (%)': f"{deg * 100:.0f}%",
        'Proteína (%)': f"{proteina:.1f}%",
        'Pérdida (%)': f"-{perdida:.1f}%",
        'Calidad': f"{color} {calidad}"
    })

df_resultados = pd.DataFrame(resultados_proteina)
st.dataframe(df_resultados, use_container_width=True)

# ===== SECCIÓN 5: INTERPRETACIÓN CIENTÍFICA =====
st.header("🧪 Interpretación Científica")

st.markdown("""
### Mecanismos de Pérdida de Proteína

1. **Desnaturalización Térmica**: Las proteínas se desnaturalizan a temperaturas elevadas
2. **Degradación Enzimática**: Las proteasas naturales degradan las proteínas
3. **Actividad Microbiana**: Microorganismos consumen proteínas como fuente de energía
4. **Oxidación de Proteínas**: Los radicales libres oxidan aminoácidos
5. **Reacciones de Maillard**: Reacciones entre proteínas y azúcares reductores

### Factores que Afectan la Proteína

- **Temperatura elevada**: Acelera desnaturalización y reacciones químicas
- **Humedad alta**: Favorece actividad enzimática y microbiana
- **Tiempo de almacenamiento**: Acumulación de efectos degradativos
- **Exposición al oxígeno**: Acelera oxidación de proteínas
- **Daño mecánico**: Facilita acceso de enzimas y microorganismos

### Estándares de Calidad por Proteína

- **≥ 38%**: Calidad excelente, apto para proteína aislada
- **35-38%**: Calidad buena, apto para concentrado de proteína
- **30-35%**: Calidad moderada, apto para harina de soya
- **< 30%**: Calidad crítica, uso limitado

### Impacto en Productos Derivados

- **Proteína aislada**: Requiere alto contenido de proteína (>90% en base seca)
- **Concentrado de proteína**: Requiere 65-90% de proteína
- **Harina de soya**: Requiere 44-50% de proteína
- **Alimentos funcionales**: Pérdida de funcionalidad tecnológica
- **Suplementos nutricionales**: Reducción del valor nutricional
""")

# ===== SECCIÓN 6: CALCULADORA INTERACTIVA =====
st.header("🧮 Calculadora de Proteína")

col1, col2 = st.columns(2)

with col1:
    degradacion_calc = st.slider(
        "Degradación del grano (%)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=5.0,
        help="Selecciona el nivel de degradación para calcular la proteína"
    )
    
    proteina_calculada = modelo_proteina_cientifico(
        degradacion_calc/100, 
        proteina_base, 
        factor_perdida_proteina, 
        temperatura_proteina, 
        factor_temp_proteina, 
        proteina_minima
    )
    
    perdida_calculada = proteina_base - proteina_calculada
    
    st.metric(
        label="Proteína Calculada",
        value=f"{proteina_calculada:.1f}%",
        delta=f"-{perdida_calculada:.1f}%"
    )

with col2:
    # Mostrar interpretación de la proteína calculada
    if proteina_calculada >= 38:
        st.success("✅ **Calidad Excelente** - Apto para proteína aislada")
    elif proteina_calculada >= 35:
        st.warning("⚠️ **Calidad Buena** - Apto para concentrado de proteína")
    elif proteina_calculada >= 30:
        st.error("🚨 **Calidad Moderada** - Apto para harina de soya")
    else:
        st.error("🚨 **Calidad Crítica** - Uso limitado")

# Footer
st.markdown("---")
st.markdown("*Modelo de Proteína - Soya Insights*") 