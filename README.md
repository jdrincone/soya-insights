# 🌱 Soya Insights

Aplicación Streamlit para analizar la degradación de granos de soya y su impacto en productos derivados.

## 📋 Descripción

Soya Insights es una aplicación web interactiva que permite:

- **Monitorear la degradación** de granos de soya en tiempo real
- **Analizar el impacto** en productos derivados (aceite, harina, proteína, etc.)
- **Visualizar tendencias** de degradación a lo largo del tiempo
- **Generar recomendaciones** basadas en condiciones ambientales
- **Calcular pérdidas económicas** estimadas

## 🚀 Características

- 📊 **Dashboard interactivo** con métricas en tiempo real
- 📈 **Gráficos dinámicos** usando Plotly
- 🔍 **Análisis de sensibilidad** a temperatura y humedad
- 💡 **Recomendaciones automáticas** basadas en datos
- 🐳 **Contenerización completa** con Docker
- ⚡ **Gestión de dependencias** con uv

## 🛠️ Tecnologías

- **Streamlit** - Framework web para aplicaciones de datos
- **Plotly** - Gráficos interactivos
- **Pandas** - Manipulación de datos
- **Docker** - Contenerización
- **uv** - Gestión de dependencias Python

## 📦 Instalación y Uso

### Opción 1: Usando Docker (Recomendado)

1. **Clonar el repositorio:**
   ```bash
   git clone <repository-url>
   cd soya-insights
   ```

2. **Ejecutar con Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Acceder a la aplicación:**
   Abrir http://localhost:8501 en tu navegador
docker run -p 8501:8501 soya-insights
### Opción 2: Desarrollo Local

1. **Instalar uv:**
   ```bash
   pip install uv
   ```

2. **Instalar dependencias:**
   ```bash
   uv sync
   ```

3. **Ejecutar la aplicación:**
   ```bash
   uv run streamlit run app.py
   ```

### Opción 3: Docker Directo

1. **Construir la imagen:**
   ```bash
   docker build -t soya-insights .
   ```

2. **Ejecutar el contenedor:**
   ```bash
   docker run -p 8501:8501 soya-insights
   ```

## 📊 Uso de la Aplicación

### Controles Principales

- **Temperatura (°C):** Ajusta la temperatura de almacenamiento (15-40°C)
- **Humedad Relativa (%):** Controla la humedad ambiental (40-90%)
- **Tiempo de Almacenamiento (días):** Define el período de almacenamiento (0-365 días)

### Métricas Mostradas

1. **Degradación Total:** Porcentaje de degradación actual
2. **Calidad Remanente:** Calidad restante del producto
3. **Pérdida Económica:** Estimación de pérdidas en USD/ton
4. **Vida Útil Restante:** Días restantes de almacenamiento seguro

### Productos Analizados

- Aceite de Soya
- Harina de Soya
- Proteína de Soya
- Lecitina
- Biodiesel

## 🔧 Configuración

### Variables de Entorno

```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Personalización

Puedes modificar los parámetros del modelo de degradación en `app.py`:

```python
def calcular_degradacion(temperatura, humedad, tiempo):
    # Ajusta estos factores según tus necesidades
    factor_temp = 1 + (temperatura - 20) * 0.05
    factor_humedad = 1 + (humedad - 50) * 0.02
    degradacion_base = tiempo * 0.001
    # ...
```

## 📈 Modelo de Degradación

El modelo utiliza una función simplificada que considera:

- **Factor de temperatura:** Incremento de degradación con temperatura
- **Factor de humedad:** Efecto de la humedad relativa
- **Tiempo base:** Degradación acumulativa por tiempo

### Fórmula Base:
```
Degradación = tiempo_base × factor_temperatura × factor_humedad
```

## 🧪 Desarrollo

### Estructura del Proyecto

```
soya-insights/
├── app.py              # Aplicación principal
├── pyproject.toml      # Dependencias y configuración
├── Dockerfile          # Configuración de Docker
├── docker-compose.yml  # Orquestación de contenedores
├── .dockerignore       # Archivos ignorados por Docker
└── README.md           # Documentación
```

### Comandos de Desarrollo

```bash
# Instalar dependencias de desarrollo
uv sync --extra dev

# Formatear código
uv run black app.py

# Ejecutar tests (cuando se implementen)
uv run pytest

# Ejecutar linting
uv run flake8 app.py
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

- **Email:** team@soya-insights.com
- **Proyecto:** [GitHub Repository](https://github.com/your-username/soya-insights)

---

*Desarrollado con ❤️ para el análisis de la industria de la soya*