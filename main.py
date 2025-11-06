# Trabajo Final de Arquitectura de Software
# Realizado por: 
# Alex Caride
# Pablo Barrán
# Daniel López

# Archivo principal para ejecutar el sistema de alquiler de coches

from services import AlquilerServicio
from models import Vehiculo, Coche, Moto, Furgoneta, Sucursal, Tarifa, Cliente, Administrador


def main():
    # Creamos el servicio principal del sistema de alquiler
    sistema = AlquilerServicio()

    # Registramos usuarios
    admin1 = sistema.registrar_usuario("admin", "Laura", "laura@empresa.com")
    cliente1 = sistema.registrar_usuario("cliente", "Carlos", "carlos@gmail.com", licencia="B1234567", direccion="Av. Galicia 12")
    cliente2 = sistema.registrar_usuario("cliente", "Ana", "ana@gmail.com", licencia="B7654321", direccion="Rúa Barcelona 22")

    # Creamos sucursales
    sucursal1 = sistema.agregar_sucursal("Sucursal Centro", "Calle Ángel Rebollo 45", "981 000 123")
    sucursal2 = sistema.agregar_sucursal("Sucursal Norte", "Av. Finisterre 99", "981 123 456")

    # Añadimos vehículos
    v1 = sistema.registrar_vehiculo("Coche", "1234ABC", "Toyota", "Corolla", 2021, "Compacto", 25000, sucursal1, puertas=5)
    v2 = sistema.registrar_vehiculo("Moto", "5678XYZ", "Yamaha", "MT-07", 2022, "Moto", 8000, sucursal1, cilindrada=700)
    v3 = sistema.registrar_vehiculo("Furgoneta", "9999KLM", "Ford", "Transit", 2020, "Carga", 60000, sucursal2, carga=800)

    # Creamos tarifas (con los nuevos parámetros de kilometraje y recargos)
    t1 = sistema.crear_tarifa("Tarifa Coche", "Compacto", 45.0, km_incluidos=300, coste_km_extra=0.15, recargo_retraso=25.0, penalizacion_comb=40.0)
    t2 = sistema.crear_tarifa("Tarifa Moto", "Moto", 30.0, km_incluidos=200, coste_km_extra=0.10, recargo_retraso=15.0, penalizacion_comb=25.0)
    t3 = sistema.crear_tarifa("Tarifa Furgoneta", "Carga", 60.0, km_incluidos=400, coste_km_extra=0.20, recargo_retraso=30.0, penalizacion_comb=50.0)

    # Listamos los vehículos disponibles
    print("\n Vehículos disponibles:")
    for v in sistema.listar_vehiculos_disponibles():
        print(" ", v)

    # Realizamos reservas
    print("\n Reservas realizadas:")

    reserva1 = sistema.realizar_reserva(cliente1.id, v1.id, "2025-11-01", "2025-11-05", sucursal2.id)
    print(reserva1, "\n")

    reserva2 = sistema.realizar_reserva(cliente2.id, v2.id, "2025-11-02", "2025-11-03", sucursal1.id)
    print(reserva2, "\n")

    # Finalizamos una reserva (simulando entrega con km extra, retraso y combustible incorrecto)
    print("\n Finalización de reserva:")
    pago_info = sistema.finalizar_reserva(
        reserva1.id,
        km_recorridos=650,         # se superan los km incluidos
        retraso_dias=1,            # se devuelve con un día de retraso
        combustible_correcto=False,  # se devuelve con el depósito sin llenar
        metodo_pago="Tarjeta"
    )

    # Mostramos el resumen de pago
    print("Resumen de pago:")
    for clave, valor in pago_info.items():
        print(f"  {clave}: {valor}")
    print()

    # Registramos un mantenimiento (ahora con fecha de inicio y fin)
    print(" Mantenimientos realizados:")
    mantenimiento1 = sistema.registrar_mantenimiento(
        v3.id,
        "Cambio de aceite y revisión general",
        "2025-11-06",
        "2025-11-07",
        75.50,
        "Revisión"
    )
    print(mantenimiento1, "\n")

    # Finalizamos el mantenimiento
    sistema.finalizar_mantenimiento(mantenimiento1.id)

    # Listamos los vehículos tras las operaciones
    print("\n Estado final de los vehículos:")
    for v in sistema.vehiculos.values():
        print(" ", v)


if __name__ == "__main__":
    main()
