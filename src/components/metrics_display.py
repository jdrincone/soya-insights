import streamlit as st
from ..config.constants import (
    GDT_EXCELENTE, GDT_MODERADO, ACIDEZ_BASE, ACIDEZ_MAXIMA,
    PROTEINA_BASE, PROTEINA_MINIMA, CALIDAD_REMANENTE_BASE
)

class MetricsDisplay:
    """Componente para mostrar métricas de calidad"""
    
    @staticmethod
    def display_gdt_metric(gdt):
        """Mostrar métrica de GDT"""
        st.metric(
            label="GDT - Daño Total",
            value=f"{gdt:.1f}%",
            delta=f"+{gdt - GDT_EXCELENTE:.1f}%" if gdt > GDT_EXCELENTE else None
        )
    
    @staticmethod
    def display_calidad_remanente_metric(gdt):
        """Mostrar métrica de calidad remanente"""
        calidad_remanente = max(0, 100 - gdt)
        st.metric(
            label="Estado de Calidad",
            value=f"{calidad_remanente:.1f}%",
            delta=f"{(100 - gdt) - CALIDAD_REMANENTE_BASE:.1f}%" if gdt < GDT_EXCELENTE else None
        )
        st.caption("💡 Porcentaje de calidad que queda en los granos después del daño total (GDT).")
    
    @staticmethod
    def display_acidez_metric(acidez):
        """Mostrar métrica de acidez"""
        st.metric(
            label="Acidez (mg KOH/g)",
            value=f"{acidez:.2f}",
            delta=f"+{acidez - ACIDEZ_BASE:.2f}" if acidez > ACIDEZ_BASE else None
        )
        st.caption(f"💡 Valor base: {ACIDEZ_BASE} mg KOH/g. Límite máximo aceptable: {ACIDEZ_MAXIMA} mg KOH/g.")
    
    @staticmethod
    def display_proteina_metric(proteina):
        """Mostrar métrica de proteína"""
        st.metric(
            label="Proteína Soluble (%)",
            value=f"{proteina:.1f}%",
            delta=f"-{PROTEINA_BASE - proteina:.1f}%" if proteina < PROTEINA_BASE else None
        )
        st.caption(f"💡 Proteína Base: {PROTEINA_BASE}%. Límite mínimo aceptable: {PROTEINA_MINIMA}%.")
    
    @staticmethod
    def display_quality_summary(gdt, gdc, gdh, acidez, proteina):
        """Mostrar resumen de calidad"""
        if gdt < GDT_EXCELENTE:
            st.success(f"""
            **✅ Calidad Excelente**
            
            Con un daño total (GDT) de {gdt:.1f}%, los granos de soya mantienen excelente calidad:
            - **Daño térmico (GDC):** {gdc:.1f}% (controlado)
            - **Daño por hongos (GDH):** {gdh:.1f}% (mínimo)
            - **Acidez controlada:** {acidez:.2f} mg KOH/g (dentro de límites normales)
            - **Proteína preservada:** {proteina:.1f}% (excelente)
            
            **Recomendación:** Granos aptos para todos los usos industriales.
            """)
        elif gdt < GDT_MODERADO:
            st.warning(f"""
            **⚠️ Calidad Moderada**
            
            Con un daño total (GDT) de {gdt:.1f}%, se observa degradación moderada:
            - **Daño térmico (GDC):** {gdc:.1f}% (requiere monitoreo)
            - **Daño por hongos (GDH):** {gdh:.1f}% (aumentando)
            - **Acidez aumentando:** {acidez:.2f} mg KOH/g (requiere atención)
            - **Proteína reducida:** {proteina:.1f}% (pérdida de {PROTEINA_BASE - proteina:.1f}%)
            """)
        else:
            st.error(f"""
            **🚨 Calidad Crítica**
            
            Con un daño total (GDT) de {gdt:.1f}%, la degradación es crítica:
            - **Daño térmico (GDC):** {gdc:.1f}% (muy alto)
            - **Daño por hongos (GDH):** {gdh:.1f}% (crítico)
            - **Acidez elevada:** {acidez:.2f} mg KOH/g (fuera de especificaciones)
            - **Proteína significativamente reducida:** {proteina:.1f}% (pérdida de {PROTEINA_BASE - proteina:.1f}%)
            
            **Recomendación:** Venta inmediata o procesamiento urgente. Revisar condiciones.
            """)
        
        st.markdown("""
        **⚠️ Nota de validez:** 
        - Los resultados son válidos siempre que se cumplan las condiciones asumidas y el comportamiento observado se mantenga en el tiempo evaluado.
        """) 