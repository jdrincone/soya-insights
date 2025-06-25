import pandas as pd
import streamlit as st
from ..config.constants import (
    ACIDEZ_DATA_FILE, PROTEINA_DATA_FILE, SEGUIMIENTO_DATA_FILE
)

class DataService:
    """Servicio para manejo de datos con cache optimizado"""
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def load_acidez_data():
        """Cargar datos de acidez con cache"""
        try:
            return pd.read_csv(ACIDEZ_DATA_FILE)
        except Exception as e:
            st.error(f"Error cargando datos de acidez: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_proteina_data():
        """Cargar datos de proteína con cache"""
        try:
            return pd.read_csv(PROTEINA_DATA_FILE)
        except Exception as e:
            st.error(f"Error cargando datos de proteína: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_seguimiento_data():
        """Cargar datos de seguimiento con cache"""
        try:
            return pd.read_csv(SEGUIMIENTO_DATA_FILE)
        except Exception as e:
            st.error(f"Error cargando datos de seguimiento: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_acidez_media():
        """Obtener valor medio de acidez de los datos"""
        df = DataService.load_acidez_data()
        if not df.empty:
            return df['pct_oil_acidez_mean'].mean()
        return 0.0 