from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from jose import JWTError, jwt
from passlib.context import CryptContext

from services.AlquilerServicio import AlquilerServicio
from models.Usuario import Usuario, Cliente, Administrador
from models.Vehiculo import Vehiculo, Coche, Moto, Furgoneta
from models.Reserva import Reserva
from models.Sucursal import Sucursal
from models.Tarifa import Tarifa
from models.Mantenimiento import Mantenimiento

# ---------------------- CONFIGURACIÓN JWT Y SEGURIDAD ---------------------- #

# Clave secreta para firmar los tokens JWT (cambiar en producción)
SECRET_KEY = "clave_secreta_alquiler_coches_2025"
# Algoritmo de encriptación para JWT
ALGORITHM = "HS256"
# Tiempo de expiración del token de acceso en minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de hashing con bcrypt para las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para autenticación basada en tokens
# tokenUrl indica el endpoint donde el cliente obtiene el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Creamos la instancia de FastAPI
app = FastAPI(title="Sistema de Alquiler de Coches API")

# Creamos la instancia del servicio de alquiler
alquiler_service = AlquilerServicio()

# ---------------------- FUNCIONES AUXILIARES DE SEGURIDAD ---------------------- #

def hash_password(password: str) -> str:
    password_cortada = password[:72]
    print("DEBUG password:", password, "len:", len(password))
    print("DEBUG cortada:", password_cortada, "len:", len(password_cortada))
    return pwd_context.hash(password_cortada)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Aplicamos el mismo corte antes de verificar
    plain_cortada = plain_password[:72]
    return pwd_context.verify(plain_cortada, hashed_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verifica que una contraseña en texto plano coincida con su hash
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Crea un token JWT con los datos del usuario y tiempo de expiración
    to_encode = data.copy()
    # Calculamos la fecha de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # Añadimos la fecha de expiración al payload
    to_encode.update({"exp": expire})
    # Codificamos y firmamos el token JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario:
    # Obtiene el usuario actual decodificando y validando el token JWT
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificamos el token JWT usando la clave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extraemos el email del payload (almacenado en el campo "sub")
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        # Si hay error al decodificar, lanzamos excepción
        raise credentials_exception
    
    # Buscamos el usuario por email en la base de datos
    usuario = alquiler_service.obtener_usuario_por_email(email)
    if usuario is None:
        raise credentials_exception
    return usuario

# ---------------------- SCHEMAS ---------------------- #

# ------ AUTENTICACIÓN ------ #
class Token(BaseModel):
    # Esquema para la respuesta del token de autenticación
    access_token: str
    token_type: str

class UsuarioRegister(BaseModel):
    # Esquema para registrar un nuevo usuario con contraseña
    nombre: str
    email: EmailStr
    password: str = Field(min_length=4)
    tipo: str
    licencia: Optional[str] = None
    direccion: Optional[str] = None

# ------ USUARIOS ------ #
class UsuarioCreate(BaseModel):
    # Esquema para crear un nuevo usuario (legacy, sin contraseña)
    nombre: str
    email: EmailStr
    tipo: str
    licencia: Optional[str] = None
    direccion: Optional[str] = None

class UsuarioRead(BaseModel):
    # Esquema para leer/devolver información de un usuario
    id: UUID
    nombre: str
    email: str
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

# ---------------------- ENDPOINTS DE AUTENTICACIÓN ---------------------- #

@app.post("/register", response_model=UsuarioRead, status_code=201)
def registrar_usuario(datos: UsuarioRegister) -> UsuarioRead:
    # Endpoint para registrar un nuevo usuario con contraseña hasheada
    try:
        # Hasheamos la contraseña antes de guardarla
        password_hash = hash_password(datos.password)
        
        # Registramos el usuario usando el servicio
        usuario = alquiler_service.registrar_usuario(
            tipo=datos.tipo,
            nombre=datos.nombre,
            email=datos.email,
            password=password_hash,
            licencia=datos.licencia,
            direccion=datos.direccion
        )
        
        # Devolvemos el usuario creado en formato UsuarioRead
        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin()
        )
    except ValueError as e:
        # Si hay un error de validación, devolvemos un error 400
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Endpoint de autenticación que devuelve un token JWT
    # El cliente envía username (email) y password para obtener el token
    
    # Buscamos el usuario por email (el campo username del form contiene el email)
    usuario = alquiler_service.obtener_usuario_por_email(form_data.username)
    
    # Verificamos que el usuario existe y la contraseña es correcta
    if not usuario or not verify_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token JWT con el email del usuario
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    
    # Devolvemos el token de acceso
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------- ENDPOINTS DE USUARIOS ---------------------- #

@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    # Endpoint legacy para crear usuario sin contraseña (deprecado)
    try:
        # Usamos una contraseña por defecto para mantener compatibilidad
        password_hash = hash_password("default123")
        
        # Registramos el usuario usando el servicio
        usuario = alquiler_service.registrar_usuario(
            tipo=datos.tipo,
            nombre=datos.nombre,
            email=datos.email,
            password=password_hash,
            licencia=datos.licencia,
            direccion=datos.direccion
        )
        
        # Devolvemos el usuario creado en formato UsuarioRead
        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin()
        )
    except ValueError as e:
        # Si hay un error de validación, devolvemos un error 400
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
async def obtener_usuario(
    usuario_id: UUID,
    current_user: Usuario = Depends(get_current_user)
) -> UsuarioRead:
    # Endpoint PROTEGIDO para obtener un usuario específico por ID
    # Requiere autenticación: el usuario debe enviar un token válido
    try:
        # Obtenemos el usuario del servicio
        usuario = alquiler_service.obtener_usuario(usuario_id)
        
        # Devolvemos el usuario en formato UsuarioRead
        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin()
        )
    except ValueError as e:
        # Si no existe, devolvemos un error 404
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/usuarios", response_model=List[UsuarioRead])
def listar_usuarios() -> List[UsuarioRead]:
    # Endpoint para listar todos los usuarios
    # Obtenemos todos los usuarios del servicio
    usuarios = alquiler_service.listar_usuarios()
    
    # Convertimos cada usuario al formato UsuarioRead
    return [
        UsuarioRead(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            es_admin=u.is_admin()
        )
        for u in usuarios
    ]

@app.get("/me", response_model=UsuarioRead)
async def obtener_usuario_actual(current_user: Usuario = Depends(get_current_user)):
    # Endpoint PROTEGIDO para obtener información del usuario autenticado
    # Devuelve los datos del usuario que hizo la petición
    return UsuarioRead(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        es_admin=current_user.is_admin()
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
async def crear_vehiculo(
    datos: VehiculoCreate,
    current_user: Usuario = Depends(get_current_user)
) -> VehiculoRead:
    # Endpoint PROTEGIDO para crear un nuevo vehículo
    # Requiere autenticación: solo usuarios autenticados pueden crear vehículos
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

@app.delete("/vehiculos/{vehiculo_id}", status_code=204)
async def eliminar_vehiculo(
    vehiculo_id: UUID,
    current_user: Usuario = Depends(get_current_user)
) -> None:
    # Endpoint PROTEGIDO para eliminar un vehículo del inventario
    # Requiere autenticación: solo usuarios autenticados pueden eliminar vehículos
    try:
        vehiculo = alquiler_service.vehiculos.get(vehiculo_id)
        if not vehiculo:
            raise ValueError("Vehículo no encontrado.")
        del alquiler_service.vehiculos[vehiculo_id]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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
