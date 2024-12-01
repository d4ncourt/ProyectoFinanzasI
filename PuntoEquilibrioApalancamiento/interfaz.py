import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database.db_conexion import conectar_bd

# Función de cálculo integrada con Ventas Totales y Apalancamiento
def calcular_punto_equilibrio(costos_fijos, precio_venta, costo_variable):
    try:
        if precio_venta <= 0 or costo_variable <= 0 or costos_fijos <= 0:
            raise ValueError("Todos los valores deben ser positivos.")
        if precio_venta <= costo_variable:
            raise ValueError("El precio de venta debe ser mayor que el costo variable para calcular el punto de equilibrio.")
        
        # Cálculo del punto de equilibrio
        punto_equilibrio = costos_fijos / (precio_venta - costo_variable)
        ventas_totales = punto_equilibrio * precio_venta
        costo_variable_total = punto_equilibrio * costo_variable

        # Calcular el apalancamiento operativo
        contribucion_marginal_total = ventas_totales - costo_variable_total

        if contribucion_marginal_total == 0:
            apalancamiento = "No válido, no hay contribución marginal."
        else:
            apalancamiento = (ventas_totales - costos_fijos) / contribucion_marginal_total

        return punto_equilibrio, ventas_totales, apalancamiento
    except Exception as e:
        print(f"Error en el cálculo: {e}")
        return None, None, None

# Lógica para interactuar con la base de datos
def obtener_datos_y_calcular():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad FROM Parametros")  # Ajusta el nombre de la tabla si es necesario
            parametros = cursor.fetchall()

            for fila in parametros:
                try:
                    costos_fijos = fila[0]  # CostosFijos es la primera columna
                    precio_por_unidad = fila[1]  # PrecioPorUnidad es la segunda columna
                    costo_variable_por_unidad = fila[2]  # CostoVariablePorUnidad es la tercera columna
                    print(f"Costos Fijos: {costos_fijos}, Precio por Unidad: {precio_por_unidad}, Costo Variable por Unidad: {costo_variable_por_unidad}")
                except Exception as e:
                    print(f"Error al procesar la fila: {e}")

            # Si hay datos, calcula el punto de equilibrio para el primer registro como ejemplo
            if parametros:
                costos_fijos, precio_unitario, costo_variable_unitario = parametros[0]
                punto_equilibrio, ventas_totales, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_unitario, costo_variable_unitario)

                if punto_equilibrio is not None:
                    # Mostrar los resultados en la interfaz
                    messagebox.showinfo("Resultado", f"Punto de Equilibrio: {punto_equilibrio:.2f}\nVentas Totales: {ventas_totales:.2f}\nApalancamiento: {apalancamiento:.2f}")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron datos en la tabla.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {e}")
        finally:
            cursor.close()
            conexion.close()
    else:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")

# Interfaz gráfica mejorada
def interfaz_grafica():
    root = tk.Tk()
    root.title("Cálculo de Punto de Equilibrio y Apalancamiento")
    root.geometry("400x300")
    root.resizable(False, False)

    # Estilo
    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12))
    style.configure("TEntry", font=("Arial", 12))

    # Frame principal
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    # Etiquetas y campos de entrada
    ttk.Label(frame, text="Costos Fijos:").grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_costos_fijos = ttk.Entry(frame)
    entry_costos_fijos.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Precio Unitario:").grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_precio_unitario = ttk.Entry(frame)
    entry_precio_unitario.grid(row=1, column=1, pady=5)

    ttk.Label(frame, text="Costo Variable Unitario:").grid(row=2, column=0, sticky=tk.W, pady=5)
    entry_costo_variable_unitario = ttk.Entry(frame)
    entry_costo_variable_unitario.grid(row=2, column=1, pady=5)

    # Función para calcular desde los campos de entrada
    def calcular_desde_entradas():
        try:
            costos_fijos = float(entry_costos_fijos.get())
            precio_unitario = float(entry_precio_unitario.get())
            costo_variable_unitario = float(entry_costo_variable_unitario.get())

            if costos_fijos <= 0 or precio_unitario <= 0 or costo_variable_unitario <= 0:
                raise ValueError("Todos los valores deben ser positivos.")
            if precio_unitario <= costo_variable_unitario:
                raise ValueError("El precio de venta debe ser mayor que el costo variable.")

            punto_equilibrio, ventas_totales, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_unitario, costo_variable_unitario)

            if punto_equilibrio is not None:
                messagebox.showinfo("Resultado", f"Punto de Equilibrio: {punto_equilibrio}\nVentas Totales: {ventas_totales}\nApalancamiento: {apalancamiento}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")

    # Botones para calcular
    ttk.Button(frame, text="Calcular desde entradas", command=calcular_desde_entradas).grid(row=3, column=0, columnspan=2, pady=10)
    ttk.Button(frame, text="Calcular desde la base de datos", command=obtener_datos_y_calcular).grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    interfaz_grafica()
