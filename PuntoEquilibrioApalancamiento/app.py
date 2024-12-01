import pyodbc
import os
import csv
from database.db_conexion import conectar_bd

# Asegúrate de que la carpeta "exportaciones" existe
if not os.path.exists("exportaciones"):
    os.makedirs("exportaciones")

def obtener_datos():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            print("Cursor creado exitosamente")
            
            # Consulta SQL
            cursor.execute("SELECT * FROM Parametros")  # Cambia "Parametros" por el nombre de tu tabla
            print("Consulta ejecutada exitosamente")
            
            # Obtener todos los resultados
            parametros = cursor.fetchall()
            for parametro in parametros:
                print(parametro)
            
            # Llamar a la función de exportación con los datos obtenidos
            exportar_a_csv(parametros)

        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()
            conexion.close()
    else:
        print("No se pudo realizar la consulta debido a un error de conexión.")

# Esta función es la encargada de exportar a CSV
def exportar_a_csv(parametros):
    # Define el nombre del archivo CSV
    archivo_csv = 'exportaciones/datos_parametros.csv'
    
    # Escribir los datos en el archivo CSV
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Si necesitas agregar encabezados, puedes hacerlo
        writer.writerow(['ID', 'CostosFijos', 'PrecioPorunidad', 'CostoVariablePorUnidad', 'FechaRegistro'])  # Reemplaza con los nombres de tus campos
        
        # Escribir los parámetros obtenidos de la consulta
        for parametro in parametros:
            writer.writerow(parametro)
    
    print(f"Datos exportados a {archivo_csv}")

if __name__ == "__main__":
    obtener_datos()
