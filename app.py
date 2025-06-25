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
- **📉 Modelo de Degradación**: Detalle científico del modelo de degradación del grano
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
        df_protein = pd.read_csv("models/data/datos_gdt_protein.csv")
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

with col3:
    st.metric(
        label="Acidez (mg KOH/g)",
        value=f"{acidez_actual:.2f}",
        delta=f"+{acidez_actual - 0.5:.2f}" if acidez_actual > 0.5 else None
    )

with col4:
    st.metric(
        label="Proteína Soluble (%)",
        value=f"{proteina_actual:.1f}%",
        delta=f"-{70.0 - proteina_actual:.1f}%" if proteina_actual < 70.0 else None
    )

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
elif gdt < 35:
    st.warning(f"""
    **⚠️ Calidad Moderada**
    
    Con un daño total (GDT) de {gdt:.1f}%, se observa degradación moderada:
    - **Daño térmico (GDC):** {gdc:.1f}% (requiere monitoreo)
    - **Daño por hongos (GDH):** {gdh:.1f}% (aumentando)
    - **Acidez aumentando:** {acidez_actual:.2f} mg KOH/g (requiere atención)
    - **Proteína reducida:** {proteina_actual:.1f}% (pérdida de {70.0 - proteina_actual:.1f}%)
    
    **Recomendación:** Optimizar condiciones de almacenamiento y considerar rotación.
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
fig.add_hline(y=50.0, line_dash="dash", line_color="red", 
              annotation_text="Límite Proteína", yref="y2")

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

# ===== RECOMENDACIONES ESPECÍFICAS =====
st.subheader("💡 Recomendaciones Específicas")

if gdc > gdh:
    st.info(f"""
    **🔥 Daño Térmico Dominante**
    - El daño térmico ({gdc:.1f}%) es mayor que el daño por hongos ({gdh:.1f}%)
    - **Causas probables:** Exposición prolongada a altas temperaturas, secado excesivo
    - **Acciones recomendadas:**
        - Revisar temperatura de almacenamiento (mantener < 25°C)
        - Optimizar proceso de secado
        - Implementar sistema de ventilación
    """)
else:
    st.info(f"""
    **🍄 Daño por Hongos Dominante**
    - El daño por hongos ({gdh:.1f}%) es mayor que el daño térmico ({gdc:.1f}%)
    - **Causas probables:** Humedad elevada, condiciones de almacenamiento inadecuadas
    - **Acciones recomendadas:**
        - Controlar humedad relativa (< 65%)
        - Implementar fungicidas preventivos
        - Mejorar ventilación del almacén
    """)

# Recomendaciones por nivel de GDT
if gdt < 15:
    st.success("**✅ Mantener condiciones actuales** - Los granos están en excelente estado.")
elif gdt < 35:
    st.warning("**⚠️ Implementar mejoras inmediatas** - Considerar rotación de inventario.")
else:
    st.error("**🚨 Acción urgente requerida** - Procesar o vender inmediatamente.")

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