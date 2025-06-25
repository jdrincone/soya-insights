# Constantes de la aplicación
import os

# Rutas de archivos
DATA_PATH = "data"
IMAGENES_PATH = "imagenes"
MODELS_PATH = "models/artifacts"

# Archivos de datos
ACIDEZ_DATA_FILE = os.path.join(DATA_PATH, "data_acidez.csv")
PROTEINA_DATA_FILE = os.path.join(DATA_PATH, "datos_gdt_protein.csv")
SEGUIMIENTO_DATA_FILE = os.path.join(DATA_PATH, "datos_seguimiento_granos.csv")

# Archivos de modelos
ACIDEZ_MODEL_FILE = os.path.join(MODELS_PATH, "random_forest_acidez.pkl")
ACIDEZ_METRICS_FILE = os.path.join(MODELS_PATH, "metrics_acidez.json")
ACIDEZ_INFO_FILE = os.path.join(MODELS_PATH, "model_info_acidez.json")

# Archivos de visualización
SHAP_IMPORTANCE_FILE = os.path.join(IMAGENES_PATH, "shap_importance_acidez.png")
DISTRIBUCIONES_HTML_FILE = os.path.join(IMAGENES_PATH, "subplot_distribuciones_acidez_oil.html")
PREDICCIONES_HTML_FILE = os.path.join(IMAGENES_PATH, "predicciones_vs_reales_acidez.html")
RESIDUOS_HTML_FILE = os.path.join(IMAGENES_PATH, "residuos_acidez.html")
PROTEINA_DIST_HTML_FILE = os.path.join(IMAGENES_PATH, "soluble_protein_distribution.html")
GRAIN_DAMAGE_HTML_FILE = os.path.join(IMAGENES_PATH, "grain_damage_distribution.html")
PROTEINA_VS_GDT_HTML_FILE = os.path.join(IMAGENES_PATH, "soluble_protein_vs_grain_damage.html")

# Parámetros de calidad
GDT_EXCELENTE = 15.0
GDT_MODERADO = 35.0
ACIDEZ_BASE = 0.5
ACIDEZ_MAXIMA = 2.0
PROTEINA_BASE = 70.0
PROTEINA_MINIMA = 50.0
CALIDAD_REMANENTE_BASE = 85.0

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",
    "verde_claro": "#94AF92", 
    "verde_muy_claro": "#E6ECD8",
    "gris_neutro": "#C9C9C9"
}

# Configuración de la aplicación
APP_CONFIG = {
    "page_title": "Soya Insights",
    "page_icon": "🌱",
    "layout": "wide"
} 