import pyodbc

def conectar_bd():
    try:
        # Crear la conexión a la base de datos
        conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-T6NPH5F\\SQLEXPRESS;DATABASE=PEYADB;Trusted_Connection=yes;')
        print("Conexión Exitosa")
        return conexion  # Devuelve la conexión
    except Exception as e:
        print("Error en la conexión:", e)
        return None

    cursor = conexion.cursor()
    cursor.execute("Select * from Parametros;")

    parametros = cursor.fetchone()

    while parametros:
        print(parametros)
        parametros = cursor.fetchone()
    
    cursor.close()
    conexion.close()