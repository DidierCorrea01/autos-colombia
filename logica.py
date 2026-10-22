"""Autos Colombia - lógica del negocio y base de datos (sin pantallas)."""
import sqlite3
from datetime import datetime, date, timedelta

NOMBRE_BD = "parqueadero.db"
TOTAL_CELDAS = 10


def conectar():
    """Abre la conexión con la base de datos (las filas se leen por nombre de columna)."""
    conexion = sqlite3.connect(NOMBRE_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    """Crea las tablas la primera vez y las 10 celdas."""
    bd = conectar()
    with bd:
        bd.executescript("""
            CREATE TABLE IF NOT EXISTS celda (
                numero  INTEGER PRIMARY KEY,
                ocupada INTEGER NOT NULL DEFAULT 0 CHECK (ocupada IN (0, 1))
            );
            CREATE TABLE IF NOT EXISTS vehiculo (
                placa              TEXT PRIMARY KEY,
                propietario        TEXT NOT NULL,
                mensualidad_hasta  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS registro (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                placa    TEXT NOT NULL REFERENCES vehiculo(placa),
                celda    INTEGER NOT NULL REFERENCES celda(numero),
                entrada  TEXT NOT NULL,
                salida   TEXT
            );
        """)
        for n in range(1, TOTAL_CELDAS + 1):
            bd.execute("INSERT OR IGNORE INTO celda (numero) VALUES (?)", (n,))
    bd.close()


# Cada función devuelve (ok, mensaje): ok es True si todo salió bien.

def registrar_vehiculo(placa, propietario, dias_texto):
    """Guarda un vehículo o renueva su mensualidad. Devuelve (ok, mensaje)."""
    placa = placa.strip().upper()
    propietario = propietario.strip()
    if not placa:
        return False, "La placa no puede estar vacía"
    if not propietario:
        return False, "El propietario no puede estar vacío"
    try:
        dias = int(dias_texto)
    except ValueError:
        return False, "Los días deben ser un número entero"
    vence = (date.today() + timedelta(days=dias)).isoformat()
    bd = conectar()
    with bd:
        bd.execute(
            """INSERT INTO vehiculo (placa, propietario, mensualidad_hasta)
               VALUES (?, ?, ?)
               ON CONFLICT(placa) DO UPDATE SET
                 propietario = excluded.propietario,
                 mensualidad_hasta = excluded.mensualidad_hasta""",
            (placa, propietario, vence))
    bd.close()
    return True, f"{placa} guardado. Mensualidad vigente hasta {vence}"


def registrar_entrada(placa):
    """Valida y registra la entrada de un vehículo. Devuelve (ok, mensaje)."""
    placa = placa.strip().upper()
    if not placa:
        return False, "Escribe la placa"
    bd = conectar()
    try:
        bd.execute("BEGIN IMMEDIATE")
        vehiculo = bd.execute(
            "SELECT * FROM vehiculo WHERE placa = ?", (placa,)).fetchone()
        if vehiculo is None:
            bd.rollback()
            return False, f"{placa} no está registrado. Regístralo primero"
        if vehiculo["mensualidad_hasta"] < date.today().isoformat():
            bd.rollback()
            return False, f"La mensualidad de {placa} venció el {vehiculo['mensualidad_hasta']}"
        adentro = bd.execute(
            "SELECT 1 FROM registro WHERE placa = ? AND salida IS NULL",
            (placa,)).fetchone()
        if adentro:
            bd.rollback()
            return False, f"{placa} ya está adentro"
        celda = bd.execute(
            "SELECT numero FROM celda WHERE ocupada = 0 ORDER BY numero LIMIT 1"
        ).fetchone()
        if celda is None:
            bd.rollback()
            return False, "No hay celdas libres"
        ahora = datetime.now().isoformat(timespec="seconds")
        bd.execute("INSERT INTO registro (placa, celda, entrada) VALUES (?, ?, ?)",
                   (placa, celda["numero"], ahora))
        bd.execute("UPDATE celda SET ocupada = 1 WHERE numero = ?", (celda["numero"],))
        bd.commit()
        return True, f"Entró {placa} - celda {celda['numero']}"
    finally:
        bd.close()


def registrar_salida(placa):
    """Registra la salida, libera la celda y calcula la permanencia. Devuelve (ok, mensaje)."""
    placa = placa.strip().upper()
    if not placa:
        return False, "Escribe la placa"
    bd = conectar()
    try:
        bd.execute("BEGIN IMMEDIATE")
        registro = bd.execute(
            "SELECT * FROM registro WHERE placa = ? AND salida IS NULL",
            (placa,)).fetchone()
        if registro is None:
            bd.rollback()
            return False, f"{placa} no está adentro"
        ahora = datetime.now()
        bd.execute("UPDATE registro SET salida = ? WHERE id = ?",
                   (ahora.isoformat(timespec="seconds"), registro["id"]))
        bd.execute("UPDATE celda SET ocupada = 0 WHERE numero = ?", (registro["celda"],))
        vehiculo = bd.execute(
            "SELECT mensualidad_hasta FROM vehiculo WHERE placa = ?", (placa,)).fetchone()
        bd.commit()
    finally:
        bd.close()
    minutos = int((ahora - datetime.fromisoformat(registro["entrada"])).total_seconds() // 60)
    mensaje = f"Salió {placa} - celda {registro['celda']} liberada. Permanencia: {minutos} min"
    if vehiculo["mensualidad_hasta"] < date.today().isoformat():
        mensaje += f". Aviso: la mensualidad venció el {vehiculo['mensualidad_hasta']}"
    return True, mensaje


def vehiculos_adentro():
    """Devuelve los vehículos que están dentro, ordenados por celda."""
    bd = conectar()
    filas = bd.execute(
        """SELECT r.celda, r.placa, v.propietario, r.entrada
           FROM registro r JOIN vehiculo v ON v.placa = r.placa
           WHERE r.salida IS NULL ORDER BY r.celda""").fetchall()
    bd.close()
    return filas


def estado_celdas():
    """Devuelve el número y el estado (libre u ocupada) de cada celda."""
    bd = conectar()
    filas = bd.execute("SELECT numero, ocupada FROM celda ORDER BY numero").fetchall()
    bd.close()
    return filas


def historial(limite=50):
    """Devuelve los últimos movimientos, del más reciente al más antiguo."""
    bd = conectar()
    filas = bd.execute(
        "SELECT placa, celda, entrada, salida FROM registro ORDER BY id DESC LIMIT ?",
        (limite,)).fetchall()
    bd.close()
    return filas
