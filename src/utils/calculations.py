import numpy as np
from ..config.constants import GDT_EXCELENTE, GDT_MODERADO

class Calculations:
    """Utilidades para cálculos de calidad"""
    
    @staticmethod
    def calcular_impacto_productos(gdt):
        """Calcular impacto en productos basado en GDT"""
        # GDT más alto = mayor impacto negativo
        factor_calidad = max(0.05, 1 - (gdt / 100))
        
        productos = {
            "Aceite de Soya": factor_calidad * 0.9,  # 90% de calidad base
            "Harina de Soya": factor_calidad * 0.85,  # 85% de calidad base
            "Proteína de Soya": factor_calidad * 0.8,  # 80% de calidad base
            "Lecitina": factor_calidad * 0.95,  # 95% de calidad base
            "Biodiesel": factor_calidad * 0.75   # 75% de calidad base
        }
        return productos
    
    @staticmethod
    def simular_evolucion_temporal(temperatura, humedad, gdc_ini, gdh_ini, meses):
        """Simular evolución de GDC y GDH a lo largo del tiempo"""
        tiempos = np.arange(0, meses + 1, 0.5)  # Cada 15 días
        
        # Factores de degradación basados en condiciones
        factor_temp = 1 + (temperatura - 20) * 0.02  # 2% por °C sobre 20°C
        factor_hum = 1 + (humedad - 50) * 0.01       # 1% por % de humedad sobre 50%
        
        # Ecuación real del daño del grano: y = 0.0730x² - 0.7741x + 14.8443
        def ecuacion_daño_grano(tiempo):
            return 0.0730 * tiempo**2 - 0.7741 * tiempo + 14.8443
        
        # Evolución de GDC (daño térmico)
        gdc_evol = []
        for t in tiempos:
            daño_base = ecuacion_daño_grano(t)
            daño_ajustado = daño_base * factor_temp
            gdc_final = min(gdc_ini + daño_ajustado, 100)
            gdc_evol.append(max(0, gdc_final))
        
        # Evolución de GDH (daño por hongos)
        gdh_evol = []
        for t in tiempos:
            daño_hongos_base = ecuacion_daño_grano(t) * 0.6
            daño_hongos_ajustado = daño_hongos_base * factor_hum
            gdh_final = min(gdh_ini + daño_hongos_ajustado, 50)
            gdh_evol.append(max(0, gdh_final))
        
        # Calcular GDT
        gdt_evol = [gdc + gdh for gdc, gdh in zip(gdc_evol, gdh_evol)]
        
        return tiempos, gdc_evol, gdh_evol, gdt_evol
    
    @staticmethod
    def obtener_ecuacion_base():
        """Obtener ecuación base del daño del grano"""
        return {
            'coeficientes': [0.0730, -0.7741, 14.8443],
            'ecuacion': 'y = 0.0730x² - 0.7741x + 14.8443',
            'descripcion': 'Ecuación cuadrática del daño del grano vs tiempo'
        } 