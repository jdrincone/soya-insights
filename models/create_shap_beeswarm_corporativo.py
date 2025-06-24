import json
import numpy as np
import shap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",      # rgb(26,73,76)
    "verde_claro": "#94AF92",       # rgb(148,175,146)
    "verde_muy_claro": "#E6ECD8",   # rgb(230,236,216)
    "gris_neutro": "#C9C9C9"        # rgb(201,201,201)
}

# Crear colormap personalizado de verde_claro a verde_oscuro
cmap = LinearSegmentedColormap.from_list(
    "corporativo_verde",
    [CORPORATE_COLORS["verde_claro"], CORPORATE_COLORS["verde_oscuro"]]
)

def main():
    # Cargar valores SHAP
    with open("models/artifacts/shap_values_acidez.json", "r") as f:
        shap_data = json.load(f)
    shap_values = np.array(shap_data['shap_values'])
    feature_names = shap_data['feature_names']
    
    # Crear datos de ejemplo para el plot (usando los valores SHAP como proxy)
    # En un caso real, usarías los valores originales de las features
    X_display = shap_values.copy()
    
    # Crear objeto Explanation
    explanation = shap.Explanation(
        values=shap_values,
        base_values=shap_data['expected_value'],
        data=X_display,
        feature_names=feature_names
    )
    
    # Configurar matplotlib con colores corporativos
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    
    # Crear el plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot beeswarm con colormap personalizado
    shap.plots.beeswarm(explanation, show=False, color=cmap)
    
    # Personalizar el plot
    ax.set_title("SHAP Summary Plot - Análisis de Acidez", fontsize=14, fontweight='bold')
    ax.set_xlabel("SHAP Value", fontsize=12)
    ax.set_ylabel("Features", fontsize=12)
    
    # Ajustar layout y guardar
    plt.tight_layout()
    plt.savefig("models/artifacts/shap_summary_acidez.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✅ SHAP summary plot generado exitosamente con colores corporativos")

if __name__ == "__main__":
    main() 