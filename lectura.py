# Módulo que define la estructura de datos para lecturas de sensores
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Lectura:
    valor: float
    fecha_hora: datetime
    sensor_id: int

    def __str__(self) -> str:
        return f"Lectura(sensor={self.sensor_id}, valor={self.valor}, fecha={self.fecha_hora.isoformat()})"

# --- Pruebas ---
"""def _tests():
    l = Lectura(valor=23.5, fecha_hora=datetime(2025, 1, 1, 12, 0, 0), sensor_id=1)
    s = str(l)
    assert "sensor=1" in s
    assert "23.5" in s
    print("[lectura] OK")

if __name__ == "__main__":
    _tests()"""
