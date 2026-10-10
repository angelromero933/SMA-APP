# Guía de Uso del Backend y Firmware

## Índice
1. [Requisitos Previos](#requisitos)
2. [Configuración del Backend](#backend)
3. [Ejecutar la app](#ejecutar)
4. [Configuración del Firmware (ESP32)](#firmware)
5. [Prueba con ESP32 Físico](#esp32-fisico)

---

## 1️ Requisitos Previos {#requisitos}

### Hardware
- ESP32 (físico o simulación en Wokwi)
- Sensores: DHT22, BMP280, MQ-135 (para pruebas físicas), ...

### Software
- **Python 3.8+**
- **Git** (para clonar el repositorio)
- **VS Code** con PlatformIO (para firmware)
- **Cuenta en HiveMQ Cloud** (gratuita)
- **Cuenta en Supabase** (gratuita)
- **Cuenta en Streamlit Cloud** (gratuita)

---

## 2️ Configuración del Backend {#backend}

### Estructura del backend

```
Monitor-Ambiental-IoT/
├── backend/
│   ├── src/
│   │   ├── app.py
│   │   └── requirements.txt
```

### Crear el archivo `.toml`, por teminal o el explorador de archivos

```bash
# 1. Navegar al backend, y pegar las crecenciales dadas correspondientes en secrets.toml
```

### Contenido del `.toml`

```env
# ============ SUPABASE ============
[supabase]
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=_secretKey_...  # Service Key

# ============ HIVEMQ CLOUD ============
[hivemq]
MQTT_BROKER=tu-cluster.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USER=tu_usuario
MQTT_PASS=tu_contraseña
MQTT_TOPIC=sensores/esp32/datos
```

### **IMPORTANTE: El `secrets.toml` NO se sube a GitHub**

```gitignore
# .gitignore (añadir si no esta en el propio)
.toml
backend/.toml
*.toml
```

---

## 3️ Activar la app {#ejecutar}

**Windows (PowerShell, CMD), Linux/macOS:**
```bash
#el comando es el mismo en todos los SO
#en backend/src/
streamlit run app.py
```

### Instalar dependencias

```bash
#instala todas las necesarias de una vez
pip install -r requirements.txt
```

### Salida esperada

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.0.39:8501
```

### Detener el backend
streamlit si tiene 30 minutos de inactividad se desactiva
`Ctrl+C` #en la terminal.


## 4️ Configuración del Firmware {#firmware}

### Estructura del firmware

```
Monitor-Ambiental-IoT/
└── firmware/
    ├── src/
    │   └── ...
    │   └── main.cpp
    ├── platformio.ini
    ├── diagram.json
    └── wokwi.toml
```

### Configurar `src/config.h`

```cpp
// ============ WIFI ============
// 🔹 Para ESP32 físico
const char* WIFI_SSID = "TU_WIFI";
const char* WIFI_PASSWORD = "TU_CONTRASEÑA";

// 🔹 Para Wokwi (simulación)
// const char* WIFI_SSID = "Wokwi-GUEST";
// const char* WIFI_PASSWORD = "";

// ============ HIVEMQ ============
const char* MQTT_BROKER = "tu-cluster.s1.eu.hivemq.cloud";
const int MQTT_PORT = 8883;
const char* MQTT_USER = "tu_usuario";
const char* MQTT_PASS = "tu_contraseña";
const char* MQTT_TOPIC = "sensores/esp32/datos";

// ============ PINES ============
#define DHT_PIN 15
#define MQ135_PIN 34
#define BMP_SDA 21
#define BMP_SCL 22
#define ...

```

---

## 5️ Prueba con ESP32 Físico {#esp32-fisico}

### Pasos

1. **Configurar Wi-Fi real en `config.h`**
   ```cpp
   const char* WIFI_SSID = "MiWiFi";
   const char* WIFI_PASSWORD = "MiContraseña";
   ```

2. **Compilar y/o subir el firmware a placa**
  

3. **Verificar funcionamiento en el monitor serie**

4. **Activar el backend (app.py)**


5. **Ver los datos en el monitor serie del ESP32**
   ```
   Datos publicados: {"temperatura":25.5,"humedad":55.2, ...}
   Wi-Fi conectado
   Conectando a HiveMQ... Conectado!
   ```

6. **Ver los datos en la pagina generada por streamlit**
