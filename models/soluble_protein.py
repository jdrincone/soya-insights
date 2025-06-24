# Reejecutar el modelo solo con datos sin outliers y usarlo para graficar con stats correctos

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats
from math import sqrt
import plotly.express as px
import plotly.graph_objects as go
import os

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",      # rgb(26,73,76)
    "verde_claro": "#94AF92",       # rgb(148,175,146)
    "verde_muy_claro": "#E6ECD8",   # rgb(230,236,216)
    "gris_neutro": "#C9C9C9"        # rgb(201,201,201)
}

# Paleta personalizada usando colores corporativos
PALETTE = [CORPORATE_COLORS["verde_oscuro"], CORPORATE_COLORS["verde_claro"], 
           CORPORATE_COLORS["verde_muy_claro"], CORPORATE_COLORS["gris_neutro"]]

# Función que grafica y usa el modelo entrenado para mostrar stats reales
def scatter_reg_final(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: str,
    model: LinearRegression,
    palette: list[str] = PALETTE,
    point_size: int = 100,
):
    df_plot = df.copy()
    
    # Crear figura con Plotly
    fig = go.Figure()
    
    # Colores por grupo
    groups = sorted(df_plot[hue].unique())
    color_map = {g: palette[i % len(palette)] for i, g in enumerate(groups)}
    
    for g in groups:
        sub = df_plot[df_plot[hue] == g]
        fig.add_trace(go.Scatter(
            x=sub[x],
            y=sub[y],
            mode='markers',
            name=str(g),
            marker=dict(
                size=point_size/10,  # Ajustar tamaño para Plotly
                opacity=0.8,
                color=color_map[g],
                line=dict(color=CORPORATE_COLORS["verde_oscuro"], width=0.6)
            )
        ))
    
    # Línea del modelo ajustado (solo con datos limpios)
    x_range = np.linspace(df_plot[x].min(), df_plot[x].max(), 200).reshape(-1, 1)
    y_line = model.predict(x_range)
    fig.add_trace(go.Scatter(
        x=x_range.flatten(),
        y=y_line,
        mode='lines',
        name="Fitted Regression",
        line=dict(color=CORPORATE_COLORS["verde_oscuro"], width=2.2, dash='dash')
    ))
    
    # Calcular stats reales del modelo
    r2 = r2_score(y_clean, model.predict(X_clean))
    slope = model.coef_[0]
    intercept = model.intercept_
    
    # Mostrar ecuación en la gráfica
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"PS = {intercept:.3f} + {slope:.3f} × GDT<br>R² = {r2:.3f}",
        showarrow=False,
        font=dict(color=CORPORATE_COLORS["verde_oscuro"], size=11),
        bgcolor=CORPORATE_COLORS["verde_muy_claro"],
        bordercolor=CORPORATE_COLORS["verde_oscuro"],
        borderwidth=1
    )
    
    fig.update_layout(
        title="Soluble Protein (%) vs Total Grain Damage (%)",
        xaxis_title="Total Grain Damage (%)",
        yaxis_title="Soluble Protein (%)",
        height=500,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=CORPORATE_COLORS["verde_oscuro"])
    )
    
    # Guardar gráfica
    fig.write_html("models/plots/soluble_protein_vs_grain_damage.html")
    fig.write_image("models/plots/soluble_protein_vs_grain_damage.png", width=800, height=500)
    
    fig.show()


# Cargar datos y procesar
df = pd.read_csv("models/data/datos_gdt_protein.csv")
df = df.rename(columns={"pct_soluble_protein_quim": "PS"})


# Modelo inicial para detectar outliers
X_full = df[["GDT"]]
y_full = df["PS"]
model_all = LinearRegression().fit(X_full, y_full)
df["y_pred"] = model_all.predict(X_full)
df["residuo"] = df["PS"] - df["y_pred"]

# Outliers como residuos ±2σ
sigma = df["residuo"].std()
df["outlier"] = df["residuo"].abs() > 2 * sigma

# Filtrar datos sin outliers
df_clean = df[df["outlier"] == False].copy()
X_clean = df_clean[["GDT"]]
y_clean = df_clean["PS"]

# Entrenar modelo limpio
model_clean = LinearRegression()
model_clean.fit(X_clean, y_clean)

# Etiquetar para visualización
df_clean["grupo"] = "sin outliers"
df_outliers = df[df["outlier"] == True].copy()
df_outliers["grupo"] = "outlier"
df_total = pd.concat([df_clean, df_outliers], ignore_index=True)

# Crear directorio para guardar gráficas si no existe
os.makedirs("models/plots", exist_ok=True)

# Graficar con Plotly
scatter_reg_final(df_total, x="GDT", y="PS", hue="grupo", model=model_clean, palette=PALETTE)

# Mostrar estadísticas del modelo
print(f"R² del modelo sin outliers: {r2_score(y_clean, model_clean.predict(X_clean)):.3f}")
print(f"RMSE del modelo sin outliers: {sqrt(mean_squared_error(y_clean, model_clean.predict(X_clean))):.3f}")

# Gráfico adicional de residuos con Plotly
residuos = y_clean - model_clean.predict(X_clean)

fig_residuos = go.Figure()

fig_residuos.add_trace(go.Scatter(
    x=model_clean.predict(X_clean),
    y=residuos,
    mode='markers',
    name='Residuals',
    marker=dict(
        color=CORPORATE_COLORS["verde_claro"],
        size=8,
        opacity=0.7
    )
))

# Agregar línea horizontal en y=0
fig_residuos.add_hline(
    y=0, 
    line_dash="dash", 
    line_color=CORPORATE_COLORS["gris_neutro"],
    annotation_text="Reference Line"
)

fig_residuos.update_layout(
    title="Residual Analysis",
    xaxis_title="Predicted Values",
    yaxis_title="Residuals (Observed - Predicted)",
    height=400,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial, sans-serif", size=12, color=CORPORATE_COLORS["verde_oscuro"])
)

# Guardar gráfica de residuos
fig_residuos.write_html("models/plots/residual_analysis.html")
fig_residuos.write_image("models/plots/residual_analysis.png", width=800, height=400)

fig_residuos.show()

# Gráfico de distribución de residuos
fig_hist_residuos = px.histogram(
    x=residuos,
    title="Residuals Distribution",
    nbins=20,
    color_discrete_sequence=[CORPORATE_COLORS["verde_claro"]]
)

fig_hist_residuos.update_layout(
    xaxis_title="Residuos",
    yaxis_title="Frequency",
    height=400,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial, sans-serif", size=12, color=CORPORATE_COLORS["verde_oscuro"])
)

# Guardar gráfica de distribución de residuos
fig_hist_residuos.write_html("models/plots/residuals_distribution.html")
fig_hist_residuos.write_image("models/plots/residuals_distribution.png", width=800, height=400)

fig_hist_residuos.show()

# NUEVA GRÁFICA: Distribución de Proteína Soluble
fig_dist_ps = px.histogram(
    x=df_clean["PS"],
    title="Soluble Protein Distribution",
    nbins=15,
    color_discrete_sequence=[CORPORATE_COLORS["verde_oscuro"]]
)

fig_dist_ps.update_layout(
    xaxis_title="Soluble Protein (%)",
    yaxis_title="Frequency",
    height=400,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial, sans-serif", size=12, color=CORPORATE_COLORS["verde_oscuro"])
)

# Agregar línea vertical para la mediana
mean_ps = df_clean["PS"].median()
fig_dist_ps.add_vline(
    x=mean_ps,
    line_dash="dash",
    line_color=CORPORATE_COLORS["gris_neutro"]
)
# Agregar anotación más arriba
fig_dist_ps.add_annotation(
    x=mean_ps+3,
    y=24,  # 15% más arriba del valor máximo
    text=f"Median: {mean_ps:.1f}%",
    showarrow=False,
    font=dict(color=CORPORATE_COLORS["verde_oscuro"], size=12)
)

# Guardar gráfica de distribución de PS
fig_dist_ps.write_html("models/plots/soluble_protein_distribution.html")
fig_dist_ps.write_image("models/plots/soluble_protein_distribution.png", width=800, height=400)

fig_dist_ps.show()

# Gráfico de distribución de daño total del grano
fig_dist_gdt = px.histogram(
    x=df_clean["GDT"],
    title="Total Grain Damage Distribution",
    nbins=15,
    color_discrete_sequence=[CORPORATE_COLORS["verde_claro"]]
)

fig_dist_gdt.update_layout(
    xaxis_title="Total Grain Damage (%)",
    yaxis_title="Frequency",
    height=400,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial, sans-serif", size=12, color=CORPORATE_COLORS["verde_oscuro"])
)

# Agregar línea vertical para la media
mean_gdt = df_clean["GDT"].mean()
fig_dist_gdt.add_vline(
    x=mean_gdt,
    line_dash="dash",
    line_color=CORPORATE_COLORS["gris_neutro"],
    annotation_text=f"Median: {mean_gdt:.1f}%"
)

# Guardar gráfica de distribución de GDT
fig_dist_gdt.write_html("models/plots/grain_damage_distribution.html")
fig_dist_gdt.write_image("models/plots/grain_damage_distribution.png", width=800, height=400)

fig_dist_gdt.show()

print("\n🎉 Análisis completado! Todos los gráficos se han generado con Plotly.")
print("📊 Los gráficos son interactivos - puedes hacer zoom, pan y hover para más detalles.")
print("💾 Gráficos guardados en la carpeta 'models/plots/':")
print("   - soluble_protein_vs_grain_damage.html/png")
print("   - residual_analysis.html/png")
print("   - residuals_distribution.html/png")
print("   - soluble_protein_distribution.html/png")
print("   - grain_damage_distribution.html/png")

