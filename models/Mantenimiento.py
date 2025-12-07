from __future__ import annotations
from datetime import datetime
from uuid import uuid4, UUID


class Mantenimiento:

    # Clase que representa una operación de mantenimiento o reparación de un vehículo. Nos permite registrar cuándo se realiza, qué se ha hecho y el coste asociado.

    def __init__(self, vehiculo, motivo: str, fecha_inicio: str, fecha_fin: str, coste: float, tipo: str = "REVISIÓN"):
        # Asignamos un ID incremental a cada registro de mantenimiento
        self.id: UUID = uuid4()

        # Asociamos el mantenimiento a un vehículo concreto
        self.vehiculo = vehiculo

        # Guardamos la información del mantenimiento
        self.motivo = motivo.strip()
        self.fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        self.fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        self.coste = coste
        self.tipo = tipo.strip().upper()  # Ejemplo: "REVISIÓN", "REPARACIÓN", "ITV"

        # Validaciones básicas
        if not self.motivo:
            raise ValueError("El motivo no puede estar vacío.")
        if self.coste < 0:
            raise ValueError("El coste no puede ser negativo.")
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        if self.tipo not in ["REVISIÓN", "REPARACIÓN", "ITV", "OTRO"]:
            raise ValueError("El tipo de mantenimiento no es válido.")

        # Al registrar un mantenimiento, cambiamos el estado del vehículo
        self.vehiculo.cambiar_estado("MANTENIMIENTO")

    def finalizar_mantenimiento(self):
        # Una vez finalizado el mantenimiento, devolvemos el vehículo a disponible
        self.vehiculo.cambiar_estado("DISPONIBLE")

    def __str__(self):
        # Mostramos un resumen del mantenimiento
        return (f"[Mantenimiento#{self.id}] Vehículo: {self.vehiculo.matricula} | "
                f"Tipo: {self.tipo} | Desde: {self.fecha_inicio.date()} Hasta: {self.fecha_fin.date()} | "
                f"Coste: {self.coste:.2f}€ | Motivo: {self.motivo}")
