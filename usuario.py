# Módulo que define la gestión de usuarios del sistema
# Maneja permisos y asignación de parcelas a usuarios
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

@dataclass
class Usuario:
    id: int
    nombre: str
    rol: str
    email: str
    telefono: str
    zonas_interes: List[int]
    permisos: List[str]
    parcelas_asignadas: List[int] = field(default_factory=list)

    def puede_acceder_parcela(self, parcela_id: int) -> bool:
        return "lectura_parcela" in self.permisos and parcela_id in self.parcelas_asignadas

    def asignar_parcela(self, parcela_id: int) -> None:
        if parcela_id not in self.parcelas_asignadas:
            self.parcelas_asignadas.append(parcela_id)

    def obtener_parcelas(self) -> List[int]:
        return list(self.parcelas_asignadas)

    def __str__(self) -> str:
        return f"Usuario(id={self.id}, nombre='{self.nombre}', rol='{self.rol}', parcelas={self.parcelas_asignadas})"

# --- Pruebas ---
"""
def _tests():
    u = Usuario(id=1, nombre="Luis", rol="tecnico", email="l@x.com", telefono="123", zonas_interes=[1], permisos=["lectura_parcela"])
    u.asignar_parcela(10)
    assert u.puede_acceder_parcela(10) is True
    assert u.puede_acceder_parcela(11) is False
    assert u.obtener_parcelas() == [10]
    print("[usuario] OK")

if __name__ == "__main__":
    _tests()"""
