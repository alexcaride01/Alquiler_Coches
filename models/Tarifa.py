from __future__ import annotations
from uuid import uuid4, UUID


class Tarifa:

    # Clase que representa una tarifa dentro del sistema de alquiler. Con ella gestionamos los precios diarios según el tipo de vehículo y las condiciones del alquiler.

    def __init__(self, nombre: str, categoria: str, precio_diario: float,
                 km_incluidos: float = 300.0, coste_km_extra: float = 0.10,
                 recargo_retraso: float = 20.0, penalizacion_comb: float = 30.0):
        # Asignamos un identificador a la tarifa
        self.id: UUID = uuid4()

        # Guardamos los datos principales
        self.nombre = nombre.strip()
        self.categoria = categoria.strip()  # Ejemplo: "Económico", "SUV", "Premium"
        self.precio_diario = precio_diario
        self.km_incluidos = km_incluidos
        self.coste_km_extra = coste_km_extra
        self.recargo_retraso = recargo_retraso
        self.penalizacion_comb = penalizacion_comb

        # Validamos los datos
        if not self.nombre:
            raise ValueError("El nombre de la tarifa no puede estar vacío.")
        if self.precio_diario <= 0:
            raise ValueError("El precio diario debe ser positivo.")
        if self.km_incluidos < 0:
            raise ValueError("Los km incluidos no pueden ser negativos.")
        if self.coste_km_extra < 0 or self.recargo_retraso < 0 or self.penalizacion_comb < 0:
            raise ValueError("Los valores de recargos y penalizaciones deben ser no negativos.")

    def calcular_precio(self, dias: int, km_recorridos: float = 0,
                        retraso_dias: int = 0, combustible_correcto: bool = True) -> float:
        # Calculamos el precio total del alquiler según los días, kilómetros y penalizaciones
        if dias <= 0:
            raise ValueError("El número de días debe ser mayor que cero.")
        if km_recorridos < 0 or retraso_dias < 0:
            raise ValueError("Los valores de km o retraso no pueden ser negativos.")

        # Calculamos el precio base multiplicando los días por el precio diario
        total = dias * self.precio_diario

        # Si el cliente supera los kilómetros incluidos, aplicamos un coste adicional por cada km extra
        if km_recorridos > self.km_incluidos * dias:
            km_extra = km_recorridos - (self.km_incluidos * dias)
            total += km_extra * self.coste_km_extra

        # Si el cliente devuelve el coche con retraso, aplicamos un recargo por día
        if retraso_dias > 0:
            total += retraso_dias * self.recargo_retraso

        # Si el vehículo se devuelve con el depósito sin llenar, aplicamos una penalización fija
        if not combustible_correcto:
            total += self.penalizacion_comb

        # Devolvemos el total redondeado a dos decimales
        return round(total, 2)

    def __str__(self):
        # Mostramos la información de la tarifa de forma legible
        return (f"[Tarifa#{self.id}] {self.nombre} | Categoría: {self.categoria} | "
                f"Precio diario: {self.precio_diario:.2f}€ | Km incluidos/día: {self.km_incluidos:.0f} | "
                f"Coste km extra: {self.coste_km_extra:.2f}€ | Recargo retraso: {self.recargo_retraso:.2f}€ | "
                f"Penalización combustible: {self.penalizacion_comb:.2f}€")
