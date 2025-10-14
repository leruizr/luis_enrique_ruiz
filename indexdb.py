import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

DB_NAME = r"D:\4. UNAD//meteorologiadb.db"

# ==============================================
# CONEXIÓN Y CREACIÓN DE BASE DE DATOS / TABLAS
# ==============================================
def create_connection():
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def crear_bd():
    con = create_connection()
    cur = con.cursor()

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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parcela_propietario ON parcela(propietario_id);")

    # USUARIO_PARCELA
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_estacion_parcela ON estacion_meteorologica(parcela_id);")

    # SENSOR
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,         -- temperatura | humedad | precipitacion | viento
        unidad TEXT NOT NULL,       -- °C | % | mm | km/h
        precision REAL NOT NULL,
        rango_min REAL,
        rango_max REAL,
        estado INTEGER NOT NULL DEFAULT 1,  -- 0/1
        estacion_id INTEGER NOT NULL,
        tipo_humedad TEXT,
        fecha_calibracion NUMERIC,
        tipo_medidor TEXT,
        area_captacion REAL,
        FOREIGN KEY (estacion_id) REFERENCES estacion_meteorologica(id)
            ON UPDATE NO ACTION ON DELETE CASCADE
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_estacion ON sensor(estacion_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_tipo ON sensor(tipo);")

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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lectura_sensor_fecha ON lectura(sensor_id, fecha_hora);")

    con.commit()
    con.close()

# ==========================
# MANAGERS (CRUD LADO DB)
# ==========================
class EstacionManager:
    def listar(self, con):
        cur = con.cursor()
        cur.execute("SELECT id, nombre FROM estacion_meteorologica ORDER BY nombre;")
        return cur.fetchall()

class SensorManager:
    def leer(self, con):
        cur = con.cursor()
        cur.execute("""
            SELECT s.id, s.tipo, s.unidad, s.precision, s.rango_min, s.rango_max, s.estado,
                   s.estacion_id, e.nombre AS estacion
            FROM sensor s
            JOIN estacion_meteorologica e ON e.id = s.estacion_id
            ORDER BY s.id;
        """)
        # devolver diccionarios
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def guardar(self, con, tipo, unidad, precision, rmin, rmax, estado, estacion_id):
        cur = con.cursor()
        cur.execute("""
            INSERT INTO sensor (tipo, unidad, precision, rango_min, rango_max, estado, estacion_id)
            VALUES (?,?,?,?,?,?,?)
        """, (tipo, unidad, precision, rmin, rmax, estado, estacion_id))
        con.commit()

    def actualizar(self, con, sensor_id, tipo, unidad, precision, rmin, rmax, estado, estacion_id):
        cur = con.cursor()
        cur.execute("""
            UPDATE sensor
               SET tipo=?, unidad=?, precision=?, rango_min=?, rango_max=?, estado=?, estacion_id=?
             WHERE id=?
        """, (tipo, unidad, precision, rmin, rmax, estado, estacion_id, sensor_id))
        con.commit()

    def borrar(self, con, sensor_id):
        cur = con.cursor()
        cur.execute("DELETE FROM sensor WHERE id=?;", (sensor_id,))
        con.commit()
        return cur.rowcount > 0

# ==========================
# TKINTER APP (CRUD SENSOR)
# ==========================
class AppCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Sensores (SQLite)")
        self.root.geometry("720x420")

        # BD
        crear_bd()
        self.conn = create_connection()
        self.sensor_manager = SensorManager()
        self.estacion_manager = EstacionManager()

        # UI
        self._build_widgets()
        self._load_estaciones()
        self._load_sensores()

    def _build_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Campos
        row = 0
        ttk.Label(frm, text="Tipo:").grid(column=0, row=row, sticky="e")
        self.tipo_var = tk.StringVar()
        self.tipo_cb = ttk.Combobox(frm, textvariable=self.tipo_var, values=["temperatura","humedad","precipitacion","viento"], state="readonly")
        self.tipo_cb.grid(column=1, row=row, sticky="w", padx=6)
        self.tipo_cb.current(0)

        ttk.Label(frm, text="Unidad:").grid(column=2, row=row, sticky="e")
        self.unidad_var = tk.StringVar()
        self.unidad_cb = ttk.Combobox(frm, textvariable=self.unidad_var, values=["°C","%","mm","km/h"], state="readonly")
        self.unidad_cb.grid(column=3, row=row, sticky="w", padx=6)
        self.unidad_cb.current(0)

        row += 1
        ttk.Label(frm, text="Precisión:").grid(column=0, row=row, sticky="e")
        self.precision_entry = ttk.Entry(frm)
        self.precision_entry.grid(column=1, row=row, sticky="w", padx=6)

        ttk.Label(frm, text="Rango mín:").grid(column=2, row=row, sticky="e")
        self.rmin_entry = ttk.Entry(frm)
        self.rmin_entry.grid(column=3, row=row, sticky="w", padx=6)

        row += 1
        ttk.Label(frm, text="Rango máx:").grid(column=0, row=row, sticky="e")
        self.rmax_entry = ttk.Entry(frm)
        self.rmax_entry.grid(column=1, row=row, sticky="w", padx=6)

        ttk.Label(frm, text="Estado:").grid(column=2, row=row, sticky="e")
        self.estado_var = tk.IntVar(value=1)
        self.estado_cb = ttk.Combobox(frm, values=["Activo (1)", "Inactivo (0)"], state="readonly")
        self.estado_cb.current(0)
        self.estado_cb.grid(column=3, row=row, sticky="w", padx=6)

        row += 1
        ttk.Label(frm, text="Estación:").grid(column=0, row=row, sticky="e")
        self.estacion_var = tk.StringVar()
        self.estacion_cb = ttk.Combobox(frm, textvariable=self.estacion_var, state="readonly")
        self.estacion_cb.grid(column=1, row=row, sticky="w", padx=6, columnspan=3)

        # Botones
        row += 1
        btns = ttk.Frame(frm)
        btns.grid(column=0, row=row, columnspan=4, pady=8, sticky="w")
        ttk.Button(btns, text="Guardar", command=self._guardar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Actualizar", command=self._actualizar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Borrar", command=self._borrar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Limpiar", command=self._limpiar).pack(side=tk.LEFT, padx=4)

        # Listado
        row += 1
        self.sensor_list = tk.Listbox(frm, width=100, height=12)
        self.sensor_list.grid(column=0, row=row, columnspan=4, pady=8, sticky="nsew")
        frm.rowconfigure(row, weight=1)
        frm.columnconfigure(3, weight=1)
        self.sensor_list.bind("<<ListboxSelect>>", self._on_select)

        # Mapa id_estacion <-> nombre
        self._estaciones_map = {}   # nombre -> id
        self._estaciones_rev = {}   # id -> nombre

        # ID seleccionado
        self._selected_id = None

    def _load_estaciones(self):
        estaciones = self.estacion_manager.listar(self.conn)
        if not estaciones:
            # Crea una estación por defecto si no hay
            cur = self.conn.cursor()
            cur.execute("""INSERT INTO estacion_meteorologica
                           (nombre, latitud, longitud, altitud, activa, capacidad_registro, parcela_id)
                           VALUES (?,?,?,?,?,?,?)""",
                        ("Estación Centro", 6.25, -75.57, 1500, 1, 100, 1))
            self.conn.commit()
            estaciones = self.estacion_manager.listar(self.conn)

        nombres = []
        self._estaciones_map.clear()
        self._estaciones_rev.clear()
        for eid, nombre in estaciones:
            nombres.append(nombre)
            self._estaciones_map[nombre] = eid
            self._estaciones_rev[eid] = nombre
        self.estacion_cb["values"] = nombres
        if nombres:
            self.estacion_cb.current(0)

    def _load_sensores(self):
        self.sensor_list.delete(0, tk.END)
        registros = self.sensor_manager.leer(self.conn)
        for r in registros:
            linea = (f"ID={r['id']} | tipo={r['tipo']} | unidad={r['unidad']} | prec={r['precision']} "
                     f"| rango=({r['rango_min']},{r['rango_max']}) | estado={r['estado']} "
                     f"| estacion_id={r['estacion_id']} ({r['estacion']})")
            self.sensor_list.insert(tk.END, linea)

    def _leer_estado_cb(self):
        sel = self.estado_cb.get()
        return 1 if "Activo" in sel else 0

    def _guardar(self):
        try:
            tipo = self.tipo_var.get().strip()
            unidad = self.unidad_var.get().strip()
            precision = float(self.precision_entry.get())
            rmin = self.rmin_entry.get().strip()
            rmax = self.rmax_entry.get().strip()
            rmin_val = float(rmin) if rmin else None
            rmax_val = float(rmax) if rmax else None
            estado = self._leer_estado_cb()
            est_nombre = self.estacion_var.get()
            if not est_nombre:
                messagebox.showerror("Error", "Seleccione una estación.")
                return
            estacion_id = self._estaciones_map.get(est_nombre)

            if not tipo or not unidad:
                messagebox.showerror("Error", "Tipo y unidad son obligatorios.")
                return

            self.sensor_manager.guardar(self.conn, tipo, unidad, precision, rmin_val, rmax_val, estado, estacion_id)
            messagebox.showinfo("Éxito", "Sensor guardado.")
            self._limpiar()
            self._load_sensores()
        except ValueError:
            messagebox.showerror("Error", "Revise los campos numéricos (precisión, rangos).")

    def _actualizar(self):
        if self._selected_id is None:
            messagebox.showerror("Error", "Seleccione un sensor de la lista.")
            return
        try:
            tipo = self.tipo_var.get().strip()
            unidad = self.unidad_var.get().strip()
            precision = float(self.precision_entry.get())
            rmin = self.rmin_entry.get().strip()
            rmax = self.rmax_entry.get().strip()
            rmin_val = float(rmin) if rmin else None
            rmax_val = float(rmax) if rmax else None
            estado = self._leer_estado_cb()
            est_nombre = self.estacion_var.get()
            if not est_nombre:
                messagebox.showerror("Error", "Seleccione una estación.")
                return
            estacion_id = self._estaciones_map.get(est_nombre)

            self.sensor_manager.actualizar(self.conn, self._selected_id, tipo, unidad, precision, rmin_val, rmax_val, estado, estacion_id)
            messagebox.showinfo("Éxito", "Sensor actualizado.")
            self._limpiar()
            self._load_sensores()
        except ValueError:
            messagebox.showerror("Error", "Revise los campos numéricos (precisión, rangos).")

    def _borrar(self):
        if self._selected_id is None:
            messagebox.showerror("Error", "Seleccione un sensor de la lista.")
            return
        if messagebox.askyesno("Confirmar", f"¿Borrar sensor ID {self._selected_id}?"):
            if self.sensor_manager.borrar(self.conn, self._selected_id):
                messagebox.showinfo("Éxito", "Sensor borrado.")
                self._limpiar()
                self._load_sensores()

    def _limpiar(self):
        self._selected_id = None
        self.tipo_cb.current(0)
        self.unidad_cb.current(0)
        self.precision_entry.delete(0, tk.END)
        self.rmin_entry.delete(0, tk.END)
        self.rmax_entry.delete(0, tk.END)
        self.estado_cb.current(0)
        if self.estacion_cb["values"]:
            self.estacion_cb.current(0)
        self.sensor_list.selection_clear(0, tk.END)

    def _on_select(self, _event):
        sel = self.sensor_list.curselection()
        if not sel:
            return
        line = self.sensor_list.get(sel[0])
        # Parseo simple
        try:
            # ID=1 | tipo=temperatura | unidad=°C | prec=0.1 | rango=(0.0,60.0) | estado=1 | estacion_id=1 (Estación Centro)
            parts = {kv.split("=")[0].strip(): kv.split("=")[1].strip()
                     for kv in [seg.strip() for seg in line.split("|")] if "=" in kv}
            self._selected_id = int(parts["ID"])
            self.tipo_var.set(parts["tipo"])
            self.unidad_var.set(parts["unidad"])
            self.precision_entry.delete(0, tk.END)
            self.precision_entry.insert(0, parts["prec"])
            rango_txt = parts.get("rango", "(,)")
            rango_txt = rango_txt.strip().strip("()")
            rmin, rmax = [x.strip() for x in rango_txt.split(",")]
            self.rmin_entry.delete(0, tk.END)
            self.rmin_entry.insert(0, rmin if rmin != "" else "")
            self.rmax_entry.delete(0, tk.END)
            self.rmax_entry.insert(0, rmax if rmax != "" else "")
            self.estado_cb.current(0 if parts["estado"] == "1" else 1)

            # estación (extrae lo que viene al final entre paréntesis)
            if "(" in line and ")" in line:
                est_nombre = line[line.rfind("(")+1: line.rfind(")")]
                self.estacion_var.set(est_nombre)
        except Exception:
            # En caso de formato inesperado, simplemente ignora
            pass

if __name__ == "__main__":
    # Asegurar BD
    crear_bd()

    # Lanzar GUI
    root = tk.Tk()
    app = AppCRUD(root)
    root.mainloop()
