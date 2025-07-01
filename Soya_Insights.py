import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Importar módulos de la nueva arquitectura
from src.config.constants import APP_CONFIG
from src.services import DataService, ModelService
from src.components import MetricsDisplay
from src.utils import Calculations

# Configuración de la página
st.set_page_config(**APP_CONFIG)

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

# Cargar modelos usando el servicio
acidez_model = ModelService.load_acidez_model()
proteina_model = ModelService.load_proteina_model()

# Calcular métricas usando los servicios
acidez_actual = ModelService.predict_acidez(gdc, gdh, acidez_model)
proteina_actual = ModelService.predict_proteina(gdt, proteina_model)
impacto_productos = Calculations.calcular_impacto_productos(gdt)

# ===== SECCIÓN PRINCIPAL: CALCULADORA Y RESULTADOS =====
st.markdown("---")
st.header("📊 Calculadora de Degradación y Resultados")

# Métricas principales en tarjetas usando componentes
col1, col2, col3, col4 = st.columns(4)

with col1:
    MetricsDisplay.display_gdt_metric(gdt)

with col2:
    MetricsDisplay.display_calidad_remanente_metric(gdt)

with col3:
    MetricsDisplay.display_acidez_metric(acidez_actual)

with col4:
    MetricsDisplay.display_proteina_metric(proteina_actual)

# Resumen textual de resultados usando componentes
st.subheader("📋 Resumen de Resultados")
MetricsDisplay.display_quality_summary(gdt, gdc, gdh, acidez_actual, proteina_actual)

# ===== GRÁFICOS DE EVOLUCIÓN =====
st.markdown("---")
st.header("📈 Análisis de Evolución Temporal")

# Parámetros de simulación
col1, col2 = st.columns(2)
temperatura_alm = 25
humedad_alm = 13

# Valores iniciales
gdc_inicial = 5.0
gdh_inicial = 2.0

# Crear datos para el gráfico
gdt_range = np.linspace(0, 100, 50)
acidez_range = [ModelService.predict_acidez(gdt_val * 0.7, gdt_val * 0.3, acidez_model) for gdt_val in gdt_range]
proteina_range = [ModelService.predict_proteina(gdt_val, proteina_model) for gdt_val in gdt_range]

# Gráfico de evolución
fig_evolucion = go.Figure()

# Acidez
fig_evolucion.add_trace(go.Scatter(
    x=gdt_range,
    y=acidez_range,
    mode='lines',
    name='Acidez (mg KOH/g)',
    line=dict(color='#FF6B6B', width=3),
    yaxis='y'
))

# Proteína
fig_evolucion.add_trace(go.Scatter(
    x=gdt_range,
    y=proteina_range,
    mode='lines',
    name='Proteína Soluble (%)',
    line=dict(color='#4ECDC4', width=3),
    yaxis='y2'
))

# Línea vertical para el promedio de GDT de la empresa
fig_evolucion.add_vline(x=38.16, line_dash="dash", line_color="purple", line_width=2,
                        annotation_text="Promedio GDT (38.16%)", 
                        annotation_position="top right",
                        annotation=dict(font=dict(color="purple", size=12)))

fig_evolucion.update_layout(
    title="Evolución de Acidez y Proteína vs GDT",
    xaxis_title="GDT - Daño Total (%)",
    yaxis=dict(title="Acidez (mg KOH/g)", side="left"),
    yaxis2=dict(title="Proteína Soluble (%)", side="right", overlaying="y"),
    height=500,
    showlegend=True,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig_evolucion, use_container_width=True)

# Simular evolución temporal usando utilidades
tiempos, gdc_evol, gdh_evol, gdt_evol = Calculations.simular_evolucion_temporal(
    temperatura_alm, humedad_alm, gdc_inicial, gdh_inicial, 36
)

# Calcular acidez y proteína en cada punto
acidez_evol = [ModelService.predict_acidez(gdc, gdh, acidez_model) for gdc, gdh in zip(gdc_evol, gdh_evol)]
proteina_evol = [ModelService.predict_proteina(gdt, proteina_model) for gdt in gdt_evol]

# Gráfico de la ecuación base (sin ajustes)
ecuacion_info = Calculations.obtener_ecuacion_base()
tiempos_base = np.linspace(7, 36, 100)  # Rango de 7 a 36 meses
ecuacion_base = [ecuacion_info['coeficientes'][0] * t**2 + ecuacion_info['coeficientes'][1] * t + ecuacion_info['coeficientes'][2] for t in tiempos_base]

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
                            annotation_text="Promedio GDT (38.16%)", 
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