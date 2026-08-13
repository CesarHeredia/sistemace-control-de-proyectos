import eel
import sqlite3
import os
import pandas as pd
import zipfile
import io
import json

# Inicializar Eel
eel.init('.')

# Conexión a la base de datos
DB_FILE = 'colegio.db'

def get_conn():
    """Abre una conexión con timeout y WAL mode para evitar 'database locked'."""
    conn = sqlite3.connect(DB_FILE, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nivel TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            nivel TEXT NOT NULL,
            estado TEXT DEFAULT 'Activo',
            tipo TEXT DEFAULT 'Regular',
            ingreso_periodo TEXT,
            direccion TEXT,
            ciudad TEXT,
            estado_residencia TEXT,
            telefono_casa TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            periodo TEXT NOT NULL,
            archivo_nombre TEXT NOT NULL,
            archivo_ruta TEXT NOT NULL,
            FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS familiares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            cedula TEXT,
            telefono TEXT,
            parentesco TEXT DEFAULT 'Padre/Madre',
            FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE
        )
    ''')
    # Migrations
    for col_def in [
        "ALTER TABLE notas ADD COLUMN anio TEXT",
        "ALTER TABLE alumnos ADD COLUMN tipo TEXT DEFAULT 'Regular'",
        "ALTER TABLE alumnos ADD COLUMN ingreso_periodo TEXT",
        "ALTER TABLE alumnos ADD COLUMN direccion TEXT",
        "ALTER TABLE alumnos ADD COLUMN ciudad TEXT",
        "ALTER TABLE alumnos ADD COLUMN estado_residencia TEXT",
        "ALTER TABLE alumnos ADD COLUMN telefono_casa TEXT",
    ]:
        try:
            cursor.execute(col_def)
        except sqlite3.OperationalError:
            pass
    try:
        cursor.execute("UPDATE usuarios SET nivel = 'primaria_prescolar' WHERE nivel IN ('primaria', 'prescolar')")
    except Exception:
        pass
    conn.commit()
    conn.close()
    
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

@eel.expose
def login(username, password):
    try:
        if username == 'admin' and password == 'admin':
            return {'success': True, 'user': {'username': 'admin', 'level': None, 'isAdmin': True}}
            
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, nivel FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {'success': True, 'user': {'id': user[0], 'username': user[1], 'level': user[2], 'isAdmin': False}}
        else:
            return {'success': False, 'error': 'Usuario o contraseña incorrectos'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def register(username, password, nivel):
    if username == 'admin':
        return {'success': False, 'error': 'Ese usuario no está disponible'}
        
    try:
        conn = get_conn()
        cursor = conn.cursor()
        # Verificar si existe
        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'error': 'El usuario ya existe'}
            
        cursor.execute("INSERT INTO usuarios (username, password, nivel) VALUES (?, ?, ?)", (username, password, nivel))
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_users():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, nivel FROM usuarios WHERE username != 'admin'")
        rows = cursor.fetchall()
        conn.close()
        return {'success': True, 'users': [{'id': r[0], 'username': r[1], 'nivel': r[2]} for r in rows]}
    except Exception as e:
        return {'success': False, 'error': str(e)}
import base64
import shutil

@eel.expose
def get_alumnos(nivel=None):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if nivel:
            cursor.execute("SELECT a.id, a.cedula, a.nombre, a.apellido, a.nivel, a.estado, GROUP_CONCAT(n.anio), a.tipo, a.ingreso_periodo, a.direccion, a.ciudad, a.estado_residencia, a.telefono_casa FROM alumnos a LEFT JOIN notas n ON a.id = n.alumno_id WHERE a.nivel = ? GROUP BY a.id", (nivel,))
        else:
            cursor.execute("SELECT a.id, a.cedula, a.nombre, a.apellido, a.nivel, a.estado, GROUP_CONCAT(n.anio), a.tipo, a.ingreso_periodo, a.direccion, a.ciudad, a.estado_residencia, a.telefono_casa FROM alumnos a LEFT JOIN notas n ON a.id = n.alumno_id GROUP BY a.id")
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for r in rows:
            anios_str = r[6]
            anios_list = []
            if anios_str:
                anios_list = list(set([a for a in anios_str.split(',') if a]))
                
            result.append({
                'id': r[0],
                'cedula': r[1],
                'nombre': r[2],
                'apellido': r[3],
                'level': r[4],
                'status': r[5],
                'anios': anios_list,
                'tipo': r[7] if len(r) > 7 and r[7] else 'Regular',
                'ingreso_periodo': r[8] if len(r) > 8 else None,
                'direccion': r[9] if len(r) > 9 else None,
                'ciudad': r[10] if len(r) > 10 else None,
                'estado_residencia': r[11] if len(r) > 11 else None,
                'telefono_casa': r[12] if len(r) > 12 else None,
            })
        return result
    except Exception as e:
        return []

@eel.expose
def add_alumno(cedula, nombre, apellido, nivel, tipo='Regular', ingreso_periodo=None,
               direccion=None, ciudad=None, estado_residencia=None, telefono_casa=None):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alumnos (cedula, nombre, apellido, nivel, tipo, ingreso_periodo, direccion, ciudad, estado_residencia, telefono_casa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (cedula, nombre, apellido, nivel, tipo, ingreso_periodo, direccion, ciudad, estado_residencia, telefono_casa)
        )
        alumno_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'success': True, 'id': alumno_id}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'Ya existe un alumno con esa cédula'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def save_familiares(alumno_id, familiares):
    """Reemplaza todos los familiares de un alumno."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM familiares WHERE alumno_id = ?", (alumno_id,))
        for f in familiares:
            cursor.execute(
                "INSERT INTO familiares (alumno_id, nombre, apellido, cedula, telefono, parentesco) VALUES (?, ?, ?, ?, ?, ?)",
                (alumno_id, f.get('nombre',''), f.get('apellido',''), f.get('cedula',''), f.get('telefono',''), f.get('parentesco', 'Padre/Madre'))
            )
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_familiares(alumno_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, cedula, telefono, parentesco FROM familiares WHERE alumno_id = ?", (alumno_id,))
        rows = cursor.fetchall()
        conn.close()
        return {'success': True, 'familiares': [
            {'id': r[0], 'nombre': r[1], 'apellido': r[2], 'cedula': r[3], 'telefono': r[4], 'parentesco': r[5]}
            for r in rows
        ]}
    except Exception as e:
        return {'success': False, 'familiares': []}

@eel.expose
def update_alumno_datos(alumno_id, direccion, ciudad, estado_residencia, telefono_casa):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE alumnos SET direccion=?, ciudad=?, estado_residencia=?, telefono_casa=? WHERE id=?",
            (direccion, ciudad, estado_residencia, telefono_casa, alumno_id)
        )
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def delete_alumno(id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # Eliminar archivos físicamente
        cursor.execute("SELECT archivo_ruta FROM notas WHERE alumno_id = ?", (id,))
        for row in cursor.fetchall():
            if os.path.exists(row[0]):
                os.remove(row[0])
                
        cursor.execute("DELETE FROM alumnos WHERE id = ?", (id,))
        cursor.execute("DELETE FROM notas WHERE alumno_id = ?", (id,))
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def upload_nota(alumno_id, periodo, base64_data, filename, anio):
    try:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
            
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
            
        file_path = os.path.join('uploads', f'alumno_{alumno_id}_{periodo.replace(" ", "_")}_{filename}')
        
        with open(file_path, "wb") as fh:
            fh.write(base64.b64decode(base64_data))
            
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, archivo_ruta FROM notas WHERE alumno_id = ? AND periodo = ?", (alumno_id, periodo))
        existing = cursor.fetchone()
        
        if existing:
            if os.path.exists(existing[1]):
                os.remove(existing[1])
            cursor.execute("UPDATE notas SET archivo_nombre = ?, archivo_ruta = ?, anio = ? WHERE id = ?", (filename, file_path, anio, existing[0]))
        else:
            cursor.execute("INSERT INTO notas (alumno_id, periodo, archivo_nombre, archivo_ruta, anio) VALUES (?, ?, ?, ?, ?)", (alumno_id, periodo, filename, file_path, anio))
            
        # Promotion and cleanup logic for primaria/prescolar
        cursor.execute("SELECT nivel, tipo, ingreso_periodo FROM alumnos WHERE id = ?", (alumno_id,))
        student = cursor.fetchone()
        if student:
            nivel, tipo, ingreso_periodo = student
            if nivel in ('primaria', 'prescolar') and tipo in ('Regular', 'Nuevo Ingreso') and periodo == ingreso_periodo:
                SEQUENCE_PERIODOS = [
                    '2do Nivel', '3er Nivel',
                    '1er Grado', '2do Grado', '3er Grado', '4to Grado', '5to Grado', '6to Grado'
                ]
                if ingreso_periodo in SEQUENCE_PERIODOS:
                    idx = SEQUENCE_PERIODOS.index(ingreso_periodo)
                    
                    # 1. Delete the old previous period note
                    if idx > 0:
                        prev_period = SEQUENCE_PERIODOS[idx - 1]
                        cursor.execute("SELECT archivo_ruta FROM notas WHERE alumno_id = ? AND periodo = ?", (alumno_id, prev_period))
                        old_note = cursor.fetchone()
                        if old_note:
                            try:
                                if os.path.exists(old_note[0]):
                                    os.remove(old_note[0])
                            except Exception:
                                pass
                            cursor.execute("DELETE FROM notas WHERE alumno_id = ? AND periodo = ?", (alumno_id, prev_period))
                    
                    # 2. Promote student to the next period
                    if idx + 1 < len(SEQUENCE_PERIODOS):
                        next_period = SEQUENCE_PERIODOS[idx + 1]
                        next_level = 'primaria' if 'Grado' in next_period else 'prescolar'
                        cursor.execute("UPDATE alumnos SET ingreso_periodo = ?, nivel = ? WHERE id = ?", (next_period, next_level, alumno_id))
                    else:
                        # Finished 6to Grado: promote to Egresado
                        cursor.execute("UPDATE alumnos SET tipo = 'Egresado', ingreso_periodo = '6to Grado' WHERE id = ?", (alumno_id,))
                        
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_notas(alumno_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, archivo_nombre, anio FROM notas WHERE alumno_id = ?", (alumno_id,))
        rows = cursor.fetchall()
        conn.close()
        return {'success': True, 'notas': {r[0]: {'archivo': r[1], 'anio': r[2]} for r in rows}}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def open_nota_file(alumno_id, periodo):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT archivo_ruta FROM notas WHERE alumno_id = ? AND periodo = ?", (alumno_id, periodo))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {'success': False, 'error': 'Archivo no encontrado'}
        file_path = os.path.abspath(row[0])
        if not os.path.exists(file_path):
            return {'success': False, 'error': 'El archivo ya no existe en el disco'}
        import subprocess, sys
        if sys.platform.startswith('win'):
            os.startfile(file_path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', file_path])
        else:
            subprocess.Popen(['xdg-open', file_path])
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def update_anios(alumno_id, periodos_anios):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        for periodo, anio in periodos_anios.items():
            cursor.execute("UPDATE notas SET anio = ? WHERE alumno_id = ? AND periodo = ?", (anio, alumno_id, periodo))
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def get_egresado_years(nivel=None):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if nivel in ('primaria_prescolar', 'primaria', 'prescolar'):
            cursor.execute("""
                SELECT DISTINCT n.anio FROM notas n 
                JOIN alumnos a ON a.id = n.alumno_id 
                WHERE a.nivel IN ('primaria', 'prescolar', 'primaria_prescolar') 
                AND (a.tipo = 'Egresado' OR a.ingreso_periodo = '6to Grado')
                AND n.anio IS NOT NULL AND n.anio != ''
                ORDER BY n.anio DESC
            """)
        elif nivel == 'bachillerato':
            cursor.execute("""
                SELECT DISTINCT n.anio FROM notas n 
                JOIN alumnos a ON a.id = n.alumno_id 
                WHERE a.nivel = 'bachillerato' 
                AND (a.tipo = 'Egresado' OR a.ingreso_periodo = '5to Año')
                AND n.anio IS NOT NULL AND n.anio != ''
                ORDER BY n.anio DESC
            """)
        else:
            cursor.execute("""
                SELECT DISTINCT n.anio FROM notas n 
                JOIN alumnos a ON a.id = n.alumno_id 
                WHERE (a.tipo = 'Egresado' OR a.ingreso_periodo IN ('6to Grado', '5to Año'))
                AND n.anio IS NOT NULL AND n.anio != ''
                ORDER BY n.anio DESC
            """)
        rows = cursor.fetchall()
        conn.close()
        years = [r[0] for r in rows if r[0]]
        return {'success': True, 'years': years}
    except Exception as e:
        return {'success': False, 'error': str(e), 'years': []}

@eel.expose
def export_students(nivel, selected_year=None, export_all=False, export_mode='all', egresado_year=None):
    try:
        conn = get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Determinación de la consulta según export_mode
        if export_mode == 'egresados' or selected_year == 'Egresados':
            target_egresado_year = egresado_year if (egresado_year and egresado_year != 'all') else None
            
            if nivel in ('primaria_prescolar', 'primaria', 'prescolar'):
                level_filter = "a.nivel IN ('primaria', 'prescolar', 'primaria_prescolar') AND (a.tipo = 'Egresado' OR a.ingreso_periodo = '6to Grado')"
                nivel_tag = "Egresados_Primaria"
            elif nivel == 'bachillerato':
                level_filter = "a.nivel = 'bachillerato' AND (a.tipo = 'Egresado' OR a.ingreso_periodo = '5to Año')"
                nivel_tag = "Egresados_Bachillerato"
            else:
                level_filter = "(a.tipo = 'Egresado' OR a.ingreso_periodo IN ('6to Grado', '5to Año'))"
                nivel_tag = "Egresados"

            if target_egresado_year:
                cursor.execute(f"""
                    SELECT DISTINCT a.* FROM alumnos a 
                    INNER JOIN notas n ON a.id = n.alumno_id 
                    WHERE {level_filter}
                    AND n.anio = ?
                """, (target_egresado_year,))
            else:
                cursor.execute(f"SELECT DISTINCT a.* FROM alumnos a WHERE {level_filter}")
        elif export_mode == 'year' and selected_year:
            nivel_tag = selected_year.replace(' ', '_')
            if nivel in ('primaria_prescolar', 'primaria', 'prescolar'):
                cursor.execute("""
                    SELECT DISTINCT a.* FROM alumnos a 
                    LEFT JOIN notas n ON a.id = n.alumno_id 
                    WHERE a.nivel IN ('primaria', 'prescolar', 'primaria_prescolar') 
                    AND (a.ingreso_periodo = ? OR n.periodo = ?)
                    AND (a.tipo IS NULL OR a.tipo != 'Egresado')
                """, (selected_year, selected_year))
            elif nivel == 'bachillerato':
                cursor.execute("""
                    SELECT DISTINCT a.* FROM alumnos a 
                    LEFT JOIN notas n ON a.id = n.alumno_id 
                    WHERE a.nivel = 'bachillerato' 
                    AND (a.ingreso_periodo = ? OR n.periodo = ?)
                    AND (a.tipo IS NULL OR a.tipo != 'Egresado')
                """, (selected_year, selected_year))
            else:
                cursor.execute("""
                    SELECT DISTINCT a.* FROM alumnos a 
                    LEFT JOIN notas n ON a.id = n.alumno_id 
                    WHERE (a.ingreso_periodo = ? OR n.periodo = ?)
                    AND (a.tipo IS NULL OR a.tipo != 'Egresado')
                """, (selected_year, selected_year))
        else: # export_all or export_mode == 'all'
            nivel_tag = "Todos"
            if nivel in ('primaria_prescolar', 'primaria', 'prescolar'):
                cursor.execute("SELECT * FROM alumnos WHERE nivel IN ('primaria', 'prescolar', 'primaria_prescolar') AND (tipo IS NULL OR tipo != 'Egresado')")
            elif nivel == 'bachillerato':
                cursor.execute("SELECT * FROM alumnos WHERE nivel = 'bachillerato' AND (tipo IS NULL OR tipo != 'Egresado')")
            else: # admin u otro
                cursor.execute("SELECT * FROM alumnos WHERE tipo IS NULL OR tipo != 'Egresado'")
                
        alumnos = cursor.fetchall()
        
        if not alumnos:
            conn.close()
            det_err = f" (Año de egreso: {egresado_year})" if (export_mode == 'egresados' and egresado_year) else (f" de {selected_year}" if selected_year else "")
            return {'success': False, 'error': f'No hay estudiantes para exportar{det_err}.'}
            
        alumnos_list = [dict(r) for r in alumnos]
        
        for alumno in alumnos_list:
            cursor.execute("SELECT * FROM familiares WHERE alumno_id = ?", (alumno['id'],))
            alumno['familiares'] = [dict(f) for f in cursor.fetchall()]
            cursor.execute("SELECT * FROM notas WHERE alumno_id = ?", (alumno['id'],))
            alumno['notas'] = [dict(n) for n in cursor.fetchall()]
            
        df = pd.DataFrame(alumnos_list)
        excel_buffer = io.BytesIO()
        df.drop(columns=['familiares', 'notas'], errors='ignore').to_excel(excel_buffer, index=False)
        excel_data = excel_buffer.getvalue()
        
        # Directorio de exportaciones
        export_dir = os.path.abspath('exportaciones')
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        year_suffix = f"_{egresado_year}" if (export_mode == 'egresados' and egresado_year and egresado_year != 'all') else ""
        zip_filename = f'exportacion_{nivel}_{nivel_tag}{year_suffix}_{timestamp}.zip'
        zip_path = os.path.join(export_dir, zip_filename)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('estudiantes.xlsx', excel_data)
            
            for alumno in alumnos_list:
                for nota in alumno['notas']:
                    ruta_rel = nota.get('archivo_ruta', '')
                    ruta_abs = os.path.join(base_dir, ruta_rel) if ruta_rel else ''
                    if not os.path.exists(ruta_abs):
                        ruta_abs = ruta_rel
                    if ruta_abs and os.path.exists(ruta_abs):
                        arcname = f"archivos/{os.path.basename(ruta_abs)}"
                        zf.write(ruta_abs, arcname)
                        nota['archivo_zip_path'] = arcname

            # Escribir data.json una sola vez con la info completa
            zf.writestr('data.json', json.dumps(alumnos_list, ensure_ascii=False))

        conn.close()
        
        import subprocess
        subprocess.Popen(f'explorer /select,"{zip_path}"')
        
        return {
            'success': True, 
            'filename': zip_filename, 
            'path': zip_path, 
            'count': len(alumnos_list)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def import_students(base64_zip, target_level, is_new_entry, selected_year=None):
    try:
        if ',' in base64_zip:
            base64_zip = base64_zip.split(',')[1]
            
        zip_data = base64.b64decode(base64_zip)
        zip_buffer = io.BytesIO(zip_data)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        uploads_dir = os.path.join(base_dir, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            if 'data.json' not in zf.namelist():
                return {'success': False, 'error': 'El archivo ZIP no tiene el formato correcto (falta data.json)'}
                
            data = json.loads(zf.read('data.json').decode('utf-8'))
            
            # Extraer archivos de notas a la carpeta uploads
            for name in zf.namelist():
                if (name.startswith('archivos/') or name.startswith('uploads/')) and not name.endswith('/'):
                    fname = os.path.basename(name)
                    if fname:
                        target_file = os.path.join(uploads_dir, fname)
                        with zf.open(name) as src, open(target_file, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                    
        conn = get_conn()
        cursor = conn.cursor()
        
        # Si se especifica un año en particular, intentar filtrar o asignar dicho año
        if selected_year and selected_year not in ('all', 'todos', 'None', ''):
            matching_data = [a for a in data if a.get('ingreso_periodo') == selected_year]
            if matching_data:
                data = matching_data
            else:
                for a in data:
                    a['ingreso_periodo'] = selected_year
        
        count = 0
        for alumno in data:
            cursor.execute("SELECT id FROM alumnos WHERE cedula = ?", (alumno['cedula'],))
            existing = cursor.fetchone()
            
            if target_level == 'bachillerato':
                nuevo_nivel = 'bachillerato'
                if is_new_entry:
                    tipo = 'Nuevo Ingreso'
                    ingreso_periodo = selected_year if selected_year and selected_year not in ('all', 'todos') else '1er Año'
                else:
                    tipo = alumno.get('tipo', 'Regular')
                    ingreso_periodo = selected_year if (selected_year and selected_year not in ('all', 'todos')) else alumno.get('ingreso_periodo', '1er Año')
            else:
                rec_lvl = alumno.get('nivel', 'primaria')
                nuevo_nivel = rec_lvl if rec_lvl in ('primaria', 'prescolar', 'primaria_prescolar') else 'primaria'
                tipo = alumno.get('tipo', 'Regular')
                ingreso_periodo = selected_year if (selected_year and selected_year not in ('all', 'todos')) else alumno.get('ingreso_periodo')
                
            if existing:
                new_id = existing[0]
                cursor.execute(
                    "UPDATE alumnos SET nombre=?, apellido=?, nivel=?, tipo=?, ingreso_periodo=?, direccion=?, ciudad=?, estado_residencia=?, telefono_casa=? WHERE id=?",
                    (alumno['nombre'], alumno['apellido'], nuevo_nivel, tipo, ingreso_periodo, alumno.get('direccion'), alumno.get('ciudad'), alumno.get('estado_residencia'), alumno.get('telefono_casa'), new_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO alumnos (cedula, nombre, apellido, nivel, tipo, ingreso_periodo, direccion, ciudad, estado_residencia, telefono_casa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (alumno['cedula'], alumno['nombre'], alumno['apellido'], nuevo_nivel, tipo, ingreso_periodo, alumno.get('direccion'), alumno.get('ciudad'), alumno.get('estado_residencia'), alumno.get('telefono_casa'))
                )
                new_id = cursor.lastrowid
            
            for fam in alumno.get('familiares', []):
                cursor.execute("SELECT id FROM familiares WHERE alumno_id = ? AND nombre = ? AND apellido = ?", (new_id, fam['nombre'], fam['apellido']))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO familiares (alumno_id, nombre, apellido, cedula, telefono, parentesco) VALUES (?, ?, ?, ?, ?, ?)",
                        (new_id, fam['nombre'], fam['apellido'], fam.get('cedula'), fam.get('telefono'), fam.get('parentesco', 'Padre/Madre'))
                    )
                
            for nota in alumno.get('notas', []):
                fname = ''
                if 'archivo_zip_path' in nota:
                    fname = os.path.basename(nota['archivo_zip_path'])
                if not fname and nota.get('archivo_ruta'):
                    fname = os.path.basename(nota['archivo_ruta'])
                    
                new_ruta = os.path.join('uploads', fname) if fname else nota.get('archivo_ruta', '')
                
                cursor.execute("SELECT id FROM notas WHERE alumno_id = ? AND periodo = ?", (new_id, nota['periodo']))
                n_exist = cursor.fetchone()
                if n_exist:
                    cursor.execute(
                        "UPDATE notas SET archivo_nombre = ?, archivo_ruta = ?, anio = ? WHERE id = ?",
                        (nota['archivo_nombre'], new_ruta, nota.get('anio'), n_exist[0])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO notas (alumno_id, periodo, archivo_nombre, archivo_ruta, anio) VALUES (?, ?, ?, ?, ?)",
                        (new_id, nota['periodo'], nota['archivo_nombre'], new_ruta, nota.get('anio'))
                    )
            count += 1
            
        conn.commit()
        conn.close()
        
        return {'success': True, 'imported_count': count}
    except Exception as e:
        return {'success': False, 'error': str(e)}

import webview
import socket

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

if __name__ == '__main__':
    init_db()
    
    import threading

    # Conseguir un puerto libre automáticamente para evitar el error "Address already in use"
    port = get_free_port()
    
    def run_eel():
        # Iniciar Eel de fondo desactivando su apertura de navegador integrada (mode=None)
        eel.start('index.html', mode=None, host='localhost', port=port)

    # Lanzar Eel en un hilo daemon
    eel_thread = threading.Thread(target=run_eel, daemon=True)
    eel_thread.start()
    
    import time
    time.sleep(1) # Dar tiempo a que Eel levante el servidor antes de abrir la UI

    # Abrir una ventana nativa de escritorio con pywebview usando qt
    webview.create_window('República de Indonesia', f'http://localhost:{port}/index.html', width=1024, height=768)
    webview.start()
