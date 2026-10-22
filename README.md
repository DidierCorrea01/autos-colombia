# Autos Colombia – Control de entrada y salida (Iteración 1)

Programa de escritorio para un parqueadero de mensualidades. Esta primera iteración cubre
**la entrada y la salida de vehículos**: registro de vehículos con su mensualidad, asignación
automática de celda, salida con liberación de la celda y consulta de vehículos, celdas e historial.

Trabajo de la asignatura Ingeniería de Software – Institución Universitaria Digital de Antioquia
(Evidencia de Aprendizaje 1). Autor: Didier Alejandro Correa Muñoz.

## Requisitos

- Python 3 (se descarga de https://www.python.org/downloads/; en Windows marcar **Add python.exe to PATH**).
- No se instala ninguna librería: usa `tkinter`, `sqlite3` y `datetime`, que vienen con Python.

## Cómo ejecutarlo

```
python main.py
```

Se abre la ventana y se crea el archivo `parqueadero.db` con las 10 celdas la primera vez.

## Cómo probarlo

Pruebas automáticas de las reglas del negocio (no abren ventana):

```
python -m unittest -v
```

Pruebas manuales: registrar un vehículo con 30 días, darle entrada (queda en la celda 1),
intentar entrada otra vez (rechazada), registrar otro con `-5` días (mensualidad vencida,
entrada rechazada) y registrar la salida (la celda vuelve a quedar libre).

## Estructura

| Archivo | Qué contiene |
|---|---|
| `main.py` | Ventana principal (tkinter) |
| `logica.py` | Reglas del negocio y acceso a la base de datos SQLite |
| `test_logica.py` | Pruebas automáticas de `logica.py` |

## Reglas implementadas

- La placa se guarda en mayúsculas.
- Solo entra un vehículo registrado, con mensualidad vigente y que no esté ya adentro.
- La celda asignada es la libre de menor número; si no hay, se rechaza la entrada.
- Al salir se libera la celda, se calcula la permanencia y se avisa si la mensualidad venció.
- Cada entrada o salida se guarda completa o no se guarda (transacciones de SQLite).
