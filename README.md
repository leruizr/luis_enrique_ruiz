# Tarea 2 — Modelando la Realidad con Clases y Objetos


**Autor:** Luis Enrique Ruiz Restrepo

El diagrama se elaboro en diagram.io y se encuentra de dos formas el  png y el .drawio 

Proyecto en **Python** orientado a objetos para gestionar **Usuarios**, **Parcelas**, **Estaciones** y **Sensores** que generan **Lecturas**.

## Archivos
- `lectura.py` — Clase `Lectura` (+ pruebas dentro del archivo).
- `sensores.py` — Clases `Sensor` (abstracta), `SensorTemperatura`, `SensorHumedad`, `SensorPrecipitacion` (+ pruebas).
- `estacion.py` — Clase `EstacionMeteorologica` (+ pruebas).
- `parcela.py` — Clase `Parcela` (+ pruebas).
- `usuario.py` — Clase `Usuario` (+ pruebas).
- `main.py` — Menú simple para ejecutar una demo y operar objetos.

## Requisitos
- Python 3.11+

## Ejecutar menú/demostración
```bash
python main.py


Proyecto: Sistema de Gestión Meteorológica con SQLite y Tkinter

Script principal
- Ejecutar: `main.py` (muestra el menú en interfaz gráfica)
- Requisitos: Python 3.8+

Ejecución (menú gráfico)
- Desde esta carpeta, ejecutar: `python main.py`
- Se abre una ventana con el menú METEOROL (botones equivalentes a las opciones).

Interfaz gráfica (GUI)
- Para abrir la GUI Tkinter de gestión de sensores, ejecutar: `python indexdb.py`
- La GUI crea el archivo de base de datos `meteorologiadb.db` en esta carpeta si no existe.
- Funcionalidades GUI:
  - CRUD de Sensores (crear, consultar, actualizar, eliminar)
  - Estación/parcela por defecto automática para asociar sensores
  - Botón "Generar informe": crea `informe.html` con gráficos (SVG) y datos

Estructura de datos (SQLite)
- Tablas: `usuario`, `parcela`, `usuario_parcela`, `estacion_meteorologica`, `sensor`, `lectura`.
- Se habilitan claves foráneas (`PRAGMA foreign_keys = ON`).

Pruebas
- En `indexdb.py` se incluyen fragmentos de pruebas comentadas (al final del archivo).
- Para usarlas, descomente los bloques indicados y ejecute el script.

Notas
- No se requieren librerías externas para los gráficos; el informe es HTML con SVG.
- Abra `informe.html` con cualquier navegador.
