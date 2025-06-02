# Importación de módulos necesarios para pruebas, manejo de archivos y logging
import unittest       # Módulo de pruebas unitarias
import os             # Operaciones con archivos y rutas
import json           # Para leer y escribir archivos JSON
import csv            # Para manejo de archivos CSV
import logging        # Para verificar registros (logs)
from io import StringIO
from contextlib import redirect_stdout  # Para capturar salida en consola (no se usa en este test)

# Importación de clases y funciones del sistema veterinario
from peludos_sprint_6 import Dueno, Mascota, Consulta, guardar_datos, cargar_datos, mascotasregistradas

# Clase que contiene todas las pruebas unitarias
class TestVeterinaria(unittest.TestCase):

    # Método que se ejecuta antes de cada prueba
    def setUp(self):
        # Crear un dueño, una mascota y una consulta
        self.dueno = Dueno("Carlos", "123456789", "Calle Falsa 123")
        self.mascota = Mascota("Firulais", "Perro", "Labrador", 5, self.dueno)
        self.consulta = Consulta("01/06/2025", "Revisión general", "Saludable")
        
        # Asociar la consulta con la mascota
        self.mascota.agregarconsulta(self.consulta)
        
        # Asegurar que la lista de mascotas esté limpia y registrar una mascota
        mascotasregistradas.clear()
        mascotasregistradas.append(self.mascota)

    # Prueba los atributos del dueño
    def test_atributos_dueno(self):
        self.assertEqual(self.dueno.nombre, "Carlos")
        self.assertEqual(self.dueno.telefono, "123456789")
        self.assertEqual(self.dueno.direccion, "Calle Falsa 123")

    # Prueba los atributos de la mascota
    def test_atributos_mascota(self):
        self.assertEqual(self.mascota.nombre, "Firulais")
        self.assertEqual(self.mascota.raza, "Labrador")
        self.assertEqual(self.mascota.edad, 5)
        self.assertEqual(self.mascota.dueno, self.dueno)

    # Verifica que se haya agregado una consulta correctamente
    def test_agregar_consulta(self):
        self.assertEqual(len(self.mascota.consultas), 1)
        self.assertIn(self.consulta, self.mascota.consultas)

    # Verifica el método __str__ de la clase Consulta
    def test_str_consulta(self):
        esperado = "[01/06/2025] Motivo: Revisión general | Diagnóstico: Saludable"
        self.assertEqual(str(self.consulta), esperado)

    # Prueba la exportación de datos a CSV y JSON y valida su contenido
    def test_serializacion_csv_y_json(self):
        guardar_datos()
        
        # Comprueba que los archivos se hayan creado
        self.assertTrue(os.path.exists("exportaciones/mascotas_dueños.csv"))
        self.assertTrue(os.path.exists("exportaciones/consultas.json"))

        # Abre el JSON y comprueba que contenga la consulta registrada
        with open("exportaciones/consultas.json", encoding="utf-8") as f:
            data = json.load(f)
            key = "Firulais_Carlos"
            self.assertIn(key, data)
            self.assertEqual(data[key][0]["diagnostico"], "Saludable")

    # Verifica que se lanza una excepción si se intenta registrar una mascota con edad negativa
    def test_manejo_de_excepcion_edad_negativa(self):
        with self.assertRaises(ValueError):
            Mascota("Toby", "Gato", "Siames", -3, self.dueno)

    # Comprueba que el mensaje de exportación aparece en el archivo de log
    def test_logging_evento_exportacion(self):
        with open('clinica_veterinaria.log', 'r', encoding='latin-1') as log_file:
            logs = log_file.read()
        self.assertIn("Datos exportados", logs)

    # Verifica la salida del historial de consultas
    def test_mostrar_historial(self):
        salida = self.mascota.mostrarhistorial()
        self.assertIn("Historial de Firulais:", salida)
        self.assertIn("Revisión general", salida)

    # Limpia los archivos generados después de cada prueba
    def tearDown(self):
        if os.path.exists("exportaciones/mascotas_dueños.csv"):
            os.remove("exportaciones/mascotas_dueños.csv")
        if os.path.exists("exportaciones/consultas.json"):
            os.remove("exportaciones/consultas.json")
