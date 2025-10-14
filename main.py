# Módulo principal que implementa un menú interactivo de demostración
# Permite crear y gestionar objetos del sistema meteorológico
from datetime import date
from usuario import Usuario
from parcela import Parcela
from estacion import EstacionMeteorologica
from sensores import SensorTemperatura, SensorHumedad, SensorPrecipitacion

def demo_datos():
    # Función que crea datos de ejemplo para la demostración
    est = EstacionMeteorologica(id=1, nombre="Estación Norte", coordenadas=(6.25, -75.56), altitud=1500.0, activa=True)
    s_temp = SensorTemperatura(id=101, tipo="temperatura", estacion_id=1, estado=True, unidad="°C", rango_min=-5.0, rango_max=45.0)
    s_hum  = SensorHumedad(id=102, tipo="humedad", estacion_id=1, estado=True, tipo_humedad="relativa", fecha_calibracion=date(2025,1,1))
    s_prec = SensorPrecipitacion(id=103, tipo="precipitacion", estacion_id=1, estado=True, tipo_medidor="pluviómetro", area_captacion=0.02)
    est.agregar_sensor(s_temp); est.agregar_sensor(s_hum); est.agregar_sensor(s_prec)

    parcela = Parcela(id=10, nombre="Parcela A", latitud=6.25, longitud=-75.56, altitud=1500.0,
                      area_ha=3.5, descripcion="Lote experimental", propietario_id=999)
    parcela.agregar_estacion(est)

    user = Usuario(id=500, nombre="Luis", rol="tecnico", email="leruizres@unadvirtual.edu.co",
                   telefono="+57-3000000000", zonas_interes=[1,2], permisos=["lectura_parcela"])
    user.asignar_parcela(parcela.id)
    return user, parcela, est

def menu():
    # Función principal que implementa el menú interactivo
    user, parcela, est = demo_datos()
    while True:
        print("""
===== MENÚ METEOROL =====
1) Ver usuario
2) Ver estaciones de la parcela
3) Ver sensores activos
4) Obtener lecturas actuales
5) Agregar sensor de temperatura a la estación
6) Remover sensor por ID
0) Salir
""")
        op = input("Opción: ").strip()
        if op == "1":
            print(user)
        elif op == "2":
            print(parcela)
            for e in parcela.estaciones:
                print(" -", e)
        elif op == "3":
            for s in est.obtener_sensores_activos():
                print(" -", s)
        elif op == "4":
            lects = parcela.obtener_datos_clima()
            for l in lects:
                print(f"{l.fecha_hora.isoformat()} | sensor={l.sensor_id} | valor={l.valor}")
            print(f"Total: {len(lects)} lecturas")
        elif op == "5":
            try:
                nuevo_id = int(input("ID del nuevo sensor de temperatura: ").strip())
                rmin = float(input("Rango mínimo (°C): ").strip())
                rmax = float(input("Rango máximo (°C): ").strip())
                s = SensorTemperatura(id=nuevo_id, tipo="temperatura", estacion_id=est.id, estado=True, unidad="°C", rango_min=rmin, rango_max=rmax)
                est.agregar_sensor(s)
                print("Sensor agregado.")
            except Exception as e:
                print("Error:", e)
        elif op == "6":
            try:
                sid = int(input("ID del sensor a remover: ").strip())
                est.remover_sensor(sid)
                print("Sensor removido (si existía).")
            except Exception as e:
                print("Error:", e)
        elif op == "0":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()
