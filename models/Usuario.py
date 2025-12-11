from __future__ import annotations
from uuid import uuid4, UUID


class Usuario:
    # Clase base que representa a cualquier usuario del sistema de alquiler. Aquí guardamos la información general y el comportamiento común a clientes y administradores.

    def __init__(self, nombre: str, email: str, password: str):
        # Asignamos un identificador único automáticamente
        self.id: UUID = uuid4()

        # Guardamos los datos básicos del usuario
        self.nombre = nombre.strip()
        self.email = email.strip()
        # Guardamos la contraseña (ya viene hasheada desde el servicio)
        self.password = password

        # Validamos que los datos sean correctos
        if not self.nombre:
            raise ValueError("El nombre no puede estar vacío.")
        if "@" not in self.email:
            raise ValueError("El email debe ser válido.")
        # Validamos que la contraseña no esté vacía
        if not password:
            raise ValueError("La contraseña no puede estar vacía.")

    def is_admin(self) -> bool:
        # Indicamos si este usuario es un administrador (por defecto, no lo es)
        return False

    def __str__(self):
        # Mostramos una representación legible del usuario
        return f"[Usuario#{self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    """
    Representa a un cliente del sistema.
    Hereda de Usuario e incorpora datos adicionales como la licencia y dirección.
    """

    def __init__(self, nombre: str, email: str, password: str, licencia: str, direccion: str):
        # Llamamos al constructor de Usuario para reutilizar su lógica (ahora incluye password)
        super().__init__(nombre, email, password)

        # Guardamos los datos específicos del cliente
        self.licencia = licencia.strip()
        self.direccion = direccion.strip()
        self.reservas = []  # Aquí iremos guardando las reservas que haga el cliente

        # Validamos los nuevos campos
        if not self.licencia:
            raise ValueError("La licencia no puede estar vacía.")
        if not self.direccion:
            raise ValueError("La dirección no puede estar vacía.")

    def agregar_reserva(self, reserva):
        # Asociamos una reserva al cliente
        self.reservas.append(reserva)

    def __str__(self):
        # Mostramos los datos principales del cliente
        return (f"[Cliente#{self.id}] {self.nombre} ({self.email}) | "
                f"Licencia: {self.licencia} | Dirección: {self.direccion}")


class Administrador(Usuario):
    """
    Representa a un administrador del sistema.
    Este tipo de usuario puede gestionar vehículos, tarifas o mantenimientos.
    """

    def __init__(self, nombre: str, email: str, password: str):
        # Reutilizamos el constructor de Usuario (ahora incluye password)
        super().__init__(nombre, email, password)

    def is_admin(self) -> bool:
        # En este caso, siempre devolvemos True
        return True

    def __str__(self):
        # Mostramos los datos principales del administrador
        return f"[Admin#{self.id}] {self.nombre} ({self.email})"
