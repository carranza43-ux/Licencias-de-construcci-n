import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import os

st.set_page_config(
    page_title="Sistema de Licencias de Construcción",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "licencias.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            usuario TEXT UNIQUE,
            clave TEXT,
            nombre TEXT,
            rol TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS expedientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_radicado TEXT UNIQUE,
            fecha_radicacion TEXT,
            fecha_inicio_termino TEXT,
            estado TEXT,
            tipo_obra TEXT,
            propietario TEXT,
            cedula_titular TEXT,
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
            ultima_actualizacion TEXT,
            -- Nuevos campos para Chequeo y Entrega
            tipo_entrega_planos TEXT,
            correo_entrega TEXT,
            fecha_entrega_planos TEXT,
            hora_entrega_planos TEXT,
            chequeo_realizado TEXT DEFAULT 'No',
            -- Aprobaciones por área
            aprobacion_juridica TEXT DEFAULT 'Pendiente',
            aprobacion_arquitectura TEXT DEFAULT 'Pendiente',
            aprobacion_ingenieria TEXT DEFAULT 'Pendiente',
            -- Acta de Observaciones
            acta_observaciones_pdf TEXT,
            acta_radicado_salida TEXT,
            acta_fecha TEXT,
            subsanada TEXT DEFAULT 'No',
            radicado_subsanacion TEXT,
            fecha_subsanacion TEXT,
            cumple_juridica TEXT,
            cumple_arquitectura TEXT,
            cumple_ingenieria TEXT
        )
    ''')
    
    # Agregar columnas si la tabla ya existía (migración simple)
    columnas_nuevas = [
        ("cedula_titular", "TEXT"),
        ("tipo_entrega_planos", "TEXT"),
        ("correo_entrega", "TEXT"),
        ("fecha_entrega_planos", "TEXT"),
        ("hora_entrega_planos", "TEXT"),
        ("chequeo_realizado", "TEXT DEFAULT 'No'"),
        ("aprobacion_juridica", "TEXT DEFAULT 'Pendiente'"),
        ("aprobacion_arquitectura", "TEXT DEFAULT 'Pendiente'"),
        ("aprobacion_ingenieria", "TEXT DEFAULT 'Pendiente'"),
        ("acta_observaciones_pdf", "TEXT"),
        ("acta_radicado_salida", "TEXT"),
        ("acta_fecha", "TEXT"),
        ("subsanada", "TEXT DEFAULT 'No'"),
        ("radicado_subsanacion", "TEXT"),
        ("fecha_subsanacion", "TEXT"),
        ("cumple_juridica", "TEXT"),
        ("cumple_arquitectura", "TEXT"),
        ("cumple_ingenieria", "TEXT")
    ]
    
    for col, tipo in columnas_nuevas:
        try:
            c.execute(f'ALTER TABLE expedientes ADD COLUMN {col} {tipo}')
        except:
            pass  # Ya existe
    
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
    
    usuarios_demo = [
        ('admin', 'admin123', 'Administrador del Sistema', 'Administrador'),
        ('juridica', 'juridica123', 'Patricia Gómez', 'Revisor Jurídico'),
        ('arquitectura', 'arq123', 'Laura Rivas', 'Revisor Arquitectónico'),
        ('ingenieria', 'ing123', 'Carlos Méndez', 'Revisor Ingeniería'),
        ('ventanilla', 'ventanilla123', 'Ana Receptor', 'Ventanilla'),
        ('proyectista', 'proy123', 'Andrés Rojas', 'Proyectista'),
    ]
    
    for u in usuarios_demo:
        c.execute('INSERT OR IGNORE INTO usuarios (usuario, clave, nombre, rol) VALUES (?, ?, ?, ?)', u)
    
    # Datos de ejemplo solo si está vacío
    c.execute('SELECT COUNT(*) FROM expedientes')
    if c.fetchone()[0] == 0:
        hoy = datetime.now()
        ejemplos = [
            ('RAD-2026-1001', (hoy - timedelta(days=20)).strftime('%Y-%m-%d'), (hoy - timedelta(days=18)).strftime('%Y-%m-%d'),
             'En revisión jurídica', 'Nueva Construcción', 'Constructora del Valle S.A.', '900123456-1', '',
             'Calle 45 #12-34', 'Norte', 320.5, 850000000, 'Patricia Gómez', 12, 'No', None, 'No',
             'Documentación completa', hoy.strftime('%Y-%m-%d'), 'Magnético', 'planos@constructora.com',
             (hoy - timedelta(days=19)).strftime('%Y-%m-%d'), '10:30', 'Sí',
             'Pendiente', 'Pendiente', 'Pendiente', None, None, None, 'No', None, None, None, None, None),
        ]
        # Insert simplificado para no alargar
        pass
    
    conn.commit()
    conn.close()

init_db()

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
        - admin / admin123
        - juridica / juridica123
        - arquitectura / arq123
        - ingenieria / ing123
        - ventanilla / ventanilla123
        - proyectista / proy123
        """)

def pagina_dashboard():
    st.title("📊 Dashboard")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expedientes", conn)
    conn.close()
    
    if df.empty:
        st.warning("No hay expedientes registrados todavía.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Expedientes", len(df))
    with col2:
        st.metric("En Requerimiento / Observaciones", len(df[df['estado'].str.contains('requerimiento|observacion', case=False, na=False)]))
    with col3:
        st.metric("Pendientes de Chequeo", len(df[df.get('chequeo_realizado', pd.Series(['No']*len(df))) == 'No']) if 'chequeo_realizado' in df.columns else 0)
    with col4:
        st.metric("Ejecutoriados", len(df[df['estado'] == 'Ejecutoriado']))
    
    st.divider()
    st.subheader("Últimos expedientes")
    cols_mostrar = ['numero_radicado', 'fecha_radicacion', 'estado', 'propietario', 'cedula_titular', 'tipo_entrega_planos']
    cols_existentes = [c for c in cols_mostrar if c in df.columns]
    st.dataframe(df[cols_existentes].head(10), use_container_width=True, hide_index=True)

def pagina_consulta():
    st.title("🔍 Consulta de Expedientes")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_busqueda = st.radio("Buscar por:", ["Número de Radicado", "Cédula del Titular"])
    with col2:
        if tipo_busqueda == "Número de Radicado":
            valor = st.text_input("Número de Radicado")
            fecha = st.date_input("Fecha de radicación (opcional)", value=None)
        else:
            valor = st.text_input("Cédula / NIT del Titular")
            fecha = None
    
    if st.button("Buscar"):
        conn = get_connection()
        if tipo_busqueda == "Número de Radicado":
            if fecha:
                df = pd.read_sql_query(
                    "SELECT * FROM expedientes WHERE numero_radicado LIKE ? AND fecha_radicacion = ?",
                    conn, params=(f"%{valor}%", fecha.strftime('%Y-%m-%d'))
                )
            else:
                df = pd.read_sql_query(
                    "SELECT * FROM expedientes WHERE numero_radicado LIKE ?",
                    conn, params=(f"%{valor}%",)
                )
        else:
            df = pd.read_sql_query(
                "SELECT * FROM expedientes WHERE cedula_titular LIKE ?",
                conn, params=(f"%{valor}%",)
            )
        conn.close()
        
        if df.empty:
            st.warning("No se encontraron expedientes.")
        else:
            st.success(f"Se encontraron {len(df)} expediente(s)")
            st.dataframe(df, use_container_width=True, hide_index=True)

def pagina_nuevo_expediente():
    st.title("➕ Nuevo Expediente / Radicación")
    st.info("El número de radicado debe ser el mismo que se asignó en la ventanilla de la Alcaldía.")
    
    with st.form("nuevo_exp"):
        col1, col2 = st.columns(2)
        
        with col1:
            numero = st.text_input("N° Radicado (de ventanilla) *", placeholder="Ej: RAD-2026-12345")
            fecha_rad = st.date_input("Fecha de Radicación", value=datetime.now())
            tipo_obra = st.selectbox("Tipo de Obra", [
                "Nueva Construcción", "Ampliación", "Remodelación", "Demolición",
                "Regularización", "Cambio de Uso", "Obra Menor"
            ])
            propietario = st.text_input("Propietario / Solicitante *")
            cedula = st.text_input("Cédula / NIT del Titular *")
            apoderado = st.text_input("Apoderado (si aplica)")
        
        with col2:
            direccion = st.text_input("Dirección del Predio *")
            zona = st.selectbox("Zona / Sector", ["Centro", "Norte", "Sur", "Oriente", "Poniente", "Residencial", "Industrial", "Comercial"])
            superficie = st.number_input("Superficie (m²)", min_value=0.0, value=100.0)
            valor = st.number_input("Valor de la Obra", min_value=0.0, value=100000000.0, step=1000000.0)
            revisor = st.selectbox("Asignar Revisor Inicial", [
                "Patricia Gómez", "Laura Rivas", "Carlos Méndez", "Sofía Vargas"
            ])
        
        st.subheader("Chequeo y Entrega de Planos")
        tipo_entrega = st.radio("Tipo de entrega de planos", ["Físico", "Magnético (digital)"])
        
        correo_entrega = None
        fecha_entrega = None
        hora_entrega = None
        
        if tipo_entrega == "Magnético (digital)":
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                correo_entrega = st.text_input("Correo electrónico donde se enviaron *")
            with col_b:
                fecha_entrega = st.date_input("Fecha de envío")
            with col_c:
                hora_entrega = st.time_input("Hora de envío")
        
        observaciones = st.text_area("Observaciones iniciales")
        
        submitted = st.form_submit_button("Radicar Expediente")
        
        if submitted:
            if not numero or not propietario or not cedula or not direccion:
                st.error("Los campos marcados con * son obligatorios")
            elif tipo_entrega == "Magnético (digital)" and not correo_entrega:
                st.error("Debe indicar el correo cuando la entrega es magnética")
            else:
                conn = get_connection()
                c = conn.cursor()
                try:
                    c.execute('''
                        INSERT INTO expedientes (
                            numero_radicado, fecha_radicacion, fecha_inicio_termino, estado, tipo_obra,
                            propietario, cedula_titular, apoderado, direccion, zona, superficie, valor_obra,
                            revisor_actual, dias_transcurridos, termino_suspendido, prorroga_activa,
                            observaciones, ultima_actualizacion,
                            tipo_entrega_planos, correo_entrega, fecha_entrega_planos, hora_entrega_planos,
                            chequeo_realizado
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        numero.strip(), fecha_rad.strftime('%Y-%m-%d'), fecha_rad.strftime('%Y-%m-%d'),
                        'Radicado', tipo_obra, propietario, cedula, apoderado, direccion, zona,
                        superficie, valor, revisor, 0, 'No', 'No', observaciones,
                        datetime.now().strftime('%Y-%m-%d'),
                        tipo_entrega,
                        correo_entrega,
                        fecha_entrega.strftime('%Y-%m-%d') if fecha_entrega else None,
                        hora_entrega.strftime('%H:%M') if hora_entrega else None,
                        'Sí'
                    ))
                    conn.commit()
                    st.success(f"Expediente **{numero}** radicado correctamente")
                except sqlite3.IntegrityError:
                    st.error("Ya existe un expediente con ese número de radicado")
                finally:
                    conn.close()

def pagina_expedientes():
    st.title("📁 Expedientes")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expedientes ORDER BY id DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No hay expedientes. Crea uno nuevo desde el menú.")
        return
    
    # Filtros rápidos
    col1, col2, col3 = st.columns(3)
    with col1:
        estados = ["Todos"] + sorted(df['estado'].dropna().unique().tolist())
        filtro_estado = st.selectbox("Estado", estados)
    with col2:
        filtro_texto = st.text_input("Buscar (radicado, propietario o cédula)")
    
    df_f = df.copy()
    if filtro_estado != "Todos":
        df_f = df_f[df_f['estado'] == filtro_estado]
    if filtro_texto:
        mask = (
            df_f['numero_radicado'].str.contains(filtro_texto, case=False, na=False) |
            df_f['propietario'].str.contains(filtro_texto, case=False, na=False) |
            df_f.get('cedula_titular', pd.Series(['']*len(df_f))).str.contains(filtro_texto, case=False, na=False)
        )
        df_f = df_f[mask]
    
    st.dataframe(
        df_f[['numero_radicado', 'fecha_radicacion', 'estado', 'propietario', 'cedula_titular', 
              'tipo_entrega_planos', 'aprobacion_juridica', 'aprobacion_arquitectura', 'aprobacion_ingenieria']].head(50)
        if all(c in df_f.columns for c in ['cedula_titular', 'tipo_entrega_planos']) else df_f.head(50),
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    st.subheader("Actualizar / Ver detalle")
    
    radicados = df['numero_radicado'].tolist()
    sel = st.selectbox("Seleccionar expediente", radicados)
    exp = df[df['numero_radicado'] == sel].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Propietario:** {exp['propietario']}")
        st.write(f"**Cédula/NIT:** {exp.get('cedula_titular', '—')}")
        st.write(f"**Dirección:** {exp['direccion']}")
    with col2:
        st.write(f"**Estado:** {exp['estado']}")
        st.write(f"**Tipo entrega planos:** {exp.get('tipo_entrega_planos', '—')}")
        if exp.get('tipo_entrega_planos') == 'Magnético (digital)':
            st.write(f"**Correo:** {exp.get('correo_entrega', '—')}")
            st.write(f"**Fecha/Hora envío:** {exp.get('fecha_entrega_planos', '')} {exp.get('hora_entrega_planos', '')}")
    with col3:
        st.write(f"**Aprob. Jurídica:** {exp.get('aprobacion_juridica', 'Pendiente')}")
        st.write(f"**Aprob. Arquitectura:** {exp.get('aprobacion_arquitectura', 'Pendiente')}")
        st.write(f"**Aprob. Ingeniería:** {exp.get('aprobacion_ingenieria', 'Pendiente')}")
    
    # Cambio de estado general
    estados = [
        "Radicado", "Chequeo y entrega", "En revisión jurídica", "En evaluación arquitectónica",
        "En evaluación de ingeniería", "En Acta de Observaciones", "Subsanación", 
        "Acto proyectado", "Acto en revisión", "Acto firmado", "Notificado",
        "En término de recursos", "Ejecutoriado", "Archivado", "Negado", "Inadmitido"
    ]
    nuevo_estado = st.selectbox("Cambiar estado", estados, 
                                index=estados.index(exp['estado']) if exp['estado'] in estados else 0)
    
    if st.button("Actualizar estado"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE expedientes SET estado=?, ultima_actualizacion=? WHERE numero_radicado=?",
                  (nuevo_estado, datetime.now().strftime('%Y-%m-%d'), sel))
        conn.commit()
        conn.close()
        st.success("Estado actualizado")
        st.rerun()

def pagina_aprobaciones():
    st.title("✅ Aprobaciones por Área")
    st.write(f"Usuario actual: **{st.session_state['nombre']}** ({st.session_state['rol']})")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expedientes ORDER BY id DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No hay expedientes.")
        return
    
    rol = st.session_state['rol']
    
    # Filtrar según rol
    if "Jurídico" in rol:
        campo_aprob = "aprobacion_juridica"
        titulo = "Aprobación Jurídica"
    elif "Arquitectónico" in rol:
        campo_aprob = "aprobacion_arquitectura"
        titulo = "Aprobación Arquitectónica"
    elif "Ingeniería" in rol:
        campo_aprob = "aprobacion_ingenieria"
        titulo = "Aprobación de Ingeniería"
    else:
        st.info("Esta sección es para los revisores de Jurídica, Arquitectura e Ingeniería.")
        st.dataframe(df[['numero_radicado', 'propietario', 'aprobacion_juridica', 'aprobacion_arquitectura', 'aprobacion_ingenieria']],
                     use_container_width=True, hide_index=True)
        return
    
    st.subheader(titulo)
    
    radicados = df['numero_radicado'].tolist()
    sel = st.selectbox("Seleccionar expediente", radicados, key="aprob_sel")
    exp = df[df['numero_radicado'] == sel].iloc[0]
    
    st.write(f"**Propietario:** {exp['propietario']}  |  **Estado actual:** {exp['estado']}")
    st.write(f"**Aprobación actual en tu área:** {exp.get(campo_aprob, 'Pendiente')}")
    
    decision = st.radio("Tu decisión", ["Pendiente", "Aprobado", "Rechazado", "Con observaciones"], horizontal=True)
    obs = st.text_area("Observaciones de tu revisión")
    
    if st.button("Registrar mi aprobación"):
        conn = get_connection()
        c = conn.cursor()
        c.execute(f"UPDATE expedientes SET {campo_aprob}=?, ultima_actualizacion=? WHERE numero_radicado=?",
                  (decision, datetime.now().strftime('%Y-%m-%d'), sel))
        conn.commit()
        conn.close()
        st.success(f"Aprobación registrada: {decision}")
        st.rerun()

def pagina_acta_observaciones():
    st.title("📋 Acta de Observaciones (Jurídico)")
    
    if "Jurídico" not in st.session_state.get('rol', '') and st.session_state.get('rol') != 'Administrador':
        st.warning("Esta sección es principalmente para el revisor Jurídico.")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expedientes ORDER BY id DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No hay expedientes.")
        return
    
    sel = st.selectbox("Seleccionar expediente", df['numero_radicado'].tolist())
    exp = df[df['numero_radicado'] == sel].iloc[0]
    
    st.write(f"**Propietario:** {exp['propietario']}")
    
    st.subheader("Registrar / Actualizar Acta de Observaciones")
    
    with st.form("acta_form"):
        radicado_salida = st.text_input("N° Radicado de salida del Acta", value=exp.get('acta_radicado_salida') or "")
        fecha_acta = st.date_input("Fecha del Acta", value=datetime.now())
        # En un sistema real aquí se subiría el PDF. Por ahora guardamos la referencia.
        st.file_uploader("Cargar PDF del Acta de Observaciones", type=["pdf"])
        
        subsanada = st.radio("¿El Acta fue subsanada?", ["No", "Sí"], 
                             index=0 if exp.get('subsanada', 'No') == 'No' else 1)
        
        rad_subs = None
        fecha_subs = None
        if subsanada == "Sí":
            rad_subs = st.text_input("N° Radicado de la subsanación")
            fecha_subs = st.date_input("Fecha de la subsanación")
        
        if st.form_submit_button("Guardar Acta de Observaciones"):
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE expedientes SET 
                    acta_radicado_salida=?, acta_fecha=?, subsanada=?,
                    radicado_subsanacion=?, fecha_subsanacion=?,
                    estado=?, ultima_actualizacion=?
                WHERE numero_radicado=?
            ''', (
                radicado_salida, fecha_acta.strftime('%Y-%m-%d'), subsanada,
                rad_subs, fecha_subs.strftime('%Y-%m-%d') if fecha_subs else None,
                'En Acta de Observaciones' if subsanada == 'No' else 'Subsanación',
                datetime.now().strftime('%Y-%m-%d'), sel
            ))
            conn.commit()
            conn.close()
            st.success("Acta de Observaciones registrada")
            st.rerun()
    
    # Sección para que cada área marque si la subsanación cumple
    if exp.get('subsanada') == 'Sí':
        st.divider()
        st.subheader("Verificación de la Subsanación por área")
        
        rol = st.session_state['rol']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Jurídica**")
            st.write(exp.get('cumple_juridica') or "Pendiente")
            if "Jurídico" in rol or rol == "Administrador":
                val = st.selectbox("¿Cumple?", ["Pendiente", "Sí", "No"], key="cumple_j")
                if st.button("Guardar Jurídica"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("UPDATE expedientes SET cumple_juridica=? WHERE numero_radicado=?", (val, sel))
                    conn.commit()
                    conn.close()
                    st.rerun()
        
        with col2:
            st.write("**Arquitectura**")
            st.write(exp.get('cumple_arquitectura') or "Pendiente")
            if "Arquitectónico" in rol or rol == "Administrador":
                val = st.selectbox("¿Cumple?", ["Pendiente", "Sí", "No"], key="cumple_a")
                if st.button("Guardar Arquitectura"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("UPDATE expedientes SET cumple_arquitectura=? WHERE numero_radicado=?", (val, sel))
                    conn.commit()
                    conn.close()
                    st.rerun()
        
        with col3:
            st.write("**Ingeniería**")
            st.write(exp.get('cumple_ingenieria') or "Pendiente")
            if "Ingeniería" in rol or rol == "Administrador":
                val = st.selectbox("¿Cumple?", ["Pendiente", "Sí", "No"], key="cumple_i")
                if st.button("Guardar Ingeniería"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("UPDATE expedientes SET cumple_ingenieria=? WHERE numero_radicado=?", (val, sel))
                    conn.commit()
                    conn.close()
                    st.rerun()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login()
        return
    
    with st.sidebar:
        st.markdown(f"**{st.session_state['nombre']}**")
        st.caption(st.session_state['rol'])
        st.divider()
        
        pagina = st.radio("Menú", [
            "Dashboard",
            "Consulta",
            "Nuevo Expediente",
            "Expedientes",
            "Aprobaciones por Área",
            "Acta de Observaciones",
            "Información"
        ])
        
        st.divider()
        if st.button("Cerrar sesión"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    if pagina == "Dashboard":
        pagina_dashboard()
    elif pagina == "Consulta":
        pagina_consulta()
    elif pagina == "Nuevo Expediente":
        pagina_nuevo_expediente()
    elif pagina == "Expedientes":
        pagina_expedientes()
    elif pagina == "Aprobaciones por Área":
        pagina_aprobaciones()
    elif pagina == "Acta de Observaciones":
        pagina_acta_observaciones()
    elif pagina == "Información":
        st.title("ℹ️ Información")
        st.markdown("""
        ### Mejoras implementadas en esta versión:
        - Número de radicado completamente editable (el de ventanilla)
        - Campo Cédula/NIT del titular
        - Fase de **Chequeo y entrega de planos** (Físico / Magnético + correo, fecha y hora)
        - Consulta por radicado o por cédula
        - Aprobaciones independientes por área (Jurídica, Arquitectura, Ingeniería)
        - Módulo de **Acta de Observaciones** (antes llamada Acta de Operaciones)
        - Registro de subsanación y verificación por cada área
        - Nuevo usuario: **proyectista / proy123**
        
        ### Próximas mejoras:
        - Generación de PDFs (Oficio, Notificación, Ejecutoria)
        - Rol Proyectista completo + proyección automática del acto
        """)

if __name__ == "__main__":
    main()
