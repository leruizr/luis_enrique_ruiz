-- ========================================
-- BASE DE DATOS: Gestión de Clima y Datos Ambientales
-- ========================================

-- Activa las claves foráneas en SQLite
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ========== USUARIO ==========
CREATE TABLE IF NOT EXISTS usuario (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre         TEXT    NOT NULL,
  rol            TEXT    NOT NULL,          -- agricultor | tecnico | admin
  email          TEXT    UNIQUE,
  telefono       TEXT,
  zonas_interes  TEXT,
  permisos       TEXT
);

-- ========== PARCELA ==========
CREATE TABLE IF NOT EXISTS parcela (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre         TEXT   NOT NULL,
  latitud        REAL   NOT NULL,
  longitud       REAL   NOT NULL,
  altitud        REAL,
  area_ha        REAL,
  descripcion    TEXT,
  propietario_id INTEGER,
  FOREIGN KEY (propietario_id) REFERENCES usuario(id)
    ON UPDATE NO ACTION ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_parcela_propietario
  ON parcela(propietario_id);

-- ========== USUARIO_PARCELA ==========
CREATE TABLE IF NOT EXISTS usuario_parcela (
  usuario_id INTEGER NOT NULL,
  parcela_id INTEGER NOT NULL,
  PRIMARY KEY (usuario_id, parcela_id),
  FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    ON UPDATE NO ACTION ON DELETE CASCADE,
  FOREIGN KEY (parcela_id) REFERENCES parcela(id)
    ON UPDATE NO ACTION ON DELETE CASCADE
);

-- ========== ESTACION_METEOROLOGICA ==========
CREATE TABLE IF NOT EXISTS estacion_meteorologica (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre             TEXT    NOT NULL,
  latitud            REAL    NOT NULL,
  longitud           REAL    NOT NULL,
  altitud            REAL,
  activa             INTEGER NOT NULL DEFAULT 1,  -- 0/1
  capacidad_registro INTEGER NOT NULL DEFAULT 100,
  parcela_id         INTEGER NOT NULL,
  FOREIGN KEY (parcela_id) REFERENCES parcela(id)
    ON UPDATE NO ACTION ON DELETE CASCADE,
  UNIQUE (nombre, parcela_id)
);

CREATE INDEX IF NOT EXISTS idx_estacion_parcela
  ON estacion_meteorologica(parcela_id);

-- ========== SENSOR ==========
CREATE TABLE IF NOT EXISTS sensor (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo               TEXT   NOT NULL,      -- temperatura | humedad | precipitacion | viento
  unidad             TEXT   NOT NULL,      -- °C | % | mm | km/h
  precision          REAL   NOT NULL,
  rango_min          REAL,
  rango_max          REAL,
  estado             INTEGER NOT NULL DEFAULT 1,   -- 0/1
  estacion_id        INTEGER NOT NULL,
  tipo_humedad       TEXT,
  fecha_calibracion  NUMERIC,              -- DATE/DATETIME ISO-8601
  tipo_medidor       TEXT,
  area_captacion     REAL,
  FOREIGN KEY (estacion_id) REFERENCES estacion_meteorologica(id)
    ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sensor_estacion ON sensor(estacion_id);
CREATE INDEX IF NOT EXISTS idx_sensor_tipo     ON sensor(tipo);

-- ========== LECTURA ==========
CREATE TABLE IF NOT EXISTS lectura (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  sensor_id    INTEGER  NOT NULL,
  fecha_hora   NUMERIC  NOT NULL,          -- DATETIME ISO-8601
  valor        REAL     NOT NULL,
  calidad_dato TEXT     DEFAULT 'OK',
  fuente       TEXT     DEFAULT 'automatica',
  FOREIGN KEY (sensor_id) REFERENCES sensor(id)
    ON UPDATE NO ACTION ON DELETE CASCADE,
  UNIQUE (sensor_id, fecha_hora)
);

CREATE INDEX IF NOT EXISTS idx_lectura_sensor_fecha
  ON lectura(sensor_id, fecha_hora);

-- ===============================
-- DATOS DE PRUEBA
-- ===============================

-- Usuario
INSERT INTO usuario (nombre, rol, email, telefono)
VALUES ('Luis Enrique Ruiz', 'tecnico', 'luis@example.com', '+57-3000000000');

-- Parcela
INSERT INTO parcela (nombre, latitud, longitud, altitud, area_ha, descripcion, propietario_id)
VALUES ('Parcela La Esperanza', 6.2518, -75.5636, 1500, 12.5, 'Parcela demostrativa para lecturas climáticas', 1);

-- Relación usuario-parcela
INSERT INTO usuario_parcela (usuario_id, parcela_id) VALUES (1, 1);

-- Estación meteorológica
INSERT INTO estacion_meteorologica (nombre, latitud, longitud, altitud, activa, capacidad_registro, parcela_id)
VALUES ('Estación Centro', 6.2519, -75.5637, 1510, 1, 100, 1);

-- Sensores
INSERT INTO sensor (tipo, unidad, precision, rango_min, rango_max, estado, estacion_id)
VALUES
  ('temperatura', '°C', 0.1, -20, 60, 1, 1),
  ('humedad', '%', 1.0, 0, 100, 1, 1),
  ('precipitacion', 'mm', 0.1, 0, 500, 1, 1);

-- Lecturas
INSERT INTO lectura (sensor_id, fecha_hora, valor)
VALUES
  (1, '2025-10-13 08:00:00', 21.8),
  (2, '2025-10-13 08:00:00', 63.0),
  (3, '2025-10-13 08:00:00', 2.4),
  (1, '2025-10-13 12:00:00', 24.1),
  (2, '2025-10-13 12:00:00', 58.0),
  (3, '2025-10-13 12:00:00', 0.0);

COMMIT;
