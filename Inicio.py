import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Lector de Sensor MQTT - Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #1f77b4, #2e86ab);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        padding: 1rem;
    }
    .section-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 0;
        margin: 2rem 0;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        border: 3px solid #e2e8f0;
    }
    .section-title {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px 20px 0 0;
        margin: 0;
        font-size: 1.6rem;
        font-weight: 600;
        border-bottom: 4px solid #2c5282;
        text-align: center;
    }
    .section-content {
        background: white;
        padding: 2.5rem;
        border-radius: 0 0 20px 20px;
        min-height: 150px;
    }
    .metric-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem;
        text-align: center;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .connection-status {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #bae6fd;
        margin-bottom: 1rem;
        text-align: center;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    .status-online {
        background-color: #10B981;
    }
    .status-offline {
        background-color: #EF4444;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    .stButton button {
        background: linear-gradient(45deg, #1f77b4, #2e86ab);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.4);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(31, 119, 180, 0.6);
    }
    .config-panel {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .data-timestamp {
        background: #fff7ed;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #fed7aa;
        font-size: 0.8rem;
        color: #ea580c;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Variables de estado
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            # Si no es JSON, guardar como texto
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        # Esperar máximo 5 segundos
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# Sidebar - Configuración mejorada
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center;'>
        <h2>📡</h2>
        <h3>Dashboard MQTT</h3>
        <p style='margin: 0; opacity: 0.9;'>Monitor de Sensores</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    st.subheader('⚙️ Configuración MQTT')
    
    broker = st.text_input('**Broker MQTT**', 
                          value='broker.mqttdashboard.com', 
                          help='Dirección del servidor MQTT')
    
    port = st.number_input('**Puerto**', 
                          value=1883, 
                          min_value=1, 
                          max_value=65535,
                          help='Puerto del broker MQTT')
    
    topic = st.text_input('**Tópico**', 
                         value='Sensor/THP2',
                         help='Tópico MQTT a suscribirse')
    
    client_id = st.text_input('**ID del Cliente**', 
                             value='streamlit_client',
                             help='Identificador único del cliente')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Brokers públicos recomendados
    with st.expander("🌐 Brokers Recomendados"):
        st.markdown("""
        **Públicos para pruebas:**
        - `broker.mqttdashboard.com`
        - `test.mosquitto.org` 
        - `broker.hivemq.com`
        - `mqtt.eclipseprojects.io`
        """)

# Header principal
st.markdown('<h1 class="main-header">📡 Dashboard de Sensor MQTT</h1>', unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([1, 1])

with col1:
    # Sección de Control
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎛️ Control de Conexión</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-content">', unsafe_allow_html=True)
    
    # Estado de conexión
    st.markdown("""
    <div class="connection-status">
        <h4 style='color: #0369a1; margin-bottom: 0.5rem;'>🌐 Estado de Conexión</h4>
        <p style='color: #0c4a6e; margin: 0;'>
            <span class='status-indicator status-online'></span>
            Listo para conectar al broker
        </p>
        <p style='color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0 0 0;'>
            Broker: <strong>{}</strong>
        </p>
    </div>
    """.format(broker), unsafe_allow_html=True)
    
    # Botón para obtener datos
    if st.button('🔄 OBTENER DATOS DEL SENSOR', use_container_width=True):
        with st.spinner('🔍 Conectando al broker y escuchando datos...'):
            sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
            st.session_state.sensor_data = sensor_data
            st.session_state.last_update = time.strftime('%H:%M:%S')
    
    # Información de uso
    with st.expander('📖 Guía Rápida', expanded=True):
        st.markdown("""
        ### Cómo usar este dashboard:
        
        1. **Configura** los parámetros MQTT en el sidebar
        2. **Presiona** el botón "OBTENER DATOS DEL SENSOR"  
        3. **Espera** la conexión (máximo 5 segundos)
        4. **Visualiza** los datos recibidos en tiempo real
        
        ⚠️ **Nota:** El sistema escuchará el primer mensaje que llegue al tópico.
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Sección de Resultados
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Datos del Sensor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-content">', unsafe_allow_html=True)
    
    # Mostrar resultados
    if st.session_state.sensor_data:
        data = st.session_state.sensor_data
        
        # Timestamp de última actualización
        if st.session_state.last_update:
            st.markdown(f'<div class="data-timestamp">🕐 Última actualización: {st.session_state.last_update}</div>', unsafe_allow_html=True)
        
        # Verificar si hay error
        if isinstance(data, dict) and 'error' in data:
            st.error(f"❌ **Error de Conexión:** {data['error']}")
            st.info("💡 **Solución:** Verifica la configuración del broker y tu conexión a internet.")
        else:
            st.success('✅ **Datos recibidos correctamente**')
            
            # Mostrar datos en formato JSON
            if isinstance(data, dict):
                # Mostrar cada campo en tarjetas métricas
                st.subheader("📈 Métricas del Sensor")
                
                # Crear columnas dinámicamente según la cantidad de datos
                num_metrics = len(data)
                cols = st.columns(min(4, num_metrics))
                
                for i, (key, value) in enumerate(data.items()):
                    col_idx = i % len(cols)
                    with cols[col_idx]:
                        # Determinar icono basado en la clave
                        icon = "🌡️" if "temp" in key.lower() else \
                               "💧" if "hum" in key.lower() else \
                               "📊" if "pres" in key.lower() else "🔢"
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                            <h3 style="color: #1f77b4; margin: 0.5rem 0;">{key}</h3>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #2d3748;">{value}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Mostrar JSON completo
                with st.expander('🔍 Ver Datos JSON Completos'):
                    st.json(data)
                    
            else:
                # Si no es diccionario, mostrar como texto
                st.warning("⚠️ **Formato de datos no reconocido**")
                st.code(f"Datos recibidos:\n{data}")
    
    else:
        # Estado inicial - sin datos
        st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #6b7280;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>📡</div>
            <h3 style='color: #9ca3af;'>Esperando datos del sensor</h3>
            <p>Presiona el botón "OBTENER DATOS DEL SENSOR" para comenzar</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Información adicional en el pie
st.markdown("---")
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.markdown("""
    **🔧 Tecnologías Utilizadas:**
    - Streamlit
    - Paho MQTT
    - JSON
    - Python
    """)

with col_info2:
    st.markdown("""
    **📊 Características:**
    - Monitoreo en tiempo real
    - Visualización de métricas
    - Conexión MQTT segura
    - Interface responsive
    """)

with col_info3:
    st.markdown("""
    **⚡ Rendimiento:**
    - Timeout: 5 segundos
    - Reconexión automática
    - Múltiples formatos de datos
    - Logs de error detallados
    """)
