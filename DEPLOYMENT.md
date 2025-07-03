# 🚀 Guía de Despliegue - Soya Insights

## 📋 Prerequisitos

### **Servidor Remoto**
- **Sistema Operativo**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Docker**: Versión 20.10+
- **Docker Compose**: Versión 2.0+
- **Memoria RAM**: Mínimo 2GB (recomendado 4GB+)
- **Espacio en disco**: Mínimo 5GB libre
- **Puerto**: 8501 disponible

### **Instalación de Docker (si no está instalado)**

#### **Ubuntu/Debian:**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar repositorio oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Habilitar Docker al inicio
sudo systemctl enable docker
sudo systemctl start docker
```

#### **CentOS/RHEL:**
```bash
# Instalar Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Habilitar Docker
sudo systemctl enable docker
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

## 🚀 Despliegue Automático

### **Opción 1: Script Automático (Recomendado)**

1. **Clonar el repositorio:**
```bash
git clone <URL_DEL_REPOSITORIO>
cd soya-insights
```

2. **Ejecutar script de despliegue:**
```bash
./deploy.sh
```

3. **Verificar despliegue:**
```bash
# Verificar que el contenedor esté corriendo
docker ps

# Ver logs en tiempo real
docker-compose logs -f

# Acceder a la aplicación
curl http://localhost:8501
```

### **Opción 2: Despliegue Manual**

1. **Construir la imagen:**
```bash
docker-compose build
```

2. **Iniciar servicios:**
```bash
docker-compose up -d
```

3. **Verificar estado:**
```bash
docker-compose ps
```

## 🔧 Configuración de Producción

### **Variables de Entorno**

Crear archivo `.env` para configuración específica:

```bash
# Configuración de Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Configuración de la aplicación
ENVIRONMENT=production
DEBUG=false
```

### **Configuración de Nginx (Opcional)**

Si necesitas un proxy reverso, crear `/etc/nginx/sites-available/soya-insights`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

## 📊 Monitoreo y Mantenimiento

### **Comandos Útiles**

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f soya-insights

# Verificar uso de recursos
docker stats

# Reiniciar servicios
docker-compose restart

# Parar servicios
docker-compose down

# Actualizar aplicación
git pull
./deploy.sh
```

### **Health Check**

La aplicación incluye health check automático:

```bash
# Verificar estado de salud
curl http://localhost:8501/_stcore/health

# Verificar desde Docker
docker-compose ps
```

### **Backup de Datos**

```bash
# Crear backup de datos
docker run --rm -v soya-insights_soya_cache:/data -v $(pwd):/backup alpine tar czf /backup/soya-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restaurar backup
docker run --rm -v soya-insights_soya_cache:/data -v $(pwd):/backup alpine tar xzf /backup/soya-backup-YYYYMMDD.tar.gz -C /data
```

## 🔒 Seguridad

### **Firewall**

```bash
# Configurar firewall (Ubuntu/Debian)
sudo ufw allow 22/tcp
sudo ufw allow 8501/tcp
sudo ufw enable

# Configurar firewall (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### **SSL/TLS (Opcional)**

Para HTTPS, usar Let's Encrypt con Certbot:

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com
```

## 🐛 Troubleshooting

### **Problemas Comunes**

1. **Puerto 8501 ocupado:**
```bash
# Verificar qué está usando el puerto
sudo netstat -tulpn | grep 8501

# Matar proceso
sudo kill -9 <PID>
```

2. **Error de permisos Docker:**
```bash
# Reiniciar sesión después de agregar usuario al grupo docker
newgrp docker
```

3. **Contenedor no inicia:**
```bash
# Ver logs detallados
docker-compose logs soya-insights

# Verificar configuración
docker-compose config
```

4. **Problemas de memoria:**
```bash
# Verificar uso de memoria
free -h

# Limpiar cache Docker
docker system prune -a
```

### **Logs de Diagnóstico**

```bash
# Ver logs de la aplicación
docker-compose logs --tail=100 soya-insights

# Ver logs del sistema
journalctl -u docker.service

# Verificar recursos del sistema
htop
df -h
```

## 📞 Soporte

### **Información de Contacto**
- **Desarrollador**: Juan David Rincón
- **Empresa**: Okuo-Analytics
- **Proyecto**: Soya Insights

### **Archivos de Configuración Importantes**
- `Dockerfile`: Configuración del contenedor
- `docker-compose.yml`: Orquestación de servicios
- `.streamlit/config.toml`: Configuración de Streamlit
- `deploy.sh`: Script de despliegue automático

---

**🎯 Objetivo**: Despliegue seguro y confiable de Soya Insights en servidor remoto con configuración optimizada para producción. 

#streamlit run Soya_Insights.py
#./deploy.sh