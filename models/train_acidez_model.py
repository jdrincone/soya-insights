import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from scipy.stats import randint, uniform
import shap
import joblib
import os
import json
from datetime import datetime
from sklearn.tree import export_text

# Colores corporativos
CORPORATE_COLORS = {
    "verde_oscuro": "#1A494C",
    "verde_claro": "#94AF92", 
    "verde_muy_claro": "#E6ECD8",
    "gris_neutro": "#C9C9C9"
}

def load_and_prepare_data():
    """Cargar y preparar los datos"""
    print("📊 Cargando datos...")
    
    # Cargar datos
    df = pd.read_csv("data/data_acidez.csv")
    
    # Definir features y target
    feats = ['gdc_mean_in', 'gdh_mean_in']
    targets = ['pct_oil_acidez_mean']
    
    # Verificar que las columnas existen
    for col in feats + targets:
        if col not in df.columns:
            raise ValueError(f"Columna {col} no encontrada en los datos")
    
    # Limpiar datos (eliminar filas con valores faltantes)
    df_clean = df[feats + targets].dropna()
    
    print(f"✅ Datos cargados: {df_clean.shape[0]} muestras, {df_clean.shape[1]} variables")
    print(f"📈 Features: {feats}")
    print(f"🎯 Target: {targets}")
    
    return df_clean, feats, targets

def train_random_forest(X_train, y_train, X_test, y_test):
    """Entrenar modelo Random Forest con RandomizedSearchCV"""
    print("\n🌲 Entrenando modelo Random Forest...")
    
    # Definir el pipeline y parámetros
    rf = RandomForestRegressor(random_state=42)
    
    param_dist = {
        "n_estimators": randint(200, 800),
        "max_depth": randint(3, 20),
        "min_samples_split": randint(2, 10),
        "min_samples_leaf": randint(1, 10),
        "max_features": uniform(0.5, 0.5)
    }
    
    # RandomizedSearchCV
    random_search = RandomizedSearchCV(
        rf, 
        param_distributions=param_dist,
        n_iter=50,
        cv=5,
        scoring='neg_mean_squared_error',
        random_state=42,
        n_jobs=-1
    )
    
    # Entrenar
    random_search.fit(X_train, y_train)
    
    print(f"✅ Mejores parámetros: {random_search.best_params_}")
    print(f"✅ Mejor score CV: {-random_search.best_score_:.4f}")
    
    return random_search.best_estimator_

def evaluate_model(model, X_train, y_train, X_test, y_test):
    """Evaluar el modelo y calcular métricas"""
    print("\n📊 Evaluando modelo...")
    
    # Predicciones
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Métricas
    metrics = {
        'train': {
            'mse': mean_squared_error(y_train, y_train_pred),
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'mae': mean_absolute_error(y_train, y_train_pred),
            'r2': r2_score(y_train, y_train_pred)
        },
        'test': {
            'mse': mean_squared_error(y_test, y_test_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'mae': mean_absolute_error(y_test, y_test_pred),
            'r2': r2_score(y_test, y_test_pred)
        }
    }
    
    print("📈 Métricas de entrenamiento:")
    print(f"   R²: {metrics['train']['r2']:.4f}")
    print(f"   RMSE: {metrics['train']['rmse']:.4f}")
    print(f"   MAE: {metrics['train']['mae']:.4f}")
    
    print("📈 Métricas de test:")
    print(f"   R²: {metrics['test']['r2']:.4f}")
    print(f"   RMSE: {metrics['test']['rmse']:.4f}")
    print(f"   MAE: {metrics['test']['mae']:.4f}")
    
    return metrics, y_train_pred, y_test_pred

def create_shap_analysis(model, X_train, X_test, feats):
    """Crear análisis SHAP"""
    print("\n🔍 Generando análisis SHAP...")
    
    # Crear directorio para SHAP
    os.makedirs("models/artifacts", exist_ok=True)
    
    # SHAP para el conjunto de test
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Gráfico de importancia de features
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, feature_names=feats, show=False, 
                     color=plt.cm.Set1(0))
    plt.title("SHAP Summary Plot - Acidez del Aceite", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("imagenes/shap_summary_acidez.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Gráfico de barras de importancia
    plt.figure(figsize=(8, 6))
    shap.summary_plot(shap_values, X_test, feature_names=feats, plot_type="bar", show=False,
                     color=CORPORATE_COLORS["verde_oscuro"])
    plt.title("SHAP Feature Importance - Acidez del Aceite", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("imagenes/shap_importance_acidez.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Valores SHAP para uso posterior
    shap_data = {
        'shap_values': shap_values.tolist(),
        'feature_names': feats,
        'expected_value': float(explainer.expected_value)
    }
    
    with open("models/artifacts/shap_values_acidez.json", "w") as f:
        json.dump(shap_data, f)
    
    print("✅ Análisis SHAP guardado en models/artifacts/")
    
    return explainer, shap_values

def create_visualizations(df, feats, targets, y_train_pred, y_test_pred, X_train, X_test, y_train, y_test):
    """Crear visualizaciones del modelo"""
    print("\n📊 Generando visualizaciones...")
    
    os.makedirs("models/plots", exist_ok=True)
    
    # 1. Predicciones vs Valores reales
    fig = go.Figure()
    
    # Datos de entrenamiento
    fig.add_trace(go.Scatter(
        x=y_train,
        y=y_train_pred,
        mode='markers',
        name='Entrenamiento',
        marker=dict(color=CORPORATE_COLORS["verde_oscuro"], size=8),
        hovertemplate='Real: %{x:.2f}<br>Predicho: %{y:.2f}<extra></extra>'
    ))
    
    # Datos de test
    fig.add_trace(go.Scatter(
        x=y_test,
        y=y_test_pred,
        mode='markers',
        name='Test',
        marker=dict(color=CORPORATE_COLORS["verde_claro"], size=8),
        hovertemplate='Real: %{x:.2f}<br>Predicho: %{y:.2f}<extra></extra>'
    ))
    
    # Línea perfecta
    min_val = min(y_train.min(), y_test.min())
    max_val = max(y_train.max(), y_test.max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Predicción Perfecta',
        line=dict(color='red', dash='dash'),
        showlegend=True
    ))
    
    fig.update_layout(
        title="Predicciones vs Valores Reales - Modelo de Acidez",
        xaxis_title="Valor Real (mg KOH/g)",
        yaxis_title="Valor Predicho (mg KOH/g)",
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.write_html("imagenes/predicciones_vs_reales_acidez.html")
    fig.write_image("imagenes/predicciones_vs_reales_acidez.png", width=1000, height=500)
    
    # 2. Residuos
    residuos_train = y_train - y_train_pred
    residuos_test = y_test - y_test_pred
    
    fig_res = go.Figure()
    
    fig_res.add_trace(go.Scatter(
        x=y_train_pred,
        y=residuos_train,
        mode='markers',
        name='Entrenamiento',
        marker=dict(color=CORPORATE_COLORS["verde_oscuro"], size=8)
    ))
    
    fig_res.add_trace(go.Scatter(
        x=y_test_pred,
        y=residuos_test,
        mode='markers',
        name='Test',
        marker=dict(color=CORPORATE_COLORS["verde_claro"], size=8)
    ))
    
    # Línea horizontal en y=0
    fig_res.add_hline(y=0, line_dash="dash", line_color="red")
    
    fig_res.update_layout(
        title="Análisis de Residuos - Modelo de Acidez",
        xaxis_title="Valor Predicho (mg KOH/g)",
        yaxis_title="Residuo (Real - Predicho)",
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig_res.write_html("imagenes/residuos_acidez.html")
    fig_res.write_image("imagenes/residuos_acidez.png", width=1000, height=500)
    
    print("✅ Visualizaciones guardadas en imagenes/")

def save_artifacts(model, metrics, feats, targets):
    """Guardar todos los artefactos del modelo"""
    print("\n💾 Guardando artefactos...")
    
    os.makedirs("models/artifacts", exist_ok=True)
    
    # 1. Guardar modelo
    joblib.dump(model, "models/artifacts/random_forest_acidez.pkl")
    
    # 2. Guardar métricas
    with open("models/artifacts/metrics_acidez.json", "w") as f:
        json.dump(metrics, f, indent=4)
    
    # 3. Guardar información del modelo
    model_info = {
        'model_type': 'RandomForestRegressor',
        'features': feats,
        'target': targets[0],
        'training_date': datetime.now().isoformat(),
        'best_params': model.get_params(),
        'feature_importance': dict(zip(feats, model.feature_importances_.tolist()))
    }
    
    with open("models/artifacts/model_info_acidez.json", "w") as f:
        json.dump(model_info, f, indent=4)
    
    print("✅ Artefactos guardados en models/artifacts/")
    print("   - random_forest_acidez.pkl (modelo)")
    print("   - metrics_acidez.json (métricas)")
    print("   - model_info_acidez.json (información)")
    print("   - shap_values_acidez.json (valores SHAP)")

def main():
    """Función principal"""
    print("🚀 Iniciando entrenamiento del modelo de acidez...")
    print("=" * 60)
    
    # 1. Cargar y preparar datos
    df, feats, targets = load_and_prepare_data()
    
    # 2. Dividir datos
    X = df[feats]
    y = df[targets[0]]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"📊 División de datos: {X_train.shape[0]} train, {X_test.shape[0]} test")
    
    # 3. Entrenar modelo
    model = train_random_forest(X_train, y_train, X_test, y_test)
    
    # 4. Evaluar modelo
    metrics, y_train_pred, y_test_pred = evaluate_model(model, X_train, y_train, X_test, y_test)
    
    # 5. Análisis SHAP
    explainer, shap_values = create_shap_analysis(model, X_train, X_test, feats)
    
    # 6. Visualizaciones
    create_visualizations(df, feats, targets, y_train_pred, y_test_pred, X_train, X_test, y_train, y_test)
    
    # 7. Guardar artefactos
    save_artifacts(model, metrics, feats, targets)

    # 8. Extraer reglas del árbol más representativo (primer árbol)
    tree_rules = export_text(model.estimators_[0], feature_names=list(X.columns))
    with open("models/artifacts/tree_rules_acidez.txt", "w") as f:
        f.write(tree_rules)
    print("✅ Reglas del árbol guardadas en models/artifacts/tree_rules_acidez.txt")

    print("\n" + "=" * 60)
    print("🎉 ¡Entrenamiento completado exitosamente!")
    print(f"📊 R² en test: {metrics['test']['r2']:.4f}")
    print(f"📊 RMSE en test: {metrics['test']['rmse']:.4f}")
    print("📁 Todos los artefactos guardados en models/artifacts/")
    print("📊 Visualizaciones guardadas en imagenes/")

if __name__ == "__main__":
    main() 