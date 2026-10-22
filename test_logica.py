"""Pruebas automáticas de logica.py (no abren ventana). Ejecutar con: python -m unittest -v"""
import os
import tempfile
import unittest

import logica


class PruebasParqueadero(unittest.TestCase):
    """Reglas de entrada, salida, celdas y mensualidad."""

    def setUp(self):
        # cada prueba usa una base de datos nueva y temporal
        self.carpeta = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        logica.NOMBRE_BD = os.path.join(self.carpeta.name, "prueba.db")
        logica.crear_tablas()

    def tearDown(self):
        self.carpeta.cleanup()

    def test_entrada_sin_registrar(self):
        """Una placa que no está registrada no puede entrar."""
        ok, mensaje = logica.registrar_entrada("ABC123")
        self.assertFalse(ok)
        self.assertIn("no está registrado", mensaje)

    def test_registrar_y_entrar_asigna_celda_1(self):
        """El primer vehículo que entra queda en la celda 1, aunque la placa venga en minúsculas."""
        logica.registrar_vehiculo("abc123", "Juan Pérez", "30")
        ok, mensaje = logica.registrar_entrada("abc123")
        self.assertTrue(ok)
        self.assertIn("celda 1", mensaje)

    def test_no_entra_dos_veces(self):
        """Un vehículo que ya está adentro no puede entrar otra vez."""
        logica.registrar_vehiculo("ABC123", "Juan", "30")
        logica.registrar_entrada("ABC123")
        ok, mensaje = logica.registrar_entrada("ABC123")
        self.assertFalse(ok)
        self.assertIn("ya está adentro", mensaje)

    def test_mensualidad_vencida_no_entra(self):
        """Con la mensualidad vencida no se permite la entrada."""
        logica.registrar_vehiculo("OLD111", "Luis", "-5")
        ok, mensaje = logica.registrar_entrada("OLD111")
        self.assertFalse(ok)
        self.assertIn("venció", mensaje)

    def test_salida_libera_celda(self):
        """Al salir, la celda queda libre y el vehículo deja de estar adentro."""
        logica.registrar_vehiculo("ABC123", "Juan", "30")
        logica.registrar_entrada("ABC123")
        ok, mensaje = logica.registrar_salida("ABC123")
        self.assertTrue(ok)
        self.assertIn("liberada", mensaje)
        libres = [c for c in logica.estado_celdas() if not c["ocupada"]]
        self.assertEqual(len(libres), 10)
        self.assertEqual(logica.vehiculos_adentro(), [])

    def test_salida_sin_estar_adentro(self):
        """No se puede registrar la salida de quien no está adentro."""
        logica.registrar_vehiculo("ABC123", "Juan", "30")
        ok, mensaje = logica.registrar_salida("ABC123")
        self.assertFalse(ok)
        self.assertIn("no está adentro", mensaje)

    def test_salida_con_aviso_de_mensualidad_vencida(self):
        """Si la mensualidad venció estando adentro, sale con un aviso."""
        logica.registrar_vehiculo("ABC123", "Juan", "10")
        logica.registrar_entrada("ABC123")
        logica.registrar_vehiculo("ABC123", "Juan", "-3")  # se le vence estando adentro
        ok, mensaje = logica.registrar_salida("ABC123")
        self.assertTrue(ok)
        self.assertIn("Aviso", mensaje)

    def test_celda_libre_de_menor_numero(self):
        """La celda asignada es la libre de menor número."""
        for placa in ("AAA111", "BBB222", "CCC333"):
            logica.registrar_vehiculo(placa, "X", "30")
            logica.registrar_entrada(placa)
        logica.registrar_salida("BBB222")           # queda libre la celda 2
        logica.registrar_vehiculo("DDD444", "X", "30")
        _, mensaje = logica.registrar_entrada("DDD444")
        self.assertIn("celda 2", mensaje)

    def test_sin_celdas_libres(self):
        """Con las 10 celdas ocupadas se rechaza una entrada más."""
        for i in range(logica.TOTAL_CELDAS):
            placa = f"CAR{i:03d}"
            logica.registrar_vehiculo(placa, "X", "30")
            self.assertTrue(logica.registrar_entrada(placa)[0])
        logica.registrar_vehiculo("EXTRA1", "X", "30")
        ok, mensaje = logica.registrar_entrada("EXTRA1")
        self.assertFalse(ok)
        self.assertIn("No hay celdas libres", mensaje)

    def test_datos_invalidos(self):
        """Placa vacía, propietario vacío o días que no son número se rechazan."""
        self.assertFalse(logica.registrar_vehiculo("", "Juan", "30")[0])
        self.assertFalse(logica.registrar_vehiculo("ABC123", "", "30")[0])
        self.assertFalse(logica.registrar_vehiculo("ABC123", "Juan", "abc")[0])

    def test_historial_conserva_movimientos(self):
        """Cada entrada y salida queda guardada en el historial."""
        logica.registrar_vehiculo("ABC123", "Juan", "30")
        logica.registrar_entrada("ABC123")
        logica.registrar_salida("ABC123")
        filas = logica.historial()
        self.assertEqual(len(filas), 1)
        self.assertIsNotNone(filas[0]["salida"])


if __name__ == "__main__":
    unittest.main()
