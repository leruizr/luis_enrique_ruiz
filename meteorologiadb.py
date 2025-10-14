import sqlite3

DB_NAME = "D://4. UNAD//meteorologiadb.db"

# ==============================
# CREAR BASE DE DATOS Y TABLAS
# ==============================
def crear_bd():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # USUARIO
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        rol TEXT NOT NULL,
        email TEXT UNIQUE,
        telefono TEXT,
        zonas_interes TEXT,
        permisos TEXT
    );
    """)

    # PARCELA
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parcela (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        altitud REAL,
        area_ha REAL,
        descripcion TEXT,
        propietario_id INTEGER,
        FOREIGN KEY (propietario_id) REFERENCES usuario(id)
            ON UPDATE NO ACTION ON DELETE SET NULL
    );
    """)
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_parcela_propietario ON parcela(propietario_id);""")

    # USUARIO_PARCELA (N..M)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuario_parcela (
        usuario_id INTEGER NOT NULL,
        parcela_id INTEGER NOT NULL,
        PRIMARY KEY (usuario_id, parcela_id),
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
            ON UPDATE NO ACTION ON DELETE CASCADE,
        FOREIGN KEY (parcela_id) REFERENCES parcela(id)
            ON UPDATE NO ACTION ON DELETE CASCADE
    );
    """)

    # ESTACION_METEOROLOGICA
    cur.execute("""
    CREATE TABLE IF NOT EXISTS estacion_meteorologica (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        altitud REAL,
        activa INTEGER NOT NULL DEFAULT 1,
        capacidad_registro INTEGER NOT NULL DEFAULT 100,
        parcela_id INTEGER NOT NULL,
        FOREIGN KEY (parcela_id) REFERENCES parcela(id)
            ON UPDATE NO ACTION ON DELETE CASCADE,
        UNIQUE (nombre, parcela_id)
    );
    """)
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_estacion_parcela ON estacion_meteorologica(parcela_id);""")

    # SENSOR
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        unidad TEXT NOT NULL,
        precision REAL NOT NULL,
        rango_min REAL,
        rango_max REAL,
        estado INTEGER NOT NULL DEFAULT 1,
        estacion_id INTEGER NOT NULL,
        tipo_humedad TEXT,
        fecha_calibracion NUMERIC,
        tipo_medidor TEXT,
        area_captacion REAL,
        FOREIGN KEY (estacion_id) REFERENCES estacion_meteorologica(id)
            ON UPDATE NO ACTION ON DELETE CASCADE
    );
    """)
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_sensor_estacion ON sensor(estacion_id);""")
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_sensor_tipo ON sensor(tipo);""")

    # LECTURA
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lectura (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id INTEGER NOT NULL,
        fecha_hora NUMERIC NOT NULL,
        valor REAL NOT NULL,
        calidad_dato TEXT DEFAULT 'OK',
        fuente TEXT DEFAULT 'automatica',
        FOREIGN KEY (sensor_id) REFERENCES sensor(id)
            ON UPDATE NO ACTION ON DELETE CASCADE,
        UNIQUE (sensor_id, fecha_hora)
    );
    """)
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_lectura_sensor_fecha ON lectura(sensor_id, fecha_hora);""")

    con.commit()
    con.close()


# ==============================
# FUNCIONES CRUD GENERICAS
# ==============================
def insertar(query, valores=()):
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    cur.execute(query, valores)
    con.commit()
    con.close()

def listar(query, valores=()):
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    cur.execute(query, valores)
    filas = cur.fetchall()
    con.close()
    return filas

def actualizar(query, valores=()):
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    cur.execute(query, valores)
    con.commit()
    con.close()

def eliminar(query, valores=()):
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    cur.execute(query, valores)
    con.commit()
    con.close()


# ==============================
# CRUD DE CADA TABLA
# ==============================
def crud_usuario():
    while True:
        print("\n--- CRUD Usuario ---")
        print("1. Insertar")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")
        op = input("Seleccione: ")

        if op == "1":
            nombre = input("Nombre: ")
            rol = input("Rol (agricultor/tecnico/admin): ")
            email = input("Email (opcional): ")
            telefono = input("Teléfono (opcional): ")
            insertar("""INSERT INTO usuario (nombre, rol, email, telefono) VALUES (?,?,?,?)""",
                     (nombre, rol, email or None, telefono or None))
            print("Usuario insertado.")
        elif op == "2":
            for f in listar("SELECT * FROM usuario"):
                print(f)
        elif op == "3":
            id_ = input("ID a actualizar: ")
            nombre = input("Nuevo nombre: ")
            rol = input("Nuevo rol: ")
            email = input("Nuevo email: ")
            telefono = input("Nuevo teléfono: ")
            actualizar("""UPDATE usuario SET nombre=?, rol=?, email=?, telefono=? WHERE id=?""",
                       (nombre, rol, email or None, telefono or None, id_))
            print("Usuario actualizado.")
        elif op == "4":
            id_ = input("ID a eliminar: ")
            eliminar("DELETE FROM usuario WHERE id=?", (id_,))
            print("Usuario eliminado.")
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def crud_parcela():
    while True:
        print("\n--- CRUD Parcela ---")
        print("1. Insertar")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")
        op = input("Seleccione: ")

        if op == "1":
            nombre = input("Nombre: ")
            lat = float(input("Latitud: "))
            lon = float(input("Longitud: "))
            alt = input("Altitud (opcional): ")
            area = input("Área (ha, opcional): ")
            desc = input("Descripción (opcional): ")
            prop = input("ID Propietario (opcional): ")
            insertar("""INSERT INTO parcela (nombre, latitud, longitud, altitud, area_ha, descripcion, propietario_id)
                        VALUES (?,?,?,?,?,?,?)""",
                     (nombre, lat, lon, float(alt) if alt else None, float(area) if area else None,
                      desc or None, int(prop) if prop else None))
            print("Parcela insertada.")
        elif op == "2":
            for f in listar("""SELECT p.*, u.nombre AS propietario
                               FROM parcela p LEFT JOIN usuario u ON u.id = p.propietario_id"""):
                print(f)
        elif op == "3":
            id_ = input("ID a actualizar: ")
            nombre = input("Nuevo nombre: ")
            lat = float(input("Nueva latitud: "))
            lon = float(input("Nueva longitud: "))
            alt = input("Nueva altitud (opcional): ")
            area = input("Nueva área (ha, opcional): ")
            desc = input("Nueva descripción (opcional): ")
            prop = input("Nuevo ID Propietario (opcional): ")
            actualizar("""UPDATE parcela SET nombre=?, latitud=?, longitud=?, altitud=?, area_ha=?, descripcion=?, propietario_id=?
                          WHERE id=?""",
                       (nombre, lat, lon, float(alt) if alt else None, float(area) if area else None,
                        desc or None, int(prop) if prop else None, id_))
            print("Parcela actualizada.")
        elif op == "4":
            id_ = input("ID a eliminar: ")
            eliminar("DELETE FROM parcela WHERE id=?", (id_,))
            print("Parcela eliminada.")
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def crud_usuario_parcela():
    while True:
        print("\n--- CRUD Usuario_Parcela ---")
        print("1. Insertar relación")
        print("2. Listar relaciones")
        print("3. Eliminar relación")
        print("0. Volver")
        op = input("Seleccione: ")

        if op == "1":
            uid = input("ID Usuario: ")
            pid = input("ID Parcela: ")
            insertar("INSERT INTO usuario_parcela (usuario_id, parcela_id) VALUES (?,?)", (uid, pid))
            print("Relación inserta.")
        elif op == "2":
            for f in listar("""SELECT up.usuario_id, u.nombre, up.parcela_id, p.nombre
                               FROM usuario_parcela up
                               JOIN usuario u ON u.id = up.usuario_id
                               JOIN parcela p ON p.id = up.parcela_id"""):
                print(f)
        elif op == "3":
            uid = input("ID Usuario: ")
            pid = input("ID Parcela: ")
            eliminar("DELETE FROM usuario_parcela WHERE usuario_id=? AND parcela_id=?", (uid, pid))
            print("Relación eliminada.")
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def crud_estacion():
    while True:
        print("\n--- CRUD Estación Meteorológica ---")
        print("1. Insertar")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")
        op = input("Seleccione: ")

        if op == "1":
            nombre = input("Nombre: ")
            lat = float(input("Latitud: "))
            lon = float(input("Longitud: "))
            alt = input("Altitud (opcional): ")
            activa = int(input("Activa (1/0): "))
            cap = int(input("Capacidad de registro: "))
            parcela_id = int(input("ID Parcela: "))
            insertar("""INSERT INTO estacion_meteorologica
                        (nombre, latitud, longitud, altitud, activa, capacidad_registro, parcela_id)
                        VALUES (?,?,?,?,?,?,?)""",
                     (nombre, lat, lon, float(alt) if alt else None, activa, cap, parcela_id))
            print("Estación insertada.")
        elif op == "2":
            for f in listar("""SELECT e.*, p.nombre AS parcela
                               FROM estacion_meteorologica e
                               JOIN parcela p ON p.id = e.parcela_id"""):
                print(f)
        elif op == "3":
            id_ = input("ID a actualizar: ")
            nombre = input("Nuevo nombre: ")
            lat = float(input("Nueva latitud: "))
            lon = float(input("Nueva longitud: "))
            alt = input("Nueva altitud (opcional): ")
            activa = int(input("Activa (1/0): "))
            cap = int(input("Capacidad de registro: "))
            parcela_id = int(input("ID Parcela: "))
            actualizar("""UPDATE estacion_meteorologica
                          SET nombre=?, latitud=?, longitud=?, altitud=?, activa=?, capacidad_registro=?, parcela_id=?
                          WHERE id=?""",
                       (nombre, lat, lon, float(alt) if alt else None, activa, cap, parcela_id, id_))
            print("Estación actualizada.")
        elif op == "4":
            id_ = input("ID a eliminar: ")
            eliminar("DELETE FROM estacion_meteorologica WHERE id=?", (id_,))
            print("Estación eliminada.")
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def crud_sensor():
    while True:
        print("\n--- CRUD Sensor ---")
        print("1. Insertar")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")
        op = input("Seleccione: ")

        if op == "1":
            tipo = input("Tipo (temperatura/humedad/precipitacion/viento): ")
            unidad = input("Unidad (°C/%/mm/km/h): ")
            precision = float(input("Precisión: "))
            rmin = input("Rango mínimo (opcional): ")
            rmax = input("Rango máximo (opcional): ")
            estado = int(input("Estado (1 activo / 0 inactivo): "))
            est_id = int(input("ID Estación: "))
            tipo_humedad = input("Tipo humedad (opcional): ")
            fecha_calib = input("Fecha calibración (YYYY-MM-DD, opcional): ")
            tipo_medidor = input("Tipo medidor (opcional): ")
            area_cap = input("Área captación (opcional): ")
            insertar("""INSERT INTO sensor
                        (tipo, unidad, precision, rango_min, rango_max, estado, estacion_id,
                         tipo_humedad, fecha_calibracion, tipo_medidor, area_captacion)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                     (tipo, unidad, precision,
                      float(rmin) if rmin else None,
                      float(rmax) if rmax else None,
                      estado, est_id,
                      tipo_humedad or None,
                      fecha_calib or None,
                      tipo_medidor or None,
                      float(area_cap) if area_cap else None))
            print("Sensor insertado.")
        elif op == "2":
            for f in listar("""SELECT s.*, e.nombre AS estacion
                               FROM sensor s JOIN estacion_meteorologica e ON e.id = s.estacion_id"""):
                print(f)
        elif op == "3":
            id_ = input("ID a actualizar: ")
            tipo = input("Tipo: ")
            unidad = input("Unidad: ")
            precision = float(input("Precisión: "))
            rmin = input("Rango mínimo (opcional): ")
            rmax = input("Rango máximo (opcional): ")
            estado = int(input("Estado (1/0): "))
            est_id = int(input("ID Estación: "))
            tipo_humedad = input("Tipo humedad (opcional): ")
            fecha_calib = input("Fecha calibración (YYYY-MM-DD, opcional): ")
            tipo_medidor = input("Tipo medidor (opcional): ")
            area_cap = input("Área captación (opcional): ")
            actualizar("""UPDATE sensor SET
                          tipo=?, unidad=?, precision=?, rango_min=?, rango_max=?, estado=?, estacion_id=?,
                          tipo_humedad=?, fecha_calibracion=?, tipo_medidor=?, area_captacion=?
                          WHERE id=?""",
                       (tipo, unidad, precision,
                        float(rmin) if rmin else None,
                        float(rmax) if rmax else None,
                        estado, est_id,
                        tipo_humedad or None,
                        fecha_calib or None,
                        tipo_medidor or None,
                        float(area_cap) if area_cap else None,
                        id_))
            print("Sensor actualizado.")
        elif op == "4":
            id_ = input("ID a eliminar: ")
            eliminar("DELETE FROM sensor WHERE id=?", (id_,))
            print("Sensor eliminado.")
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def crud_lectura():
    while True:
        print("\n--- CRUD Lectura ---")
        print("1. Insertar")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")
        op = input("Seleccione: ")

        if op == "1":
            sensor_id = int(input("ID Sensor: "))
            fecha_hora = input("Fecha-Hora (YYYY-MM-DD HH:MM:SS): ")
            valor = float(input("Valor: "))
            calidad = input("Calidad dato (OK/FLAG/MISSING, opcional): ")
            fuente = input("Fuente (automatica/manual, opcional): ")
            insertar("""INSERT INTO lectura (sensor_id, fecha_hora, valor, calidad_dato, fuente)
                        VALUES (?,?,?,?,?)""",
                     (sensor_id, fecha_hora, valor, calidad or None, fuente or None))
            print("Lectura insertada.")
        elif op == "2":
            for f in listar("""SELECT l.*, s.tipo, s.unidad
                               FROM lectura l JOIN sensor s ON s.id = l.sensor_id
                               ORDER BY l.sensor_id, l.fecha_hora"""):
                print(f)
        elif op == "3":
            id_ = input("ID a actualizar: ")
            sensor_id = int(input("Nuevo ID Sensor: "))
            fecha_hora = input("Nueva Fecha-Hora (YYYY-MM-DD HH:MM:SS): ")
            valor = float(input("Nuevo Valor: "))
            calidad = input("Nueva Calidad dato (opcional): ")
            fuente = input("Nueva Fuente (opcional): ")
            actualizar("""UPDATE lectura SET sensor_id=?, fecha_hora=?, valor=?, calidad_dato=?, fuente=?
                          WHERE id=?""",
                       (sensor_id, fecha_hora, valor, calidad or None, fuente or None, id_))
            print("Lectura actualizada.")
        elif op == "4":
            id_ = input("ID a eliminar: ")
            eliminar("DELETE FROM lectura WHERE id=?", (id_,))
            print("Lectura eliminada.")
        elif op == "0":
            break
        else:
            print("Opción inválida.")


# ==============================
# MENÚ PRINCIPAL
# ==============================
def menu():
    crear_bd()
    while True:
        print("\n===== MENÚ PRINCIPAL (Clima) =====")
        print("1. CRUD Usuario")
        print("2. CRUD Parcela")
        print("3. CRUD Usuario_Parcela")
        print("4. CRUD Estación Meteorológica")
        print("5. CRUD Sensor")
        print("6. CRUD Lectura")
        print("0. Salir")
        op = input("Seleccione: ")

        if op == "1":
            crud_usuario()
        elif op == "2":
            crud_parcela()
        elif op == "3":
            crud_usuario_parcela()
        elif op == "4":
            crud_estacion()
        elif op == "5":
            crud_sensor()
        elif op == "6":
            crud_lectura()
        elif op == "0":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
