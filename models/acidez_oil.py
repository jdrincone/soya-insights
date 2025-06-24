import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.subplots as sp
import os
import numpy as np

# Colores corporativos
def get_color(var, target):
    if var == target:
        return CORPORATE_COLORS["target"]
    idx = variables.index(var)
    return box_colors[idx]

CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",      # rgb(26,73,76)
    "verde_claro": "#94AF92",       # rgb(148,175,146)
    "verde_muy_claro": "#E6ECD8",   # rgb(230,236,216)
    "gris_neutro": "#C9C9C9",       # rgb(201,201,201)
    "target": "#FFC107"              # Amarillo para la variable target
}

# Leer datos
df = pd.read_csv("models/data/data_acidez.csv")

# Variables y colores
variables = ["gdc_mean_in", "gdh_mean_in", "pct_oil_acidez_mean"]
colores = [
    CORPORATE_COLORS["verde_oscuro"],
    CORPORATE_COLORS["verde_claro"],
    CORPORATE_COLORS["target"]
]

# Títulos descriptivos para los subplots
titulos_subplots = ["GDC (Daño Térmico)", "GDH (Daño por Hongos)", "Acidez del Aceite (%)"]

# Crear directorio para guardar gráficas si no existe
os.makedirs("models/plots", exist_ok=True)

# Crear subplots 1x3
fig = sp.make_subplots(rows=1, cols=3, subplot_titles=titulos_subplots)

for i, (var, color) in enumerate(zip(variables, colores)):
    # Histograma
    fig.add_trace(
        go.Histogram(
            x=df[var],
            marker_color=color,
            opacity=1,
            nbinsx=30,
            showlegend=False,
            name=f"{var} (Hist)"
        ),
        row=1, col=i+1
    )
    # KDE (curva de densidad)
    kde = ff.create_distplot([df[var].dropna()], [var], show_hist=False, show_rug=False, colors=[color])
    kde_trace = kde['data'][0]
    kde_trace.showlegend = False
    kde_trace.name = f"{var} (KDE)"
    kde_trace.line.width = 3
    fig.add_trace(kde_trace, row=1, col=i+1)
    # Mediana
    median_val = df[var].median()
    fig.add_shape(
        type="line",
        x0=median_val, x1=median_val,
        y0=0, y1=1,
        xref=f"x{i+1}", yref=f"paper",
        line=dict(color=color, width=2, dash="dash"),
        row=1, col=i+1
    )
    fig.add_annotation(
        x=median_val, y=1, xref=f"x{i+1}", yref="paper",
        text=f"Mediana: {median_val:.2f}",
        showarrow=False, yshift=18,
        font=dict(color=color, size=11, family="Arial"),
        bgcolor="white",
        bordercolor=color,
        borderwidth=1,
        row=1, col=i+1
    )

fig.update_layout(
    title="Distribuciones",
    height=400, width=900,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial, sans-serif", size=12, color=CORPORATE_COLORS["verde_oscuro"]),
    showlegend=False
)

# Actualizar etiquetas de ejes para todos los subplots
for i in range(1, 4):
    fig.update_xaxes(title_text="Porcentaje de cada medida", row=1, col=i)
    fig.update_yaxes(title_text="Frecuencia", row=1, col=i)

# Guardar la figura
fig.write_html("models/plots/subplot_distribuciones_acidez_oil.html")
fig.write_image("models/plots/subplot_distribuciones_acidez_oil.png", width=1200, height=500)

fig.show()
