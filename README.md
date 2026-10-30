# Autos Colombia – Control del parqueadero (Iteración 2)

Programa de escritorio para un parqueadero de mensualidades. La iteración 1 cubrió **la entrada
y la salida de vehículos**. Esta segunda iteración agrega la **gestión de clientes** (registrar,
buscar, editar, desactivar y asociarles vehículos) y la **gestión de celdas** (crear celdas de
carro o moto y ponerlas en mantenimiento).

Trabajo de la asignatura Ingeniería de Software – Institución Universitaria Digital de Antioquia
(Evidencia de Aprendizaje 2). Autor: Didier Alejandro Correa Muñoz.

## Requisitos

- Python 3 (se descarga de https://www.python.org/downloads/; en Windows marcar **Add python.exe to PATH**).
- No se instala ninguna librería: usa `tkinter`, `sqlite3` y `datetime`, que vienen con Python.

## Cómo ejecutarlo

```
python main.py
```

Se abre la ventana y se crea el archivo `parqueadero.db` la primera vez. Si ya existía una base
de la iteración 1, se actualiza sola y conserva los vehículos y el historial.

## Cómo probarlo

Pruebas automáticas de las reglas del negocio (no abren ventana):

```
python -m unittest -v
```

Pruebas manuales por historia de usuario:

1. **Clientes:** registrar un cliente con documento de 8 a 10 números, intentar repetirlo
   (rechazado), buscarlo por nombre, editarlo y desactivarlo.
2. **Vehículos:** en Operación, guardar una placa con el documento del cliente y el tipo.
3. **Celdas:** crear una celda de moto, poner una celda libre en mantenimiento (se ve gris) e
   intentarlo con una ocupada (rechazado).
4. **Entrada:** una moto solo entra a una celda de moto; un carro nunca entra a una celda en
   mantenimiento.

## Estructura

| Archivo | Qué contiene |
|---|---|
| `main.py` | Ventana principal (tkinter) con las pestañas Operación, Clientes, Celdas e Historial |
| `logica.py` | Reglas del negocio y acceso a la base de datos SQLite |
| `test_logica.py` | 30 pruebas automáticas de `logica.py` |

## Reglas implementadas

Iteración 1:
- La placa se guarda en mayúsculas.
- Solo entra un vehículo registrado, con mensualidad vigente y que no esté ya adentro.
- Al salir se libera la celda, se calcula la permanencia y se avisa si la mensualidad venció.
- Cada entrada o salida se guarda completa o no se guarda (transacciones de SQLite).

Iteración 2:
- El documento del cliente solo tiene números, de 8 a 10 cifras, y no se repite.
- Un cliente no se borra: se desactiva, y no puede desactivarse con un vehículo adentro.
- Un vehículo se registra a nombre de un cliente activo, con tipo carro o moto.
- Una celda tiene tipo (carro o moto) y estado (activa o mantenimiento); no se puede poner en
  mantenimiento una celda ocupada.
- En la entrada solo se asigna una celda activa, libre y del mismo tipo del vehículo.
