import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect('notas.db')
    cursor = conexion.cursor()

    # Tabla de Niveles Educativos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS niveles_educativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    )
    ''')

    # Tabla de Grados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        nivel_id INTEGER,
        FOREIGN KEY (nivel_id) REFERENCES niveles_educativos(id)
    )
    ''')

    # Tabla de Estudiantes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primer_nombre TEXT NOT NULL,
        segundo_nombre TEXT,
        primer_apellido TEXT NOT NULL,
        segundo_apellido TEXT,
        cedula TEXT UNIQUE NOT NULL,
        fecha_nacimiento DATE,
        foto BLOB,
        grado_id INTEGER,
        FOREIGN KEY (grado_id) REFERENCES grados(id)
    )
    ''')

    # Tabla de Documentos por Estudiante
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documentos_estudiante (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER,
        ano_bachillerato TEXT NOT NULL,
        ruta_archivo TEXT NOT NULL,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
    )
    ''')

    # Insertar datos por defecto para niveles y grados según la interfaz
    niveles_grados = {
        "Maternal": ["Segundo Nivel", "Tercer Nivel"],
        "Primaria": ["1er Grado", "2do Grado", "3er Grado", "4to Grado", "5to Grado", "6to Grado"],
        "Bachillerato": ["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"]
    }

    for nivel, grados in niveles_grados.items():
        # Insertar nivel
        cursor.execute('INSERT OR IGNORE INTO niveles_educativos (nombre) VALUES (?)', (nivel,))
        cursor.execute('SELECT id FROM niveles_educativos WHERE nombre = ?', (nivel,))
        nivel_id = cursor.fetchone()[0]
        
        for grado in grados:
            # Insertar grado asegurándose de que no exista duplicado para ese nivel
            cursor.execute('SELECT id FROM grados WHERE nombre = ? AND nivel_id = ?', (grado, nivel_id))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO grados (nombre, nivel_id) VALUES (?, ?)', (grado, nivel_id))

    conexion.commit()
    conexion.close()
    print("Base de datos y tablas creadas exitosamente.")

if __name__ == "__main__":
    crear_base_de_datos()
