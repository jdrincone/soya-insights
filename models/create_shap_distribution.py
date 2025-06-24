import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import pandas as pd

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",      # rgb(26,73,76)
    "verde_claro": "#94AF92",       # rgb(148,175,146)
    "verde_muy_claro": "#E6ECD8",   # rgb(230,236,216)
    "gris_neutro": "#C9C9C9"        # rgb(201,201,201)
}

def create_shap_distribution_plot():
    """Crear gráfica de distribución de efectos SHAP con colores corporativos"""
    
    # Cargar valores SHAP
    with open("artifacts/shap_values_acidez.json", "r") as f:
        shap_data = json.load(f)
    
    # Extraer valores SHAP por columna
    shap_values = np.array(shap_data['shap_values'])  # shape: (n_samples, n_features)
    feature_names = shap_data['feature_names']
    gdc_shap_values = shap_values[:, 0]
    gdh_shap_values = shap_values[:, 1]
    
    # Crear figura con estilo corporativo
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Configurar estilo
    plt.style.use('default')
    
    # Gráfica 1: Distribución de efectos SHAP para GDC
    ax1.hist(gdc_shap_values, bins=30, alpha=0.7, color=CORPORATE_COLORS["verde_claro"], 
             edgecolor=CORPORATE_COLORS["verde_oscuro"], linewidth=1)
    ax1.axvline(x=np.mean(gdc_shap_values), color=CORPORATE_COLORS["verde_oscuro"], 
                linestyle='--', linewidth=2, label=f'Media: {np.mean(gdc_shap_values):.3f}')
    ax1.axvline(x=0, color='red', linestyle='-', linewidth=1, alpha=0.7, label='Sin efecto')
    
    ax1.set_title(f'Distribución de Efectos SHAP - {feature_names[0]}', 
                  fontsize=14, fontweight='bold', color=CORPORATE_COLORS["verde_oscuro"])
    ax1.set_xlabel('Valor SHAP', fontsize=12, color=CORPORATE_COLORS["verde_oscuro"])
    ax1.set_ylabel('Frecuencia', fontsize=12, color=CORPORATE_COLORS["verde_oscuro"])
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfica 2: Distribución de efectos SHAP para GDH
    ax2.hist(gdh_shap_values, bins=30, alpha=0.7, color=CORPORATE_COLORS["verde_claro"], 
             edgecolor=CORPORATE_COLORS["verde_oscuro"], linewidth=1)
    ax2.axvline(x=np.mean(gdh_shap_values), color=CORPORATE_COLORS["verde_oscuro"], 
                linestyle='--', linewidth=2, label=f'Media: {np.mean(gdh_shap_values):.3f}')
    ax2.axvline(x=0, color='red', linestyle='-', linewidth=1, alpha=0.7, label='Sin efecto')
    
    ax2.set_title(f'Distribución de Efectos SHAP - {feature_names[1]}', 
                  fontsize=14, fontweight='bold', color=CORPORATE_COLORS["verde_oscuro"])
    ax2.set_xlabel('Valor SHAP', fontsize=12, color=CORPORATE_COLORS["verde_oscuro"])
    ax2.set_ylabel('Frecuencia', fontsize=12, color=CORPORATE_COLORS["verde_oscuro"])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar gráfica
    plt.savefig('artifacts/shap_distribution_acidez.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✅ Gráfica de distribución SHAP creada exitosamente")
    
    # Crear también una versión combinada
    create_combined_shap_plot(gdc_shap_values, gdh_shap_values, feature_names)

def create_combined_shap_plot(gdc_values, gdh_values, feature_names):
    """Crear gráfica combinada de distribución SHAP"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Crear histogramas superpuestos
    ax.hist(gdc_values, bins=25, alpha=0.6, color=CORPORATE_COLORS["verde_claro"], 
            label=f'{feature_names[0]}', edgecolor=CORPORATE_COLORS["verde_oscuro"], linewidth=1)
    ax.hist(gdh_values, bins=25, alpha=0.6, color=CORPORATE_COLORS["gris_neutro"], 
            label=f'{feature_names[1]}', edgecolor='gray', linewidth=1)
    
    # Líneas de media
    ax.axvline(x=np.mean(gdc_values), color=CORPORATE_COLORS["verde_oscuro"], 
               linestyle='--', linewidth=2, label=f'Media {feature_names[0]}: {np.mean(gdc_values):.3f}')
    ax.axvline(x=np.mean(gdh_values), color='gray', 
               linestyle='--', linewidth=2, label=f'Media {feature_names[1]}: {np.mean(gdh_values):.3f}')
    
    # Línea de referencia
    ax.axvline(x=0, color='red', linestyle='-', linewidth=1, alpha=0.7, label='Sin efecto')
    
    ax.set_title('Distribución de Efectos SHAP - Comparación de Variables', 
                 fontsize=16, fontweight='bold', color=CORPORATE_COLORS["verde_oscuro"])
    ax.set_xlabel('Valor SHAP', fontsize=14, color=CORPORATE_COLORS["verde_oscuro"])
    ax.set_ylabel('Frecuencia', fontsize=14, color=CORPORATE_COLORS["verde_oscuro"])
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Agregar estadísticas
    stats_text = f"""
    Estadísticas SHAP:
    {feature_names[0]} - Media: {np.mean(gdc_values):.3f}, Std: {np.std(gdc_values):.3f}
    {feature_names[1]} - Media: {np.mean(gdh_values):.3f}, Std: {np.std(gdh_values):.3f}
    """
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('artifacts/shap_distribution_combined.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✅ Gráfica combinada SHAP creada exitosamente")

if __name__ == "__main__":
    create_shap_distribution_plot() 