from __future__ import annotations
from datetime import datetime
from uuid import uuid4, UUID


class Reserva:
    # Clase que representa una reserva dentro del sistema de alquiler. En ella gestionamos la relación entre un cliente, un vehículo y las fechas del alquiler.

    def __init__(self, cliente, vehiculo, fecha_inicio: str, fecha_fin: str, tarifa, sucursal_recogida, sucursal_devolucion):
        # Asignamos un ID incremental a la reserva
        self.id: UUID = uuid4()

        # Asociamos el cliente y el vehículo implicados
        self.cliente = cliente
        self.vehiculo = vehiculo

        # Asociamos también las sucursales de recogida y devolución
        self.sucursal_recogida = sucursal_recogida
        self.sucursal_devolucion = sucursal_devolucion

        # Guardamos la tarifa como objeto (ya no solo el precio diario)
        self.tarifa = tarifa

        # Guardamos las fechas de inicio y fin del alquiler
        self.fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        self.fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        # Validaciones básicas
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # Calculamos la duración total y el coste estimado usando la tarifa
        self.dias = (self.fecha_fin - self.fecha_inicio).days
        self.total_estimado = self.tarifa.calcular_precio(self.dias)

        # Estado inicial de la reserva
        self.estado = "ACTIVA"  # Podrá cambiar a FINALIZADA o CANCELADA

        # Añadimos campos para el control de pago
        self.pagada = False
        self.total_final = None
        self.metodo_pago = None

    def finalizar_reserva(self, km_recorridos: float = 0, retraso_dias: int = 0, combustible_correcto: bool = True):
        # Calculamos el coste final utilizando la tarifa, teniendo en cuenta días, km, retrasos y combustible
        coste_final = self.tarifa.calcular_precio(
            self.dias,
            km_recorridos=km_recorridos,
            retraso_dias=retraso_dias,
            combustible_correcto=combustible_correcto
        )

        # Cambiamos el estado de la reserva y guardamos el total final
        self.total_final = round(coste_final, 2)
        self.estado = "FINALIZADA"

        # Devolvemos el importe total final
        return self.total_final

    def registrar_pago(self, metodo: str = "Tarjeta"):
        # Marcamos la reserva como pagada (simulamos el proceso de cobro)
        if self.estado != "FINALIZADA":
            raise ValueError("Solo se pueden pagar reservas finalizadas.")
        self.pagada = True
        self.metodo_pago = metodo

    def cancelar_reserva(self):
        # Permitimos cancelar una reserva antes de que comience
        if self.estado != "ACTIVA":
            raise ValueError("Solo se pueden cancelar reservas activas.")
        self.estado = "CANCELADA"

    def __str__(self):
        # Mostramos la información principal de la reserva
        estado_pago = "PAGADA" if self.pagada else "PENDIENTE"
        return (f"[Reserva#{self.id}] Cliente: {self.cliente.nombre} | Vehículo: {self.vehiculo.matricula} | "
                f"Desde: {self.fecha_inicio.date()} Hasta: {self.fecha_fin.date()} | "
                f"Recogida: {self.sucursal_recogida.nombre} | Devolución: {self.sucursal_devolucion.nombre} | "
                f"Estado: {self.estado} | Pago: {estado_pago} | Total estimado: {self.total_estimado:.2f}€")
