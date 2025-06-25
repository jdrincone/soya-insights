import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import joblib
import os

# Configuración de la página
st.set_page_config(
    page_title="Soya Insights",
    page_icon="🌱",
    layout="wide"
)

# Título principal
st.title("🌱 Soya Insights")

# Información sobre las páginas disponibles
st.info("""
📚 **Páginas Disponibles:**
- **📊 Resumen Principal** (actual): Soya Insights
- **📉 Modelo de Degradación**: Detalle del modelo de degradación del grano en función del tiempo
- **🧪 Modelo de Acidez**: Análisis del cambio de acidez en función del daño
- **🥜 Modelo de Proteína**: Estudio del cambio de proteína soluble por degradación
""")

# Sidebar para controles
st.sidebar.header("Configuración de Análisis")

# Parámetros de degradación reales
st.sidebar.subheader("Parámetros de Daño del Grano")
gdc = st.sidebar.slider("GDC - Daño Térmico (%)", 0.0, 100.0, 25.0, 0.1)
gdh = st.sidebar.slider("GDH - Daño por Hongos (%)", 0.0, 50.0, 10.0, 0.1)
gdt = gdc + gdh

# Mostrar GDT calculado
st.sidebar.info(f"""
**GDT - Daño Total: {gdt:.1f}%**
- GDC: {gdc:.1f}%
- GDH: {gdh:.1f}%
""")

# Cargar modelos entrenados
@st.cache_resource
def load_models():
    """Cargar modelos entrenados"""
    models = {}
    
    # Modelo de acidez
    if os.path.exists("models/artifacts/random_forest_acidez.pkl"):
        models['acidez'] = joblib.load("models/artifacts/random_forest_acidez.pkl")
    
    # Modelo de proteína (usar regresión lineal simple)
    try:
        from sklearn.linear_model import LinearRegression
        # Cargar datos de proteína para entrenar modelo simple
        df_protein = pd.read_csv("data/datos_gdt_protein.csv")
        X_protein = df_protein[["GDT"]].values
        y_protein = df_protein["pct_soluble_protein_quim"].values
        
        model_protein = LinearRegression()
        model_protein.fit(X_protein, y_protein)
        models['proteina'] = model_protein
    except Exception as e:
        st.warning(f"No se pudo cargar el modelo de proteína: {e}")
        models['proteina'] = None
    
    return models

# Cargar modelos
models = load_models()

# Función para calcular acidez usando el modelo real
def calcular_acidez_real(gdc, gdh, model):
    """Calcular acidez usando el modelo Random Forest entrenado"""
    if model is None:
        # Fallback: modelo simplificado
        acidez_base = 0.5
        incremento_acidez = (gdc + gdh) * 0.02  # 2% por cada % de daño
        return acidez_base + incremento_acidez
    
    # Usar modelo real
    X_pred = np.array([[gdc, gdh]])
    return model.predict(X_pred)[0]

# Función para calcular proteína usando el modelo real
def calcular_proteina_real(gdt, model):
    """Calcular proteína soluble usando el modelo entrenado"""
    if model is None:
        # Fallback: modelo simplificado
        proteina_base = 70.0  # 70% proteína típica
        perdida_proteina = gdt * 0.3  # 0.3% de pérdida por cada % de GDT
        return max(proteina_base - perdida_proteina, 30.0)
    
    # Usar modelo real
    X_pred = np.array([[gdt]])
    return model.predict(X_pred)[0]

# Función para calcular impacto en productos
def calcular_impacto_productos(gdt):
    """Calcular impacto en productos basado en GDT"""
    # GDT más alto = mayor impacto negativo
    factor_calidad = max(0.05, 1 - (gdt / 100))
    
    productos = {
        "Aceite de Soya": factor_calidad * 0.9,  # 90% de calidad base
        "Harina de Soya": factor_calidad * 0.85,  # 85% de calidad base
        "Proteína de Soya": factor_calidad * 0.8,  # 80% de calidad base
        "Lecitina": factor_calidad * 0.95,  # 95% de calidad base
        "Biodiesel": factor_calidad * 0.75   # 75% de calidad base
    }
    return productos

# Calcular métricas usando modelos reales
acidez_actual = calcular_acidez_real(gdc, gdh, models.get('acidez'))
proteina_actual = calcular_proteina_real(gdt, models.get('proteina'))
impacto_productos = calcular_impacto_productos(gdt)

# ===== SECCIÓN PRINCIPAL: CALCULADORA Y RESULTADOS =====
st.markdown("---")
st.header("📊 Calculadora de Degradación y Resultados")

# Métricas principales en tarjetas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="GDT - Daño Total",
        value=f"{gdt:.1f}%",
        delta=f"+{gdt - 15:.1f}%" if gdt > 15 else None
    )

with col2:
    calidad_remanente = max(0, 100 - gdt)
    st.metric(
        label="Calidad Remanente",
        value=f"{calidad_remanente:.1f}%",
        delta=f"{(100 - gdt) - 85:.1f}%" if gdt < 15 else None
    )
    st.caption("💡 Porcentaje de calidad que queda en los granos después del daño total (GDT), se toma como base un  85% Calidad Remanente.")

with col3:
    st.metric(
        label="Acidez (mg KOH/g)",
        value=f"{acidez_actual:.2f}",
        delta=f"+{acidez_actual - 0.5:.2f}" if acidez_actual > 0.5 else None
    )
    st.caption("💡 Valor base: 0.5 mg KOH/g. Límite máximo aceptable: 2.0 mg KOH/g.")

with col4:
    st.metric(
        label="Proteína Soluble (%)",
        value=f"{proteina_actual:.1f}%",
        delta=f"-{70.0 - proteina_actual:.1f}%" if proteina_actual < 70.0 else None
    )
    st.caption("💡 Proteína Base: 70.0%. Límite mínimo aceptable: 50.0%.")

# Resumen textual de resultados
st.subheader("📋 Resumen de Resultados")

if gdt < 15:
    st.success(f"""
    **✅ Calidad Excelente**
    
    Con un daño total (GDT) de {gdt:.1f}%, los granos de soya mantienen excelente calidad:
    - **Daño térmico (GDC):** {gdc:.1f}% (controlado)
    - **Daño por hongos (GDH):** {gdh:.1f}% (mínimo)
    - **Acidez controlada:** {acidez_actual:.2f} mg KOH/g (dentro de límites normales)
    - **Proteína preservada:** {proteina_actual:.1f}% (excelente)
    
    **Recomendación:** Granos aptos para todos los usos industriales.
       """)
    st.markdown("""

     **⚠️ Nota de validez:** 
   -  Los resultados son válidos siempre que se cumplan las condiciones asumidas y el comportamiento observado se mantenga en el tiempo evaluado.
      """)
elif gdt < 35:
    st.warning(f"""
    **⚠️ Calidad Moderada**
    
    Con un daño total (GDT) de {gdt:.1f}%, se observa degradación moderada:
    - **Daño térmico (GDC):** {gdc:.1f}% (requiere monitoreo)
    - **Daño por hongos (GDH):** {gdh:.1f}% (aumentando)
    - **Acidez aumentando:** {acidez_actual:.2f} mg KOH/g (requiere atención)
    - **Proteína reducida:** {proteina_actual:.1f}% (pérdida de {70.0 - proteina_actual:.1f}%)
    
  
    """)
    st.markdown("""

     **⚠️ Nota de validez:** 
   -  Los resultados son válidos siempre que se cumplan las condiciones asumidas y el comportamiento observado se mantenga en el tiempo evaluado.
      """)
    
else:
    st.error(f"""
    **🚨 Calidad Crítica**
    
    Con un daño total (GDT) de {gdt:.1f}%, la degradación es crítica:
    - **Daño térmico (GDC):** {gdc:.1f}% (muy alto)
    - **Daño por hongos (GDH):** {gdh:.1f}% (crítico)
    - **Acidez elevada:** {acidez_actual:.2f} mg KOH/g (fuera de especificaciones)
    - **Proteína significativamente reducida:** {proteina_actual:.1f}% (pérdida de {70.0 - proteina_actual:.1f}%)
    
    **Recomendación:** Venta inmediata o procesamiento urgente. Revisar condiciones.

    """)
    st.markdown("""

     **⚠️ Nota de validez:** 
   -  Los resultados son válidos siempre que se cumplan las condiciones asumidas y el comportamiento observado se mantenga en el tiempo evaluado.
      """)


# ===== GRÁFICOS DE EVOLUCIÓN =====
st.subheader("📈 Evolución de Parámetros por GDT")

# Crear datos para el gráfico
gdt_range = np.linspace(0, 100, 50)
acidez_range = [calcular_acidez_real(gdt_val * 0.7, gdt_val * 0.3, models.get('acidez')) for gdt_val in gdt_range]
proteina_range = [calcular_proteina_real(gdt_val, models.get('proteina')) for gdt_val in gdt_range]

# Gráfico de evolución
fig = go.Figure()

# Acidez
fig.add_trace(go.Scatter(
    x=gdt_range,
    y=acidez_range,
    mode='lines',
    name='Acidez (mg KOH/g)',
    line=dict(color='#FF6B6B', width=3),
    yaxis='y'
))

# Proteína
fig.add_trace(go.Scatter(
    x=gdt_range,
    y=proteina_range,
    mode='lines',
    name='Proteína Soluble (%)',
    line=dict(color='#4ECDC4', width=3),
    yaxis='y2'
))

# Líneas de referencia
fig.add_hline(y=1.0, line_dash="dash", line_color="orange", 
              annotation_text="Límite Acidez", yref="y")

# Línea vertical para el promedio de GDT de la empresa
fig.add_vline(x=38.16, line_dash="dash", line_color="purple", line_width=2,
              annotation_text="Promedio Empresa (38.16%)", 
              annotation_position="top right",
              annotation=dict(font=dict(color="purple", size=12)))

# Punto actual
fig.add_trace(go.Scatter(
    x=[gdt],
    y=[acidez_actual],
    mode='markers',
    name='Valor Actual - Acidez',
    marker=dict(color='#FF6B6B', size=12, symbol='diamond'),
    yaxis='y'
))

fig.add_trace(go.Scatter(
    x=[gdt],
    y=[proteina_actual],
    mode='markers',
    name='Valor Actual - Proteína',
    marker=dict(color='#4ECDC4', size=12, symbol='diamond'),
    yaxis='y2'
))

fig.update_layout(
    title="Evolución de Acidez y Proteína vs GDT",
    xaxis_title="GDT - Daño Total (%)",
    yaxis=dict(title="Acidez (mg KOH/g)", side="left"),
    yaxis2=dict(title="Proteína Soluble (%)", side="right", overlaying="y"),
    height=500,
    showlegend=True,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)

# ===== EVOLUCIÓN TEMPORAL =====
st.subheader("⏰ Evolución Temporal de Calidad")

# Información sobre la ecuación utilizada
with st.expander("🔬 Ecuación del Daño del Grano Utilizada"):
    st.markdown("""
    **📊 Modelo Matemático del Daño del Grano:**
    
    **Ecuación Principal:** `y = 0.0730x² - 0.7741x + 14.8443`
    
    **Donde:**
    - **y** = Daño del grano (%)
    - **x** = Tiempo de almacenamiento (meses)
    
    **Características de la Ecuación:**
    - **Tipo:** Ecuación cuadrática (parábola)
    - **Coeficiente cuadrático:** 0.0730 (curvatura positiva)
    - **Coeficiente lineal:** -0.7741 (pendiente inicial negativa)
    - **Término independiente:** 14.8443 (daño inicial)
    
    **Interpretación:**
    - **Daño inicial:** 14.84% al tiempo 0
    - **Comportamiento:** Decrece inicialmente, luego aumenta exponencialmente
    - **Punto mínimo:** Aproximadamente a los 5.3 meses
    - **Tendencia:** Aceleración del daño a largo plazo
    
    **Asunciones en la adquisición de datos:**
    - Datos fueron recolectados bajo las mismas condiciones operativas en planta (extrusión, secado, molienda, etc.). Esto es importante porque, de no cumplirse, podrían introducirse sesgos por condiciones no controladas.
     - Intervalo temporal debradación del grano: 19 meses (sin informacíon de meses calendario).
    - Intervalo temporal proteína soluble: entre el 1 de noviembre de 2024 y el 13 de mayo de 2025.
    - Intervalo temporal de acidez: entre el 1 de octubre de 2024 y el 6 de Junio de 2025.
    """)

# Valores fijos para la simulación
temperatura_alm = 25  # Temperatura fija
humedad_alm = 60      # Humedad fija
tiempo_max = 20       # Período fijo de 20 meses
gdc_inicial = 5.0     # Valor fijo inicial
gdh_inicial = 2.0     # Valor fijo inicial

# Función para simular evolución temporal
def simular_evolucion_temporal(temperatura, humedad, gdc_ini, gdh_ini, meses):
    """Simular evolución de GDC y GDH a lo largo del tiempo usando ecuación real"""
    tiempos = np.arange(0, meses + 1, 0.5)  # Cada 15 días
    
    # Factores de degradación basados en condiciones
    factor_temp = 1 + (temperatura - 20) * 0.02  # 2% por °C sobre 20°C
    factor_hum = 1 + (humedad - 50) * 0.01       # 1% por % de humedad sobre 50%
    
    # Ecuación real del daño del grano: y = 0.0730x² - 0.7741x + 14.8443
    # Donde x es el tiempo en meses
    def ecuacion_daño_grano(tiempo):
        return 0.0730 * tiempo**2 - 0.7741 * tiempo + 14.8443
    
    # Evolución de GDC (daño térmico) usando ecuación real
    gdc_evol = []
    for t in tiempos:
        # Aplicar ecuación real y ajustar por condiciones
        daño_base = ecuacion_daño_grano(t)
        daño_ajustado = daño_base * factor_temp
        gdc_final = min(gdc_ini + daño_ajustado, 100)  # Máximo 100%
        gdc_evol.append(max(0, gdc_final))  # Mínimo 0%
    
    # Evolución de GDH (daño por hongos, más sensible a humedad)
    gdh_evol = []
    for t in tiempos:
        # Para hongos, usar una ecuación similar pero más sensible a humedad
        daño_hongos_base = ecuacion_daño_grano(t) * 0.6  # 60% del daño térmico
        daño_hongos_ajustado = daño_hongos_base * factor_hum
        gdh_final = min(gdh_ini + daño_hongos_ajustado, 50)  # Máximo 50%
        gdh_evol.append(max(0, gdh_final))  # Mínimo 0%
    
    # Calcular GDT, acidez y proteína en cada punto
    gdt_evol = [gdc + gdh for gdc, gdh in zip(gdc_evol, gdh_evol)]
    acidez_evol = [calcular_acidez_real(gdc, gdh, models.get('acidez')) 
                   for gdc, gdh in zip(gdc_evol, gdh_evol)]
    proteina_evol = [calcular_proteina_real(gdt, models.get('proteina')) 
                     for gdt in gdt_evol]
    
    return tiempos, gdc_evol, gdh_evol, gdt_evol, acidez_evol, proteina_evol

# Simular evolución
tiempos, gdc_evol, gdh_evol, gdt_evol, acidez_evol, proteina_evol = simular_evolucion_temporal(
    temperatura_alm, humedad_alm, gdc_inicial, gdh_inicial, 36  # Cambiar a 36 meses
)

# Gráfico de la ecuación base (sin ajustes)
tiempos_base = np.linspace(7, 36, 100)  # Rango de 7 a 36 meses
ecuacion_base = [0.0730 * t**2 - 0.7741 * t + 14.8443 for t in tiempos_base]

fig_ecuacion_base = go.Figure()

fig_ecuacion_base.add_trace(go.Scatter(
    x=tiempos_base,
    y=ecuacion_base,
    mode='lines',
    name='Ecuación Base',
    line=dict(color='#1A494C', width=3, dash='dash'),
    hovertemplate='Tiempo: %{x:.1f} meses<br>Daño: %{y:.2f}%<extra></extra>'
))

# Línea horizontal para el promedio de GDT de la empresa
fig_ecuacion_base.add_hline(y=38.16, line_dash="dash", line_color="purple", line_width=2,
                            annotation_text="Promedio Empresa (38.16%)", 
                            annotation_position="right",
                            annotation=dict(font=dict(color="purple", size=12)))

fig_ecuacion_base.update_layout(
    title="Ecuación Base del Daño del Grano (7-36 meses)",
    xaxis_title="Tiempo (meses)",
    yaxis_title="Daño del Grano (%)",
    xaxis=dict(range=[7, 36]),  # Forzar rango de 7 a 36
    height=400,
    showlegend=True,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig_ecuacion_base, use_container_width=True)

# Gráfico de evolución de acidez y proteína en el tiempo
fig_calidad_temporal = go.Figure()

# Acidez
fig_calidad_temporal.add_trace(go.Scatter(
    x=tiempos,
    y=acidez_evol,
    mode='lines+markers',
    name='Acidez (mg KOH/g)',
    line=dict(color='#FF6B6B', width=3),
    yaxis='y'
))

# Proteína
fig_calidad_temporal.add_trace(go.Scatter(
    x=tiempos,
    y=proteina_evol,
    mode='lines+markers',
    name='Proteína Soluble (%)',
    line=dict(color='#4ECDC4', width=3),
    yaxis='y2'
))

# Líneas de referencia
fig_calidad_temporal.add_hline(y=1.0, line_dash="dash", line_color="orange", 
                              annotation_text="Límite Acidez", yref="y")

fig_calidad_temporal.update_layout(
    title="Evolución de Calidad del Grano (7-36 meses)",
    xaxis_title="Tiempo (meses)",
    yaxis=dict(title="Acidez (mg KOH/g)", side="left"),
    yaxis2=dict(title="Proteína Soluble (%)", side="right", overlaying="y"),
    xaxis=dict(range=[7, 36]),  # Forzar rango de 7 a 36
    height=500,
    showlegend=True,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig_calidad_temporal, use_container_width=True)



# ===== RECOMENDACIONES ESPECÍFICAS =====
st.subheader("💡 Insights")


st.info(f"""
    **🔬 Análisis de Datos y Modelado:**
    
    **📊 Limitaciones del Modelo:**
    - No se logra predecir la degradación de los granos en el período inicial (0-7 meses) debido a datos insuficientes para modelar este comportamiento.
    
    **🔥 Factor Dominante - Daño Térmico:**
    - El **Daño Térmico (GDC)** es el factor dominante en la predicción del porcentaje de acidez del aceite, contribuyendo hasta un **61.5%** en la predicción del resultado.
    
    **⚠️ Nivel de Acidez Crítico:**
    - El valor promedio de acidez en las muestras analizadas fue de **2.76 mg KOH/g**, es decir, **0.76 unidades por encima** del umbral máximo sugerido por los estándares internacionales (2.0 mg KOH/g).
    
    **🔧 Variables Propuestas para Mejorar el Modelo:**
    
    **Proceso de Extrusión:**
    - `temp_proceso_max`: Temperatura máxima de proceso (°C)
    - `tiempo_extrusion`: Tiempo de extrusión (min)
    - `humedad_entrada`: Humedad de entrada (%)
    
    **Composición del Grano:**
    - `fibra`: Contenido de fibra (%)
    - `cenizas`: Composición estructural (%)
    
    **Condiciones de Almacenamiento:**
    - `tiempo_almac_bolsas`: Tiempo de almacenamiento en bolsas (días)
    
    
    **Variables Categóricas:**
    - `proveedor`: Origen/procedencia del grano

    **Otras:**
    - Acesoria con personas del negocio y expertos en los procesos operacionales para entender mejor el comportamiento de los datos.

    """)

# Recomendaciones por nivel de GDT
if gdt < 15:
    st.success("**Antes de cualquier acción basada en el modelo se debe mejorar/controlar y garantizar el manejo de la soya, luego tomar acciones (agregar efectos externos en pos del negocio)**")

    st.success("**✅ Mantener condiciones actuales** - Los granos están en excelente estado.")

elif gdt < 35:
    st.markdown("**Antes de cualquier acción basada en el modelo se debe mejorar/controlar y garantizar el manejo de la soya, luego tomar acciones (agregar efectos externos en pos del negocio)**")

    st.success("**⚠️ Implementar mejoras inmediatas** - Considerar rotación de inventario.")
else:
    st.success("**Antes de cualquier acción basada en el modelo se debe mejorar/controlar y garantizar el manejo de la soya, luego tomar acciones (agregar efectos externos en pos del negocio)**")

    st.error("**🚨 Acción urgente requerida** - Tener cuidado, el contenido nutricional de la muestra de granos no cumple los criterios mínimos para una buena dieta.")

# ===== INFORMACIÓN TÉCNICA =====
with st.expander("🔬 Información Técnica de los Modelos"):
    st.markdown("""
    **Modelos Utilizados:**
    
    **🧪 Modelo de Acidez:**
    - **Algoritmo:** Random Forest Regressor
    - **Features:** GDC (Daño Térmico), GDH (Daño por Hongos)
    - **Target:** Acidez del aceite (mg KOH/g)
    - **Rango normal:** 0.5 - 1.0 mg KOH/g
    
    **🥜 Modelo de Proteína:**
    - **Algoritmo:** Regresión Lineal
    - **Feature:** GDT (Daño Total = GDC + GDH)
    - **Target:** Proteína soluble (%)
    - **Rango normal:** 50% - 70%
    
    **📊 Interpretación de GDT:**
    - **< 15%:** Calidad excelente
    - **15-35%:** Calidad moderada
    - **> 35%:** Calidad crítica
    """) 

    # Footer
st.markdown("---")
st.markdown("*Soya Insights - Okuo-Analytics - Juan David Rincón *") 