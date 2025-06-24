import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import os

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",      # rgb(26,73,76)
    "verde_claro": "#94AF92",       # rgb(148,175,146)
    "verde_muy_claro": "#E6ECD8",   # rgb(230,236,216)
    "gris_neutro": "#C9C9C9"        # rgb(201,201,201)
}

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

# Calcular datos para gráficos
# degradaciones = np.arange(0, degradacion_max/100 + 0.01, 0.01)
degradaciones = np.arange(0, degradacion_max + 0.01, 0.5)  # degradacion en %
proteinas = 70.828 - 0.225 * degradaciones

# Crear DataFrame para análisis
df_proteina = pd.DataFrame({
    'Degradación (%)': degradaciones,
    'Proteína (%)': proteinas,
    'Pérdida Proteína (%)': 70.828 - proteinas
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

# ===== SECCIÓN 2: DISTRIBUCIONES DE DATOS REALES =====
st.header("📊 Distribuciones de Datos Reales")

st.markdown("""
A continuación se muestran las distribuciones de proteína soluble y daño total de grano basadas en datos reales de laboratorio.
""")

# Ruta base de las gráficas
plots_path = "models/plots"

# Distribuciones en 2 columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("**Distribución de Soluble Protein (%)**")
    st.caption("Histograma de la distribución de proteína soluble en las muestras. La línea vertical indica el valor promedio observado.")
    components.html(open(os.path.join(plots_path, "soluble_protein_distribution.html")).read(), height=420)

with col2:
    st.subheader("**Distribución de Total Grain Damage (%)**")
    st.caption("Histograma de la distribución del daño total de grano en las muestras. La línea vertical indica el valor promedio observado.")
    components.html(open(os.path.join(plots_path, "grain_damage_distribution.html")).read(), height=420)

# ===== SECCIÓN 3: CALCULADORA INTERACTIVA =====
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
    
    # Usar la ecuación lineal para el cálculo
    proteina_calculada = 70.828 - 0.225 * degradacion_calc
    perdida_calculada = 70.828 - proteina_calculada
    
    st.metric(
        label="Proteína Calculada",
        value=f"{proteina_calculada:.1f}%",
        delta=f"-{perdida_calculada:.1f}%"
    )
    st.info(f"""
    **Fórmula utilizada:**
    Proteína = 70.828 - 0.225 × Degradación
    **Cálculo actual:**
    Proteína = 70.828 - 0.225 × {degradacion_calc} = {proteina_calculada:.1f}%
    """)

with col2:
    # Semáforo según el rango de proteína soluble (ecuación lineal)
    if proteina_calculada > 80:
        st.success("🟥 > 80% Torta Soya Cruda")
    elif 75 <= proteina_calculada <= 80:
        st.warning("🟩 Entre 75% y 80% Torta Soya Cocida")
    else:
        st.error("🟨 < 75% Torta Soya Muy Cocida")

# ===== SECCIÓN 5: GRÁFICA DE DISPERSIÓN DE PROTEÍNA SOLUBLE VS DAÑO TOTAL DE GRANO =====
st.header("📈 Dispersión de Proteína Soluble vs Daño Total de Grano (Datos Reales)")
st.caption("Esta gráfica muestra la dispersión real de los datos de laboratorio entre el daño total del grano y el porcentaje de proteína soluble. Cada punto representa una muestra real.")
components.html(open(os.path.join(plots_path, "soluble_protein_vs_grain_damage.html")).read(), height=520)

# ===== SECCIÓN 7: TABLA DE RESULTADOS =====
st.header("📋 Resultados Detallados")

# Crear tabla con puntos clave de degradación
puntos_degradacion = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
resultados_proteina = []
for deg in puntos_degradacion:
    proteina = 70.828 - 0.225 * deg
    perdida = 70.828 - proteina
    if proteina > 80:
        calidad = "Torta Soya Cruda (>80%)"
        color = "🟥"
    elif 75 <= proteina <= 80:
        calidad = "Torta Soya Cocida (75-80%)"
        color = "🟩"
    else:
        calidad = "Torta Soya Muy Cocida (<75%)"
        color = "🟨"
    resultados_proteina.append({
        'Degradación (%)': f"{deg:.0f}%",
        'Proteína (%)': f"{proteina:.1f}%",
        'Pérdida (%)': f"-{perdida:.1f}%",
        'Calidad': f"{color} {calidad}"
    })
df_resultados = pd.DataFrame(resultados_proteina)
st.dataframe(df_resultados, use_container_width=True)

# ===== SECCIÓN 8: INTERPRETACIÓN CIENTÍFICA =====
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

# Footer
st.markdown("---")
st.markdown("*Modelo de Proteína - Soya Insights*") 