import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Base de datos dentro de la carpeta del proyecto (requisito 8)
DB_NAME = os.path.join(os.path.dirname(__file__), "meteorologiadb.db")

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
        ttk.Button(btns, text="Generar informe", command=self._generar_informe).pack(side=tk.LEFT, padx=12)

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

        # Barra de estado inferior
        self.status = tk.StringVar(value="Listo")
        status_bar = ttk.Label(self.root, textvariable=self.status, anchor="w")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _load_estaciones(self):
        estaciones = self.estacion_manager.listar(self.conn)
        if not estaciones:
            # Crea una estación por defecto si no hay
            cur = self.conn.cursor()
            # Asegurar que exista una parcela por defecto (id) para la FK
            cur.execute("SELECT id FROM parcela ORDER BY id LIMIT 1;")
            row = cur.fetchone()
            if row:
                parcela_id = row[0]
            else:
                # crear parcela por defecto y usar su id
                cur.execute("INSERT INTO parcela (nombre, latitud, longitud, altitud, area_ha, descripcion, propietario_id) VALUES (?,?,?,?,?,?,?)", 
                            ("Parcela Default", 6.25, -75.57, 1500, 1.0, "Parcela creada por la app", None))
                parcela_id = cur.lastrowid
                self.conn.commit()

            cur.execute("""INSERT INTO estacion_meteorologica
                           (nombre, latitud, longitud, altitud, activa, capacidad_registro, parcela_id)
                           VALUES (?,?,?,?,?,?,?)""",
                        ("Estación Centro", 6.25, -75.57, 1500, 1, 100, parcela_id))
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
        # estado
        try:
            self.status.set(f"Sensores cargados: {len(registros)}")
        except Exception:
            pass

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

    # ------------------------
    # Reporte (datos + gráfico)
    # ------------------------
    def _generar_informe(self):
        try:
            cur = self.conn.cursor()
            # Estadísticas por tipo de sensor
            cur.execute("SELECT tipo, COUNT(*) FROM sensor GROUP BY tipo ORDER BY tipo;")
            por_tipo = cur.fetchall()

            # Sensores por estación
            cur.execute(
                """
                SELECT e.nombre, COUNT(s.id) AS total
                  FROM estacion_meteorologica e
             LEFT JOIN sensor s ON s.estacion_id = e.id
              GROUP BY e.id
              ORDER BY e.nombre
                """
            )
            por_estacion = cur.fetchall()

            # Lecturas por tipo de sensor
            cur.execute(
                """
                SELECT s.tipo, COUNT(l.id) AS n
                  FROM sensor s LEFT JOIN lectura l ON l.sensor_id = s.id
              GROUP BY s.tipo
              ORDER BY s.tipo
                """
            )
            lecturas_por_tipo = cur.fetchall()

            # Construir HTML con SVG de barras (sin librerías externas)
            html_path = os.path.join(os.path.dirname(__file__), "informe.html")

            def svg_barras(tuplas, titulo):
                if not tuplas:
                    return f"<h3>{titulo}</h3><p>Sin datos para mostrar.</p>"
                etiquetas = [str(t[0]) for t in tuplas]
                valores = [int(t[1]) for t in tuplas]
                max_v = max(valores) or 1
                ancho, alto, margen = 600, 220, 30
                escala = (alto - 2*margen) / max_v
                barras = []
                sep = (ancho - 2*margen) / max(1, len(valores))
                for i, v in enumerate(valores):
                    x = margen + i*sep + 8
                    bh = v * escala
                    y = alto - margen - bh
                    barras.append(f'<rect x="{x}" y="{y}" width="{max(10, sep-16):.1f}" height="{bh:.1f}" fill="#4e79a7" />')
                    barras.append(f'<text x="{x + max(10, sep-16)/2:.1f}" y="{y-4:.1f}" font-size="10" text-anchor="middle">{v}</text>')
                    barras.append(f'<text x="{x + max(10, sep-16)/2:.1f}" y="{alto - margen + 12}" font-size="10" text-anchor="middle">{etiquetas[i]}</text>')
                svg = f"""
                <h3>{titulo}</h3>
                <svg width="{ancho}" height="{alto}" role="img" aria-label="{titulo}">
                  <line x1="{margen}" y1="{alto-margen}" x2="{ancho-margen}" y2="{alto-margen}" stroke="#333" />
                  <line x1="{margen}" y1="{margen}" x2="{margen}" y2="{alto-margen}" stroke="#333" />
                  {''.join(barras)}
                </svg>
                """
                return svg

            html = """
            <!doctype html>
            <html lang=\"es\">
            <head>
              <meta charset=\"utf-8\">
              <title>Informe de Sensores y Lecturas</title>
              <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { margin-top: 0; }
                table { border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ccc; padding: 6px 10px; }
              </style>
            </head>
            <body>
              <h1>Informe de Sensores y Lecturas</h1>
            """

            html += svg_barras(por_tipo, "Sensores por tipo")
            html += svg_barras(por_estacion, "Sensores por estación")
            html += svg_barras(lecturas_por_tipo, "Lecturas por tipo de sensor")

            # Tabla de sensores
            cur.execute(
                """
                SELECT s.id, s.tipo, s.unidad, s.precision, e.nombre AS estacion
                  FROM sensor s JOIN estacion_meteorologica e ON e.id = s.estacion_id
                 ORDER BY s.id
                """
            )
            filas = cur.fetchall()
            html += "<h3>Listado de sensores</h3>"
            html += "<table><thead><tr><th>ID</th><th>Tipo</th><th>Unidad</th><th>Precisión</th><th>Estación</th></tr></thead><tbody>"
            for fid, tipo, unidad, prec, est in filas:
                html += f"<tr><td>{fid}</td><td>{tipo}</td><td>{unidad}</td><td>{prec}</td><td>{est}</td></tr>"
            html += "</tbody></table>"

            html += "</body></html>"

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)

            messagebox.showinfo("Informe", f"Informe generado: {html_path}")
            try:
                self.status.set("Informe generado correctamente")
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el informe: {e}")
            try:
                self.status.set("Error al generar el informe")
            except Exception:
                pass

if __name__ == "__main__":
    # Asegurar BD
    crear_bd()

    # Lanzar GUI
    root = tk.Tk()
    app = AppCRUD(root)
    root.mainloop()

# ----------------------------------------------
# Pruebas de software (comentadas) - Requisito 6
# ----------------------------------------------
# Para ejecutar estas pruebas rápidas, descomente los bloques "assert" y ejecute el script.
# No requieren librerías externas, sólo crearán/usaràn la BD local.
#
# from contextlib import closing
# def _run_small_tests():
#     crear_bd()
#     with closing(create_connection()) as con:
#         sm = SensorManager()
#         em = EstacionManager()
#         ests = em.listar(con)
#         if not ests:
#             # Forzar estación por defecto si no existe
#             cur = con.cursor()
#             cur.execute("INSERT INTO parcela (nombre, latitud, longitud, altitud, area_ha, descripcion) VALUES (?,?,?,?,?,?)",
#                         ("Test", 0.0, 0.0, None, None, ""))
#             parcela_id = cur.lastrowid
#             cur.execute("INSERT INTO estacion_meteorologica (nombre, latitud, longitud, parcela_id) VALUES (?,?,?,?)",
#                         ("Test Est", 0.0, 0.0, parcela_id))
#             con.commit()
#             est_id = cur.lastrowid
#         else:
#             est_id = ests[0][0]
#         # Crear
#         sm.guardar(con, "temperatura", "C", 0.1, None, None, 1, est_id)
#         filas = sm.leer(con)
#         assert any(f["tipo"] == "temperatura" for f in filas)
#         new_id = max(f["id"] for f in filas)
#         # Actualizar
#         sm.actualizar(con, new_id, "temperatura", "C", 0.5, None, None, 1, est_id)
#         filas = sm.leer(con)
#         assert any(f["id"] == new_id and float(f["precision"]) == 0.5 for f in filas)
#         # Borrar
#         ok = sm.borrar(con, new_id)
#         assert ok is True
#         print("Pruebas CRUD Sensor: OK")
#
# if __name__ == "__main__":
#     _run_small_tests()
