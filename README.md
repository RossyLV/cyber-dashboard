# 🛡️ Cyber Sentinel — Security Analytics Dashboard

**Interactive Cybersecurity Event Monitoring & Risk Analytics**

Dashboard académico, interactivo y visualmente profesional para el análisis
exploratorio de eventos de ciberseguridad, construido con **Python 3.11**,
**Streamlit**, **Pandas**, **NumPy** y **Plotly**.

> ⚠️ **Aviso importante:** este proyecto utiliza el dataset **sintético**
> [`incribo-inc/cybersecurity_attacks`](https://github.com/incribo-inc/cybersecurity_attacks)
> con fines **exclusivamente educativos y de análisis exploratorio de datos (EDA)**.
> **No es** un SIEM real, ni un sistema de detección de intrusiones (IDS/IPS)
> en producción, y **no debe utilizarse** para tomar decisiones de seguridad reales.

---

## 1. Origen y evolución del proyecto

Este dashboard parte de una plantilla previa (`cybersecurity_dashboard.py`)
que usaba datos simulados con `numpy.random` y una taxonomía básica de
incidentes ("Phishing Email", "Malware", etc.). De esa plantilla se
**reutilizó**:

- La estructura visual general (título, subtítulo, banda informativa, cajas
  de información con borde de color, codificación de colores por riesgo).
- El uso de `st.set_page_config`, `st.sidebar` para filtros, y `plotly.express`
  como motor de gráficos.
- La idea de combinar KPIs numéricos + gráficos + tabla de eventos +
  sección educativa/glosario.

Y se **reemplazó por completo**:

- La fuente de datos: ya no se generan incidentes aleatorios, sino que se
  carga y procesa el dataset real `cybersecurity_attacks.csv` (40.000
  eventos, 25 variables).
- Toda la lógica analítica: KPIs, filtros, agregaciones y visualizaciones
  se rediseñaron en torno a las columnas reales del dataset (protocolos,
  puertos, firmas de ataque, indicadores de compromiso, etc.), sin inventar
  columnas ni categorías inexistentes.
- La arquitectura del código: se modularizó en `src/data_loader.py`,
  `src/charts.py` y `src/styles.py` en lugar de un único script monolítico.
- La identidad visual: paleta oscura tipo centro de operaciones de
  seguridad (SOC), tarjetas KPI con sombra y gradiente, y un aviso académico
  permanente sobre la naturaleza sintética del dataset.

---

## 2. Dataset

- **Fuente:** [github.com/incribo-inc/cybersecurity_attacks](https://github.com/incribo-inc/cybersecurity_attacks)
- **Archivo:** `cybersecurity_attacks.csv`
- **Tamaño:** 40.000 registros × 25 variables originales
- **Naturaleza:** datos **sintéticos**, generados para fines de práctica y
  demostración (no corresponden a incidentes reales)

### Columnas originales (sin modificar)

`Timestamp`, `Source IP Address`, `Destination IP Address`, `Source Port`,
`Destination Port`, `Protocol`, `Packet Length`, `Packet Type`,
`Traffic Type`, `Payload Data`, `Malware Indicators`, `Anomaly Scores`,
`Alerts/Warnings`, `Attack Type`, `Attack Signature`, `Action Taken`,
`Severity Level`, `User Information`, `Device Information`,
`Network Segment`, `Geo-location Data`, `Proxy Information`,
`Firewall Logs`, `IDS/IPS Alerts`, `Log Source`.

### Columnas derivadas (calculadas en `src/data_loader.py`)

| Columna derivada | Origen | Descripción |
|---|---|---|
| `Date`, `Year`, `Month`, `Hour`, `DayOfWeek` | `Timestamp` | Descomposición temporal para series de tiempo y mapas de calor |
| `IoC_Detected` | `Malware Indicators` (no nulo) | Bandera booleana de indicador de compromiso |
| `Alert_Triggered` | `Alerts/Warnings` (no nulo) | Bandera booleana de alerta disparada |
| `Firewall_Logged` | `Firewall Logs` (no nulo) | Bandera booleana de registro en firewall |
| `IDS_IPS_Alerted` | `IDS/IPS Alerts` (no nulo) | Bandera booleana de alerta IDS/IPS |
| `Has_Proxy` | `Proxy Information` (no nulo) | Bandera booleana de uso de proxy |
| `Is_Blocked` | `Action Taken == "Blocked"` | Bandera booleana de bloqueo |
| `Geo_City`, `Geo_Region` | `Geo-location Data` (split por coma) | Ciudad y región reportadas |
| `Browser_Family`, `OS_Family` | `Device Information` (user-agent) | Familia de navegador/SO vía coincidencia de patrones de texto |

No se realizan llamadas a APIs externas, servicios de geolocalización,
autenticación ni modelos de machine learning: toda la lógica es analítica
(pandas/numpy) y determinista.

---

## 3. Estructura del proyecto

```
cyber_sentinel/
├── app.py                     # Aplicación principal Streamlit (UI y navegación)
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # Carga, limpieza, feature engineering, filtros, KPIs
│   ├── charts.py              # Construcción de todas las figuras Plotly
│   └── styles.py              # CSS personalizado y paleta de colores
├── data/
│   └── cybersecurity_attacks.csv   # Dataset real (40.000 filas, 25 columnas)
├── killercoda/                # Escenario de despliegue para Killercoda
│   ├── index.json
│   └── 01-run-dashboard/
│       ├── intro.md
│       ├── step1.md
│       └── finish.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

---

## 4. Funcionalidades del dashboard

### Filtros interactivos (barra lateral)
Rango de fechas, tipo de ataque, nivel de severidad, protocolo, acción
tomada y, en un panel avanzado desplegable: tipo de tráfico, segmento de
red, tipo de paquete, fuente del log y rango de puntaje de anomalía.

### KPIs en tiempo real
Eventos totales, % bloqueados, % severidad alta, puntaje de anomalía
promedio, tasa de detección de IoC y ataque más frecuente — todos
recalculados dinámicamente según los filtros activos.

### Pestañas de análisis
1. **📊 Resumen** — distribución por tipo de ataque, severidad, evolución
   mensual, protocolo y acción tomada vs. severidad.
2. **🎯 Amenazas** — histograma y boxplot del Anomaly Score por severidad,
   mapa de calor tráfico↔ataque, sunburst segmento↔ataque.
3. **🌐 Red y Tráfico** — mapa de actividad hora×día, puertos de origen y
   destino más frecuentes, distribución de longitud de paquete por
   protocolo.
4. **🛡️ Detección y Respuesta** — cobertura de indicadores (IoC, alertas,
   firewall, IDS/IPS, proxy) y tabla de firmas de ataque.
5. **🌍 Geografía y Usuarios** — regiones/ciudades más reportadas,
   navegadores y sistemas operativos inferidos del user-agent.
6. **📄 Datos Crudos** — explorador tabular de eventos filtrados con
   descarga en CSV.

---

## 5. Ejecución local (sin Docker)

Requisitos: Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

La aplicación quedará disponible en `http://localhost:8501`.

---

## 6. Ejecución con Docker

```bash
docker build -t cyber-sentinel .
docker run -d -p 8501:8501 --name cyber-sentinel-dashboard cyber-sentinel
```

O bien, con **docker-compose**:

```bash
docker compose up --build
```

Accede luego a `http://localhost:8501`.

---

## 7. Despliegue en Killercoda

La carpeta `killercoda/` contiene un escenario mínimo (`index.json` +
pasos en Markdown) listo para importarse en una plataforma Killercoda:
construye la imagen con `docker build`, levanta el contenedor exponiendo el
puerto `8501` y expone dicho puerto en la interfaz del entorno para
visualizar el dashboard en vivo durante la clase.

---

## 8. Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework de UI | Streamlit |
| Procesamiento de datos | Pandas, NumPy |
| Visualización | Plotly Express / Graph Objects |
| Contenerización | Docker / docker-compose |
| Demostración en clase | Killercoda |

Sin bases de datos, sin Redis, sin autenticación, sin APIs de terceros
(VirusTotal, geolocalización externa, etc.), sin WebSockets y sin
machine learning obligatorio, conforme a los requisitos del proyecto.

---

## 9. Limitaciones y alcance académico

- El dataset es **sintético**: los patrones observados (distribución
  uniforme del Anomaly Score, proporciones fijas de IoC/alertas, etc.) no
  reflejan necesariamente el comportamiento de tráfico malicioso real.
- Las columnas con un único valor no nulo posible (`Malware Indicators`,
  `Alerts/Warnings`, `Firewall Logs`, `IDS/IPS Alerts`) se interpretan como
  banderas de presencia/ausencia, no como catálogos de indicadores.
- La geolocalización proviene del propio dataset (texto libre) y no se
  contrasta con ningún servicio de geolocalización real ni con
  coordenadas verificadas.
- Este proyecto se entrega con fines **didácticos**, como ejercicio de
  analítica de datos aplicada a ciberseguridad, y no debe presentarse ni
  utilizarse como herramienta de monitoreo de seguridad en producción.
