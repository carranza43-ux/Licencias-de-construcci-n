import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import os
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Licencias de Construcción",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== BASE DE DATOS ====================
DB_PATH = "licencias.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla de usuarios (demo)
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            usuario TEXT UNIQUE,
            clave TEXT,
            nombre TEXT,
            rol TEXT
        )
    ''')
    
    # Tabla de expedientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS expedientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_radicado TEXT UNIQUE,
            fecha_radicacion TEXT,
            fecha_inicio_termino TEXT,
            estado TEXT,
            tipo_obra TEXT,
            propietario TEXT,
            apoderado TEXT,
            direccion TEXT,
            zona TEXT,
            superficie REAL,
            valor_obra REAL,
            revisor_actual TEXT,
            dias_transcurridos INTEGER DEFAULT 0,
            termino_suspendido TEXT DEFAULT 'No',
            fecha_limite_respuesta TEXT,
            prorroga_activa TEXT DEFAULT 'No',
            observaciones TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    
    # Tabla de requerimientos
    c.execute('''
        CREATE TABLE IF NOT EXISTS requerimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_requerimiento TEXT,
            numero_radicado TEXT,
            fecha_acta TEXT,
            tipo TEXT,
            descripcion TEXT,
            fecha_limite_respuesta TEXT,
            fecha_respuesta TEXT,
            estado TEXT,
            elaborado_por TEXT,
            observaciones TEXT
        )
    ''')
    
    # Tabla de prórrogas
    c.execute('''
        CREATE TABLE IF NOT EXISTS prorrogas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_prorroga TEXT,
            numero_radicado TEXT,
            solicitante TEXT,
            calidad TEXT,
            fecha_solicitud TEXT,
            motivo TEXT,
            dias_solicitados INTEGER,
            decision TEXT,
            fecha_decision TEXT,
            nuevo_vencimiento TEXT,
            observaciones TEXT
        )
    ''')
    
    # Usuarios demo
    usuarios_demo = [
        ('admin', 'admin123', 'Administrador del Sistema', 'Administrador'),
        ('juridica', 'juridica123', 'Patricia Gómez', 'Revisor Jurídico'),
        ('arquitectura', 'arq123', 'Laura Rivas', 'Revisor Arquitectónico'),
        ('ingenieria', 'ing123', 'Carlos Méndez', 'Revisor Ingeniería'),
        ('ventanilla', 'ventanilla123', 'Ana Receptor', 'Ventanilla'),
    ]
    
    for u in usuarios_demo:
        c.execute('INSERT OR IGNORE INTO usuarios (usuario, clave, nombre, rol) VALUES (?, ?, ?, ?)', u)
    
    # Datos de ejemplo si la tabla está vacía
    c.execute('SELECT COUNT(*) FROM expedientes')
    if c.fetchone()[0] == 0:
        hoy = datetime.now()
        ejemplos = [
            ('RAD-2026-5001', (hoy - timedelta(days=25)).strftime('%Y-%m-%d'), (hoy - timedelta(days=23)).strftime('%Y-%m-%d'),
             'En revisión jurídica', 'Nueva Construcción', 'Constructora del Valle S.A.', '', 'Calle 45 #12-34', 'Norte', 320.5, 850000000,
             'Patricia Gómez', 12, 'No', None, 'No', 'Documentación completa', hoy.strftime('%Y-%m-%d')),
            ('RAD-2026-5002', (hoy - timedelta(days=40)).strftime('%Y-%m-%d'), (hoy - timedelta(days=38)).strftime('%Y-%m-%d'),
             'En evaluación arquitectónica', 'Ampliación', 'Juan Pérez García', 'Dr. Andrés Molina', 'Carrera 7 #89-01', 'Centro', 180.0, 420000000,
             'Laura Rivas', 22, 'No', None, 'No', '', hoy.strftime('%Y-%m-%d')),
            ('RAD-2026-5003', (hoy - timedelta(days=35)).strftime('%Y-%m-%d'), (hoy - timedelta(days=33)).strftime('%Y-%m-%d'),
             'En evaluación de ingeniería', 'Remodelación', 'Inmobiliaria Horizonte', '', 'Av. Principal 234', 'Sur', 450.0, 1200000000,
             'Carlos Méndez', 28, 'No', None, 'No', 'Pendiente revisión estructural', hoy.strftime('%Y-%m-%d')),
            ('RAD-2026-5004', (hoy - timedelta(days=20)).strftime('%Y-%m-%d'), (hoy - timedelta(days=18)).strftime('%Y-%m-%d'),
             'En requerimiento', 'Nueva Construcción', 'María Elena Soto', 'Abg. Carolina Ruiz', 'Calle 12 #5-67', 'Oriente', 95.0, 280000000,
             'Patricia Gómez', 15, 'Sí', (hoy + timedelta(days=12)).strftime('%Y-%m-%d'), 'No', 'Esperando planos estructurales', hoy.strftime('%Y-%m-%d')),
            ('RAD-2026-5005', (hoy - timedelta(days=50)).strftime('%Y-%m-%d'), (hoy - timedelta(days=48)).strftime('%Y-%m-%d'),
             'Acto proyectado', 'Regularización', 'Grupo Constructor Andino', '', 'Carrera 15 #23-45', 'Poniente', 600.0, 2100000000,
             'Patricia Gómez', 35, 'No', None, 'Sí', '', hoy.strftime('%Y-%m-%d')),
            ('RAD-2026-5006', (hoy - timedelta(days=55)).strftime('%Y-%m-%d'), (hoy - timedelta(days=53)).strftime('%Y-%m-%d'),
             'Ejecutoriado', 'Nueva Construcción', 'Pedro Ramírez López', '', 'Diagonal 30 #8-90', 'Residencial', 220.0, 680000000,
             'Laura Rivas', 42, 'No', None, 'No', 'Licencia otorgada', hoy.strftime('%Y-%m-%d')),
        ]
        c.executemany('''
            INSERT INTO expedientes (numero_radicado, fecha_radicacion, fecha_inicio_termino, estado, tipo_obra,
            propietario, apoderado, direccion, zona, superficie, valor_obra, revisor_actual, dias_transcurridos,
            termino_suspendido, fecha_limite_respuesta, prorroga_activa, observaciones, ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ejemplos)
    
    conn.commit()
    conn.close()

# Inicializar DB
init_db()

# ==================== AUTENTICACIÓN ====================
def login():
    st.markdown("## 🏗️ Sistema de Gestión de Licencias de Construcción")
    st.markdown("### Inicio de sesión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", use_container_width=True):
            conn = get_connection()
            c = conn.cursor()
            c.execute('SELECT nombre, rol FROM usuarios WHERE usuario=? AND clave=?', (usuario, clave))
            result = c.fetchone()
            conn.close()
            
            if result:
                st.session_state['logged_in'] = True
                st.session_state['nombre'] = result[0]
                st.session_state['rol'] = result[1]
                st.session_state['usuario'] = usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        
        st.info("""
        **Usuarios de prueba:**
        - admin / admin123 (Administrador)
        - juridica / juridica123
        - arquitectura / arq123
        - ingenieria / ing123
        - ventanilla / ventanilla123
        """)

# ==================== FUNCIONES AUXILIARES ====================
def calcular_dias_restantes(dias_transcurridos, suspendido):
    if suspendido == 'Sí':
        return "Suspendido"
    return max(0, 45 - dias_transcurridos)

def color_estado(estado):
    colores = {
        'Radicado': 'blue',
        'En revisión jurídica': 'orange',
        'En evaluación arquitectónica': 'violet',
        'En evaluación de ingeniería': 'violet',
        'En requerimiento': 'red',
        'Acto proyectado': 'blue',
        'Acto en revisión': 'blue',
        'Acto firmado': 'green',
        'Notificado': 'green',
        'En término de recursos': 'orange',
        'Ejecutoriado': 'green',
        'Archivado': 'gray',
        'Negado': 'red',
        'Inadmitido': 'red',
    }
    return colores.get(estado, 'gray')

# ==================== PÁGINAS ====================
def pagina_dashboard():
    st.title("📊 Dashboard")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expedientes", conn)
    df_req = pd.read_sql_query("SELECT * FROM requerimientos", conn)
    conn.close()
    
    if df.empty:
        st.warning("No hay expedientes registrados.")
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Expedientes", len(df))
    with col2:
        en_req = len(df[df['estado'] == 'En requerimiento'])
        st.metric("En Requerimiento", en_req)
    with col3:
        suspendidos = len(df[df['termino_suspendido'] == 'Sí'])
        st.metric("Términos Suspendidos", suspendidos)
    with col4:
        ejecutoriados = len(df[df['estado'] == 'Ejecutoriado'])
        st.metric("Ejecutoriados", ejecutoriados)
    
    st.divider()
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Distribución por Estado")
        conteo = df['estado'].value_counts().reset_index()
        conteo.columns = ['Estado', 'Cantidad']
        st.dataframe(conteo, use_container_width=True, hide_index=True)
    
    with col_b:
        st.subheader("Control de Tiempos")
        df['dias_restantes'] = df.apply(
            lambda x: calcular_dias_restantes(x['dias_transcurridos'], x['termino_suspendido']), axis=1
        )
        
        # Alertas
        alertas = df[
            (df['termino_suspendido'] == 'No') & 
            (df['dias_transcurridos'] >= 35)
        ]
        if not alertas.empty:
            st.warning(f"⚠️ {len(alertas)} expediente(s) con más de 35 días transcurridos")
        
        st.dataframe(
            df[['numero_radicado', 'estado', 'dias_transcurridos', 'dias_restantes', 'termino_suspendido', 'prorroga_activa']],
            use_container_width=True,
            hide_index=True
        )

def pagina_expedientes():
    st.title("📁 Expedientes / Licencias")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expedientes ORDER BY id DESC", conn)
    conn.close()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos"] + sorted(df['estado'].unique().tolist()) if not df.empty else ["Todos"])
    with col2:
        filtro_suspendido = st.selectbox("Término Suspendido", ["Todos", "Sí", "No"])
    with col3:
        buscar = st.text_input("Buscar (radicado o propietario)")
    
    df_filtrado = df.copy()
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_estado]
    if filtro_suspendido != "Todos":
        df_filtrado = df_filtrado[df_filtrado['termino_suspendido'] == filtro_suspendido]
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado['numero_radicado'].str.contains(buscar, case=False, na=False) |
            df_filtrado['propietario'].str.contains(buscar, case=False, na=False)
        ]
    
    st.dataframe(
        df_filtrado[[
            'numero_radicado', 'fecha_radicacion', 'estado', 'tipo_obra', 'propietario',
            'revisor_actual', 'dias_transcurridos', 'termino_suspendido', 'prorroga_activa'
        ]],
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    st.subheader("Detalle / Actualizar Expediente")
    
    if not df.empty:
        radicados = df['numero_radicado'].tolist()
        seleccionado = st.selectbox("Seleccionar expediente", radicados)
        
        exp = df[df['numero_radicado'] == seleccionado].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Propietario:** {exp['propietario']}")
            st.write(f"**Dirección:** {exp['direccion']}")
            st.write(f"**Tipo de obra:** {exp['tipo_obra']}")
            st.write(f"**Revisor actual:** {exp['revisor_actual']}")
        with col2:
            st.write(f"**Estado actual:** {exp['estado']}")
            st.write(f"**Días transcurridos:** {exp['dias_transcurridos']}")
            st.write(f"**Término suspendido:** {exp['termino_suspendido']}")
            st.write(f"**Prórroga activa:** {exp['prorroga_activa']}")
        
        st.markdown("#### Cambiar Estado")
        estados = [
            "Radicado", "En revisión jurídica", "En evaluación arquitectónica",
            "En evaluación de ingeniería", "En requerimiento", "Acto proyectado",
            "Acto en revisión", "Acto firmado", "Notificado", "En término de recursos",
            "Ejecutoriado", "Archivado", "Negado", "Inadmitido"
        ]
        
        nuevo_estado = st.selectbox("Nuevo estado", estados, index=estados.index(exp['estado']) if exp['estado'] in estados else 0)
        nuevas_obs = st.text_area("Observaciones", value=exp['observaciones'] or "")
        
        if st.button("Actualizar Estado"):
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE expedientes 
                SET estado=?, observaciones=?, ultima_actualizacion=?
                WHERE numero_radicado=?
            ''', (nuevo_estado, nuevas_obs, datetime.now().strftime('%Y-%m-%d'), seleccionado))
            conn.commit()
            conn.close()
            st.success("Estado actualizado correctamente")
            st.rerun()

def pagina_nuevo_expediente():
    st.title("➕ Nuevo Expediente (Radicación)")
    
    with st.form("nuevo_exp"):
        col1, col2 = st.columns(2)
        
        with col1:
            numero = st.text_input("N° Radicado *", value=f"RAD-2026-{datetime.now().strftime('%H%M%S')}")
            fecha_rad = st.date_input("Fecha de Radicación", value=datetime.now())
            tipo_obra = st.selectbox("Tipo de Obra", [
                "Nueva Construcción", "Ampliación", "Remodelación", "Demolición",
                "Regularización", "Cambio de Uso", "Obra Menor"
            ])
            propietario = st.text_input("Propietario / Solicitante *")
            apoderado = st.text_input("Apoderado (si aplica)")
        
        with col2:
            direccion = st.text_input("Dirección del Predio *")
            zona = st.selectbox("Zona / Sector", ["Centro", "Norte", "Sur", "Oriente", "Poniente", "Residencial", "Industrial", "Comercial"])
            superficie = st.number_input("Superficie (m²)", min_value=0.0, value=100.0)
            valor = st.number_input("Valor de la Obra", min_value=0.0, value=100000000.0, step=1000000.0)
            revisor = st.selectbox("Asignar Revisor Inicial", [
                "Patricia Gómez", "Laura Rivas", "Carlos Méndez", "Sofía Vargas"
            ])
        
        observaciones = st.text_area("Observaciones iniciales")
        
        submitted = st.form_submit_button("Radicar Expediente")
        
        if submitted:
            if not propietario or not direccion:
                st.error("Propietario y Dirección son obligatorios")
            else:
                conn = get_connection()
                c = conn.cursor()
                try:
                    c.execute('''
                        INSERT INTO expedientes (
                            numero_radicado, fecha_radicacion, fecha_inicio_termino, estado, tipo_obra,
                            propietario, apoderado, direccion, zona, superficie, valor_obra, revisor_actual,
                            dias_transcurridos, termino_suspendido, prorroga_activa, observaciones, ultima_actualizacion
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        numero, fecha_rad.strftime('%Y-%m-%d'), fecha_rad.strftime('%Y-%m-%d'),
                        'Radicado', tipo_obra, propietario, apoderado, direccion, zona,
                        superficie, valor, revisor, 0, 'No', 'No', observaciones,
                        datetime.now().strftime('%Y-%m-%d')
                    ))
                    conn.commit()
                    st.success(f"Expediente {numero} radicado correctamente")
                except sqlite3.IntegrityError:
                    st.error("Ya existe un expediente con ese número de radicado")
                finally:
                    conn.close()

def pagina_requerimientos():
    st.title("📋 Actas de Operaciones / Requerimientos")
    st.info("Al crear un requerimiento se debe marcar el expediente como 'En requerimiento' y activar la suspensión del término.")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM requerimientos ORDER BY id DESC", conn)
    df_exp = pd.read_sql_query("SELECT numero_radicado, propietario, estado FROM expedientes", conn)
    conn.close()
    
    st.subheader("Requerimientos existentes")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No hay requerimientos registrados.")
    
    st.divider()
    st.subheader("Crear nuevo Requerimiento / Acta de Operaciones")
    
    with st.form("nuevo_req"):
        radicado = st.selectbox("N° Radicado", df_exp['numero_radicado'].tolist() if not df_exp.empty else [])
        tipo = st.selectbox("Tipo", ["Acta de Operaciones", "Requerimiento de Información", "Requerimiento Técnico"])
        descripcion = st.text_area("Descripción del requerimiento *")
        fecha_acta = st.date_input("Fecha del Acta", value=datetime.now())
        fecha_limite = fecha_acta + timedelta(days=30)
        st.write(f"**Fecha límite de respuesta (30 días):** {fecha_limite.strftime('%d/%m/%Y')}")
        elaborado = st.text_input("Elaborado por", value=st.session_state.get('nombre', ''))
        
        if st.form_submit_button("Crear Requerimiento y Suspender Término"):
            if not descripcion:
                st.error("La descripción es obligatoria")
            else:
                conn = get_connection()
                c = conn.cursor()
                id_req = f"REQ-2026-{datetime.now().strftime('%H%M%S')}"
                
                c.execute('''
                    INSERT INTO requerimientos (
                        id_requerimiento, numero_radicado, fecha_acta, tipo, descripcion,
                        fecha_limite_respuesta, estado, elaborado_por, observaciones
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    id_req, radicado, fecha_acta.strftime('%Y-%m-%d'), tipo, descripcion,
                    fecha_limite.strftime('%Y-%m-%d'), 'Pendiente de respuesta', elaborado,
                    'Término suspendido automáticamente'
                ))
                
                # Actualizar expediente
                c.execute('''
                    UPDATE expedientes 
                    SET estado='En requerimiento', termino_suspendido='Sí',
                        fecha_limite_respuesta=?, ultima_actualizacion=?
                    WHERE numero_radicado=?
                ''', (fecha_limite.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'), radicado))
                
                conn.commit()
                conn.close()
                st.success(f"Requerimiento {id_req} creado. Término del expediente {radicado} suspendido.")
                st.rerun()

def pagina_prorrogas():
    st.title("⏳ Prórrogas")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM prorrogas ORDER BY id DESC", conn)
    df_exp = pd.read_sql_query("SELECT numero_radicado, propietario FROM expedientes", conn)
    conn.close()
    
    st.subheader("Prórrogas registradas")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No hay prórrogas registradas.")
    
    st.divider()
    st.subheader("Registrar solicitud de Prórroga")
    
    with st.form("nueva_pro"):
        radicado = st.selectbox("N° Radicado", df_exp['numero_radicado'].tolist() if not df_exp.empty else [])
        solicitante = st.text_input("Solicitante *")
        calidad = st.selectbox("Calidad", ["Titular", "Apoderado"])
        motivo = st.selectbox("Motivo", [
            "Complejidad técnica del proyecto",
            "Necesidad de estudios adicionales",
            "Carga laboral del área",
            "Solicitud del interesado",
            "Otras razones justificadas"
        ])
        dias = st.number_input("Días solicitados", min_value=5, max_value=60, value=15)
        fecha_sol = st.date_input("Fecha de solicitud", value=datetime.now())
        
        if st.form_submit_button("Registrar Solicitud"):
            if not solicitante:
                st.error("El solicitante es obligatorio")
            else:
                conn = get_connection()
                c = conn.cursor()
                id_pro = f"PRO-2026-{datetime.now().strftime('%H%M%S')}"
                
                c.execute('''
                    INSERT INTO prorrogas (
                        id_prorroga, numero_radicado, solicitante, calidad, fecha_solicitud,
                        motivo, dias_solicitados, decision, observaciones
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    id_pro, radicado, solicitante, calidad, fecha_sol.strftime('%Y-%m-%d'),
                    motivo, dias, 'En estudio', 'Pendiente de decisión'
                ))
                conn.commit()
                conn.close()
                st.success(f"Solicitud de prórroga {id_pro} registrada (En estudio)")
                st.rerun()
    
    # Decidir prórroga
    st.divider()
    st.subheader("Resolver Prórroga")
    
    conn = get_connection()
    df_pend = pd.read_sql_query("SELECT * FROM prorrogas WHERE decision='En estudio'", conn)
    conn.close()
    
    if not df_pend.empty:
        pro_sel = st.selectbox("Seleccionar prórroga pendiente", df_pend['id_prorroga'].tolist())
        decision = st.selectbox("Decisión", ["Concedida", "Negada"])
        obs_dec = st.text_area("Observaciones de la decisión")
        
        if st.button("Registrar Decisión"):
            conn = get_connection()
            c = conn.cursor()
            pro = df_pend[df_pend['id_prorroga'] == pro_sel].iloc[0]
            nuevo_venc = None
            if decision == "Concedida":
                nuevo_venc = (datetime.now() + timedelta(days=int(pro['dias_solicitados']))).strftime('%Y-%m-%d')
                c.execute("UPDATE expedientes SET prorroga_activa='Sí' WHERE numero_radicado=?", (pro['numero_radicado'],))
            
            c.execute('''
                UPDATE prorrogas 
                SET decision=?, fecha_decision=?, nuevo_vencimiento=?, observaciones=?
                WHERE id_prorroga=?
            ''', (decision, datetime.now().strftime('%Y-%m-%d'), nuevo_venc, obs_dec, pro_sel))
            conn.commit()
            conn.close()
            st.success(f"Prórroga {pro_sel} marcada como {decision}")
            st.rerun()
    else:
        st.info("No hay prórrogas pendientes de decisión.")

def pagina_info():
    st.title("ℹ️ Información del Sistema")
    st.markdown("""
    ### Flujo del proceso (45 días hábiles)
    
    1. **Radicación**
    2. **En revisión jurídica** → 5 días
    3. **En evaluación arquitectónica** → 8 días
    4. **En evaluación de ingeniería** → 15 días
    5. **En requerimiento** (Acta de Operaciones) → Suspende el término + 30 días para responder
    6. **Acto proyectado → Acto en revisión → Acto firmado**
    7. **Notificado → En término de recursos → Ejecutoriado**
    
    ### Características del prototipo
    - Control de estados del expediente
    - Suspensión de términos por requerimientos
    - Gestión de prórrogas (solicitud y decisión)
    - Dashboard con indicadores
    - Usuarios con roles (demo)
    
    ### Próximos pasos posibles
    - Cálculo real de días hábiles (excluyendo festivos)
    - Generación automática de PDFs (resoluciones, notificaciones)
    - Notificaciones por correo
    - Historial / línea de tiempo del expediente
    - Firmas digitales
    - Acceso para el ciudadano
    """)

# ==================== MAIN ====================
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login()
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"**Usuario:** {st.session_state['nombre']}")
        st.markdown(f"**Rol:** {st.session_state['rol']}")
        st.divider()
        
        pagina = st.radio("Navegación", [
            "Dashboard",
            "Expedientes",
            "Nuevo Expediente",
            "Requerimientos",
            "Prórrogas",
            "Información"
        ])
        
        st.divider()
        if st.button("Cerrar sesión"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    if pagina == "Dashboard":
        pagina_dashboard()
    elif pagina == "Expedientes":
        pagina_expedientes()
    elif pagina == "Nuevo Expediente":
        pagina_nuevo_expediente()
    elif pagina == "Requerimientos":
        pagina_requerimientos()
    elif pagina == "Prórrogas":
        pagina_prorrogas()
    elif pagina == "Información":
        pagina_info()

if __name__ == "__main__":
    main()
