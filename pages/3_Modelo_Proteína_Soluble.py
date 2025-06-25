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



# Calcular datos para gráficos
degradacion_max = 120
degradaciones = np.arange(0, degradacion_max/100 + 0.01, 0.01)
#degradaciones = np.arange(0, degradacion_max + 0.01, 0.5)
proteinas = 70.828 - 0.225 * degradaciones

# Crear DataFrame para análisis
df_proteina = pd.DataFrame({
    'Degradación (%)': degradaciones,
    'Proteína (%)': proteinas,
    'Pérdida Proteína (%)': 70.828 - proteinas
})


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
    with st.expander("ℹ️ Detalles del cálculo de proteína"):
        st.markdown(f"""
        **Fórmula utilizada:**
         - **P**(Degradación) = 70.828 - 0.225 × Degradación
         - **Cálculo actual:** 70.828 - 0.225 × {degradacion_calc} = {proteina_calculada:.1f}%
        - **R²** = 0.674
        """)
        # Si tienes el valor de R², muéstralo aquí
        try:
            st.markdown(f"**R² del modelo:** {r2_proteina:.3f}")
        except NameError:
            pass

with col2:
    # Semáforo según el rango de proteína soluble (ecuación lineal)
    if proteina_calculada > 80:
        st.success("🟥 > 80% Torta Soya Cruda")
    elif 75 <= proteina_calculada <= 80:
        st.warning("🟩 Entre 75% y 80% Torta Soya Cocida")
    else:
        st.error("🟨 < 75% Torta Soya Muy Cocida")

# ===== SECCIÓN 1: EXPLICACIÓN DEL MODELO =====
st.header("🔬 Explicación del Modelo de Proteína")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""

        El presente modelo busca describir el comportamiento de la **proteína soluble (PS)** en la torta de soya como función del **nivel de daño del grano (D)**. Se utiliza una formulación lineal simple, que representa una primera aproximación fisiológica y técnica al fenómeno observado:

        **P(D) = P₀ - α × D**
        ### 📌 Parámetros de la ecuación

        - **P(D)**: Contenido de proteína soluble (%) observado cuando el grano tiene un daño total \\( D \\).
        - **P₀**: Contenido de proteína soluble esperado en condiciones ideales, es decir, cuando no hay daño observable en el grano (grano completamente sano).
        - **\\(alpha\\)**: Coeficiente de pérdida, que representa la **sensibilidad de la proteína soluble ante el daño**. Este valor indica cuántos puntos porcentuales de proteína se pierden por cada unidad de daño en el grano.

        ---

        ### 🎯 Supuestos y consideraciones importantes

        Este modelo parte de una serie de supuestos simplificadores que deben ser tenidos en cuenta al momento de su interpretación y uso:

        1. **No se modelan otros factores** que pueden afectar la proteína soluble, tales como:
        - Temperatura de procesamiento.
        - Tiempo de exposición térmica.
        - Humedad del grano.
        - Variedad genética de la soya.
        - Procedencia o proveedor del grano.

        Por tanto, la pérdida de proteína se atribuye exclusivamente al **nivel de daño físico o térmico observado** en los granos, representado por la variable \\( D \\).

        2. **Condiciones constantes de proceso:** Se asume que todos los datos fueron recolectados bajo **las mismas condiciones operativas** en planta (extrusión, secado, molienda, etc.). Esto es importante porque, de no cumplirse, podrían introducirse sesgos por condiciones no controladas.

        3. **Intervalo temporal de los datos:** Los datos utilizados para construir el modelo fueron recolectados entre el **1 de noviembre de 2024** y el **13 de mayo de 2025**, lo que representa un intervalo de 6 meses de producción. El modelo es válido **dentro de ese rango de condiciones productivas y de materia prima**.

        4. **Validez en el rango observado:** La extrapolación fuera del rango de daño observado en los datos puede no ser válida. La relación lineal puede no mantenerse en niveles extremos de daño (e.g., saturación de pérdida o cambios no lineales).

        ---

        ### 📈 Aplicación práctica

        Este modelo permite:

        - Estimar rápidamente la pérdida de proteína esperada dado un nivel de daño.
        - Establecer un umbral de calidad basado en el contenido mínimo aceptable de proteína soluble.
        - Identificar condiciones de producción que puedan estar generando daño excesivo y pérdida de valor nutricional.

        ---
    """)

with col2:
    st.info(f"""
    **Parámetros generales de la Torta de Soya:**
    
    - **Proteína Soluble Promedio:** {63.2}%
    - **Proteína Soluble Max:** {75.80}%
    - **Proteína Soluble Mín:** {48.21}%
    - **Ph muestra:** {6.97}
    - **Humedad:** {13.14}%
    """)

# ===== SECCIÓN 2: DISTRIBUCIONES DE DATOS =====
st.header("📊 Distribuciones de Datos")

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


# ===== SECCIÓN 5: GRÁFICA DE DISPERSIÓN DE PROTEÍNA SOLUBLE VS DAÑO TOTAL DE GRANO =====
st.header("📈 Dispersión de Proteína Soluble vs Daño Total de Grano (Datos Reales)")
st.caption("Esta gráfica muestra la dispersión real de los datos de laboratorio entre el daño total del grano y el porcentaje de proteína soluble. Cada punto representa una muestra real.")
components.html(open(os.path.join(plots_path, "soluble_protein_vs_grain_damage.html")).read(), height=520)

# ===== SECCIÓN 7: TABLA DE RESULTADOS =====
st.header("📋 Resultados Detallados")

# Crear tabla con puntos clave de degradación
puntos_degradacion = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
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
- La **solubilidad de la proteína** se correlaciona con su digestibilidad en animales, según la tabla de negocio (Todas las muestras de grano análizados muestran la característica de soya muy cocida, por tanto el modelo debe ser refinado con una nueva variable que nos indique el grado de cosión de la soya analizada).
- Procesos como secado, extrusión o tostado mal controlados pueden generar **pérdidas funcionales** importantes.
- Rangos de proteína soluble considerados óptimos en torta de soya están típicamente entre **60% y 80%**, cuando se mide sobre la proteína total mediante métodos estandarizados.
''')



st.subheader("🔎 Interpretación técnica")
st.markdown('''
- Existe una **relación negativa moderada y estadísticamente significativa**: a mayor daño del grano, menor proporción de proteína soluble.
- Esto es consistente con procesos de **desnaturalización térmica** y formación de agregados insolubles.
- El modelo permite anticipar posibles pérdidas en la calidad funcional de la torta según el nivel de daño observado.
''')



st.subheader("🧮 Modelo Avanzado Propuesto")

st.markdown(r'''
Un modelo avanzado en pos de mejorar y entender la predecir de proteína soluble (PS) puede incorporar múltiples variables críticas del proceso y la materia prima, permitiendo capturar mejor la complejidad del fenómeno:

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
> El análisis evidencia una **relación negativa significativa** entre el daño total del grano (GDT) y la proteína soluble (PS) en la torta de soya. Este comportamiento sugiere que a mayor daño —probablemente por procesos térmicos o físicos agresivos— se reduce la solubilidad de la proteína, afectando su valor nutricional y funcional.
>
> El modelo lineal ajustado:
>
> **PS = 70.828 − 0.225 × GDT**, con un **R² = 0.674**, permite cuantificar esta pérdida bajo los supuestos de condiciones de proceso constantes.
>
> Esta herramienta:
> - Puede ser usada como **indicador de control de calidad en planta**, al vincular condiciones de materia prima y proceso con el resultado final en PS.
> - Ayuda a **identificar desviaciones críticas** que afectan la funcionalidad de la torta de soya.
>
> Sin embargo, el modelo actual **no captura otras fuentes importantes de variabilidad**, como temperatura real de extrusión, humedad, tiempo de procesamiento, variedad genética o condiciones de almacenamiento. Estas variables pueden tener un efecto confusor o amplificador del fenómeno.
>
> Se recomienda avanzar hacia un **modelo multivariable integrado**, que permita ajustar por estos factores y mejorar tanto la capacidad predictiva como la interpretación técnica del proceso.
''')

# Footer
st.markdown("---")
st.markdown("*Modelo de Proteína Soluble - Soya Insights - Okuo-Analytics - Juan David Rincón *") 