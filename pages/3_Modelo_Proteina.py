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

# ===== SECCIÓN: ANÁLISIS Y ARGUMENTACIÓN CIENTÍFICA =====
st.header("🧪 Análisis del Comportamiento de la Proteína Soluble en Función del Daño del Grano de Soya")

st.subheader("📚 Resumen desde la literatura")
st.markdown('''
La proteína soluble (PS) en la torta de soya es un indicador clave de la calidad nutricional y del procesamiento térmico del grano. Diversos estudios han demostrado que:

- El **daño del grano de soya** (ya sea físico o térmico) provoca **desnaturalización de proteínas** y reduce su solubilidad.
- La **solubilidad de la proteína** se correlaciona con su digestibilidad en animales monogástricos.
- Procesos como secado, extrusión o tostado mal controlados pueden generar **pérdidas funcionales** importantes.
- Rangos de proteína soluble considerados óptimos en torta de soya están típicamente entre **60% y 80%**, cuando se mide sobre la proteína total mediante métodos estandarizados.
''')

st.subheader("📈 Resultados del modelo con datos reales")
st.markdown('''
Se analizó una base de datos experimental con mediciones de:

- **GDT**: Daño total del grano (porcentaje).
- **PS**: Porcentaje de proteína soluble medida por química húmeda.

Luego de eliminar valores atípicos mediante análisis de residuos (±2σ), se ajustó un modelo lineal simple con los datos válidos:

```
PS = 70.828 − 0.225 × GDT
```

Este modelo presentó un coeficiente de determinación:

```
R² = 0.674
```

Lo que significa que **el 67.4% de la variabilidad** en la proteína soluble se explica por el nivel de daño total del grano.
''')

st.subheader("🔎 Interpretación técnica")
st.markdown('''
- Existe una **relación negativa moderada y estadísticamente significativa**: a mayor daño del grano, menor proporción de proteína soluble.
- Esto es consistente con procesos de **desnaturalización térmica** y formación de agregados insolubles.
- El modelo permite anticipar posibles pérdidas en la calidad funcional de la torta según el nivel de daño observado.
''')

st.subheader("🧠 Variables adicionales recomendadas")
st.markdown("Para mejorar la predicción de PS, se recomienda incorporar otras variables que capturen aspectos críticos del proceso y la materia prima. A continuación se detallan:")

st.table([
    {"Variable sugerida": "tiempo_almac_bolsas", "Justificación técnica": "Después de cocinada la soya, esta se almacena en bolsas por que la sobrecocina la soya.", "Tipo": "Numérica"},
    {"Variable sugerida": "temp_proceso_max", "Justificación técnica": "A mayor temperatura, mayor desnaturalización proteica.", "Tipo": "Numérica"},
    {"Variable sugerida": "tiempo_extrusion", "Justificación técnica": "Aumenta la exposición al calor; potencia la desnaturalización.", "Tipo": "Numérica"},
    {"Variable sugerida": "humedad_entrada", "Justificación técnica": "Afecta la transferencia de calor y la tasa de daño.", "Tipo": "Numérica"},
    {"Variable sugerida": "fibra, cenizas", "Justificación técnica": "Modulan la absorción térmica y la composición estructural.", "Tipo": "Numérica"},
    #{"Variable sugerida": "proteina_total_quim/NIR", "Justificación técnica": "Permite contextualizar el % soluble sobre una base más precisa.", "Tipo": "Numérica"},
    #{"Variable sugerida": "metodo_prot_total", "Justificación técnica": "Ajusta posibles sesgos por tipo de medición (química húmeda vs NIR).", "Tipo": "Categórica"},
    {"Variable sugerida": "sol_KOH, indice_color", "Justificación técnica": "Indicadores directos del daño térmico; mejor correlación con la desnaturalización.", "Tipo": "Numérica"},
    #{"Variable sugerida": "variedad, proveedor", "Justificación técnica": "Diferencias genéticas o estructurales en la composición de la proteína del grano.", "Tipo": "Categórica"},
])


st.subheader("🧮 Modelo Avanzado Propuesto")

st.markdown(r'''
Un modelo avanzado para predecir la proteína soluble (PS) puede incorporar múltiples variables críticas del proceso y la materia prima, permitiendo capturar mejor la complejidad del fenómeno:

$$
\begin{align*}
PS =\ & \beta_0 \\
   & - \beta_1 \times GDT \\
   & - \beta_2 \times temp\_proceso\_max \\
   & - \beta_3 \times tiempo\_extrusion \\
   & - \beta_4 \times humedad\_entrada \\
   & - \beta_5 \times fibra \\
   & - \beta_6 \times cenizas \\
   & - \beta_7 \times tiempo\_almac\_bolsas \\
   & - \beta_8 \times sol\_KOH \\
   & - \beta_9 \times indice\_color \\
   & + \gamma_1 \times variedad \\
   & + \gamma_2 \times proveedor \\
   & + \varepsilon
\end{align*}
$$

**Donde:**
- $PS$: Porcentaje de proteína soluble
- $GDT$: Daño total del grano (%)
- $temp\_proceso\_max$: Temperatura máxima de proceso (°C)
- $tiempo\_extrusion$: Tiempo de extrusión (min)
- $humedad\_entrada$: Humedad de entrada (%)
- $fibra$, $cenizas$: Composición estructural (%)
- $tiempo\_almac\_bolsas$: Tiempo de almacenamiento en bolsas (días)
- $sol\_KOH$, $indice\_color$: Indicadores de daño térmico
- $variedad$, $proveedor$: Variables categóricas (genética/procedencia)
- $\beta_0...\beta_9, \gamma_1, \gamma_2$: Coeficientes a estimar
- $\varepsilon$: Término de error aleatorio

Este modelo permitiría anticipar la calidad funcional de la torta de soya considerando no solo el daño del grano, sino también las condiciones térmicas, estructurales y de almacenamiento, así como la variabilidad genética y de origen.
''')

st.subheader("✅ Conclusión")
st.markdown('''
> Existe una **relación clara, cuantificable y consistente** entre el daño del grano de soya y la reducción de su proteína soluble. Este indicador puede ser utilizado como herramienta de control de calidad del proceso industrial y también como proxy de digestibilidad en productos terminados.
>
> Para obtener **modelos más robustos**, se recomienda incluir variables térmicas, estructurales y composicionales que afectan directamente la fracción de proteína soluble.
''')

# Footer
st.markdown("---")
st.markdown("*Modelo de Proteína - Soya Insights*") 