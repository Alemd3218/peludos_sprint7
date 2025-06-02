import csv
import json
import logging
import os

# Configuración del sistema de logging
logging.basicConfig(
    filename='clinica_veterinaria.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='latin-1'
)

# ------------------------------
# Clases
class Dueno:
    def __init__(self, nombre, telefono, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

    def __str__(self):
        return f"Dueño: {self.nombre}, Tel: {self.telefono}, Dirección: {self.direccion}"


class Mascota:
    def __init__(self, nombre, especie, raza, edad, dueno):
        if edad < 0:
            raise ValueError("La edad no puede ser negativa.")
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.dueno = dueno
        self.consultas = []

    def agregarconsulta(self, consulta):
        self.consultas.append(consulta)

    def mostrarhistorial(self):
        if not self.consultas:
            return "No hay consultas registradas para esta mascota."
        historial = f"Historial de {self.nombre}:\n"
        for c in self.consultas:
            historial += str(c) + "\n"
        return historial

    def __str__(self):
        return f"{self.nombre} ({self.especie}, {self.raza}, {self.edad} años)\n{self.dueno}"


class Consulta:
    def __init__(self, fecha, motivo, diagnostico):
        self.fecha = fecha
        self.motivo = motivo
        self.diagnostico = diagnostico

    def __str__(self):
        return f"[{self.fecha}] Motivo: {self.motivo} | Diagnóstico: {self.diagnostico}"


# ------------------------------
# Base de datos simulada
mascotasregistradas = []

# ------------------------------
# Funciones de serialización y deserialización

def guardar_datos():
    try:
        carpeta_exportaciones = "exportaciones"
        os.makedirs(carpeta_exportaciones, exist_ok=True)  # Crea la carpeta si no existe

        ruta_csv = os.path.join(carpeta_exportaciones, "mascotas_dueños.csv")
        ruta_json = os.path.join(carpeta_exportaciones, "consultas.json")

        with open(ruta_csv, "w", newline='', encoding='latin-1') as csvfile:
            fieldnames = ['nombre_mascota', 'especie', 'raza', 'edad', 'nombre_dueno', 'telefono', 'direccion']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for m in mascotasregistradas:
                writer.writerow({
                    'nombre_mascota': m.nombre,
                    'especie': m.especie,
                    'raza': m.raza,
                    'edad': m.edad,
                    'nombre_dueno': m.dueno.nombre,
                    'telefono': m.dueno.telefono,
                    'direccion': m.dueno.direccion
                })

        with open(ruta_json, "w", encoding='latin-1') as jsonfile:
            consultas_data = {}
            for m in mascotasregistradas:
                key = f"{m.nombre}_{m.dueno.nombre}"
                consultas_data[key] = [{
                    "fecha": c.fecha,
                    "motivo": c.motivo,
                    "diagnostico": c.diagnostico
                } for c in m.consultas]
            json.dump(consultas_data, jsonfile, indent=4)

        print("Datos guardados exitosamente en carpeta 'exportaciones/'.")
        logging.info("Datos exportados a carpeta 'exportaciones/'.")
    
    except Exception as e:
        print("Error al guardar datos.")
        logging.error(f"Error al guardar datos: {e}")

def cargar_datos():
    try:
        carpeta_exportaciones = "exportaciones"
        ruta_csv = os.path.join(carpeta_exportaciones, "mascotas_dueños.csv")
        ruta_json = os.path.join(carpeta_exportaciones, "consultas_mascotas.json")

        if not os.path.exists(ruta_csv) or not os.path.exists(ruta_json):
            print("No se encontraron archivos de datos previos en la carpeta 'exportaciones'.")
            logging.warning("Archivos de importación no encontrados en 'exportaciones'.")
            return

        with open(ruta_csv, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    if not row['edad'].isdigit():
                        raise ValueError("Edad no es un número válido")
                    edad = int(row['edad'])
                    dueno = Dueno(row['nombre_dueno'], row['telefono'], row['direccion'])
                    mascota = Mascota(
                        row['nombre_mascota'],
                        row['especie'],
                        row['raza'],
                        edad,
                        dueno
                    )
                    mascotasregistradas.append(mascota)
                except (ValueError, KeyError) as e:
                    logging.warning(f"Fila inválida ignorada en CSV: {row} - Error: {e}")

        with open(ruta_json, encoding='latin-1') as jsonfile:
            consultas_data = json.load(jsonfile)
            for key, consultas in consultas_data.items():
                nombre_mascota, nombre_dueno = key.split("_", 1)
                mascota = buscarmascotapornombre(nombre_mascota)
                if mascota and mascota.dueno.nombre == nombre_dueno:
                    for c in consultas:
                        consulta = Consulta(c["fecha"], c["motivo"], c["diagnostico"])
                        mascota.agregarconsulta(consulta)

        print("Datos cargados correctamente desde la carpeta 'exportaciones'.")
        logging.info("Datos importados desde carpeta 'exportaciones'.")
        print(f"{len(mascotasregistradas)} mascotas cargadas desde CSV")

    except Exception as e:
        print("Error al cargar datos.")
        logging.error(f"Error al cargar datos: {e}")
    

# ------------------------------
# Funciones principales

def registrarmascota():
    print("\n--- Registrar Nueva Mascota ---")
    try:
        nombre = input("Nombre de la mascota: ")
        especie = input("Especie: ")
        raza = input("Raza: ")
        edad = int(input("Edad (número positivo): "))
        if edad < 0:
            raise ValueError("La edad no puede ser negativa.")

        print("\n--- Datos del Dueño ---")
        nombre_dueno = input("Nombre del dueño: ")
        telefono = input("Teléfono: ")
        direccion = input("Dirección: ")

        dueno = Dueno(nombre_dueno, telefono, direccion)
        mascota = Mascota(nombre, especie, raza, edad, dueno)
        mascotasregistradas.append(mascota)

        print(f"\nMascota '{nombre}' registrada exitosamente.")
        logging.info(f"Mascota registrada: {nombre}, Dueño: {nombre_dueno}")

    except ValueError as e:
        print(f"Error: {e}")
        logging.error(f"Error al registrar mascota: {e}")
    except Exception as e:
        print("Ha ocurrido un error inesperado al registrar la mascota.")
        logging.error(f"Error inesperado en registrarmascota: {e}")


def registrarconsulta():
    print("\n--- Registrar Consulta ---")
    try:
        nombre_mascota = input("Nombre de la mascota: ")
        mascota = buscarmascotapornombre(nombre_mascota)

        if not mascota:
            raise LookupError("Mascota no encontrada.")

        fecha = input("Fecha de la consulta (DD/MM/AAAA): ")
        motivo = input("Motivo de la consulta: ")
        diagnostico = input("Diagnóstico: ")

        consulta = Consulta(fecha, motivo, diagnostico)
        mascota.agregarconsulta(consulta)

        print(f"\nConsulta registrada para {mascota.nombre}.")
        logging.info(f"Consulta registrada para: {mascota.nombre}, Fecha: {fecha}")

    except LookupError as e:
        print(f"Error: {e}")
        logging.warning(f"Intento de registrar consulta para mascota inexistente: {nombre_mascota}")
    except Exception as e:
        print("Ha ocurrido un error inesperado al registrar la consulta.")
        logging.error(f"Error inesperado en registrarconsulta: {e}")


def listarmascotas():
    print("\n--- Lista de Mascotas Registradas ---")
    try:
        if not mascotasregistradas:
            print("No hay mascotas registradas.")
        else:
            for mascota in mascotasregistradas:
                print(mascota)
                print("-" * 40)
    except Exception as e:
        print("Error al listar mascotas.")
        logging.error(f"Error en listarmascotas: {e}")


def verhistorial():
    print("\n--- Historial de Consultas ---")
    try:
        nombre_mascota = input("Nombre de la mascota: ")
        mascota = buscarmascotapornombre(nombre_mascota)

        if mascota:
            print(mascota.mostrarhistorial())
        else:
            raise LookupError("Mascota no encontrada.")

    except LookupError as e:
        print(f"Error: {e}")
        logging.warning(f"Intento de ver historial de mascota inexistente: {nombre_mascota}")
    except Exception as e:
        print("Error inesperado al mostrar el historial.")
        logging.error(f"Error en verhistorial: {e}")


def buscarmascotapornombre(nombre):
    for mascota in mascotasregistradas:
        if mascota.nombre.lower() == nombre.lower():
            return mascota
    return None


def menu():
    cargar_datos()
    logging.info("Inicio de la aplicación")
    while True:
        try:
            print("\nClínica Veterinaria 'Amigos Peludos'")
            print("1. Registrar mascota")
            print("2. Registrar consulta")
            print("3. Listar mascotas")
            print("4. Ver historial de consultas")
            print("5. Exportar datos")
            print("6. Importar datos")
            print("7. Salir")
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                registrarmascota()
            elif opcion == "2":
                registrarconsulta()
            elif opcion == "3":
                listarmascotas()
            elif opcion == "4":
                verhistorial()
            elif opcion == "5":
                guardar_datos()
                print("Datos exportados correctamente.")
            elif opcion == "6":
                mascotasregistradas.clear()
                cargar_datos()
                print("Datos importados correctamente.")
            elif opcion == "7":
                guardar_datos()
                print("¡Gracias por usar el sistema de Amigos Peludos!")
                logging.info("Cierre de la aplicación")
                break
            else:
                print("Opción no válida. Intente de nuevo.")
                logging.warning(f"Opción inválida seleccionada: {opcion}")

        except Exception as e:
            print("Error inesperado en el menú.")
            logging.error(f"Error inesperado en el menú: {e}")

# ------------------------------
# Punto de entrada
if __name__ == "__main__":
    menu()