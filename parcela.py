# Módulo que define la estructura de una parcela agrícola
# Incluye información geográfica y gestión de estaciones meteorológicas
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from estacion import EstacionMeteorologica
from lectura import Lectura

@dataclass
class Suelo:
    tipo: str | None = None

@dataclass
class FuenteAgua:
    nombre: str | None = None

@dataclass
class Parcela:
    id: int
    nombre: str
    latitud: float
    longitud: float
    altitud: float
    area_ha: float
    descripcion: str
    propietario_id: int
    suelo: Optional[Suelo] = None
    fuentes_agua: Optional[List[FuenteAgua]] = None
    estaciones: List[EstacionMeteorologica] = field(default_factory=list)

    def agregar_estacion(self, estacion: EstacionMeteorologica) -> None:
        self.estaciones.append(estacion)

    def remover_estacion(self, estacion_id: int) -> None:
        self.estaciones = [e for e in self.estaciones if e.id != estacion_id]

    def obtener_estaciones_activas(self) -> List[EstacionMeteorologica]:
        return [e for e in self.estaciones if e.activa]

    def obtener_datos_clima(self) -> List[Lectura]:
        lecturas: List[Lectura] = []
        for e in self.obtener_estaciones_activas():
            lecturas.extend(e.obtener_todas_lecturas())
        return lecturas

    def __str__(self) -> str:
        return f"Parcela(id={self.id}, nombre='{self.nombre}', estaciones={len(self.estaciones)})"

# --- Pruebas  ---
"""def _tests():
    from sensores import SensorTemperatura
    from estacion import EstacionMeteorologica
    p = Parcela(id=1, nombre="P1", latitud=0, longitud=0, altitud=0, area_ha=1, descripcion="x", propietario_id=1)
    e = EstacionMeteorologica(id=1, nombre="E1", coordenadas=(0.0,0.0), altitud=10.0, activa=True)
    s = SensorTemperatura(id=10, tipo="temperatura", estacion_id=1, estado=True, unidad="°C", rango_min=0, rango_max=1)
    e.agregar_sensor(s)
    p.agregar_estacion(e)
    lects = p.obtener_datos_clima()
    assert len(lects) >= 1
    p.remover_estacion(1)
    assert len(p.estaciones) == 0
    print("[parcela] OK")

if __name__ == "__main__":
    _tests()"""
