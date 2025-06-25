# 🏗️ Arquitectura Modular - Soya Insights

## 📁 Estructura del Proyecto

```
soya-insights/
├── src/                          # 🎯 Módulo principal
│   ├── __init__.py
│   ├── config/                   # ⚙️ Configuración centralizada
│   │   ├── __init__.py
│   │   └── constants.py          # Constantes, rutas, colores
│   ├── services/                 # 🔧 Servicios de datos y modelos
│   │   ├── __init__.py
│   │   ├── data_service.py       # Carga de datos con cache
│   │   └── model_service.py      # Modelos ML con cache
│   ├── components/               # 🧩 Componentes reutilizables
│   │   ├── __init__.py
│   │   └── metrics_display.py    # Visualización de métricas
│   ├── utils/                    # 🛠️ Utilidades y cálculos
│   │   ├── __init__.py
│   │   └── calculations.py       # Cálculos de calidad
│   └── models/                   # 🤖 Modelos ML (futuro)
│       └── __init__.py
├── data/                         # 📊 Datos CSV
├── imagenes/                     # 🖼️ Visualizaciones HTML
├── models/artifacts/             # 🎯 Modelos entrenados
├── pages/                        # 📄 Páginas Streamlit
├── Soya_Insights.py              # 🚀 Aplicación principal
└── requirements.txt              # 📦 Dependencias
```

## 🚀 Características Principales

### **1. Cache Optimizado**
- **@st.cache_data**: Para datos CSV (TTL: 1 hora)
- **@st.cache_resource**: Para modelos ML (persistente)
- **Carga agil**: Información en memoria para respuestas rápidas

### **2. Servicios Modulares**

#### **DataService**
```python
# Carga de datos con cache automático
df_acidez = DataService.load_acidez_data()
df_proteina = DataService.load_proteina_data()
acidez_media = DataService.get_acidez_media()
```

#### **ModelService**
```python
# Modelos con cache persistente
acidez_model = ModelService.load_acidez_model()
proteina_model = ModelService.load_proteina_model()

# Predicciones
acidez = ModelService.predict_acidez(gdc, gdh, model)
proteina = ModelService.predict_proteina(gdt, model)
```

### **3. Componentes Reutilizables**

#### **MetricsDisplay**
```python
# Métricas con diseño consistente
MetricsDisplay.display_gdt_metric(gdt)
MetricsDisplay.display_acidez_metric(acidez)
MetricsDisplay.display_quality_summary(gdt, gdc, gdh, acidez, proteina)
```

### **4. Configuración Centralizada**

#### **constants.py**
- Rutas de archivos
- Parámetros de calidad
- Colores corporativos
- Configuración de la app

### **5. Utilidades de Cálculos**

#### **Calculations**
```python
# Simulación temporal
tiempos, gdc_evol, gdh_evol, gdt_evol = Calculations.simular_evolucion_temporal(
    temperatura, humedad, gdc_ini, gdh_ini, meses
)

# Impacto en productos
impacto = Calculations.calcular_impacto_productos(gdt)
```

## 🔄 Flujo de Datos

```
1. Usuario interactúa con controles
   ↓
2. DataService carga datos (con cache)
   ↓
3. ModelService carga modelos (con cache)
   ↓
4. Calculations procesa datos
   ↓
5. MetricsDisplay muestra resultados
   ↓
6. Streamlit renderiza interfaz
```

## ⚡ Beneficios de la Arquitectura

### **Performance**
- ✅ Cache inteligente para datos y modelos
- ✅ Carga agil de información en memoria
- ✅ Respuestas instantáneas para cálculos repetidos

### **Mantenibilidad**
- ✅ Código modular y organizado
- ✅ Separación clara de responsabilidades
- ✅ Fácil testing y debugging

### **Escalabilidad**
- ✅ Fácil agregar nuevos servicios
- ✅ Componentes reutilizables
- ✅ Configuración centralizada

### **Reutilización**
- ✅ Servicios independientes
- ✅ Componentes modulares
- ✅ Utilidades compartidas

## 🛠️ Uso de la Arquitectura

### **Agregar Nuevo Servicio**
```python
# src/services/nuevo_service.py
import streamlit as st

class NuevoService:
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_nuevos_datos():
        # Implementación
        pass
```

### **Agregar Nuevo Componente**
```python
# src/components/nuevo_componente.py
import streamlit as st

class NuevoComponente:
    @staticmethod
    def display_algo():
        # Implementación
        pass
```

### **Agregar Nueva Constante**
```python
# src/config/constants.py
NUEVA_CONSTANTE = "valor"
```

## 🔧 Configuración de Cache

### **Tipos de Cache**
- **@st.cache_data**: Para datos que cambian ocasionalmente
- **@st.cache_resource**: Para recursos pesados (modelos)
- **TTL**: Time To Live (tiempo de vida del cache)

### **Ejemplo de Configuración**
```python
@st.cache_data(ttl=3600)  # 1 hora
def load_data():
    return pd.read_csv("data.csv")

@st.cache_resource  # Persistente
def load_model():
    return joblib.load("model.pkl")
```

## 📈 Métricas de Performance

- **Tiempo de carga inicial**: ~2-3 segundos
- **Tiempo de respuesta**: <100ms (con cache)
- **Uso de memoria**: Optimizado con cache TTL
- **Escalabilidad**: Modular y extensible

---

**🎯 Objetivo**: Mantener la agilidad y funcionalidad completa mientras se mejora la organización y mantenibilidad del código. 