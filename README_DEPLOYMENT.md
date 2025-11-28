# 🏨 Agente de Optimización Hotelera - HotelDo

## Descripción
Agente conversacional inteligente para AI Olympics 2.0 - Categoría GROWTH.
Ayuda a proveedores hoteleros a recuperar requests perdidos mediante optimización de pricing y disponibilidad.

## Características
- ✅ Análisis de competitividad de precios (sin revelar competidores)
- ✅ Detección de requests perdidos por falta de disponibilidad
- ✅ Recomendaciones personalizadas por hotel
- ✅ Análisis por nacionalidad y segmentación
- ✅ Dashboard interactivo
- ✅ Chat conversacional

## 🚀 Deployment Rápido en VM

### Opción 1: Google Cloud Platform (GCP)

#### Paso 1: Crear VM
```bash
# En GCP Console, crear Compute Engine VM:
# - Tipo: e2-medium (2 vCPU, 4 GB memoria)
# - SO: Ubuntu 22.04 LTS
# - Disco: 20 GB
# - Firewall: Permitir tráfico HTTP/HTTPS
```

#### Paso 2: Conectar por SSH y preparar ambiente
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Crear directorio del proyecto
mkdir hoteldo-agent
cd hoteldo-agent
```

#### Paso 3: Subir archivos
```bash
# Opción A: Usar SCP desde tu máquina local
scp streamlit_app_hoteldo.py requirements.txt detallehound_data.xlsx requests_data.csv usuario@IP_VM:/home/usuario/hoteldo-agent/

# Opción B: Usar Git (si tienes repo)
git clone [tu-repo]
```

#### Paso 4: Instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Paso 5: Ejecutar aplicación
```bash
streamlit run streamlit_app_hoteldo.py --server.port 8501 --server.address 0.0.0.0
```

#### Paso 6: Acceder
```
http://[IP_EXTERNA_VM]:8501
```

### Opción 2: Railway (Más Rápido - No-Code Deploy)

1. Crear cuenta en railway.app
2. New Project → Deploy from GitHub
3. Conectar tu repositorio
4. Railway detecta automáticamente Streamlit
5. Listo! URL generada automáticamente

### Opción 3: Streamlit Cloud (Gratis)

1. Subir código a GitHub (público o privado)
2. Ir a share.streamlit.io
3. New app → Seleccionar tu repo
4. Deploy en 2 minutos
5. URL: tu-app.streamlit.app

## 📁 Estructura de Archivos

```
hoteldo-agent/
├── streamlit_app_hoteldo.py    # App principal
├── requirements.txt             # Dependencias
├── detallehound_data.xlsx       # Datos de competitividad
├── requests_data.csv            # Datos de demanda
└── README.md                    # Esta guía
```

## 🔧 Configuración

### Variables de Entorno (opcional)
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_THEME_BASE="light"
```

### Para producción con dominio propio
```bash
# Instalar nginx
sudo apt install nginx -y

# Configurar reverse proxy
sudo nano /etc/nginx/sites-available/hoteldo

# Contenido:
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Activar configuración
sudo ln -s /etc/nginx/sites-available/hoteldo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🎯 Uso del Agente

### Como proveedor hotelero:

1. **Seleccionar tu hotel** en el sidebar
2. **Modo Chat:** Hacer preguntas directas
   - "¿Cómo está mi competitividad?"
   - "¿Cuántos requests estoy perdiendo?"
   - "Dame recomendaciones"

3. **Modo Dashboard:** Ver análisis completo con visualizaciones

### Funcionalidades clave:
- 📊 Comparativa de precios vs mercado (sin revelar competidores)
- 📉 Análisis de requests perdidos por nacionalidad
- 💡 Recomendaciones accionables priorizadas
- 🎯 Estimación de impacto de cambios

## 🔐 Seguridad

- **CRÍTICO:** Nunca menciona nombres de competidores (EXP, HBG)
- Análisis agregado de "mercado"
- Datos sensibles no expuestos al cliente final

## 📊 Datos Requeridos

### detallehound_data.xlsx
- Comparativa B2B y B2C
- VAR (diferencial vs mercado)
- Precios PAM, EXP, HBG

### requests_data.csv
- Búsquedas por hotel y nacionalidad
- Disponibilidad respondida
- Conversión y revenue

## 🚨 Troubleshooting

### Error: Puerto ocupado
```bash
# Ver qué usa el puerto 8501
sudo lsof -i :8501

# Cambiar puerto
streamlit run app.py --server.port 8502
```

### Error: Memoria insuficiente
```bash
# Monitorear uso
free -h

# Agregar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 Soporte

Para AI Olympics 2.0 - Categoría GROWTH
Contacto: [tu-email]

## 🏆 Next Steps Post-MVP

1. Autenticación por hotel
2. Conexión a SQL/Metabase real-time
3. Alertas proactivas
4. API REST
5. Integración con sistemas hoteleros
