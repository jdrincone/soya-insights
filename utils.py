import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg

# Paleta de colores personalizada
PALETTE = {
    "mean": "#1A494C",    # Verde oscuro
    "median": "#94AF92",  # Verde claro
    "max": "#E6ECD8",     # Verde muy claro
    "min": "#C9C9C9",     # Gris neutro
    "datos": "#94AF92",   # Verde claro
    "ajuste": "#1A494C",  # Verde oscuro
}

def load_and_prepare_data(file_path):
    """Carga y prepara los datos del archivo Excel."""
    df = pd.read_excel(file_path, skiprows=2)
    df.rename(columns={"Unnamed: 1": "Fecha"}, inplace=True)
    df = df.drop(columns=["Unnamed: 0"])
    
    # Filtrar columnas con menos de 12 valores nulos
    null_counts = df.isnull().sum().reset_index()
    null_counts.columns = ['column', 'null_count']
    cols_to_keep = null_counts[null_counts['null_count'] <= 12]['column'].tolist()
    
    return df[cols_to_keep]

def fit_quantile_regression(df, column, taus=[0.4, 0.5, 0.6]):
    """Ajusta modelos de regresión cuantílica para una columna específica."""
    y = pd.to_numeric(df[column], errors="coerce").dropna()
    x = df.loc[y.index, "Fecha"]
    
    results = []
    
    for tau in taus:
        # Modelo Lineal
        X_lin = sm.add_constant(x)
        res_lin = QuantReg(y, X_lin).fit(q=tau)
        results.append({
            "columna": column,
            "modelo": "Lineal (orden 1)",
            "tau": tau,
            "b0": res_lin.params.iloc[0],
            "b1": res_lin.params.iloc[1],
            "b2": np.nan,
            "pseudo_r2": res_lin.prsquared
        })
        
        # Modelo Cuadrático
        X_quad_df = pd.DataFrame({'x1': x, 'x2': x**2})
        X_quad = sm.add_constant(X_quad_df)
        res_quad = QuantReg(y, X_quad).fit(q=tau)
        results.append({
            "columna": column,
            "modelo": "Cuadrático (orden 2)",
            "tau": tau,
            "b0": res_quad.params.iloc[0],
            "b1": res_quad.params.iloc[1],
            "b2": res_quad.params.iloc[2],
            "pseudo_r2": res_quad.prsquared
        })
        
        # Modelo Logarítmico
        if (x > 0).all():
            X_log_series = np.log(x)
            X_log = sm.add_constant(X_log_series)
            res_log = QuantReg(y, X_log).fit(q=tau)
            results.append({
                "columna": column,
                "modelo": "Logarítmico",
                "tau": tau,
                "b0": res_log.params.iloc[0],
                "b1": res_log.params.iloc[1],
                "b2": np.nan,
                "pseudo_r2": res_log.prsquared
            })
    
    return pd.DataFrame(results)

def plot_best_fit(df, column, best_model_params):
    """Genera el gráfico del mejor ajuste para una columna específica."""
    x = df["Fecha"]
    y = df[column]
    
    x_fit = np.linspace(df["Fecha"].min(), df["Fecha"].max(), 100)
    b0, b1, b2 = best_model_params['b0'], best_model_params['b1'], best_model_params['b2']
    best_modelo = best_model_params['modelo']
    
    # Calcular y ajustado según el tipo de modelo
    if best_modelo == "Lineal (orden 1)":
        y_fit = b0 + b1 * x_fit
        y_fit_label = f'{b0:.2f} + {b1:.2f} * x'
    elif best_modelo == "Cuadrático (orden 2)":
        y_fit = b0 + b1 * x_fit + b2 * (x_fit**2)
        y_fit_label = f'{b0:.2f} + {b1:.2f} * x + {b2:.2f} * x^2'
    elif best_modelo == "Logarítmico":
        y_fit = b0 + b1 * np.log(x_fit)
        y_fit_label = f'{b0:.2f} + {b1:.2f} * ln(x)'
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Datos originales
    sns.scatterplot(
        ax=ax, x=x, y=y,
        color=PALETTE["datos"],
        alpha=1, s=100,
        label="Datos Originales"
    )
    
    # Línea de mejor ajuste
    sns.lineplot(
        ax=ax, x=x_fit, y=y_fit,
        color=PALETTE["ajuste"],
        linewidth=5,
        label=f'Mejor Ajuste ({best_modelo})\n y: {y_fit_label}\n pseudo_r2: {best_model_params["pseudo_r2"]:.3f}'
    )
    
    plt.xticks(rotation=45)
    ax.set_title(f"Mejor Modelo de Ajuste para '{column}'", fontsize=16)
    ax.set_xlabel("Fecha", fontsize=12)
    ax.set_ylabel(column, fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    return fig 