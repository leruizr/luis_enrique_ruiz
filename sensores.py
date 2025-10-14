# Módulo que define la jerarquía de sensores meteorológicos
# Implementa un diseño basado en clases abstractas para diferentes tipos de sensores
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from random import uniform
from typing import Final
from lectura import Lectura

@dataclass
class Sensor(ABC):
    id: int
    tipo: str
    estacion_id: int
    estado: bool

    @abstractmethod
    def obtener_lectura(self) -> Lectura: ...

    def esta_activo(self) -> bool:
        return self.estado

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, tipo={self.tipo}, activo={self.estado})"

@dataclass
class SensorTemperatura(Sensor):
    # Sensor específico para medir temperatura
    # Maneja rangos min/max y unidad de medida
    unidad: str
    rango_max: float
    rango_min: float

    def validar_rango(self, valor: float) -> bool:
        return self.rango_min <= valor <= self.rango_max

    def obtener_lectura(self) -> Lectura:
        valor = uniform(self.rango_min, self.rango_max)
        if not self.validar_rango(valor):
            raise ValueError("Temperatura fuera de rango")
        return Lectura(valor=round(valor, 2), fecha_hora=datetime.now(), sensor_id=self.id)

@dataclass
class SensorHumedad(Sensor):
    tipo_humedad: str
    fecha_calibracion: date

    _MIN: Final[float] = 0.0
    _MAX: Final[float] = 100.0

    def validar_rango(self, valor: float) -> bool:
        return self._MIN <= valor <= self._MAX

    def obtener_lectura(self) -> Lectura:
        valor = uniform(30.0, 90.0)
        if not self.validar_rango(valor):
            raise ValueError("Humedad fuera de rango")
        return Lectura(valor=round(valor, 1), fecha_hora=datetime.now(), sensor_id=self.id)

@dataclass
class SensorPrecipitacion(Sensor):
    tipo_medidor: str
    area_captacion: float  # m²

    def validar_rango(self, valor: float) -> bool:
        return valor >= 0.0

    def obtener_lectura(self) -> Lectura:
        valor = max(0.0, uniform(0.0, 15.0))
        if not self.validar_rango(valor):
            raise ValueError("Precipitación fuera de rango")
        return Lectura(valor=round(valor, 2), fecha_hora=datetime.now(), sensor_id=self.id)
    
    

# --- Pruebas  ---
"""
def _tests():
    from datetime import date
    t = SensorTemperatura(id=1, tipo="temperatura", estacion_id=1, estado=True, unidad="°C", rango_min=-5.0, rango_max=5.0)
    h = SensorHumedad(id=2, tipo="humedad", estacion_id=1, estado=True, tipo_humedad="relativa", fecha_calibracion=date(2025,1,1))
    p = SensorPrecipitacion(id=3, tipo="precipitacion", estacion_id=1, estado=True, tipo_medidor="pluv", area_captacion=0.02)
    lt = t.obtener_lectura(); assert -5.0 <= lt.valor <= 5.0
    lh = h.obtener_lectura(); assert 0.0 <= lh.valor <= 100.0
    lp = p.obtener_lectura(); assert lp.valor >= 0.0
    print("[sensores] OK")

if __name__ == "__main__":
    _tests()"""
