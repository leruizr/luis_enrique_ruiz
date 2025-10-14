# Módulo que define la estación meteorológica
# Gestiona un conjunto de sensores y coordina la obtención de lecturas
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
from lectura import Lectura
from sensores import Sensor

# Define tipo personalizado para coordenadas geográficas
Coord = tuple[float, float] | str | Tuple[float, float]

@dataclass
class EstacionMeteorologica:
    id: int
    nombre: str
    coordenadas: Coord
    altitud: float
    activa: bool
    sensores: List[Sensor] = field(default_factory=list)

    def agregar_sensor(self, sensor: Sensor) -> None:
        self.sensores.append(sensor)

    def remover_sensor(self, sensor_id: int) -> None:
        self.sensores = [s for s in self.sensores if s.id != sensor_id]

    def obtener_sensores_activos(self) -> List[Sensor]:
        return [s for s in self.sensores if s.esta_activo()]

    def obtener_todas_lecturas(self) -> List[Lectura]:
        lecturas: List[Lectura] = []
        for s in self.obtener_sensores_activos():
            lecturas.append(s.obtener_lectura())
        return lecturas

    def __str__(self) -> str:
        return f"Estacion(id={self.id}, nombre='{self.nombre}', activa={self.activa}, sensores={len(self.sensores)})"

# --- Pruebas  ---
"""def _tests():
    from sensores import SensorTemperatura
    e = EstacionMeteorologica(id=1, nombre="E1", coordenadas=(0.0,0.0), altitud=10.0, activa=True)
    s = SensorTemperatura(id=10, tipo="temperatura", estacion_id=1, estado=True, unidad="°C", rango_min=0, rango_max=1)
    e.agregar_sensor(s)
    assert len(e.sensores) == 1
    lects = e.obtener_todas_lecturas()
    assert len(lects) >= 1
    e.remover_sensor(10)
    assert len(e.sensores) == 0
    print("[estacion] OK")

if __name__ == "__main__":
    _tests()"""
