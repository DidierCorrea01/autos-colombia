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


def _columnas(bd, tabla):
    """Devuelve los nombres de las columnas que ya tiene una tabla."""
    return [f["name"] for f in bd.execute(f"PRAGMA table_info({tabla})")]


def crear_tablas():
    """Crea las tablas la primera vez y actualiza las de la iteración 1 sin perder datos."""
    bd = conectar()
    with bd:
        bd.executescript("""
            CREATE TABLE IF NOT EXISTS celda (
                numero  INTEGER PRIMARY KEY,
                ocupada INTEGER NOT NULL DEFAULT 0 CHECK (ocupada IN (0, 1))
            );
            CREATE TABLE IF NOT EXISTS cliente (
                documento TEXT PRIMARY KEY,
                nombre    TEXT NOT NULL,
                telefono  TEXT,
                correo    TEXT,
                activo    INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
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
        # Migración de la iteración 1: columnas nuevas con valores por defecto,
        # así los datos que ya existían se conservan.
        if "tipo" not in _columnas(bd, "celda"):
            bd.execute("ALTER TABLE celda ADD COLUMN tipo TEXT NOT NULL DEFAULT 'carro' "
                       "CHECK (tipo IN ('carro', 'moto'))")
        if "estado" not in _columnas(bd, "celda"):
            bd.execute("ALTER TABLE celda ADD COLUMN estado TEXT NOT NULL DEFAULT 'activa' "
                       "CHECK (estado IN ('activa', 'mantenimiento'))")
        if "tipo" not in _columnas(bd, "vehiculo"):
            bd.execute("ALTER TABLE vehiculo ADD COLUMN tipo TEXT NOT NULL DEFAULT 'carro' "
                       "CHECK (tipo IN ('carro', 'moto'))")
        if "documento_cliente" not in _columnas(bd, "vehiculo"):
            bd.execute("ALTER TABLE vehiculo ADD COLUMN documento_cliente TEXT "
                       "REFERENCES cliente(documento)")
        for n in range(1, TOTAL_CELDAS + 1):
            bd.execute("INSERT OR IGNORE INTO celda (numero) VALUES (?)", (n,))
    bd.close()


# Cada función devuelve (ok, mensaje): ok es True si todo salió bien.

def _error_en_datos(nombre, telefono, correo):
    """Revisa nombre, teléfono y correo. Devuelve el mensaje de error o None si están bien."""
    if not nombre:
        return "El nombre no puede estar vacío"
    if telefono and not telefono.isdigit():
        return "El teléfono solo debe tener números"
    if correo and "@" not in correo:
        return "El correo no es válido"
    return None


def registrar_cliente(documento, nombre, telefono="", correo=""):
    """Registra un cliente nuevo (HU-01). Devuelve (ok, mensaje)."""
    documento = documento.strip()
    nombre = nombre.strip()
    telefono = telefono.strip()
    correo = correo.strip()
    if not documento:
        return False, "El documento no puede estar vacío"
    if not (documento.isdigit() and 8 <= len(documento) <= 10):
        return False, "El documento debe tener entre 8 y 10 números"
    error = _error_en_datos(nombre, telefono, correo)
    if error:
        return False, error
    bd = conectar()
    try:
        with bd:
            bd.execute(
                "INSERT INTO cliente (documento, nombre, telefono, correo) VALUES (?, ?, ?, ?)",
                (documento, nombre, telefono, correo))
    except sqlite3.IntegrityError:
        return False, "El documento ya está registrado"
    finally:
        bd.close()
    return True, f"Cliente {nombre} registrado"


def buscar_clientes(texto=""):
    """Devuelve los clientes cuyo documento o nombre contiene el texto (HU-02)."""
    patron = f"%{texto.strip()}%"
    bd = conectar()
    filas = bd.execute(
        """SELECT documento, nombre, telefono, correo, activo FROM cliente
           WHERE documento LIKE ? OR nombre LIKE ? ORDER BY nombre""",
        (patron, patron)).fetchall()
    bd.close()
    return filas


def editar_cliente(documento, nombre, telefono="", correo=""):
    """Cambia nombre, teléfono y correo; el documento no se edita (HU-03)."""
    nombre = nombre.strip()
    telefono = telefono.strip()
    correo = correo.strip()
    error = _error_en_datos(nombre, telefono, correo)
    if error:
        return False, error
    bd = conectar()
    with bd:
        cambios = bd.execute(
            "UPDATE cliente SET nombre = ?, telefono = ?, correo = ? WHERE documento = ?",
            (nombre, telefono, correo, documento)).rowcount
        # el nombre también se copia a sus vehículos, que lo muestran como propietario
        bd.execute("UPDATE vehiculo SET propietario = ? WHERE documento_cliente = ?",
                   (nombre, documento))
    bd.close()
    if cambios == 0:
        return False, "El cliente no existe"
    return True, "Datos del cliente actualizados"


def cambiar_estado_cliente(documento, activo):
    """Activa o desactiva un cliente sin borrarlo (HU-04). Devuelve (ok, mensaje)."""
    bd = conectar()
    try:
        with bd:
            if not activo:
                adentro = bd.execute(
                    """SELECT 1 FROM registro r JOIN vehiculo v ON v.placa = r.placa
                       WHERE v.documento_cliente = ? AND r.salida IS NULL""",
                    (documento,)).fetchone()
                if adentro:
                    return False, "No se puede desactivar: tiene un vehículo adentro"
            cambios = bd.execute("UPDATE cliente SET activo = ? WHERE documento = ?",
                                 (1 if activo else 0, documento)).rowcount
    finally:
        bd.close()
    if cambios == 0:
        return False, "El cliente no existe"
    return True, "Cliente activado" if activo else "Cliente desactivado"


def registrar_vehiculo(placa, documento, tipo, dias_texto):
    """Guarda un vehículo a nombre de un cliente o renueva su mensualidad (HU-05)."""
    placa = placa.strip().upper()
    documento = documento.strip()
    if not placa:
        return False, "La placa no puede estar vacía"
    if tipo not in ("carro", "moto"):
        return False, "El tipo debe ser carro o moto"
    try:
        dias = int(dias_texto)
    except ValueError:
        return False, "Los días deben ser un número entero"
    bd = conectar()
    try:
        with bd:
            cliente = bd.execute("SELECT nombre, activo FROM cliente WHERE documento = ?",
                                 (documento,)).fetchone()
            if cliente is None:
                return False, "El cliente no existe. Regístralo primero"
            if not cliente["activo"]:
                return False, "El cliente está inactivo"
            vence = (date.today() + timedelta(days=dias)).isoformat()
            bd.execute(
                """INSERT INTO vehiculo
                       (placa, propietario, mensualidad_hasta, tipo, documento_cliente)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(placa) DO UPDATE SET
                     propietario = excluded.propietario,
                     mensualidad_hasta = excluded.mensualidad_hasta,
                     tipo = excluded.tipo,
                     documento_cliente = excluded.documento_cliente""",
                (placa, cliente["nombre"], vence, tipo, documento))
    finally:
        bd.close()
    return True, f"{placa} guardado. Mensualidad vigente hasta {vence}"


def crear_celda(numero_texto, tipo):
    """Crea una celda nueva, libre y activa (HU-06). Devuelve (ok, mensaje)."""
    try:
        numero = int(numero_texto)
    except ValueError:
        return False, "El número de celda debe ser un entero"
    if numero <= 0:
        return False, "El número de celda debe ser mayor que cero"
    if tipo not in ("carro", "moto"):
        return False, "El tipo debe ser carro o moto"
    bd = conectar()
    try:
        with bd:
            bd.execute("INSERT INTO celda (numero, tipo) VALUES (?, ?)", (numero, tipo))
    except sqlite3.IntegrityError:
        return False, f"La celda {numero} ya existe"
    finally:
        bd.close()
    return True, f"Celda {numero} creada ({tipo})"


def cambiar_estado_celda(numero, estado):
    """Pone una celda en mantenimiento o la reactiva (HU-07). Devuelve (ok, mensaje)."""
    if estado not in ("activa", "mantenimiento"):
        return False, "Estado no válido"
    bd = conectar()
    try:
        with bd:
            celda = bd.execute("SELECT ocupada FROM celda WHERE numero = ?",
                               (numero,)).fetchone()
            if celda is None:
                return False, "La celda no existe"
            if estado == "mantenimiento" and celda["ocupada"]:
                return False, "No se puede poner en mantenimiento una celda ocupada"
            bd.execute("UPDATE celda SET estado = ? WHERE numero = ?", (estado, numero))
    finally:
        bd.close()
    return True, f"Celda {numero} en estado {estado}"


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
            """SELECT numero FROM celda
               WHERE ocupada = 0 AND estado = 'activa' AND tipo = ?
               ORDER BY numero LIMIT 1""", (vehiculo["tipo"],)).fetchone()
        if celda is None:
            bd.rollback()
            return False, f"No hay celdas libres para {vehiculo['tipo']}"
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
    """Devuelve número, tipo, estado y si está ocupada, de cada celda (HU-08)."""
    bd = conectar()
    filas = bd.execute(
        "SELECT numero, tipo, estado, ocupada FROM celda ORDER BY numero").fetchall()
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
