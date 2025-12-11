from __future__ import annotations
from typing import Dict, Optional
from uuid import UUID

from models.Usuario import Usuario, Cliente, Administrador
from models.Vehiculo import Vehiculo, Coche, Moto, Furgoneta
from models.Reserva import Reserva
from models.Sucursal import Sucursal
from models.Tarifa import Tarifa
from models.Mantenimiento import Mantenimiento


class AlquilerServicio:
    # Clase principal del sistema. Desde aquí gestionamos usuarios, vehículos, tarifas, reservas, sucursales y mantenimientos.

    def __init__(self):
        # Creamos diccionarios para organizar los datos de forma sencilla
        self.usuarios: Dict[UUID, Usuario] = {}        # UUID -> Usuario
        self.vehiculos: Dict[UUID, Vehiculo] = {}      # UUID -> Vehículo
        self.reservas: Dict[UUID, Reserva] = {}        # UUID -> Reserva
        self.sucursales: Dict[UUID, Sucursal] = {}     # UUID -> Sucursal
        self.tarifas: Dict[UUID, Tarifa] = {}          # UUID -> Tarifa
        self.mantenimientos: Dict[UUID, Mantenimiento] = {}  # UUID -> Mantenimiento

    # ---------- USUARIOS ----------
    def registrar_usuario(self, tipo: str, nombre: str, email: str, password: str, licencia=None, direccion=None):
        # Registramos un nuevo cliente o administrador
        
        # Verificamos que no exista un usuario duplicado por email
        for usuario in self.usuarios.values():
            if usuario.email.lower() == email.lower():
                raise ValueError("Ya existe un usuario con ese email.")
        
        if tipo.lower() == "cliente":
            if not licencia or not direccion:
                raise ValueError("El cliente debe tener licencia y dirección.")
            usuario = Cliente(nombre, email, password, licencia, direccion)
        elif tipo.lower() in ("admin", "administrador"):
            usuario = Administrador(nombre, email, password)
        else:
            raise ValueError("Tipo de usuario no válido. Usa 'cliente' o 'admin'.")

        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: UUID):
        # Devolvemos un usuario por su ID
        usuario = self.usuarios.get(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado.")
        return usuario

    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        # Buscamos un usuario por email (necesario para autenticación)
        for usuario in self.usuarios.values():
            if usuario.email.lower() == email.lower():
                return usuario
        return None

    def listar_usuarios(self):
        # Devolvemos la lista de todos los usuarios registrados
        return list(self.usuarios.values())

    # ---------- SUCURSALES ----------
    def agregar_sucursal(self, nombre: str, direccion: str, telefono: str):
        # Creamos una nueva sucursal y la guardamos en el sistema
        sucursal = Sucursal(nombre, direccion, telefono)
        self.sucursales[sucursal.id] = sucursal
        return sucursal

    # ---------- VEHÍCULOS ----------
    def registrar_vehiculo(self, tipo: str, matricula: str, marca: str, modelo: str, año: int,
                           categoria: str, km: float, sucursal, **extras):
        # Registramos un vehículo en función de su tipo
        tipo = tipo.lower()
        if tipo == "coche":
            vehiculo = Coche(matricula, marca, modelo, año, categoria, km,
                             extras.get("puertas", 4), extras.get("motor", "Gasolina"), sucursal)
        elif tipo == "moto":
            vehiculo = Moto(matricula, marca, modelo, año, categoria, km,
                            extras.get("cilindrada", 125), sucursal)
        elif tipo == "furgoneta":
            vehiculo = Furgoneta(matricula, marca, modelo, año, categoria, km,
                                 extras.get("carga", 1000), sucursal)
        else:
            raise ValueError("Tipo de vehículo no válido.")

        self.vehiculos[vehiculo.id] = vehiculo
        sucursal.agregar_vehiculo(vehiculo)
        return vehiculo

    def obtener_vehiculo(self, vehiculo_id: UUID):
        # Devolvemos un vehículo por su ID
        vehiculo = self.vehiculos.get(vehiculo_id)
        if not vehiculo:
            raise ValueError("Vehículo no encontrado.")
        return vehiculo

    def listar_vehiculos_disponibles(self):
        # Mostramos los vehículos disponibles de todas las sucursales
        return [v for v in self.vehiculos.values() if v.estado == "DISPONIBLE"]

    # ---------- TARIFAS ----------
    def crear_tarifa(self, nombre: str, categoria: str, precio_diario: float,
                     km_incluidos: float = 300.0, coste_km_extra: float = 0.10,
                     recargo_retraso: float = 20.0, penalizacion_comb: float = 30.0):
        # Creamos una nueva tarifa y la añadimos al sistema
        tarifa = Tarifa(nombre, categoria, precio_diario, km_incluidos,
                        coste_km_extra, recargo_retraso, penalizacion_comb)
        self.tarifas[tarifa.id] = tarifa
        return tarifa

    def obtener_tarifa(self, categoria: str):
        # Buscamos la tarifa que corresponde a una categoría
        for tarifa in self.tarifas.values():
            if tarifa.categoria.lower() == categoria.lower():
                return tarifa
        raise ValueError("No existe una tarifa para esa categoría.")

    # ---------- RESERVAS ----------
    def realizar_reserva(self, cliente_id: UUID, vehiculo_id: UUID,
                         fecha_inicio: str, fecha_fin: str, id_sucursal_devolucion: UUID):
        # Creamos una nueva reserva si el vehículo está disponible
        cliente = self.usuarios.get(cliente_id)
        vehiculo = self.vehiculos.get(vehiculo_id)
        sucursal_recogida = vehiculo.sucursal if vehiculo else None
        sucursal_devolucion = self.sucursales.get(id_sucursal_devolucion)

        if not cliente or not isinstance(cliente, Cliente):
            raise ValueError("El usuario debe ser un cliente válido.")
        if not vehiculo or vehiculo.estado != "DISPONIBLE":
            raise ValueError("El vehículo no está disponible.")
        if not sucursal_devolucion:
            raise ValueError("Sucursal de devolución no válida.")

        # Obtenemos la tarifa correspondiente
        tarifa = self.obtener_tarifa(vehiculo.categoria)
        reserva = Reserva(cliente, vehiculo, fecha_inicio, fecha_fin, tarifa,
                          sucursal_recogida, sucursal_devolucion)

        # Asociamos la reserva con cliente, vehículo y sucursales
        self.reservas[reserva.id] = reserva
        cliente.agregar_reserva(reserva)
        vehiculo.cambiar_estado("RESERVADO")
        sucursal_recogida.registrar_reserva(reserva)
        sucursal_devolucion.registrar_reserva(reserva)

        return reserva

    def finalizar_reserva(self, reserva_id: UUID, km_recorridos=0, retraso_dias=0,
                          combustible_correcto=True, metodo_pago="Tarjeta"):
        # Finalizamos una reserva activa y registramos el pago
        reserva = self.reservas.get(reserva_id)
        if not reserva:
            raise ValueError("La reserva no existe.")

        # Calculamos el total final con la nueva versión de Tarifa
        total = reserva.finalizar_reserva(km_recorridos, retraso_dias, combustible_correcto)

        # Actualizamos el kilometraje y el estado del vehículo
        reserva.vehiculo.actualizar_kilometraje(km_recorridos)
        reserva.vehiculo.cambiar_estado("DISPONIBLE")

        # Registramos el pago
        reserva.registrar_pago(metodo_pago)

        # Devolvemos un pequeño resumen del pago realizado
        return {
            "reserva_id": reserva.id,
            "cliente": reserva.cliente.nombre,
            "vehiculo": reserva.vehiculo.matricula,
            "importe_total": reserva.total_final,
            "metodo_pago": metodo_pago,
            "pagada": reserva.pagada
        }

    # ---------- MANTENIMIENTOS ----------
    def registrar_mantenimiento(self, vehiculo_id: UUID, motivo: str,
                                fecha_inicio: str, fecha_fin: str,
                                coste: float, tipo: str = "REVISIÓN"):
        # Registramos un nuevo mantenimiento y cambiamos el estado del vehículo
        vehiculo = self.vehiculos.get(vehiculo_id)
        if not vehiculo:
            raise ValueError("Vehículo no encontrado.")

        mantenimiento = Mantenimiento(vehiculo, motivo, fecha_inicio, fecha_fin, coste, tipo)
        self.mantenimientos[mantenimiento.id] = mantenimiento
        return mantenimiento

    def finalizar_mantenimiento(self, mantenimiento_id: UUID):
        # Marcamos un mantenimiento como completado
        mantenimiento = self.mantenimientos.get(mantenimiento_id)
        if not mantenimiento:
            raise ValueError("Mantenimiento no encontrado.")
        mantenimiento.finalizar_mantenimiento()
        return mantenimiento
