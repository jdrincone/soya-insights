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
st.header("🧮 Calculadora de Acidez")

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


# ===== SECCIÓN 1: EXPLICACIÓN DEL MODELO =====
st.header("🔬 Explicación del Modelo de Acidez")

# Explicación del modelo Random Forest
import json
try:
    with open("models/artifacts/model_info_acidez.json", "r") as f:
        model_info = json.load(f)
    st.markdown("""
    Este modelo utiliza un **Random Forest Regressor**, un conjunto de árboles de decisión entrenados sobre los datos históricos de acidez y daño del grano.
    
    - **Tipo de modelo:** Árboles de decisión en ensamble (Random Forest)
    - **Variables de entrada:**
        - Daño térmico del grano (`gdc_mean_in`)
        - Daño por hongos (`gdh_mean_in`)
    - **Variable objetivo:** Acidez del aceite (`pct_oil_acidez_mean`)
    - **Hiperparámetros principales:**
        - `n_estimators`: {n_estimators}
        - `max_depth`: {max_depth}
        - `min_samples_leaf`: {min_samples_leaf}
        - `min_samples_split`: {min_samples_split}
        - `max_features`: {max_features:.2f}
    
    El modelo aprende reglas a partir de los datos para predecir la acidez esperada según el daño observado. Puedes ver el árbol más representativo a continuación.
    """.format(
        n_estimators=model_info['best_params']['n_estimators'],
        max_depth=model_info['best_params']['max_depth'],
        min_samples_leaf=model_info['best_params']['min_samples_leaf'],
        min_samples_split=model_info['best_params']['min_samples_split'],
        max_features=model_info['best_params']['max_features']
    ))
except Exception:
    st.warning("No se pudo cargar la información del modelo.")

# Mostrar reglas del árbol más representativo
try:
    with open("models/artifacts/tree_rules_acidez.txt", "r") as f:
        tree_rules = f.read()
    with st.expander("Ver árbol más representativo del modelo Random Forest"):
        st.code(tree_rules, language="text")
except FileNotFoundError:
    st.warning("No se encontraron las reglas del árbol representativo. Ejecuta el entrenamiento para generarlas.")

# ===== SECCIÓN 2: GRÁFICOS DE ACIDEZ =====
st.header("📈 Análisis de Distribuciones de Datos")


st.markdown("""
### 

A continuación se muestran las distribuciones de las variables relacionadas con la acidez del aceite, 
basadas en datos reales de análisis de granos de soya:
""")

# Mostrar la imagen generada
try:
    # Leer el archivo HTML
    with open("models/plots/subplot_distribuciones_acidez_oil.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Mostrar el gráfico HTML interactivo
    st.components.v1.html(html_content, height=500)
    st.markdown("""
    **Interpretación de las Distribuciones:**
    
    - **GDC (Daño Térmico)**: Muestra la distribución del daño térmico en los granos
    - **GDH (Daño por Hongos)**: Representa la distribución del daño causado por hongos
    - **Acidez del Aceite (%)**: Distribución de los valores de acidez medidos en el aceite extraído
   
    """)
    
except FileNotFoundError:
    st.warning("⚠️ No se encontró el archivo HTML de distribuciones. Ejecute el script `models/acidez_oil.py` para generarlo.")
    st.code("source xgboost_env/bin/activate && python models/acidez_oil.py")


       


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
st.header("🧪 Entendimiento de los Resultados en Base a la Literatura")

st.subheader("📚 Resumen Bibliográfico")
st.markdown('''
La **acidez del aceite de soya** es un parámetro clave para evaluar su calidad, estabilidad y aptitud para consumo humano y animal. Numerosas investigaciones científicas han evidenciado que:

- El **daño en el grano de soya**, ya sea **físico, térmico o microbiológico**, acelera la **hidrólisis de triglicéridos**, lo cual libera **ácidos grasos libres** que incrementan la acidez.
- La acidez elevada se asocia con **oxidación avanzada**, **rancidez** y pérdida del valor comercial del aceite.
- Procesos como el **secado excesivo**, la **extrusión agresiva**, o **almacenamiento prolongado en malas condiciones** pueden aumentar significativamente este parámetro.
- Rangos aceptables de acidez para aceites vegetales comestibles, según estándares como el **Codex Alimentarius**, están entre **0.1 y 1.0 mg KOH/g**.
- Niveles por encima de **2.0 mg KOH/g** son considerados señales de **degradación severa** o **contaminación microbiológica**.

📖 **Referencias sugeridas:**
- CODEX STAN 210-1999 (Codex Alimentarius – Normas para aceites vegetales)
- R. Przybylski et al., "Quality of Soybean Oil: A Review", *Journal of Food Lipids*, 2003.
- J. Rios et al., "Efecto del Almacenamiento y la Humedad sobre la Calidad del Aceite de Soya", *Revista Ciencias Agrícolas*, 2017.
''')

st.subheader("📈 Resultados del Modelo")
st.markdown(f'''
Se evaluó una base de datos experimental con las siguientes variables:

- **GDC**: Daño térmico del grano (en %).
- **GDH**: Daño fúngico (por hongos) del grano (en %).
- **Acidez**: Medida en **mg KOH/g**.

El análisis mostró una **correlación positiva consistente** entre los niveles de daño y el valor de acidez del aceite: a mayor daño, mayor es la acidez observada.

📌 **Hallazgo crítico**:
> El valor promedio de acidez en las muestras analizadas fue de **2.76 mg KOH/g**, es decir, **0.76 unidades por encima del umbral máximo sugerido por los estándares internacionales** (2.0 mg KOH/g).

Este resultado evidencia un **nivel significativo de deterioro** en la calidad del aceite producido actualmente.
''')

st.subheader("🔎 Interpretación Técnica y Recomendaciones")
st.markdown('''
Si bien es posible construir **modelos estadísticos o de machine learning más avanzados** para predecir la acidez, estos **no resuelven el problema de fondo**. El modelo puede alertar o estimar la acidez, pero:

> **Una predicción más precisa no mejora la calidad del producto.**

Por lo tanto, se requiere una **intervención directa en la calidad de la materia prima o en las condiciones del proceso**, tales como:

- 🟩 **Seleccionar soya de mejor calidad**: Menor contenido de humedad, grano más entero, mejor manejado en cosecha.
- 🌡️ **Mejorar el control de temperatura y tiempos de extrusión**.
- 🦠 **Mitigar la carga microbiana** en almacenamiento usando agentes antifúngicos permitidos o secado más efectivo.
- 🛢️ **Optimizar tiempos de almacenamiento del aceite** antes del análisis.

📌 *Conclusión: mejorar el modelo es útil como herramienta de monitoreo, pero **la solución real está en cambiar las condiciones de entrada y del proceso productivo.***
''')

# Footer
st.markdown("---")
st.markdown("*Modelo de Acidez del Aceite - Soya Insights - Okuo-Analytics - Juan David Rincón *") 