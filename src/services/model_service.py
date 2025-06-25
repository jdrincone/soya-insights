import os
import joblib
import json
import numpy as np
import streamlit as st
from sklearn.linear_model import LinearRegression
import pandas as pd
from ..config.constants import (
    ACIDEZ_MODEL_FILE, ACIDEZ_METRICS_FILE, ACIDEZ_INFO_FILE,
    PROTEINA_DATA_FILE
)
from .data_service import DataService

class ModelService:
    """Servicio para manejo de modelos con cache optimizado"""
    
    @staticmethod
    @st.cache_resource
    def load_acidez_model():
        """Cargar modelo de acidez con cache persistente"""
        try:
            if os.path.exists(ACIDEZ_MODEL_FILE):
                return joblib.load(ACIDEZ_MODEL_FILE)
            else:
                st.warning("Modelo de acidez no encontrado")
                return None
        except Exception as e:
            st.error(f"Error cargando modelo de acidez: {e}")
            return None
    
    @staticmethod
    @st.cache_resource
    def load_proteina_model():
        """Cargar modelo de proteína con cache persistente"""
        try:
            # Cargar datos de proteína para entrenar modelo simple
            df_protein = DataService.load_proteina_data()
            if df_protein.empty:
                return None
                
            X_protein = df_protein[["GDT"]].values
            y_protein = df_protein["pct_soluble_protein_quim"].values
            
            model_protein = LinearRegression()
            model_protein.fit(X_protein, y_protein)
            return model_protein
        except Exception as e:
            st.warning(f"No se pudo cargar el modelo de proteína: {e}")
            return None
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_model_metrics():
        """Cargar métricas del modelo con cache"""
        try:
            with open(ACIDEZ_METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"No se pudieron cargar las métricas del modelo: {e}")
            return {}
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_model_info():
        """Cargar información del modelo con cache"""
        try:
            with open(ACIDEZ_INFO_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"No se pudo cargar la información del modelo: {e}")
            return {}
    
    @staticmethod
    def predict_acidez(gdc, gdh, model=None):
        """Predecir acidez usando el modelo"""
        if model is None:
            # Fallback: modelo simplificado
            acidez_base = 0.5
            incremento_acidez = (gdc + gdh) * 0.02
            return acidez_base + incremento_acidez
        
        # Usar modelo real con DataFrame para evitar warnings
        try:
            X_pred = pd.DataFrame([[gdc, gdh]], columns=['GDC', 'GDH'])
            return model.predict(X_pred)[0]
        except:
            # Fallback si hay problemas con feature names
            X_pred = np.array([[gdc, gdh]])
            return model.predict(X_pred)[0]
    
    @staticmethod
    def predict_proteina(gdt, model=None):
        """Predecir proteína usando el modelo"""
        if model is None:
            # Fallback: modelo simplificado
            proteina_base = 70.0
            perdida_proteina = gdt * 0.3
            return max(proteina_base - perdida_proteina, 30.0)
        
        # Usar modelo real
        try:
            X_pred = pd.DataFrame([[gdt]], columns=['GDT'])
            return model.predict(X_pred)[0]
        except:
            # Fallback si hay problemas
            X_pred = np.array([[gdt]])
            return model.predict(X_pred)[0] 