"""Pruebas automáticas de logica.py (no abren ventana). Ejecutar con: python -m unittest -v"""
import os
import sqlite3
import tempfile
import unittest

import logica


class Base(unittest.TestCase):
    """Prepara una base de datos nueva y temporal para cada prueba."""

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        logica.NOMBRE_BD = os.path.join(self.carpeta.name, "prueba.db")
        logica.crear_tablas()
        logica.registrar_cliente("1037654321", "Juan Pérez", "3001234567", "juan@correo.com")

    def tearDown(self):
        self.carpeta.cleanup()

    def vehiculo(self, placa, dias="30", tipo="carro", documento="1037654321"):
        """Atajo: registra un vehículo a nombre del cliente de prueba."""
        return logica.registrar_vehiculo(placa, documento, tipo, dias)


class PruebasIteracion1(Base):
    """Reglas de entrada, salida, celdas y mensualidad (iteración 1)."""

    def test_entrada_sin_registrar(self):
        """Una placa que no está registrada no puede entrar."""
        ok, mensaje = logica.registrar_entrada("ABC123")
        self.assertFalse(ok)
        self.assertIn("no está registrado", mensaje)

    def test_registrar_y_entrar_asigna_celda_1(self):
        """El primer vehículo que entra queda en la celda 1, aunque la placa venga en minúsculas."""
        self.vehiculo("abc123")
        ok, mensaje = logica.registrar_entrada("abc123")
        self.assertTrue(ok)
        self.assertIn("celda 1", mensaje)

    def test_no_entra_dos_veces(self):
        """Un vehículo que ya está adentro no puede entrar otra vez."""
        self.vehiculo("ABC123")
        logica.registrar_entrada("ABC123")
        ok, mensaje = logica.registrar_entrada("ABC123")
        self.assertFalse(ok)
        self.assertIn("ya está adentro", mensaje)

    def test_mensualidad_vencida_no_entra(self):
        """Con la mensualidad vencida no se permite la entrada."""
        self.vehiculo("OLD111", "-5")
        ok, mensaje = logica.registrar_entrada("OLD111")
        self.assertFalse(ok)
        self.assertIn("venció", mensaje)

    def test_salida_libera_celda(self):
        """Al salir, la celda queda libre y el vehículo deja de estar adentro."""
        self.vehiculo("ABC123")
        logica.registrar_entrada("ABC123")
        ok, mensaje = logica.registrar_salida("ABC123")
        self.assertTrue(ok)
        self.assertIn("liberada", mensaje)
        libres = [c for c in logica.estado_celdas() if not c["ocupada"]]
        self.assertEqual(len(libres), 10)
        self.assertEqual(logica.vehiculos_adentro(), [])

    def test_salida_sin_estar_adentro(self):
        """No se puede registrar la salida de quien no está adentro."""
        self.vehiculo("ABC123")
        ok, mensaje = logica.registrar_salida("ABC123")
        self.assertFalse(ok)
        self.assertIn("no está adentro", mensaje)

    def test_salida_con_aviso_de_mensualidad_vencida(self):
        """Si la mensualidad venció estando adentro, sale con un aviso."""
        self.vehiculo("ABC123", "10")
        logica.registrar_entrada("ABC123")
        self.vehiculo("ABC123", "-3")  # se le vence estando adentro
        ok, mensaje = logica.registrar_salida("ABC123")
        self.assertTrue(ok)
        self.assertIn("Aviso", mensaje)

    def test_celda_libre_de_menor_numero(self):
        """La celda asignada es la libre de menor número."""
        for placa in ("AAA111", "BBB222", "CCC333"):
            self.vehiculo(placa)
            logica.registrar_entrada(placa)
        logica.registrar_salida("BBB222")           # queda libre la celda 2
        self.vehiculo("DDD444")
        _, mensaje = logica.registrar_entrada("DDD444")
        self.assertIn("celda 2", mensaje)

    def test_sin_celdas_libres(self):
        """Con las 10 celdas ocupadas se rechaza una entrada más."""
        for i in range(logica.TOTAL_CELDAS):
            placa = f"CAR{i:03d}"
            self.vehiculo(placa)
            self.assertTrue(logica.registrar_entrada(placa)[0])
        self.vehiculo("EXTRA1")
        ok, mensaje = logica.registrar_entrada("EXTRA1")
        self.assertFalse(ok)
        self.assertIn("No hay celdas libres", mensaje)

    def test_datos_invalidos(self):
        """Placa vacía, tipo inválido o días que no son número se rechazan."""
        self.assertFalse(self.vehiculo("")[0])
        self.assertFalse(self.vehiculo("ABC123", tipo="bus")[0])
        self.assertFalse(self.vehiculo("ABC123", "abc")[0])

    def test_historial_conserva_movimientos(self):
        """Cada entrada y salida queda guardada en el historial."""
        self.vehiculo("ABC123")
        logica.registrar_entrada("ABC123")
        logica.registrar_salida("ABC123")
        filas = logica.historial()
        self.assertEqual(len(filas), 1)
        self.assertIsNotNone(filas[0]["salida"])


class PruebasClientes(Base):
    """Gestión de clientes (HU-01 a HU-05)."""

    def test_registrar_cliente_queda_activo(self):
        """HU-01: un cliente nuevo queda registrado y activo."""
        ok, _ = logica.registrar_cliente("98765432", "Ana Gómez", "3109876543", "ana@correo.com")
        self.assertTrue(ok)
        ana = logica.buscar_clientes("98765432")[0]
        self.assertEqual(ana["nombre"], "Ana Gómez")
        self.assertEqual(ana["activo"], 1)

    def test_documento_repetido(self):
        """HU-01: no se aceptan dos clientes con el mismo documento."""
        ok, mensaje = logica.registrar_cliente("1037654321", "Otro", "", "")
        self.assertFalse(ok)
        self.assertIn("ya está registrado", mensaje)

    def test_cliente_datos_invalidos(self):
        """HU-01: documento o nombre vacío, teléfono con letras o correo sin @ se rechazan."""
        self.assertFalse(logica.registrar_cliente("", "Ana")[0])
        self.assertFalse(logica.registrar_cliente("1122334455", "")[0])
        self.assertFalse(logica.registrar_cliente("1122334455", "Ana", "abc")[0])
        self.assertFalse(logica.registrar_cliente("1122334455", "Ana", "", "sinarroba")[0])

    def test_documento_con_formato_invalido(self):
        """HU-01: el documento solo acepta de 8 a 10 números."""
        for malo in ("1001", "123456789012", "ABC12345678", "1234 5678"):
            ok, mensaje = logica.registrar_cliente(malo, "Ana")
            self.assertFalse(ok, malo)
            self.assertIn("8 y 10", mensaje)
        self.assertTrue(logica.registrar_cliente("12345678", "Ocho cifras")[0])
        self.assertTrue(logica.registrar_cliente("1234567890", "Diez cifras")[0])

    def test_buscar_por_nombre_y_documento(self):
        """HU-02: la búsqueda encuentra por parte del nombre o del documento."""
        logica.registrar_cliente("98765432", "Ana Gómez")
        self.assertEqual(len(logica.buscar_clientes("gómez")), 1)
        self.assertEqual(len(logica.buscar_clientes("10376")), 1)
        self.assertEqual(len(logica.buscar_clientes("")), 2)
        self.assertEqual(logica.buscar_clientes("zzz"), [])

    def test_editar_cliente_actualiza_vehiculos(self):
        """HU-03: al cambiar el nombre, sus vehículos muestran el nombre nuevo."""
        self.vehiculo("ABC123")
        ok, _ = logica.editar_cliente("1037654321", "Juan P. Pérez", "3000000000", "j@correo.com")
        self.assertTrue(ok)
        self.assertEqual(logica.buscar_clientes("1037654321")[0]["nombre"], "Juan P. Pérez")
        self.vehiculo("ABC123")
        logica.registrar_entrada("ABC123")
        self.assertEqual(logica.vehiculos_adentro()[0]["propietario"], "Juan P. Pérez")

    def test_editar_cliente_inexistente(self):
        """HU-03: no se puede editar un cliente que no existe."""
        self.assertFalse(logica.editar_cliente("9999", "Nadie")[0])

    def test_desactivar_cliente(self):
        """HU-04: un cliente sin vehículos adentro se puede desactivar y reactivar."""
        ok, _ = logica.cambiar_estado_cliente("1037654321", False)
        self.assertTrue(ok)
        self.assertEqual(logica.buscar_clientes("1037654321")[0]["activo"], 0)
        logica.cambiar_estado_cliente("1037654321", True)
        self.assertEqual(logica.buscar_clientes("1037654321")[0]["activo"], 1)

    def test_no_desactivar_con_vehiculo_adentro(self):
        """HU-04: no se desactiva un cliente que tiene un vehículo dentro."""
        self.vehiculo("ABC123")
        logica.registrar_entrada("ABC123")
        ok, mensaje = logica.cambiar_estado_cliente("1037654321", False)
        self.assertFalse(ok)
        self.assertIn("adentro", mensaje)

    def test_vehiculo_de_cliente_inactivo_o_inexistente(self):
        """HU-05: no se registran vehículos a clientes inactivos ni inexistentes."""
        logica.cambiar_estado_cliente("1037654321", False)
        self.assertFalse(self.vehiculo("ABC123")[0])
        self.assertFalse(self.vehiculo("ABC123", documento="9999")[0])


class PruebasCeldas(Base):
    """Gestión de celdas (HU-06 a HU-09)."""

    def test_crear_celda_moto(self):
        """HU-06: la celda nueva queda activa, libre y con su tipo."""
        ok, _ = logica.crear_celda("11", "moto")
        self.assertTrue(ok)
        nueva = [c for c in logica.estado_celdas() if c["numero"] == 11][0]
        self.assertEqual((nueva["tipo"], nueva["estado"], nueva["ocupada"]),
                         ("moto", "activa", 0))

    def test_crear_celda_repetida_o_invalida(self):
        """HU-06: número repetido, no numérico o tipo inválido se rechazan."""
        self.assertFalse(logica.crear_celda("5", "carro")[0])
        self.assertFalse(logica.crear_celda("abc", "carro")[0])
        self.assertFalse(logica.crear_celda("0", "carro")[0])
        self.assertFalse(logica.crear_celda("12", "bus")[0])

    def test_mantenimiento_no_se_asigna(self):
        """HU-07: una celda en mantenimiento se salta al asignar."""
        self.assertTrue(logica.cambiar_estado_celda(1, "mantenimiento")[0])
        self.vehiculo("ABC123")
        _, mensaje = logica.registrar_entrada("ABC123")
        self.assertIn("celda 2", mensaje)

    def test_reactivar_celda(self):
        """HU-07: al reactivarla vuelve a asignarse."""
        logica.cambiar_estado_celda(1, "mantenimiento")
        logica.cambiar_estado_celda(1, "activa")
        self.vehiculo("ABC123")
        _, mensaje = logica.registrar_entrada("ABC123")
        self.assertIn("celda 1", mensaje)

    def test_no_mantenimiento_si_ocupada(self):
        """HU-07: no se puede poner en mantenimiento una celda ocupada."""
        self.vehiculo("ABC123")
        logica.registrar_entrada("ABC123")
        ok, mensaje = logica.cambiar_estado_celda(1, "mantenimiento")
        self.assertFalse(ok)
        self.assertIn("ocupada", mensaje)

    def test_celda_inexistente(self):
        """HU-07: cambiar el estado de una celda que no existe se rechaza."""
        self.assertFalse(logica.cambiar_estado_celda(99, "activa")[0])

    def test_listado_con_tipo_y_estado(self):
        """HU-08: cada celda trae número, tipo, estado y ocupación."""
        celda = logica.estado_celdas()[0]
        self.assertEqual(sorted(celda.keys()), ["estado", "numero", "ocupada", "tipo"])

    def test_moto_solo_en_celda_de_moto(self):
        """HU-09: una moto no entra a celda de carro; con celda de moto sí."""
        self.vehiculo("MOT11A", tipo="moto")
        ok, mensaje = logica.registrar_entrada("MOT11A")
        self.assertFalse(ok)
        self.assertIn("moto", mensaje)
        logica.crear_celda("11", "moto")
        ok, mensaje = logica.registrar_entrada("MOT11A")
        self.assertTrue(ok)
        self.assertIn("celda 11", mensaje)


class PruebaMigracion(unittest.TestCase):
    """RNF-07: la base de la iteración 1 se actualiza sin perder datos."""

    def test_migracion_conserva_datos(self):
        """Una base con el esquema viejo conserva vehículos y registros tras actualizarse."""
        with tempfile.TemporaryDirectory() as carpeta:
            logica.NOMBRE_BD = os.path.join(carpeta, "vieja.db")
            bd = sqlite3.connect(logica.NOMBRE_BD)
            bd.executescript("""
                CREATE TABLE celda (numero INTEGER PRIMARY KEY,
                    ocupada INTEGER NOT NULL DEFAULT 0 CHECK (ocupada IN (0, 1)));
                CREATE TABLE vehiculo (placa TEXT PRIMARY KEY, propietario TEXT NOT NULL,
                    mensualidad_hasta TEXT NOT NULL);
                CREATE TABLE registro (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placa TEXT NOT NULL, celda INTEGER NOT NULL,
                    entrada TEXT NOT NULL, salida TEXT);
                INSERT INTO celda VALUES (1, 1);
                INSERT INTO vehiculo VALUES ('OLD123', 'Luis', '2099-01-01');
                INSERT INTO registro (placa, celda, entrada) VALUES ('OLD123', 1, '2026-10-01T08:00:00');
            """)
            bd.commit()
            bd.close()
            logica.crear_tablas()
            logica.crear_tablas()  # ejecutarla dos veces no debe fallar
            self.assertEqual(len(logica.vehiculos_adentro()), 1)
            celda1 = logica.estado_celdas()[0]
            self.assertEqual((celda1["tipo"], celda1["estado"], celda1["ocupada"]),
                             ("carro", "activa", 1))
            self.assertEqual(len(logica.estado_celdas()), logica.TOTAL_CELDAS)


if __name__ == "__main__":
    unittest.main()
