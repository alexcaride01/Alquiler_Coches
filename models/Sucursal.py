from __future__ import annotations
from uuid import uuid4, UUID


class Sucursal:
    # Clase que representa una sucursal dentro del sistema de alquiler. Cada sucursal tiene su propio inventario de vehículos y gestiona las reservas locales.

    def __init__(self, nombre: str, direccion: str, telefono: str):
        # Asignamos un ID incremental a cada sucursal
        self.id: UUID = uuid4()

        # Guardamos los datos principales de la sucursal
        self.nombre = nombre.strip()
        self.direccion = direccion.strip()
        self.telefono = telefono.strip()

        # Creamos listas para almacenar los vehículos y las reservas de esta sucursal
        self.vehiculos = []
        self.reservas = []

        # Validamos los datos básicos
        if not self.nombre:
            raise ValueError("El nombre de la sucursal no puede estar vacía.")
        if not self.direccion:
            raise ValueError("La dirección no puede estar vacía.")
        if not self.telefono:
            raise ValueError("El teléfono no puede estar vacío.")

    def agregar_vehiculo(self, vehiculo):
        # Añadimos un vehículo al inventario de la sucursal
        self.vehiculos.append(vehiculo)
        vehiculo.sucursal = self  # Asociamos el vehículo con esta sucursal

    def registrar_reserva(self, reserva):
        # Asociamos una reserva a la sucursal
        self.reservas.append(reserva)

    def listar_vehiculos_disponibles(self):
        # Devolvemos solo los vehículos que estén disponibles
        return [v for v in self.vehiculos if v.estado == "DISPONIBLE"]

    def __str__(self):
        # Mostramos la información principal de la sucursal
        return (f"[Sucursal#{self.id}] {self.nombre} | Dirección: {self.direccion} | "
                f"Teléfono: {self.telefono} | Vehículos: {len(self.vehiculos)} | Reservas: {len(self.reservas)}")
