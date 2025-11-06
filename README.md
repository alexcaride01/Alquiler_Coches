# Sistema de Gestión de Alquiler de Vehículos

Proyecto Final de la asignatura **Arquitectura de Software**, realizado por **Alex Caride**, **Pablo Barrán** y **Daniel López**.  
El trabajo tiene como objetivo simular el funcionamiento de una empresa de alquiler de vehículos de forma digital y automatizada.  
El sistema permite gestionar vehículos, clientes, reservas, tarifas, mantenimientos y sucursales desde una interfaz de línea de comandos.


## Descripción general

El proyecto busca digitalizar las operaciones típicas de una empresa de alquiler de coches, permitiendo registrar vehículos, realizar reservas, calcular precios, controlar mantenimientos y gestionar usuarios (clientes y administradores).  
Está diseñado siguiendo un enfoque orientado a objetos y con una estructura modular para facilitar su mantenimiento y escalabilidad.


## Estructura del proyecto

**models/**: Contiene las clases principales del dominio.
**services/**: Contiene la clase central "AlquilerServicio", que coordina la interacción entre los modelos.
**main.py**: Punto de entrada del programa, donde se simula el flujo completo de uso del sistema.

## Clases principales

### Vehiculo (y subclases que heredan Coche, Moto, Furgoneta)
Representan los distintos tipos de vehículos disponibles.  
Cada vehículo incluye su matrícula, marca, modelo, año, categoría, kilometraje, estado y sucursal asignada.  
Las subclases añaden atributos específicos:
- Coche: número de puertas y tipo de motor.  
- Moto: cilindrada.  
- Furgoneta: capacidad de carga.  

### Usuario (y subclases que heredan Cliente, Administrador)
Define a los usuarios del sistema.  
- Cliente: puede realizar reservas y dispone de licencia y dirección postal.  
- Administrador: gestiona vehículos, tarifas y mantenimientos.  

### Tarifa
Contiene la información de precios por categoría y duración del alquiler.  
Permite calcular el coste total aplicando descuentos por alquileres de larga duración.

### Sucursal
Representa las distintas oficinas de alquiler y devolución.  
Cada sucursal gestiona su lista de vehículos y reservas.

### Reserva
Asocia un cliente con un vehículo y un periodo de tiempo.  
Gestiona la recogida y devolución en distintas sucursales, calcula el coste final del alquiler y permite registrar el pago del mismo.

### Mantenimiento
Registra las operaciones de revisión o reparación realizadas sobre un vehículo, bloqueándolo temporalmente para evitar que sea alquilado durante el proceso.

### AlquilerServicio
Es la clase central del sistema.  
Permite:
- Registrar usuarios, sucursales, vehículos y tarifas.  
- Realizar y finalizar reservas.  
- Calcular costes y registrar pagos.  
- Gestionar mantenimientos y disponibilidad de vehículos.


