"""
Cyber Sentinel — Security Analytics Dashboard
==============================================
Dashboard académico e interactivo de analítica de eventos de ciberseguridad,
construido sobre el dataset público 'cybersecurity_attacks.csv'
(incribo-inc/cybersecurity_attacks — ~40.000 eventos, 25 variables).

IMPORTANTE (uso educativo):
Este proyecto utiliza un dataset SINTÉTICO con fines exclusivamente
académicos y de análisis exploratorio de datos. No constituye un SIEM real,
ni un sistema de detección de intrusiones en producción, ni debe utilizarse
para tomar decisiones de seguridad reales.

Autor: Proyecto académico — Cyber Sentinel
Stack: Python 3.11 + Streamlit + Pandas + NumPy + Plotly
"""

import streamlit as st
import pandas as pd
from datetime import date

from src.data_loader import load_and_enrich_data, apply_filters, compute_kpis
from src.styles import CUSTOM_CSS, kpi_card_html
from src import charts

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Cyber Sentinel | Security Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
try:
    df = load_and_enrich_data()
    DATA_LOAD_ERROR = None
except FileNotFoundError:
    df = pd.DataFrame()
    DATA_LOAD_ERROR = (
        "No se encontró el archivo 'data/cybersecurity_attacks.csv'. "
        "Descárgalo desde https://github.com/incribo-inc/cybersecurity_attacks "
        "y colócalo en la carpeta 'data/' del proyecto."
    )

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.markdown("<div class='main-title'>🛡️ Cyber Sentinel</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='main-subtitle'>Interactive Cybersecurity Event Monitoring & Risk Analytics</div>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="disclaimer-banner">
        ⚠️ <b>Aviso académico:</b> este dashboard utiliza un conjunto de datos <b>sintético</b>
        (<i>incribo-inc/cybersecurity_attacks</i>) con fines exclusivamente educativos y de
        análisis exploratorio de datos (EDA). <b>No es</b> un SIEM real ni un sistema de
        detección de intrusiones en producción, y no debe emplearse para decisiones de
        seguridad reales.
    </div>
    """,
    unsafe_allow_html=True,
)

if DATA_LOAD_ERROR:
    st.error(DATA_LOAD_ERROR)
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — Filtros
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔍 Filtros de Análisis")

    min_date, max_date = df["Date"].min(), df["Date"].max()
    date_range = st.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, date):
        date_range = (date_range, date_range)

    st.markdown("---")
    attack_types = st.multiselect(
        "Tipo de Ataque", sorted(df["Attack Type"].unique()),
        default=sorted(df["Attack Type"].unique()),
    )
    severities = st.multiselect(
        "Nivel de Severidad", ["Low", "Medium", "High"],
        default=["Low", "Medium", "High"],
    )
    protocols = st.multiselect(
        "Protocolo", sorted(df["Protocol"].unique()),
        default=sorted(df["Protocol"].unique()),
    )
    actions = st.multiselect(
        "Acción Tomada", sorted(df["Action Taken"].unique()),
        default=sorted(df["Action Taken"].unique()),
    )

    with st.expander("Filtros avanzados"):
        traffic_types = st.multiselect(
            "Tipo de Tráfico", sorted(df["Traffic Type"].unique()),
            default=sorted(df["Traffic Type"].unique()),
        )
        segments = st.multiselect(
            "Segmento de Red", sorted(df["Network Segment"].unique()),
            default=sorted(df["Network Segment"].unique()),
        )
        packet_types = st.multiselect(
            "Tipo de Paquete", sorted(df["Packet Type"].unique()),
            default=sorted(df["Packet Type"].unique()),
        )
        log_sources = st.multiselect(
            "Fuente del Log", sorted(df["Log Source"].unique()),
            default=sorted(df["Log Source"].unique()),
        )
        anomaly_range = st.slider(
            "Rango de Puntaje de Anomalía",
            float(df["Anomaly Scores"].min()), float(df["Anomaly Scores"].max()),
            (float(df["Anomaly Scores"].min()), float(df["Anomaly Scores"].max())),
        )

    st.markdown("---")
    st.markdown(
        """
        <div class="glossary-box">
        <b>Glosario rápido</b>
        <ul>
            <li><b>Anomaly Score</b>: puntaje 0–100 que estima cuánto se aleja un evento del comportamiento normal.</li>
            <li><b>IoC (Indicator of Compromise)</b>: evidencia técnica de que un sistema pudo verse comprometido.</li>
            <li><b>Attack Signature</b>: patrón conocido usado para identificar un tipo de ataque.</li>
            <li><b>Severity Level</b>: nivel de criticidad asignado al evento (Low / Medium / High).</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Fuente de datos: github.com/incribo-inc/cybersecurity_attacks (dataset sintético, CC).")

# ---------------------------------------------------------------------------
# Aplicar filtros
# ---------------------------------------------------------------------------
filtered_df = apply_filters(
    df,
    date_range=date_range,
    protocols=protocols,
    attack_types=attack_types,
    severities=severities,
    actions=actions,
    traffic_types=traffic_types,
    segments=segments,
    packet_types=packet_types,
    anomaly_range=anomaly_range,
    log_sources=log_sources,
)

if filtered_df.empty:
    st.warning("No hay eventos que coincidan con los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
kpis = compute_kpis(filtered_df)

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(kpi_card_html(f"{kpis['total']:,}", "Eventos Totales"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card_html(f"{kpis['pct_blocked']:.1f}%", "Bloqueados"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card_html(f"{kpis['pct_high']:.1f}%", "Severidad Alta"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card_html(f"{kpis['avg_anomaly']:.1f}", "Anomaly Score Prom."), unsafe_allow_html=True)
with k5:
    st.markdown(kpi_card_html(f"{kpis['ioc_rate']:.1f}%", "Tasa IoC Detectado"), unsafe_allow_html=True)
with k6:
    st.markdown(kpi_card_html(str(kpis['top_attack']), "Ataque Más Frecuente"), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Navegación por pestañas
# ---------------------------------------------------------------------------
tab_overview, tab_threats, tab_network, tab_detection, tab_geo, tab_raw = st.tabs(
    ["📊 Resumen", "🎯 Amenazas", "🌐 Red y Tráfico", "🛡️ Detección y Respuesta",
     "🌍 Geografía y Usuarios", "📄 Datos Crudos"]
)

# --- TAB: Resumen ----------------------------------------------------------
with tab_overview:
    st.markdown("<div class='section-title'>Panorama General</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.attack_type_donut(filtered_df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.severity_bar(filtered_df), use_container_width=True)

    st.plotly_chart(charts.monthly_timeline(filtered_df), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(charts.protocol_bar(filtered_df), use_container_width=True)
    with c4:
        st.plotly_chart(charts.action_by_severity_stacked(filtered_df), use_container_width=True)

# --- TAB: Amenazas -----------------------------------------------------
with tab_threats:
    st.markdown("<div class='section-title'>Análisis de Amenazas y Anomalías</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.anomaly_score_histogram(filtered_df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.anomaly_score_boxplot(filtered_df), use_container_width=True)

    st.plotly_chart(charts.traffic_vs_attack_heatmap(filtered_df), use_container_width=True)
    st.plotly_chart(charts.network_segment_sunburst(filtered_df), use_container_width=True)

    st.markdown(
        """
        <div class="info-box">
        <b>Cómo interpretar el Anomaly Score:</b> valores más altos indican comportamiento
        más atípico respecto al tráfico habitual de la red. En este dataset sintético, el
        puntaje se distribuye de forma aproximadamente uniforme entre 0 y 100, por lo que
        conviene compararlo siempre junto con la severidad asignada al evento.
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- TAB: Red y Tráfico --------------------------------------------------
with tab_network:
    st.markdown("<div class='section-title'>Actividad de Red y Tráfico</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.hour_day_heatmap(filtered_df), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.top_ports_bar(filtered_df, "Destination Port"), use_container_width=True)
    with c2:
        st.plotly_chart(charts.top_ports_bar(filtered_df, "Source Port"), use_container_width=True)

    st.plotly_chart(charts.packet_length_by_protocol(filtered_df), use_container_width=True)

# --- TAB: Detección y Respuesta -----------------------------------------
with tab_detection:
    st.markdown("<div class='section-title'>Cobertura de Detección y Respuesta</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.detection_coverage_bar(filtered_df), use_container_width=True)

    st.markdown(
        """
        <div class="info-box">
        <b>Nota metodológica:</b> las columnas <i>Malware Indicators</i>, <i>Alerts/Warnings</i>,
        <i>Firewall Logs</i> e <i>IDS/IPS Alerts</i> del dataset original solo contienen un valor
        fijo o un valor nulo. Aquí se interpretan como banderas booleanas
        (presencia/ausencia del indicador) para estimar la cobertura relativa de cada
        mecanismo de detección sobre los eventos filtrados.
        </div>
        """,
        unsafe_allow_html=True,
    )

    signature_counts = filtered_df["Attack Signature"].value_counts().reset_index()
    signature_counts.columns = ["Attack Signature", "Eventos"]
    st.markdown("<div class='section-title'>Firmas de Ataque Detectadas</div>", unsafe_allow_html=True)
    st.dataframe(signature_counts, use_container_width=True, hide_index=True)

# --- TAB: Geografía y Usuarios -------------------------------------------
with tab_geo:
    st.markdown("<div class='section-title'>Distribución Geográfica y de Dispositivos</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.top_locations_bar(filtered_df, "Geo_Region"), use_container_width=True)
    with c2:
        st.plotly_chart(charts.top_locations_bar(filtered_df, "Geo_City"), use_container_width=True)

    fig_browser, fig_os = charts.browser_os_pies(filtered_df)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_browser, use_container_width=True)
    with c4:
        st.plotly_chart(fig_os, use_container_width=True)

    st.markdown(
        """
        <div class="info-box">
        <b>Nota:</b> la geolocalización proviene directamente de la columna
        <i>Geo-location Data</i> del dataset (texto "Ciudad, Región") y no se procesa con
        ningún servicio externo de geolocalización, en línea con las restricciones del
        proyecto. La familia de navegador/SO se infiere del campo
        <i>Device Information</i> mediante coincidencia de patrones de texto simples.
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- TAB: Datos Crudos ----------------------------------------------------
with tab_raw:
    st.markdown("<div class='section-title'>Explorador de Eventos Filtrados</div>", unsafe_allow_html=True)
    st.caption(f"Mostrando {len(filtered_df):,} de {len(df):,} eventos totales según los filtros activos.")

    display_cols = [
        "Timestamp", "Source IP Address", "Destination IP Address", "Protocol",
        "Attack Type", "Severity Level", "Action Taken", "Traffic Type",
        "Anomaly Scores", "Network Segment", "Geo-location Data",
    ]
    st.dataframe(
        filtered_df[display_cols].sort_values("Timestamp", ascending=False).head(500),
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar eventos filtrados (CSV)",
        data=csv_bytes,
        file_name="cyber_sentinel_filtered_events.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="footer-note">
        Cyber Sentinel — Security Analytics Dashboard · Proyecto académico ·
        Dataset sintético (incribo-inc/cybersecurity_attacks) · No apto para uso en producción.
    </div>
    """,
    unsafe_allow_html=True,
)
