#!/usr/bin/env python3
"""
Script para configurar entorno virtual con XGBoost >= 1.3
"""

import subprocess
import sys
import os
import venv
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_xgboost_env():
    """Crear entorno virtual con XGBoost >= 1.3"""
    
    print("🌱 Configurando entorno virtual con XGBoost >= 1.3")
    print("=" * 60)
    
    # Crear directorio para el entorno virtual
    env_dir = "xgboost_env"
    if os.path.exists(env_dir):
        print(f"⚠️  El directorio {env_dir} ya existe. Eliminando...")
        run_command(f"rm -rf {env_dir}", "Eliminando entorno virtual existente")
    
    # Crear entorno virtual
    print(f"📁 Creando entorno virtual en {env_dir}...")
    venv.create(env_dir, with_pip=True)
    
    # Determinar el ejecutable de pip según el sistema operativo
    if sys.platform == "win32":
        pip_path = os.path.join(env_dir, "Scripts", "pip")
        python_path = os.path.join(env_dir, "Scripts", "python")
    else:
        pip_path = os.path.join(env_dir, "bin", "pip")
        python_path = os.path.join(env_dir, "bin", "python")
    
    # Actualizar pip
    run_command(f"{pip_path} install --upgrade pip", "Actualizando pip")
    
    # Instalar dependencias específicas
    dependencies = [
        "xgboost>=1.3.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0"
    ]
    
    print("📦 Instalando dependencias...")
    for dep in dependencies:
        run_command(f"{pip_path} install {dep}", f"Instalando {dep}")
    
    # Verificar versión de XGBoost
    print("🔍 Verificando versión de XGBoost...")
    version_check = run_command(f"{python_path} -c \"import xgboost; print('XGBoost version:', xgboost.__version__)\"", "Verificando versión")
    
    if version_check:
        print(f"✅ {version_check.strip()}")
    
    # Crear script de ejecución
    create_run_script(env_dir, python_path)
    
    print("\n" + "=" * 60)
    print("✅ Entorno virtual configurado exitosamente!")
    print(f"📁 Ubicación: {os.path.abspath(env_dir)}")
    print(f"🐍 Python: {python_path}")
    print("\n🚀 Para ejecutar el modelo de proteína soluble:")
    print(f"   ./run_soluble_protein.sh")
    print("\n📚 Para activar el entorno manualmente:")
    if sys.platform == "win32":
        print(f"   {env_dir}\\Scripts\\activate")
    else:
        print(f"   source {env_dir}/bin/activate")

def create_run_script(env_dir, python_path):
    """Crear script para ejecutar el modelo de proteína soluble"""
    
    if sys.platform == "win32":
        # Script para Windows
        script_content = f"""@echo off
echo 🌱 Ejecutando Modelo de Proteína Soluble...
echo.
echo 📁 Entorno virtual: {env_dir}
echo 🐍 Python: {python_path}
echo.
echo 🔍 Verificando versión de XGBoost...
{python_path} -c "import xgboost; print('XGBoost version:', xgboost.__version__)"
echo.
echo 🚀 Ejecutando modelo...
{python_path} models/soluble_protein.py
pause
"""
        script_path = "run_soluble_protein.bat"
    else:
        # Script para Unix/Linux/macOS
        script_content = f"""#!/bin/bash

echo "🌱 Ejecutando Modelo de Proteína Soluble..."
echo ""
echo "📁 Entorno virtual: {env_dir}"
echo "🐍 Python: {python_path}"
echo ""
echo "🔍 Verificando versión de XGBoost..."
{python_path} -c "import xgboost; print('XGBoost version:', xgboost.__version__)"
echo ""
echo "🚀 Ejecutando modelo..."

# Activar entorno virtual
source {env_dir}/bin/activate

# Ejecutar modelo
{python_path} models/soluble_protein.py
"""
        script_path = "run_soluble_protein.sh"
        # Hacer el script ejecutable
        os.chmod(script_path, 0o755)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"📝 Script de ejecución creado: {script_path}")

def create_requirements_file():
    """Crear archivo requirements.txt específico"""
    
    requirements_content = """# Dependencias para modelo de proteína soluble con XGBoost >= 1.3
xgboost>=1.3.0
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
seaborn>=0.11.0

# Dependencias opcionales para desarrollo
# jupyter>=1.0.0
# ipykernel>=6.0.0
"""
    
    with open("requirements_xgboost.txt", 'w') as f:
        f.write(requirements_content)
    
    print("📄 Archivo requirements_xgboost.txt creado")

def main():
    """Función principal"""
    try:
        create_xgboost_env()
        create_requirements_file()
        
        print("\n🎉 ¡Configuración completada!")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: ./run_soluble_protein.sh (Linux/macOS) o run_soluble_protein.bat (Windows)")
        print("2. El modelo se ejecutará automáticamente")
        print("3. Verificar que XGBoost >= 1.3 esté instalado")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 