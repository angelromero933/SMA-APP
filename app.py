import paho.mqtt.client as mqtt
from supabase import create_client
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import numpy as np
import json
from datetime import datetime

st.set_page_config(
    page_title="Monitor Ambiental IoT",
    page_icon="☁️",
    layout="wide",
)

st.logo(
    "lg.png", 
    link="https://sma-monitor.streamlit.app", 
    size="large", 
    icon_image="logo.png"
)

SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
MQTT_BROKER = st.secrets["hivemq"]["MQTT_BROKER"]
MQTT_PORT = st.secrets["hivemq"]["MQTT_PORT"]
MQTT_USER = st.secrets["hivemq"]["MQTT_USER"]
MQTT_PASS = st.secrets["hivemq"]["MQTT_PASS"]
MQTT_TOPIC = st.secrets["hivemq"]["MQTT_TOPIC"]

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Error: SUPABASE_URL o SUPABASE_KEY no están configuradas en el entorno.")
    st.stop()

@st.cache_resource
def iniciar_servicios():
    client_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    broker = MQTT_BROKER
    port = MQTT_PORT
    user = MQTT_USER
    pw = MQTT_PASS
    topic = MQTT_TOPIC

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            data = {
                "Temperatura": payload.get("Temperatura", 0.0),
                "Humedad": payload.get("Humedad", 0),
                "Presion": payload.get("Presion", 0.0),
                "Fecha": payload.get("Fecha", datetime.now().isoformat()),
                "Gas-Ppm": payload.get("Gas-Ppm", 0.0),
                "creator": payload.get("creator", "86d8ce35-705a-4413-9791-9192e5470a76"),
            }
            client_supabase.table("Lecturas").insert(data).execute()
        except Exception as e:
            print(f"Error procesando mensaje MQTT: {e}")

    client_mqtt = mqtt.Client()
    client_mqtt.username_pw_set(user, pw)
    client_mqtt.tls_set()
    client_mqtt.on_message = on_message
    client_mqtt.connect(broker, port, 60)
    client_mqtt.subscribe(topic)
    client_mqtt.loop_start() 
    
    return client_supabase

supabase = iniciar_servicios()

def obtener_todos():
    try:
        res = supabase.table("Lecturas").select("Temperatura, Humedad, Presion, Fecha, \"Gas-Ppm\"").order("id", desc=True).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def obtener_segun(limite: int = 1):
    try:
        res = supabase.table("Lecturas").select("Temperatura, Humedad, Presion, Fecha, \"Gas-Ppm\"").order("id", desc=True).limit(limite).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def obtener_ultimo(limite: int = 1):
    try:
        res = supabase.table("Lecturas").select("Temperatura, Humedad, Presion, Fecha, \"Gas-Ppm\"").order("id", desc=True).limit(limite).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def crear_gauge_gas(valor_actual):
    """Genera un tacómetro para los niveles de Gas PPM."""
    rango_completo = list((0, 1))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_actual,
        domain={'x': rango_completo, 'y': rango_completo},
        title={'text': "Calidad del Aire (Gas PPM)"},
        gauge={
            'axis': {'range': list((0, 1800)), 'tickwidth': 1},
            'bar': {'color': "gray"},
            'steps': [
                {'range': list((0, 349)), 'color': '#98fb98'},
                {'range': list((350, 999)), 'color': '#f4e04d'},
                {'range': list((1000, 1800)), 'color': '#fa8072'}
            ]
        }
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=80, b=20), height=300)
    return fig


def main():
    st.title("Proyecto IoT: Monitor Ambiental")
    st.divider()

    df_datos = obtener_segun(10)
    if df_datos.empty:
        st.info("Esperando que ingresen lecturas a la base de datos o verificando conexión...")
        st.stop()

    lineaTemp = px.line(df_datos, x='Fecha', y='Temperatura', title='Evolución de la Temperatura', labels={'Temperatura': 'Temperatura (°C)', 'Fecha': 'Fecha y Hora'}, markers=True)
    lineaHum = px.line(df_datos, x='Fecha', y='Humedad', title='Evolución de la Humedad Relativa', labels={'Humedad': 'Humedad (%)', 'Fecha': 'Fecha y Hora'}, markers=True)
    lineaPresion = px.line(df_datos, x='Fecha', y='Presion', title='Evolución de la Presión Atmosférica', labels={'Presion': 'Presión (hPa)', 'Fecha': 'Fecha y Hora'}, markers=True)

    tab1, tab2, tab3 = st.tabs(["Gráficos en Tiempo Real", "Histórico de Datos", "Registros Base de Datos"])

    with tab1:
        st.subheader("Estado actual de los sensores")
        live_placeholder = st.empty()
        
        with live_placeholder.container():
            df_ultimo_vivo = obtener_ultimo(1)
            df_datos_vivos = obtener_segun(10)
            
            if not df_ultimo_vivo.empty:
                gas_vivo = float(df_ultimo_vivo["Gas-Ppm"].iloc[0])
                temp_vivo = float(df_ultimo_vivo["Temperatura"].iloc[0])
                hum_vivo = float(df_ultimo_vivo["Humedad"].iloc[0])
                presion_vivo = float(df_ultimo_vivo["Presion"].iloc[0])
                
                fig_gas_viva = crear_gauge_gas(gas_vivo)
                
                col_grafico, col_metricas = st.columns([2, 1])
                with col_grafico:
                    st.plotly_chart(fig_gas_viva, use_container_width=True, key="gauge_live")
                with col_metricas:
                    st.markdown("### Últimas Mediciones")
                    st.metric(label="Temperatura Actual", value=f"{temp_vivo} °C")
                    st.metric(label="Humedad Relativa", value=f"{hum_vivo} %")
                    st.metric(label="Presión Atmosférica", value=f"{presion_vivo} hPa")
            else:
                st.warning("No hay lecturas en tiempo real disponibles.")
        
        time.sleep(30)
        st.rerun()

    with tab2:
        st.subheader("Evolución temporal de variables climáticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(lineaTemp, use_container_width=True)
        with col2:
            st.plotly_chart(lineaHum, use_container_width=True)
        with col3:
            st.plotly_chart(lineaPresion, use_container_width=True)

    with tab3:
        modo = st.radio("¿Cómo deseas ingresar el número?", ["Elegir de la lista", "Escribir número personalizado"])
        
        if modo == "Elegir de la lista":
            opcion = st.selectbox("registros: ", ["todos", "100", "300", "500"], index=None, placeholder="Selecciona una opcion")
        else:
            opcion = st.number_input("Escribe cualquier número:", value=0, step=1)

        if opcion is not None:
            st.write(f"Has seleccionado: {opcion}")
            plot_container = st.empty()

            if opcion == "todos":
                df_datos_tab3 = obtener_todos()
            elif str(opcion).isdigit() or isinstance(opcion, (int, float)):
                df_datos_tab3 = obtener_segun(int(opcion))
            else:
                df_datos_tab3 = pd.DataFrame()

            with plot_container.container():
                progress_bar = st.progress(0, text="Calculando datos del gráfico...")
                for percent_complete in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1)
                plot_container.empty()

            st.subheader(f"Últimos {len(df_datos_tab3)} registros en la Base de Datos (Supabase)")
            st.dataframe(df_datos_tab3, use_container_width=True, hide_index=False)
        else:
            st.info("Por favor, selecciona una opción para cargar los datos.")

if __name__ == '__main__':
    main()
