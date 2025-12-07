from __future__ import annotations
from uuid import uuid4, UUID


class Vehiculo:
    # Clase base que representa un vehículo dentro de nuestro sistema de alquiler.
    # Aquí reunimos la información general de cualquier vehículo y las funciones que nos permiten controlar su estado y kilometraje.

    def __init__(self, matricula: str, marca: str, modelo: str, año: int,
                 categoria: str, km: float, sucursal=None, estado: str = "DISPONIBLE"):
        # Asignamos un ID único a cada vehículo que creemos
        self.id: UUID = uuid4()

        # Guardamos los datos principales del vehículo
        self.matricula = matricula.strip()
        self.marca = marca.strip()
        self.modelo = modelo.strip()
        self.año = año
        self.categoria = categoria.strip()
        self.km = km
        self.estado = estado.upper()
        self.sucursal = sucursal  # Aquí podremos guardar el objeto Sucursal asociado

        # Realizamos validaciones básicas para evitar datos erróneos
        if not self.matricula:
            raise ValueError("La matrícula no puede estar vacía.")
        if self.km < 0:
            raise ValueError("El kilometraje no puede ser negativo.")
        if self.año < 1990 or self.año > 2035:
            raise ValueError("El año del vehículo no es válido.")

    def cambiar_estado(self, nuevo_estado: str):
        # Cambiamos el estado del vehículo (por ejemplo: disponible, alquilado, en mantenimiento...)
        estados_validos = ["DISPONIBLE", "RESERVADO", "ALQUILADO", "MANTENIMIENTO"]
        if nuevo_estado.upper() not in estados_validos:
            raise ValueError(f"Estado '{nuevo_estado}' no válido.")
        self.estado = nuevo_estado.upper()

    def actualizar_kilometraje(self, km_extra: float):
        # Sumamos los kilómetros recorridos al total del vehículo
        if km_extra < 0:
            raise ValueError("El kilometraje adicional no puede ser negativo.")
        self.km += km_extra

    def __str__(self):
        # Mostramos toda la información del vehículo de forma legible
        sucursal_nombre = self.sucursal.nombre if self.sucursal else "Sin asignar"
        return (f"[Vehículo #{self.id}] {self.marca} {self.modelo} ({self.año}) - "
                f"Matrícula: {self.matricula} | Categoría: {self.categoria} | "
                f"Km: {self.km} | Estado: {self.estado} | Sucursal: {sucursal_nombre}")


# ------- Subclases de Vehículo -------


class Coche(Vehiculo):
    # Creamos una subclase para coches, que hereda de Vehículo
    def __init__(self, matricula, marca, modelo, año, categoria, km, puertas: int, tipo_motor: str, sucursal=None):
        # Llamamos al constructor de la clase base para reutilizar su lógica
        super().__init__(matricula, marca, modelo, año, categoria, km, sucursal)
        # Añadimos los atributos específicos de un coche
        self.puertas = puertas
        self.tipo_motor = tipo_motor.strip()

    def __str__(self):
        # Añadimos la información extra al texto del vehículo
        return super().__str__() + f" | Puertas: {self.puertas} | Motor: {self.tipo_motor}"


class Moto(Vehiculo):
    # Subclase para motos, con un atributo de cilindrada
    def __init__(self, matricula, marca, modelo, año, categoria, km, cilindrada: int, sucursal=None):
        super().__init__(matricula, marca, modelo, año, categoria, km, sucursal)
        self.cilindrada = cilindrada

    def __str__(self):
        # Mostramos también la cilindrada
        return super().__str__() + f" | Cilindrada: {self.cilindrada}cc"


class Furgoneta(Vehiculo):
    # Subclase para furgonetas, con su capacidad de carga
    def __init__(self, matricula, marca, modelo, año, categoria, km, capacidad_carga: float, sucursal=None):
        super().__init__(matricula, marca, modelo, año, categoria, km, sucursal)
        self.capacidad_carga = capacidad_carga

    def __str__(self):
        # Incluimos el peso máximo que puede transportar
        return super().__str__() + f" | Carga: {self.capacidad_carga} kg"
