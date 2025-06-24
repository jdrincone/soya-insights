import joblib
import pandas as pd
import numpy as np
import json
import os

class AcidezPredictor:
    """Clase para hacer predicciones de acidez usando el modelo Random Forest entrenado"""
    
    def __init__(self, model_path="models/artifacts/random_forest_acidez.pkl"):
        """Inicializar el predictor cargando el modelo"""
        self.model = joblib.load(model_path)
        self.features = ['gdc_mean_in', 'gdh_mean_in']
        
        # Cargar información del modelo
        with open("models/artifacts/model_info_acidez.json", "r") as f:
            self.model_info = json.load(f)
        
        # Cargar métricas
        with open("models/artifacts/metrics_acidez.json", "r") as f:
            self.metrics = json.load(f)
    
    def predict(self, gdc, gdh):
        """
        Hacer predicción de acidez
        
        Args:
            gdc (float): Daño térmico del grano (%)
            gdh (float): Daño por hongos del grano (%)
            
        Returns:
            float: Predicción de acidez (mg KOH/g)
        """
        # Crear DataFrame con las features
        data = pd.DataFrame({
            'gdc_mean_in': [gdc],
            'gdh_mean_in': [gdh]
        })
        
        # Hacer predicción
        prediction = self.model.predict(data)[0]
        
        return prediction
    
    def predict_batch(self, data):
        """
        Hacer predicciones para múltiples muestras
        
        Args:
            data (pd.DataFrame): DataFrame con columnas 'gdc_mean_in' y 'gdh_mean_in'
            
        Returns:
            np.array: Array de predicciones
        """
        return self.model.predict(data[self.features])
    
    def get_feature_importance(self):
        """Obtener importancia de features"""
        return self.model_info['feature_importance']
    
    def get_model_metrics(self):
        """Obtener métricas del modelo"""
        return self.metrics
    
    def get_model_info(self):
        """Obtener información del modelo"""
        return self.model_info

def load_acidez_model():
    """Función helper para cargar el modelo de acidez"""
    try:
        predictor = AcidezPredictor()
        print("✅ Modelo de acidez cargado exitosamente")
        print(f"📊 R² en test: {predictor.metrics['test']['r2']:.4f}")
        print(f"📊 RMSE en test: {predictor.metrics['test']['rmse']:.4f}")
        return predictor
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Cargar modelo
    predictor = load_acidez_model()
    
    if predictor:
        # Ejemplo de predicción
        gdc_ejemplo = 30.0  # 30% daño térmico
        gdh_ejemplo = 15.0  # 15% daño por hongos
        
        acidez_pred = predictor.predict(gdc_ejemplo, gdh_ejemplo)
        
        print(f"\n🔮 Ejemplo de predicción:")
        print(f"   GDC: {gdc_ejemplo}%")
        print(f"   GDH: {gdh_ejemplo}%")
        print(f"   Acidez predicha: {acidez_pred:.3f} mg KOH/g")
        
        # Mostrar importancia de features
        print(f"\n📈 Importancia de features:")
        for feature, importance in predictor.get_feature_importance().items():
            print(f"   {feature}: {importance:.3f}") 