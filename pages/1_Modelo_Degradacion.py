import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from utils import load_and_prepare_data, fit_quantile_regression, plot_best_fit, PALETTE
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
from sklearn.metrics import r2_score

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Regresión Cuantílica",
    page_icon="📊",
    layout="wide"
)

st.title("Análisis Degradación de la Calidad del Grano en función de los meses de almacenamiento")

with st.expander("ℹ️ Descripción del Proceso"):
    st.markdown("""
    1. **Carga de Datos**: Se cargan los datos desde el archivo 'Seguimiento de datos.xlsx'.
    2. **Filtrado Muestras Válidas**: Se filtran muestras con más de 4 puntos.
    3. **Filtrado de Puntos Válidos**: Se filtran los puntos que cumplen la condición de función monótona creciente (la media debe ser mayor o igual que el punto anterior).
    4. **Ajuste de Modelos**: Se ajustan dos modelos a los puntos válidos:
       - **Modelo Lineal**: Se ajusta una línea recta a los puntos.
       - **Modelo Cuadrático**: Se ajusta una ecuación cuadrática a los puntos.
    5. **Visualización de Resultados**: Se muestran los puntos válidos junto con los ajustes lineal y cuadrático, incluyendo las ecuaciones y los valores de R².
    6. **Gráfica de la Media**: Se grafica la media vs Fecha, mostrando solo los puntos válidos y el ajuste lineal entre ellos.
    """)

try:
    df = load_and_prepare_data("data/Seguimiento de datos.xlsx")
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    numeric_cols_no_fecha = [col for col in numeric_cols if col != "Fecha"]
    st.sidebar.header("Parámetros de Análisis")
    selected_column = st.sidebar.selectbox(
        "Seleccione la columna a analizar:",
        numeric_cols_no_fecha
    )

    with st.expander("📋 Datos Raw"):
        st.dataframe(df)

    # Ajustar modelos y encontrar el mejor
    results = fit_quantile_regression(df, selected_column, taus=[0.5])
    best_model = results.loc[results.groupby('columna')['pseudo_r2'].idxmax()]

    with st.expander("📊 Comparación de Modelos"):
        st.dataframe(results.sort_values('pseudo_r2', ascending=False))

    # Graficar el mejor ajuste
    st.subheader(f"Mejor ajuste para {selected_column}")
    fig = plot_best_fit(df, selected_column, best_model.iloc[0])
    st.pyplot(fig)

    # Calculadora para la columna seleccionada
    with st.expander(f"🧮 Calculadora de Predicción - {selected_column}"):
        mes_prediccion_columna = st.number_input(
            f"Ingrese el mes para predecir el valor de {selected_column}:",
            min_value=0,
            max_value=50,
            value=10,
            step=1,
            help="Ingrese el mes (ej: 8.5 para mes 8.5)",
            key="mes_columna"
        )
        calcular_col = st.button("Calcular Predicción", key="btn_columna")

    if 'calcular_col' not in st.session_state:
        st.session_state['calcular_col'] = False
    if calcular_col:
        st.session_state['calcular_col'] = True
    if st.session_state['calcular_col']:
        b0 = best_model.iloc[0]['b0']
        b1 = best_model.iloc[0]['b1']
        b2 = best_model.iloc[0]['b2']
        modelo = best_model.iloc[0]['modelo']
        pseudo_r2 = best_model.iloc[0]['pseudo_r2']
        if modelo == "Lineal (orden 1)":
            prediccion = b0 + b1 * mes_prediccion_columna
            ecuacion = f"y = {b0:.4f} + {b1:.4f}x"
        elif modelo == "Cuadrático (orden 2)":
            prediccion = b0 + b1 * mes_prediccion_columna + b2 * (mes_prediccion_columna**2)
            ecuacion = f"y = {b0:.4f} + {b1:.4f}x + {b2:.4f}x²"
        elif modelo == "Logarítmico":
            prediccion = b0 + b1 * np.log(mes_prediccion_columna)
            ecuacion = f"y = {b0:.4f} + {b1:.4f}ln(x)"
        st.metric(
            label=f"Predicción para {selected_column}",
            value=f"{prediccion:.2f}",
            delta=f"R² = {pseudo_r2:.3f}"
        )
        st.markdown("**Detalles del modelo:**")
        st.write(f"**Mejor Modelo:** {modelo}")
        st.write(f"**Ecuación:** {ecuacion}")
        st.write(f"**Pseudo R²:** {pseudo_r2:.4f}")

    # Calcular la media y filtrar puntos que no cumplen la condición de función monótona creciente
    df["mean"] = df.drop(columns=["Fecha"]).mean(axis=1)
    df_sorted = df.sort_values("Fecha")
    df_sorted["valid"] = df_sorted["mean"].diff().fillna(0) >= 0
    df_valid = df_sorted[df_sorted["valid"]]

    st.subheader("Ajuste de la media para todas las muestras (a partir del mes 8)")
    fig_mean, ax_mean = plt.subplots(figsize=(12, 7))
    df_valid_filtered = df_valid[df_valid["Fecha"] >= 7.5]
    X = df_valid_filtered["Fecha"].values.reshape(-1, 1)
    y = df_valid_filtered["mean"].values
    mask = ~np.isnan(y)
    X = X[mask]
    y = y[mask]
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_linear = linear_model.predict(X)
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    quadratic_model = LinearRegression()
    quadratic_model.fit(X_poly, y)
    y_quadratic = quadratic_model.predict(X_poly)
    r2_linear = r2_score(y, y_linear)
    r2_quadratic = r2_score(y, y_quadratic)
    fig_fits, ax_fits = plt.subplots(figsize=(12, 7))
    sns.scatterplot(ax=ax_fits, x=df_valid_filtered["Fecha"][mask], y=df_valid_filtered["mean"][mask], color=PALETTE["mean"], label="Media (puntos válidos)")
    ax_fits.plot(df_valid_filtered["Fecha"][mask], y_linear, color=PALETTE["ajuste"], label=f'Línea Recta: y = {linear_model.coef_[0]:.2f}x + {linear_model.intercept_:.2f} (R² = {r2_linear:.3f})')
    ax_fits.plot(df_valid_filtered["Fecha"][mask], y_quadratic, color=PALETTE["median"], label=f'Cuadrática: y = {quadratic_model.coef_[2]:.2f}x² + {quadratic_model.coef_[1]:.2f}x + {quadratic_model.intercept_:.2f} (R² = {r2_quadratic:.3f})')
    ax_fits.set_title("Ajuste Lineal y Cuadrático a la Media vs Fecha", fontsize=16)
    ax_fits.set_xlabel("Fecha", fontsize=12)
    ax_fits.set_ylabel("Media", fontsize=12)
    ax_fits.legend(fontsize=11)
    ax_fits.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig_fits)

    with st.expander("📝 Recomendaciones de Muestreado y adquisición de datos"):
        st.markdown("""
        - Se recomienda que el muestreo se realice cada 15 días calendario, tondando días reales.
        - Todas las muestras deben de estar almacenadas en las mismas condiciones de temperatura y humedad.
        """)

    # Calculadora de predicción de la media
    with st.expander("🧮 Calculadora de Predicción de la Media"):
        mes_prediccion = st.number_input(
            "Ingrese el mes para predecir el valor medio:",
            min_value=0,
            max_value=50,
            value=18,
            step=1,
            help="Ingrese el mes (ej: 8.5 para mes 8.5)",
            key="mes_media"
        )
        calcular_media = st.button("Calcular Predicción", key="btn_media")

    if 'calcular_media' not in st.session_state:
        st.session_state['calcular_media'] = False
    if calcular_media:
        st.session_state['calcular_media'] = True
    if st.session_state['calcular_media']:
        prediccion_lineal = linear_model.coef_[0] * mes_prediccion + linear_model.intercept_
        prediccion_cuadratica = quadratic_model.coef_[2] * (mes_prediccion**2) + quadratic_model.coef_[1] * mes_prediccion + quadratic_model.intercept_
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Predicción Lineal",
                value=f"{prediccion_lineal:.2f}",
                delta=f"R² = {r2_linear:.3f}"
            )
        with col2:
            st.metric(
                label="Predicción Cuadrática", 
                value=f"{prediccion_cuadratica:.2f}",
                delta=f"R² = {r2_quadratic:.3f}"
            )
        st.markdown("**Ecuaciones Utilizadas:**")
        st.write(f"**Ecuación Lineal:** y = {linear_model.coef_[0]:.4f}x + {linear_model.intercept_:.4f}")
        st.write(f"**Ecuación Cuadrática:** y = {quadratic_model.coef_[2]:.4f}x² + {quadratic_model.coef_[1]:.4f}x + {quadratic_model.intercept_:.4f}")

except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.info("Asegúrese de que el archivo 'Seguimiento de datos.xlsx' está en la carpeta 'data/'") 