import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import os
import joblib
import json

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",      # rgb(26,73,76)
    "verde_claro": "#94AF92",       # rgb(148,175,146)
    "verde_muy_claro": "#E6ECD8",   # rgb(230,236,216)
    "gris_neutro": "#C9C9C9"        # rgb(201,201,201)
}

@st.cache_resource
def load_acidez_model():
    """Cargar el modelo de acidez"""
    try:
        model = joblib.load("models/artifacts/random_forest_acidez.pkl")
        with open("models/artifacts/metrics_acidez.json", "r") as f:
            metrics = json.load(f)
        with open("models/artifacts/model_info_acidez.json", "r") as f:
            model_info = json.load(f)
        return model, metrics, model_info
    except Exception as e:
        st.error(f"Error cargando modelo: {e}")
        return None, None, None

st.set_page_config(
    page_title="Modelo de Acidez - Soya Insights",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Modelo de Cambio de Acidez en Función del Daño del Grano")
st.markdown("---")

# ===== CALCULADORA PRÁCTICA =====
st.header("🧮 Calculadora de Acidez - Análisis Rápido")

# Cargar modelo ML
model, metrics, model_info = load_acidez_model()

if model is not None:
    # Obtener valor medio de acidez de los datos
    df_acidez_data = pd.read_csv("models/data/data_acidez.csv")
    acidez_media = df_acidez_data['pct_oil_acidez_mean'].mean()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Ingrese los Valores de Daño")
        
        # Inputs para GDC y GDH
        gdc_input = st.number_input(
            "GDC - Daño Térmico (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=0.1,
            help="Ingrese el porcentaje de daño térmico observado"
        )
        
        gdh_input = st.number_input(
            "GDH - Daño por Hongos (%)",
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=0.1,
            help="Ingrese el porcentaje de daño por hongos observado"
        )
        
        # Botón para calcular
        if st.button("🔍 Calcular Acidez Esperada", type="primary"):
            # Hacer predicción
            data_input = pd.DataFrame({
                'gdc_mean_in': [gdc_input],
                'gdh_mean_in': [gdh_input]
            })
            
            acidez_predicha = model.predict(data_input)[0]
            diferencia_media = acidez_predicha - acidez_media
            porcentaje_cambio = (diferencia_media / acidez_media) * 100
            
            # Guardar en session state para mostrar en la columna derecha
            st.session_state.acidez_resultado = {
                'predicha': acidez_predicha,
                'media': acidez_media,
                'diferencia': diferencia_media,
                'porcentaje': porcentaje_cambio,
                'gdc': gdc_input,
                'gdh': gdh_input
            }
    
    with col2:
        st.subheader("📈 Resultado del Análisis")
        
        if 'acidez_resultado' in st.session_state:
            resultado = st.session_state.acidez_resultado
            
            # Métrica principal
            st.metric(
                label="Acidez Esperada",
                value=f"{resultado['predicha']:.2f} mg KOH/g",
                delta=f"{resultado['diferencia']:+.2f} mg KOH/g"
            )
            
            # Comparación con media
            st.markdown("**Comparación con Valor Medio:**")
            st.markdown(f"- **Valor Medio:** {resultado['media']:.2f} mg KOH/g")
            st.markdown(f"- **Diferencia:** {resultado['diferencia']:+.2f} mg KOH/g")
            st.markdown(f"- **Cambio:** {resultado['porcentaje']:+.1f}%")
            
            # Interpretación
            st.markdown("**Interpretación:**")
            if resultado['diferencia'] > 0:
                st.warning(f"⚠️ **Por encima del promedio** (+{resultado['diferencia']:.2f} mg KOH/g)")
            elif resultado['diferencia'] < 0:
                st.success(f"✅ **Por debajo del promedio** ({resultado['diferencia']:.2f} mg KOH/g)")
            else:
                st.info("ℹ️ **En el promedio**")
            
            # Calidad según acidez
            if resultado['predicha'] < 1.0:
                st.success("🟢 **Calidad Excelente**")
            elif resultado['predicha'] < 2.0:
                st.warning("🟡 **Calidad Buena**")
            else:
                st.error("🔴 **Calidad Crítica**")
            
            # Recomendación
            st.markdown("**Recomendación:**")
            if resultado['predicha'] > 3.0:
                st.error("🔴 Revisar condiciones de almacenamiento y procesamiento")
            elif resultado['predicha'] > 2.0:
                st.warning("🟡 Monitorear parámetros de proceso")
            else:
                st.success("🟢 Condiciones óptimas mantenidas")
        
        else:
            st.info("💡 Ingrese valores y haga clic en 'Calcular' para ver el análisis")
    
    # Mostrar información del modelo
    with st.expander("ℹ️ Información del Modelo"):
        st.markdown(f"""
        **Modelo Random Forest:**
        - **Precisión (R²):** {metrics['test']['r2']:.1%}
        - **Error promedio:** {metrics['test']['mae']:.3f} mg KOH/g
        - **Valor medio histórico:** {acidez_media:.2f} mg KOH/g
        
        **Importancia de Variables:**
        - **GDC (Térmico):** {model_info['feature_importance']['gdc_mean_in']:.1%}
        - **GDH (Hongos):** {model_info['feature_importance']['gdh_mean_in']:.1%}
        """)

else:
    st.error("❌ No se pudo cargar el modelo. Verifique que el archivo `models/artifacts/random_forest_acidez.pkl` existe.")

# Mostrar análisis detallado si hay resultado (fuera de las columnas)
if 'acidez_resultado' in st.session_state:
    st.markdown("---")
    st.header("📊 Análisis Detallado")
    
    resultado = st.session_state.acidez_resultado
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Posición en la Distribución")
        
        # Crear gráfico de distribución con el punto actual
        fig_dist = go.Figure()
        
        # Histograma de datos históricos
        fig_dist.add_trace(go.Histogram(
            x=df_acidez_data['pct_oil_acidez_mean'],
            name='Datos Históricos',
            marker_color=CORPORATE_COLORS["verde_claro"],
            opacity=0.7,
            nbinsx=30
        ))
        
        # Línea de media
        fig_dist.add_vline(
            x=resultado['media'],
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Media: {resultado['media']:.2f}",
            annotation_position="top right"
        )
        
        # Punto actual
        fig_dist.add_vline(
            x=resultado['predicha'],
            line_dash="solid",
            line_color="red",
            line_width=3,
            annotation_text=f"Predicción: {resultado['predicha']:.2f}",
            annotation_position="top left"
        )
        
        fig_dist.update_layout(
            title="Distribución Histórica de Acidez",
            xaxis_title="Acidez (mg KOH/g)",
            yaxis_title="Frecuencia",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_dist, use_container_width=True, key="dist_hist")
    
    with col2:
        st.subheader("📈 Comparación de Variables")
        
        # Gráfico de radar para comparar GDC y GDH
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[resultado['gdc'], resultado['gdh']],
            theta=['GDC (Térmico)', 'GDH (Hongos)'],
            fill='toself',
            name='Valores Actuales',
            line_color=CORPORATE_COLORS["verde_oscuro"]
        ))
        
        # Valores medios históricos
        gdc_medio = df_acidez_data['gdc_mean_in'].mean()
        gdh_medio = df_acidez_data['gdh_mean_in'].mean()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[gdc_medio, gdh_medio],
            theta=['GDC (Térmico)', 'GDH (Hongos)'],
            fill='toself',
            name='Valores Medios',
            line_color=CORPORATE_COLORS["gris_neutro"]
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(resultado['gdc'], resultado['gdh'], gdc_medio, gdh_medio) * 1.2]
                )),
            showlegend=True,
            title="Comparación con Valores Medios",
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True, key="radar_comp")
    
    # Tabla de resumen
    st.subheader("📋 Resumen del Análisis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Acidez Predicha",
            f"{resultado['predicha']:.2f} mg KOH/g",
            f"{resultado['diferencia']:+.2f}"
        )
    
    with col2:
        st.metric(
            "Desviación",
            f"{resultado['porcentaje']:+.1f}%",
            "vs Media"
        )
    
    with col3:
        # Calcular percentil
        percentil = (df_acidez_data['pct_oil_acidez_mean'] < resultado['predicha']).mean() * 100
        st.metric(
            "Percentil",
            f"{percentil:.0f}%",
            "de la distribución"
        )
    
    with col4:
        # Calcular riesgo
        if resultado['predicha'] < 1.0:
            riesgo = "Bajo"
        elif resultado['predicha'] < 2.0:
            riesgo = "Moderado"
        else:
            riesgo = "Alto"
        
        st.metric(
            "Nivel de Riesgo",
            riesgo,
            "Calidad"
        )

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


st.markdown("""
### Análisis de Distribuciones de Datos

A continuación se muestran las distribuciones de las variables relacionadas con la acidez del aceite, 
basadas en datos reales de análisis de granos de soya:
""")

# Mostrar la imagen generada
try:
    # Leer el archivo HTML
    with open("models/plots/subplot_distribuciones_acidez_oil.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Mostrar el gráfico HTML interactivo
    st.components.v1.html(html_content, height=600)
    
    st.markdown("""
    **Interpretación de las Distribuciones:**
    
    - **GDC (Daño Térmico)**: Muestra la distribución del daño térmico en los granos
    - **GDH (Daño por Hongos)**: Representa la distribución del daño causado por hongos
    - **Acidez del Aceite (%)**: Distribución de los valores de acidez medidos en el aceite extraído
   
    """)
    
except FileNotFoundError:
    st.warning("⚠️ No se encontró el archivo HTML de distribuciones. Ejecute el script `models/acidez_oil.py` para generarlo.")
    st.code("source xgboost_env/bin/activate && python models/acidez_oil.py")


       
        
  
# ===== SECCIÓN 6: TABLA DE RESULTADOS =====
st.header("📋 Resultados Detallados")

# Crear tabla con puntos clave de degradación
puntos_degradacion = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
resultados_acidez = []
for deg in puntos_degradacion:
    acidez = modelo_acidez_cientifico(deg/100, acidez_base, factor_acidez, temperatura_acidez, factor_temp_acidez)
    incremento = acidez - acidez_base
    if acidez < 1.0:
        calidad = "Calidad Excelente (<1.0 mg KOH/g)"
        color = "🟢"
    elif 1.0 <= acidez < 2.0:
        calidad = "Calidad Buena (1.0-2.0 mg KOH/g)"
        color = "🟡"
    else:
        calidad = "Calidad Crítica (>2.0 mg KOH/g)"
        color = "🔴"
    resultados_acidez.append({
        'Degradación (%)': f"{deg:.0f}%",
        'Acidez (mg KOH/g)': f"{acidez:.2f}",
        'Incremento (mg KOH/g)': f"+{incremento:.2f}",
        'Calidad': f"{color} {calidad}"
    })
df_resultados = pd.DataFrame(resultados_acidez)
st.dataframe(df_resultados, use_container_width=True)

# ===== SECCIÓN 6.5: ANÁLISIS DEL MODELO ML =====
if model is not None:
    st.header("🔍 Análisis del Modelo de Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Predicciones vs Valores Reales")
        try:
            components.html(open("models/plots/predicciones_vs_reales_acidez.html").read(), height=400)
        except FileNotFoundError:
            st.warning("Gráfico de predicciones no encontrado")
    
    with col2:
        st.subheader("📈 Análisis de Residuos")
        try:
            components.html(open("models/plots/residuos_acidez.html").read(), height=400)
        except FileNotFoundError:
            st.warning("Gráfico de residuos no encontrado")
    
    # Gráficos SHAP
    st.subheader("🎯 Análisis SHAP - Summary Plot")
    try:
        st.image("models/artifacts/shap_importance_acidez.png", caption="SHAP Summary Plot - Acidez del Aceite")
    except FileNotFoundError:
        st.warning("Gráfico SHAP summary no encontrado")

# ===== SECCIÓN 7: ANÁLISIS Y ARGUMENTACIÓN CIENTÍFICA =====
st.header("🧪 Análisis del Comportamiento de la Acidez del Aceite en Función del Daño del Grano de Soya")

st.subheader("📚 Resumen desde la literatura")
st.markdown('''
La acidez del aceite de soya es un indicador crítico de la calidad y estabilidad del producto. Diversos estudios han demostrado que:

- El **daño del grano de soya** (físico o térmico) provoca **hidrólisis de triglicéridos** y liberación de ácidos grasos libres.
- La **acidez del aceite** se correlaciona directamente con la **oxidación y rancidez**, afectando la vida útil del producto.
- Procesos como secado, extrusión o almacenamiento inadecuado pueden generar **incrementos significativos** en la acidez.
- Rangos de acidez considerados óptimos en aceite de soya están típicamente entre **0.1 y 1.0 mg KOH/g**, según estándares internacionales.
- Valores superiores a **2.0 mg KOH/g** indican **deterioro avanzado** y pueden comprometer la calidad del aceite.
''')

st.subheader("📈 Resultados del modelo")
st.markdown(f'''
Se analizó una base de datos experimental con mediciones de:

- **GDC**: Daño térmico del grano (porcentaje).
- **GDH**: Daño por hongos del grano (porcentaje).
- **Acidez**: Acidez del aceite medida en mg KOH/g.

El modelo científico implementado considera múltiples factores:

**A(D) = A₀ + ΔA(D) × Fₜ**

Donde:
- **A₀**: Acidez base = {acidez_base} mg KOH/g
- **ΔA(D)**: Incremento por degradación = D × {factor_acidez} × Fₜ
- **Fₜ**: Factor de temperatura = 1 + (T - 20°C) × {factor_temp_acidez} × 0.01
- **T**: Temperatura actual = {temperatura_acidez}°C

Este modelo permite **anticipar el incremento de acidez** basado en el nivel de daño observado y las condiciones térmicas.
''')

st.subheader("🔎 Interpretación técnica")
st.markdown('''
- Existe una **relación positiva** entre el daño del grano y la acidez del aceite: a mayor daño, mayor acidez.
- Esto es consistente con procesos de **hidrólisis enzimática** y **oxidación lipídica** acelerados por el daño.
- El modelo permite establecer **umbrales de calidad** para el aceite según el nivel de daño del grano.
- La **temperatura** actúa como factor multiplicador, acelerando los procesos de deterioro.
''')

st.subheader("🧮 Modelo Avanzado Propuesto")

st.markdown(r'''
Un modelo avanzado para predecir la acidez del aceite puede incorporar múltiples variables críticas del proceso y la materia prima:

$$
\begin{align*}
Acidez =\ & \beta_0 \\
   & + \beta_1 \times GDC \\
   & + \beta_2 \times GDH \\
   & + \beta_3 \times temp\_proceso\_max \\
   & + \beta_4 \times tiempo\_almacenamiento \\
   & + \beta_5 \times humedad\_grano \\
   & + \beta_6 \times actividad\_agua \\
   & + \beta_7 \times contenido\_lipidos \\
   & + \beta_8 \times peroxidos \\
   & + \beta_9 \times indice\_acidez\_inicial \\
   & + \gamma_1 \times variedad \\
   & + \gamma_2 \times proveedor \\
   & + \varepsilon
\end{align*}
$$

**Donde:**
- $Acidez$: Acidez del aceite (mg KOH/g)
- $GDC$: Daño térmico del grano (%)
- $GDH$: Daño por hongos del grano (%)
- $temp\_proceso\_max$: Temperatura máxima de proceso (°C)
- $tiempo\_almacenamiento$: Tiempo de almacenamiento (días)
- $humedad\_grano$: Humedad del grano (%)
- $actividad\_agua$: Actividad de agua (aw)
- $contenido\_lipidos$: Contenido de lípidos (%)
- $peroxidos$: Índice de peróxidos (meq/kg)
- $indice\_acidez\_inicial$: Acidez inicial del grano (mg KOH/g)
- $variedad$, $proveedor$: Variables categóricas
- $\beta_0...\beta_9, \gamma_1, \gamma_2$: Coeficientes a estimar
- $\varepsilon$: Término de error aleatorio

Este modelo permitiría anticipar la calidad del aceite considerando no solo el daño del grano, sino también las condiciones de almacenamiento, composición lipídica y factores ambientales.
''') 

st.subheader("✅ Conclusión")
st.markdown(f'''
> El análisis evidencia una **relación positiva significativa** entre el daño del grano (GDC/GDH) y la acidez del aceite. Este comportamiento sugiere que a mayor daño —probablemente por procesos térmicos, físicos o microbiológicos— se incrementa la acidez del aceite, afectando su calidad y estabilidad.
>
> El modelo científico implementado:
>
> **A(D) = {acidez_base} + ΔA(D) × Fₜ**, permite cuantificar este incremento bajo condiciones controladas de temperatura y proceso.
>
> Esta herramienta:
> - Puede ser usada como **indicador de control de calidad en planta**, al vincular condiciones de materia prima y proceso con la acidez del aceite.
> - Ayuda a **identificar desviaciones críticas** que afectan la calidad del aceite de soya.
> - Permite establecer **umbrales de aceptación** basados en estándares internacionales.
>
> Sin embargo, el modelo actual **no captura todas las fuentes de variabilidad**, como humedad, tiempo de almacenamiento, composición lipídica o actividad enzimática residual. Estas variables pueden tener efectos significativos en la acidez del aceite.
>
> Se recomienda avanzar hacia un **modelo multivariable integrado**, que permita ajustar por estos factores y mejorar tanto la capacidad predictiva como la interpretación técnica del proceso de deterioro del aceite.
''')

# Footer
st.markdown("---")
st.markdown("*Modelo de Acidez del Aceite - Soya Insights - Okuo-Analytics - Juan David Rincón *") 