from datetime import date
import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

from usuario import Usuario
from parcela import Parcela
from estacion import EstacionMeteorologica
from sensores import (
    SensorTemperatura,
    SensorHumedad,
    SensorPrecipitacion,
)


def demo_datos():
    """Crea datos de ejemplo para la demostración (igual que antes)."""
    est = EstacionMeteorologica(
        id=1,
        nombre="Estación Norte",
        coordenadas=(6.25, -75.56),
        altitud=1500.0,
        activa=True,
    )
    s_temp = SensorTemperatura(
        id=101,
        tipo="temperatura",
        estacion_id=1,
        estado=True,
        unidad="°C",
        rango_min=-5.0,
        rango_max=45.0,
    )
    s_hum = SensorHumedad(
        id=102,
        tipo="humedad",
        estacion_id=1,
        estado=True,
        tipo_humedad="relativa",
        fecha_calibracion=date(2025, 1, 1),
    )
    s_prec = SensorPrecipitacion(
        id=103,
        tipo="precipitacion",
        estacion_id=1,
        estado=True,
        tipo_medidor="pluviómetro",
        area_captacion=0.02,
    )
    est.agregar_sensor(s_temp)
    est.agregar_sensor(s_hum)
    est.agregar_sensor(s_prec)

    parcela = Parcela(
        id=10,
        nombre="Parcela A",
        latitud=6.25,
        longitud=-75.56,
        altitud=1500.0,
        area_ha=3.5,
        descripcion="Lote experimental",
        propietario_id=999,
    )
    parcela.agregar_estacion(est)

    user = Usuario(
        id=500,
        nombre="Luis",
        rol="tecnico",
        email="leruizres@unadvirtual.edu.co",
        telefono="+57-3000000000",
        zonas_interes=[1, 2],
        permisos=["lectura_parcela"],
    )
    user.asignar_parcela(parcela.id)
    return user, parcela, est


class MenuGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MENÚ METEOROL")
        self.root.geometry("640x440")

        # Datos de demostración (igual que en consola)
        self.user, self.parcela, self.est = demo_datos()

        # Encabezado con el menú textual (exacto)
        menu_txt = (
            "===== MENÚ METEOROL =====\n"
            "1) Ver usuario\n"
            "2) Ver estaciones de la parcela\n"
            "3) Ver sensores activos\n"
            "4) Obtener lecturas actuales\n"
            "5) Agregar sensor de temperatura a la estación\n"
            "6) Remover sensor por ID\n"
            "0) Salir"
        )
        lbl = tk.Label(
            self.root, text=menu_txt, justify="left", anchor="w", font=("Consolas", 10)
        )
        lbl.pack(fill=tk.X, padx=12, pady=8)
        lbl2 = tk.Label(
            self.root,
            text=(
                "7) Iniciar/Detener servidor de soporte técnico\n"
                "8) chat_soporte_tecnico (cliente)"
            ),
            justify="left",
            anchor="w",
            font=("Consolas", 10),
        )
        lbl2.pack(fill=tk.X, padx=12, pady=(0, 8))
        # Ajuste de texto: una sola opción de soporte técnico
        try:
            lbl2.config(text="7) soporte_tecnico (inicia servidor y 2 chats)")
        except Exception:
            pass
        # Simplificación: un único label con todas las opciones
        try:
            lbl2.destroy()
        except Exception:
            pass
        lbl.config(text=menu_txt + "\n7) soporte_tecnico (inicia servidor y 2 chats)")

        # Botones de acciones
        btns = tk.Frame(self.root)
        btns.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Button(btns, text="1) Ver usuario", width=42, command=self.ver_usuario).pack(
            anchor="w", pady=4
        )
        tk.Button(
            btns, text="2) Ver estaciones de la parcela", width=42, command=self.ver_estaciones
        ).pack(anchor="w", pady=4)
        tk.Button(
            btns, text="3) Ver sensores activos", width=42, command=self.ver_sensores_activos
        ).pack(anchor="w", pady=4)
        tk.Button(
            btns,
            text="4) Obtener lecturas actuales",
            width=42,
            command=self.obtener_lecturas,
        ).pack(anchor="w", pady=4)
        tk.Button(
            btns,
            text="5) Agregar sensor de temperatura",
            width=42,
            command=self.agregar_sensor_temperatura,
        ).pack(anchor="w", pady=4)
        tk.Button(
            btns,
            text="6) Remover sensor por ID",
            width=42,
            command=self.remover_sensor,
        ).pack(anchor="w", pady=4)
        tk.Button(
            btns,
            text="7) soporte tecnico (iniciar)",
            width=42,
            command=self.soporte_tecnico,
        ).pack(anchor="w", pady=4)
        tk.Button(btns, text="0) Salir", width=42, command=self.root.destroy).pack(
            anchor="w", pady=4
        )
        # Proceso del servidor (si se abre en consola separada)
        self._server_proc = None

    def ver_usuario(self):
        messagebox.showinfo("Usuario", str(self.user))

    def ver_estaciones(self):
        lineas = [str(self.parcela)] + [f" - {e}" for e in self.parcela.estaciones]
        messagebox.showinfo("Estaciones de la parcela", "\n".join(lineas))

    def ver_sensores_activos(self):
        activos = self.est.obtener_sensores_activos()
        if not activos:
            messagebox.showinfo("Sensores activos", "No hay sensores activos")
            return
        texto = "\n".join(f" - {s}" for s in activos)
        messagebox.showinfo("Sensores activos", texto)

    def obtener_lecturas(self):
        lects = self.parcela.obtener_datos_clima()
        if not lects:
            messagebox.showinfo("Lecturas", "No hay lecturas disponibles")
            return
        texto = "\n".join(
            f"{l.fecha_hora.isoformat()} | sensor={l.sensor_id} | valor={l.valor}"
            for l in lects
        )
        texto += f"\nTotal: {len(lects)} lecturas"
        messagebox.showinfo("Lecturas", texto)

    def agregar_sensor_temperatura(self):
        try:
            nuevo_id = simpledialog.askinteger(
                "Nuevo sensor", "ID del nuevo sensor de temperatura:"
            )
            if nuevo_id is None:
                return
            rmin = simpledialog.askfloat("Rango mínimo", "Rango mínimo (°C):")
            if rmin is None:
                return
            rmax = simpledialog.askfloat("Rango máximo", "Rango máximo (°C):")
            if rmax is None:
                return
            s = SensorTemperatura(
                id=nuevo_id,
                tipo="temperatura",
                estacion_id=self.est.id,
                estado=True,
                unidad="°C",
                rango_min=rmin,
                rango_max=rmax,
            )
            self.est.agregar_sensor(s)
            messagebox.showinfo("Éxito", "Sensor agregado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remover_sensor(self):
        try:
            sid = simpledialog.askinteger("Remover sensor", "ID del sensor a remover:")
            if sid is None:
                return
            antes = len(self.est.sensores)
            self.est.remover_sensor(sid)
            despues = len(self.est.sensores)
            if despues < antes:
                messagebox.showinfo("Éxito", "Sensor removido.")
            else:
                messagebox.showinfo("Resultado", "No se encontró el sensor.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_servidor_soporte(self):
        try:
            # Si el proceso existe y sigue activo, se detiene
            if self._server_proc is not None and getattr(self._server_proc, "poll", lambda: None)() is None:
                try:
                    self._server_proc.terminate()
                except Exception:
                    pass
                self._server_proc = None
                messagebox.showinfo("Servidor", "Servidor de soporte detenido.")
                return

            # Iniciar servidor en nueva consola para permitir entrada del operador
            py = sys.executable or "python"
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            self._server_proc = subprocess.Popen(
                [py, "servidor.py"],
                creationflags=creationflags,
                cwd=os.getcwd(),
            )
            messagebox.showinfo(
                "Servidor",
                "Servidor de soporte iniciado en una nueva consola.\nUse /usuarios y /salir allí.",
            )
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró servidor.py")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar/detener: {e}")

    def abrir_cliente_chat(self):
        try:
            py = sys.executable or "python"
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            subprocess.Popen(
                [py, "cliente_chat.py"],
                creationflags=creationflags,
                cwd=os.getcwd(),
            )
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró cliente_chat.py")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el cliente: {e}")


    def soporte_tecnico(self):
        try:
            py = sys.executable or "python"
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

            # Iniciar servidor si no está corriendo
            if self._server_proc is None or getattr(self._server_proc, "poll", lambda: 1)() is not None:
                self._server_proc = subprocess.Popen(
                    [py, "servidor.py"],
                    creationflags=creationflags,
                    cwd=os.getcwd(),
                )

            # Abrir dos clientes para pruebas locales
            subprocess.Popen([py, "cliente_chat.py"], creationflags=creationflags, cwd=os.getcwd())
            subprocess.Popen([py, "cliente_chat.py"], creationflags=creationflags, cwd=os.getcwd())

            messagebox.showinfo(
                "Soporte técnico",
                "Servidor iniciado (si no lo estaba) y se abrieron 2 clientes.",
            )
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Archivo no encontrado: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar soporte técnico: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuGUI(root)
    root.mainloop()