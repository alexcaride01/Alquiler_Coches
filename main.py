from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from services.AlquilerServicio import AlquilerServicio
from models.Usuario import Usuario, Cliente, Administrador
from models.Vehiculo import Vehiculo, Coche, Moto, Furgoneta
from models.Reserva import Reserva
from models.Sucursal import Sucursal
from models.Tarifa import Tarifa
from models.Mantenimiento import Mantenimiento

app = FastAPI(title="Sistema de Alquiler de Coches API")
alquiler_service = AlquilerServicio()

# ---------------------- SCHEMAS ---------------------- #

# ------ USUARIOS ------ #
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    tipo: str
    licencia: Optional[str] = None
    direccion: Optional[str] = None

class UsuarioRead(BaseModel):
    id: UUID
    nombre: str
    email: EmailStr
    es_admin: bool

# ------ VEHÍCULOS ------ #
class VehiculoCreate(BaseModel):
    tipo: str
    matricula: str
    marca: str
    modelo: str
    año: int
    categoria: str
    km: float
    sucursal_id: UUID
    puertas: Optional[int] = None
    tipo_motor: Optional[str] = None
    cilindrada: Optional[int] = None
    capacidad_carga: Optional[float] = None

class VehiculoRead(BaseModel):
    id: UUID
    tipo: str
    matricula: str
    marca: str
    modelo: str
    año: int
    categoria: str
    km: float
    estado: str
    sucursal_nombre: str
    puertas: Optional[int] = None
    tipo_motor: Optional[str] = None
    cilindrada: Optional[int] = None
    capacidad_carga: Optional[float] = None

# ------ SUCURSALES ------ #
class SucursalCreate(BaseModel):
    nombre: str
    direccion: str
    telefono: str

class SucursalRead(BaseModel):
    id: UUID
    nombre: str
    direccion: str
    telefono: str
    num_vehiculos: int
    num_reservas: int

# ------ TARIFAS ------ #
class TarifaCreate(BaseModel):
    nombre: str
    categoria: str
    precio_diario: float
    km_incluidos: float = 300.0
    coste_km_extra: float = 0.10
    recargo_retraso: float = 20.0
    penalizacion_comb: float = 30.0

class TarifaRead(BaseModel):
    id: UUID
    nombre: str
    categoria: str
    precio_diario: float
    km_incluidos: float
    coste_km_extra: float
    recargo_retraso: float
    penalizacion_comb: float

# ------ RESERVAS ------ #
class ReservaCreate(BaseModel):
    cliente_id: UUID
    vehiculo_id: UUID
    fecha_inicio: str
    fecha_fin: str
    sucursal_devolucion_id: UUID

class ReservaRead(BaseModel):
    id: UUID
    cliente_nombre: str
    vehiculo_matricula: str
    fecha_inicio: str
    fecha_fin: str
    sucursal_recogida: str
    sucursal_devolucion: str
    dias: int
    total_estimado: float
    estado: str
    pagada: bool

class ReservaFinalizarRequest(BaseModel):
    km_recorridos: float = 0
    retraso_dias: int = 0
    combustible_correcto: bool = True
    metodo_pago: str = "Tarjeta"

# ------ MANTENIMIENTOS ------ #
class MantenimientoCreate(BaseModel):
    vehiculo_id: UUID
    motivo: str
    fecha_inicio: str
    fecha_fin: str
    coste: float
    tipo: str = "REVISIÓN"

class MantenimientoRead(BaseModel):
    id: UUID
    vehiculo_matricula: str
    motivo: str
    fecha_inicio: str
    fecha_fin: str
    coste: float
    tipo: str

# ---------------------- ENDPOINTS ---------------------- #

# ------ USUARIOS ------ #
@app.post("/usuarios", response_model=UsuarioRead)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    try:
        usuario = alquiler_service.registrar_usuario(
            tipo=datos.tipo,
            nombre=datos.nombre,
            email=str(datos.email),
            licencia=datos.licencia,
            direccion=datos.direccion,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )

@app.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios() -> list[UsuarioRead]:
    usuarios = alquiler_service.usuarios.values()
    return [
        UsuarioRead(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            es_admin=u.is_admin(),
        )
        for u in usuarios
    ]

@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: UUID) -> UsuarioRead:
    try:
        usuario = alquiler_service.obtener_usuario(usuario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )

# ------ SUCURSALES ------ #
@app.post("/sucursales", response_model=SucursalRead)
def crear_sucursal(datos: SucursalCreate) -> SucursalRead:
    try:
        sucursal = alquiler_service.agregar_sucursal(
            nombre=datos.nombre,
            direccion=datos.direccion,
            telefono=datos.telefono,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return SucursalRead(
        id=sucursal.id,
        nombre=sucursal.nombre,
        direccion=sucursal.direccion,
        telefono=sucursal.telefono,
        num_vehiculos=len(sucursal.vehiculos),
        num_reservas=len(sucursal.reservas),
    )

@app.get("/sucursales", response_model=list[SucursalRead])
def listar_sucursales() -> list[SucursalRead]:
    sucursales = alquiler_service.sucursales.values()
    return [
        SucursalRead(
            id=s.id,
            nombre=s.nombre,
            direccion=s.direccion,
            telefono=s.telefono,
            num_vehiculos=len(s.vehiculos),
            num_reservas=len(s.reservas),
        )
        for s in sucursales
    ]

@app.get("/sucursales/{sucursal_id}", response_model=SucursalRead)
def obtener_sucursal(sucursal_id: UUID) -> SucursalRead:
    sucursal = alquiler_service.sucursales.get(sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")

    return SucursalRead(
        id=sucursal.id,
        nombre=sucursal.nombre,
        direccion=sucursal.direccion,
        telefono=sucursal.telefono,
        num_vehiculos=len(sucursal.vehiculos),
        num_reservas=len(sucursal.reservas),
    )

# ------ VEHÍCULOS ------ #
@app.post("/vehiculos", response_model=VehiculoRead)
def crear_vehiculo(datos: VehiculoCreate) -> VehiculoRead:
    try:
        sucursal = alquiler_service.sucursales.get(datos.sucursal_id)
        if not sucursal:
            raise ValueError("Sucursal no encontrada.")

        extras = {}
        if datos.puertas is not None:
            extras["puertas"] = datos.puertas
        if datos.tipo_motor is not None:
            extras["motor"] = datos.tipo_motor
        if datos.cilindrada is not None:
            extras["cilindrada"] = datos.cilindrada
        if datos.capacidad_carga is not None:
            extras["carga"] = datos.capacidad_carga

        vehiculo = alquiler_service.registrar_vehiculo(
            tipo=datos.tipo,
            matricula=datos.matricula,
            marca=datos.marca,
            modelo=datos.modelo,
            año=datos.año,
            categoria=datos.categoria,
            km=datos.km,
            sucursal=sucursal,
            **extras
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _vehiculo_to_read(vehiculo)

@app.get("/vehiculos", response_model=list[VehiculoRead])
def listar_vehiculos() -> list[VehiculoRead]:
    vehiculos = alquiler_service.vehiculos.values()
    return [_vehiculo_to_read(v) for v in vehiculos]

@app.get("/vehiculos/disponibles", response_model=list[VehiculoRead])
def listar_vehiculos_disponibles() -> list[VehiculoRead]:
    vehiculos = alquiler_service.listar_vehiculos_disponibles()
    return [_vehiculo_to_read(v) for v in vehiculos]

@app.get("/vehiculos/{vehiculo_id}", response_model=VehiculoRead)
def obtener_vehiculo(vehiculo_id: UUID) -> VehiculoRead:
    try:
        vehiculo = alquiler_service.obtener_vehiculo(vehiculo_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return _vehiculo_to_read(vehiculo)

@app.delete("/vehiculos/{vehiculo_id}")
def eliminar_vehiculo(vehiculo_id: UUID):
    vehiculo = alquiler_service.vehiculos.get(vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    
    del alquiler_service.vehiculos[vehiculo_id]
    return {"mensaje": "Vehículo eliminado correctamente."}

# ------ TARIFAS ------ #
@app.post("/tarifas", response_model=TarifaRead)
def crear_tarifa(datos: TarifaCreate) -> TarifaRead:
    try:
        tarifa = alquiler_service.crear_tarifa(
            nombre=datos.nombre,
            categoria=datos.categoria,
            precio_diario=datos.precio_diario,
            km_incluidos=datos.km_incluidos,
            coste_km_extra=datos.coste_km_extra,
            recargo_retraso=datos.recargo_retraso,
            penalizacion_comb=datos.penalizacion_comb,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return TarifaRead(
        id=tarifa.id,
        nombre=tarifa.nombre,
        categoria=tarifa.categoria,
        precio_diario=tarifa.precio_diario,
        km_incluidos=tarifa.km_incluidos,
        coste_km_extra=tarifa.coste_km_extra,
        recargo_retraso=tarifa.recargo_retraso,
        penalizacion_comb=tarifa.penalizacion_comb,
    )

@app.get("/tarifas", response_model=list[TarifaRead])
def listar_tarifas() -> list[TarifaRead]:
    tarifas = alquiler_service.tarifas.values()
    return [
        TarifaRead(
            id=t.id,
            nombre=t.nombre,
            categoria=t.categoria,
            precio_diario=t.precio_diario,
            km_incluidos=t.km_incluidos,
            coste_km_extra=t.coste_km_extra,
            recargo_retraso=t.recargo_retraso,
            penalizacion_comb=t.penalizacion_comb,
        )
        for t in tarifas
    ]

# ------ RESERVAS ------ #
@app.post("/reservas", response_model=ReservaRead)
def crear_reserva(datos: ReservaCreate) -> ReservaRead:
    try:
        reserva = alquiler_service.realizar_reserva(
            cliente_id=datos.cliente_id,
            vehiculo_id=datos.vehiculo_id,
            fecha_inicio=datos.fecha_inicio,
            fecha_fin=datos.fecha_fin,
            id_sucursal_devolucion=datos.sucursal_devolucion_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _reserva_to_read(reserva)

@app.get("/reservas", response_model=list[ReservaRead])
def listar_reservas() -> list[ReservaRead]:
    reservas = alquiler_service.reservas.values()
    return [_reserva_to_read(r) for r in reservas]

@app.get("/usuarios/{cliente_id}/reservas", response_model=list[ReservaRead])
def listar_reservas_cliente(cliente_id: UUID) -> list[ReservaRead]:
    try:
        cliente = alquiler_service.obtener_usuario(cliente_id)
        if not isinstance(cliente, Cliente):
            raise ValueError("El usuario no es un cliente.")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return [_reserva_to_read(r) for r in cliente.reservas]

@app.post("/reservas/{reserva_id}/finalizar")
def finalizar_reserva(reserva_id: UUID, datos: ReservaFinalizarRequest):
    try:
        pago_info = alquiler_service.finalizar_reserva(
            reserva_id=reserva_id,
            km_recorridos=datos.km_recorridos,
            retraso_dias=datos.retraso_dias,
            combustible_correcto=datos.combustible_correcto,
            metodo_pago=datos.metodo_pago,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return pago_info

# ------ MANTENIMIENTOS ------ #
@app.post("/mantenimientos", response_model=MantenimientoRead)
def crear_mantenimiento(datos: MantenimientoCreate) -> MantenimientoRead:
    try:
        mantenimiento = alquiler_service.registrar_mantenimiento(
            vehiculo_id=datos.vehiculo_id,
            motivo=datos.motivo,
            fecha_inicio=datos.fecha_inicio,
            fecha_fin=datos.fecha_fin,
            coste=datos.coste,
            tipo=datos.tipo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return MantenimientoRead(
        id=mantenimiento.id,
        vehiculo_matricula=mantenimiento.vehiculo.matricula,
        motivo=mantenimiento.motivo,
        fecha_inicio=mantenimiento.fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=mantenimiento.fecha_fin.strftime("%Y-%m-%d"),
        coste=mantenimiento.coste,
        tipo=mantenimiento.tipo,
    )

@app.get("/mantenimientos", response_model=list[MantenimientoRead])
def listar_mantenimientos() -> list[MantenimientoRead]:
    mantenimientos = alquiler_service.mantenimientos.values()
    return [
        MantenimientoRead(
            id=m.id,
            vehiculo_matricula=m.vehiculo.matricula,
            motivo=m.motivo,
            fecha_inicio=m.fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=m.fecha_fin.strftime("%Y-%m-%d"),
            coste=m.coste,
            tipo=m.tipo,
        )
        for m in mantenimientos
    ]

@app.post("/mantenimientos/{mantenimiento_id}/finalizar")
def finalizar_mantenimiento(mantenimiento_id: UUID):
    try:
        mantenimiento = alquiler_service.finalizar_mantenimiento(mantenimiento_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"mensaje": "Mantenimiento finalizado correctamente.", "vehiculo": mantenimiento.vehiculo.matricula}

# ---------------------- FUNCIONES AUXILIARES ---------------------- #

def _vehiculo_to_read(vehiculo: Vehiculo) -> VehiculoRead:
    # Función auxiliar para convertir un vehículo a VehiculoRead
    tipo_vehiculo = "generico"
    puertas = None
    tipo_motor = None
    cilindrada = None
    capacidad_carga = None

    if isinstance(vehiculo, Coche):
        tipo_vehiculo = "coche"
        puertas = vehiculo.puertas
        tipo_motor = vehiculo.tipo_motor
    elif isinstance(vehiculo, Moto):
        tipo_vehiculo = "moto"
        cilindrada = vehiculo.cilindrada
    elif isinstance(vehiculo, Furgoneta):
        tipo_vehiculo = "furgoneta"
        capacidad_carga = vehiculo.capacidad_carga

    return VehiculoRead(
        id=vehiculo.id,
        tipo=tipo_vehiculo,
        matricula=vehiculo.matricula,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        año=vehiculo.año,
        categoria=vehiculo.categoria,
        km=vehiculo.km,
        estado=vehiculo.estado,
        sucursal_nombre=vehiculo.sucursal.nombre if vehiculo.sucursal else "Sin asignar",
        puertas=puertas,
        tipo_motor=tipo_motor,
        cilindrada=cilindrada,
        capacidad_carga=capacidad_carga,
    )

def _reserva_to_read(reserva: Reserva) -> ReservaRead:
    # Función auxiliar para convertir una reserva a ReservaRead
    return ReservaRead(
        id=reserva.id,
        cliente_nombre=reserva.cliente.nombre,
        vehiculo_matricula=reserva.vehiculo.matricula,
        fecha_inicio=reserva.fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=reserva.fecha_fin.strftime("%Y-%m-%d"),
        sucursal_recogida=reserva.sucursal_recogida.nombre,
        sucursal_devolucion=reserva.sucursal_devolucion.nombre,
        dias=reserva.dias,
        total_estimado=reserva.total_estimado,
        estado=reserva.estado,
        pagada=reserva.pagada,
    )
