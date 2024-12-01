#1 prueba 1
import matplotlib.dates as mdates
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from database.db_conexion import conectar_bd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter
import re


def validar_entrada(event, entry_widget):
    valor = entry_widget.get()
    if not re.match(r'^\d*\.?\d*$', valor):  # Solo números y un punto decimal
        entry_widget.delete(0, ttk.END)
        entry_widget.insert(0, re.sub(r'[^\d.]', '', valor))

def calcular_punto_equilibrio(costos_fijos, precio_venta, costo_variable):
    try:
        if precio_venta <= 0 or costo_variable <= 0 or costos_fijos <= 0:
            raise ValueError("Todos los valores deben ser positivos.")
        if precio_venta <= costo_variable:
            raise ValueError("El precio de venta debe ser mayor que el costo variable para calcular el punto de equilibrio.")
        
        # Cálculo del punto de equilibrio
        punto_equilibrio = costos_fijos / (precio_venta - costo_variable)
        ingresos_totales = precio_venta * punto_equilibrio
        costo_variable_total = punto_equilibrio * costo_variable
        costos_totales = costos_fijos + costo_variable_total
        ganancias = ingresos_totales - costos_totales
        ventas_totales = punto_equilibrio * precio_venta

        # Calcular el apalancamiento operativo
        contribucion_marginal_total = ventas_totales - costo_variable_total

        if contribucion_marginal_total == 0:
            apalancamiento = "No válido, no hay contribución marginal."
        else:
            apalancamiento = (ventas_totales - costos_fijos) / contribucion_marginal_total

        return punto_equilibrio, ingresos_totales, costos_totales, ganancias, apalancamiento
    except Exception as e:
        print(f"Error en el cálculo: {e}")
        return None, None, None, None, None

# Función para crear el dashboard
def crear_dashboard():
    global dashboard, lbl_pe, lbl_ventas, lbl_apalancamiento, entry_costos_fijos, entry_precio_unitario, entry_costo_variable_unitario, panel_graficos

    if dashboard is not None:
        dashboard.deiconify()
        return

    # Ventana principal del dashboard
    dashboard = ttk.Toplevel()
    dashboard.title("Dashboard Financiero")
    dashboard.geometry("900x600")
    dashboard.resizable(True, True)

    # Panel principal dividido en dos columnas
    panel_principal = ttk.Frame(dashboard, padding=10)
    panel_principal.pack(fill=BOTH, expand=True)

    # Panel izquierdo: Entradas y KPIs
    panel_izquierdo = ttk.Frame(panel_principal, padding=10)
    panel_izquierdo.pack(side=LEFT, fill=Y, expand=False)

    ttk.Label(panel_izquierdo, text="Datos de Entrada", font=("Arial", 14)).pack(anchor=W, pady=5)

    ttk.Label(panel_izquierdo, text="Costos Fijos:", font=("Arial", 12)).pack(anchor=W)
    entry_costos_fijos = ttk.Entry(panel_izquierdo, font=("Arial", 12), width=20)
    entry_costos_fijos.pack(anchor=W, pady=2)
    entry_costos_fijos.bind('<KeyRelease>', lambda e: validar_entrada(e, entry_costos_fijos))

    ttk.Label(panel_izquierdo, text="Precio Unitario:", font=("Arial", 12)).pack(anchor=W)
    entry_precio_unitario = ttk.Entry(panel_izquierdo, font=("Arial", 12), width=20)
    entry_precio_unitario.pack(anchor=W, pady=2)
    entry_precio_unitario.bind('<KeyRelease>', lambda e: validar_entrada(e, entry_precio_unitario))

    ttk.Label(panel_izquierdo, text="Costo Variable Unitario:", font=("Arial", 12)).pack(anchor=W)
    entry_costo_variable_unitario = ttk.Entry(panel_izquierdo, font=("Arial", 12), width=20)
    entry_costo_variable_unitario.pack(anchor=W, pady=2)
    entry_costo_variable_unitario.bind('<KeyRelease>', lambda e: validar_entrada(e, entry_costo_variable_unitario))

    # Botones de acción
    ttk.Button(panel_izquierdo, text="Calcular", bootstyle=SUCCESS, command=lambda: calcular_y_actualizar_kpis(
        entry_costos_fijos, entry_precio_unitario, entry_costo_variable_unitario, lbl_pe, lbl_ventas, lbl_apalancamiento, datos_evolucion=None)
    ).pack(anchor=W, pady=10)

    ttk.Button(panel_izquierdo, text="Exportar a Excel", bootstyle=INFO, command=lambda: exportar_a_excel(
        lbl_pe["text"].split(": ")[1], lbl_ventas["text"].split(": $")[1], "No calculado aquí", "No calculado aquí", lbl_apalancamiento["text"].split(": ")[1])
    ).pack(anchor=W, pady=5)

    # Indicadores Clave
    ttk.Label(panel_izquierdo, text="Indicadores Clave", font=("Arial", 14)).pack(anchor=W, pady=10)
    lbl_pe = ttk.Label(panel_izquierdo, text="Punto de Equilibrio: --", font=("Arial", 12))
    lbl_pe.pack(anchor=W, pady=5)
    lbl_ventas = ttk.Label(panel_izquierdo, text="Ventas Totales: --", font=("Arial", 12))
    lbl_ventas.pack(anchor=W, pady=5)
    lbl_apalancamiento = ttk.Label(panel_izquierdo, text="Apalancamiento Operativo: --", font=("Arial", 12))
    lbl_apalancamiento.pack(anchor=W, pady=5)

    # Panel derecho: Gráficos
    panel_graficos = ttk.Frame(panel_principal, padding=10, bootstyle="info")
    panel_graficos.pack(side=RIGHT, fill=BOTH, expand=True)

    ttk.Label(panel_graficos, text="Gráfica de Análisis", font=("Arial", 14)).pack(anchor=W, pady=5)
    ttk.Label(panel_graficos, text="(Aquí irán los gráficos generados)", font=("Arial", 12, "italic")).pack(anchor=W, pady=50)

def exportar_a_excel(punto_equilibrio, ingresos_totales, costos_totales, ganancias, apalancamiento):
    try:
        # Nombre del archivo
        nombre_archivo = "Resultados_Financieros.xlsx"

        # Crear el archivo Excel
        workbook = xlsxwriter.Workbook(nombre_archivo)
        worksheet = workbook.add_worksheet("Resultados")

        # Agregar encabezados
        headers = ["Indicador", "Valor"]
        worksheet.write_row(0, 0, headers)

        # Agregar datos
        datos = [
            ["Punto de Equilibrio (unidades)", punto_equilibrio],
            ["Ingresos Totales ($)", ingresos_totales],
            ["Costos Totales ($)", costos_totales],
            ["Ganancias ($)", ganancias],
            ["Apalancamiento Operativo", apalancamiento],
        ]
        for i, fila in enumerate(datos, start=1):
            worksheet.write_row(i, 0, fila)

        # Cerrar y guardar el archivo
        workbook.close()

        messagebox.showinfo("Éxito", f"Archivo Excel exportado correctamente como '{nombre_archivo}'.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")


def generar_grafico(panel, precio_venta, costos_fijos, costo_variable_unitario, datos_evolucion=None):
    """
    Genera gráficos en el panel del dashboard, incluyendo ingresos, costos totales y ganancias.
    
    Parámetros:
    - panel: Frame de Tkinter donde se mostrará el gráfico.
    - precio_venta: Precio de venta por unidad.
    - costos_fijos: Costos fijos totales.
    - costo_variable_unitario: Costo variable por unidad.
    - datos_evolucion: (Opcional) Lista de tuplas (fecha, ventas_totales) para el gráfico de evolución.
    """
    # Calcular el punto de equilibrio y otros valores
    punto_equilibrio, ingresos_totales_pe, costos_totales_pe, ganancias_pe, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_venta, costo_variable_unitario)

    if punto_equilibrio is None:
        print("Error en los cálculos. No se puede generar la gráfica.")
        return

    # Limpiar gráficos previos en el panel
    for widget in panel.winfo_children():
        widget.destroy()

    # Crear un Canvas para la gráfica
    canvas_grafico = ttk.Canvas(panel, width=800, height=400)  # Establecer un tamaño fijo para el Canvas
    canvas_grafico.pack(fill=ttk.BOTH, expand=True)

    # Crear figura de Matplotlib
    fig = Figure(figsize=(9, 4), dpi=100)  # Ajustar el tamaño de la figura
    ax1 = fig.add_subplot(111)

    # Calcular las líneas de la gráfica
    unidades = list(range(0, int(punto_equilibrio * 2)))  # Rango hasta 2 veces el punto de equilibrio
    ingresos = [u * precio_venta for u in unidades]
    costos_variables = [u * costo_variable_unitario for u in unidades]
    costos_totales = [costos_fijos + cv for cv in costos_variables]
    ganancias = [i - c for i, c in zip(ingresos, costos_totales)]
    
    # Línea de Ingresos Constantes Totales
    ingresos_constantes_totales = [ingresos_totales_pe] * len(unidades)

    # Graficar las líneas
    ax1.plot(unidades, ingresos, label='Ingresos', color='#458ec1', linewidth=2)
    ax1.plot(unidades, costos_totales, label='Costos Totales', color='#ff9437', linewidth=2)
    ax1.plot(unidades, ganancias, label='Ganancias', color='#4cae4c', linestyle='-', linewidth=2)
    ax1.plot(unidades, ingresos_constantes_totales, label='Ingresos Constantes Totales', color='black', linestyle='--', linewidth=2)
    ax1.axvline(punto_equilibrio, color='black', linestyle='--', label=f'Punto de Equilibrio ({punto_equilibrio:.2f} unidades)')

    # Configuración del gráfico
    ax1.set_title('Gráfica de Apalancamiento Operativo y Punto de Equilibrio', fontsize=14)
    ax1.set_xlabel('Unidades Vendidas', fontsize=12)
    ax1.set_ylabel('Monto ($)', fontsize=12)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, frameon=True, shadow=True)
    ax1.grid(alpha=0.3)

    # Ajustar el rango del eje Y para que se ajuste a los valores altos y bajos (ganancias negativas)
    ax1.set_ylim(min(ganancias) * 1.1 if min(ganancias) < 0 else 0, max(ingresos + costos_totales) * 1.1)

    # Ajustar el layout para evitar solapamientos
    fig.tight_layout()

    # Renderizar el gráfico en el Canvas
    canvas = FigureCanvasTkAgg(fig, master=canvas_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)  # Aseguramos que ocupe todo el canvas

# Función para calcular y actualizar KPIs
def calcular_y_actualizar_kpis(entry_costos_fijos, entry_precio_unitario, entry_costo_variable_unitario, lbl_pe, lbl_ventas, lbl_apalancamiento, datos_evolucion):
    try:
        # Obtener los valores de entrada
        costos_fijos = float(entry_costos_fijos.get())
        precio_unitario = float(entry_precio_unitario.get())
        costo_variable_unitario = float(entry_costo_variable_unitario.get())

        # Calcular los resultados
        punto_equilibrio, ingresos_totales, costos_totales, ganancias, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_unitario, costo_variable_unitario)

        if punto_equilibrio is not None:
            # Actualizar los KPIs en la interfaz
            lbl_pe.config(text=f"Punto de Equilibrio: {punto_equilibrio}")
            lbl_ventas.config(text=f"Ingresos Totales: ${ingresos_totales:,.2f}")
            lbl_apalancamiento.config(text=f"Apalancamiento Operativo: {apalancamiento:.2f}")

            # Obtener datos de evolución de la base de datos (Ventas Totales y Fechas)
            conexion = conectar_bd()
            datos_evolucion = None
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute("SELECT FechaRegistro, VentasTotales FROM Parametros ORDER BY FechaRegistro ASC")
                    datos_evolucion = cursor.fetchall()  # Lista de tuplas (Fecha, VentasTotales)
                except Exception as e:
                    print(f"Error al obtener datos de evolución: {e}")
                finally:
                    cursor.close()
                    conexion.close()

            # Generar el gráfico en el panel de gráficos
            generar_grafico(panel_graficos, precio_unitario, costos_fijos, costo_variable_unitario)


    except ValueError as ve:
        messagebox.showerror("Error", f"Entrada no válida: {ve}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")



# Lógica para interactuar con la base de datos
def obtener_datos_y_calcular():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad FROM Parametros")  
            parametros = cursor.fetchall()

            if parametros:
                costos_fijos, precio_unitario, costo_variable_unitario = parametros[0]
                punto_equilibrio, ventas_totales, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_unitario, costo_variable_unitario)

                if punto_equilibrio is not None:
                    messagebox.showinfo("Resultado", f"Punto de Equilibrio: {punto_equilibrio}\nVentas Totales: {ventas_totales}\nApalancamiento: {apalancamiento}")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron datos en la tabla.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {e}")
        finally:
            cursor.close()
            conexion.close()
    else:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")

# Función para guardar los datos en la base de datos
#def guardar_datos_en_bd(costos_fijos, precio_unitario, costo_variable_unitario):
#    try:
#        conexion = conectar_bd()
#        if conexion:
#            cursor = conexion.cursor()
#            cursor.execute("INSERT INTO Parametros (CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad) VALUES (?, ?, ?)",
#                           (costos_fijos, precio_unitario, costo_variable_unitario))
#            conexion.commit()
#            cursor.close()
#            messagebox.showinfo("Éxito", "Datos guardados correctamente en la base de datos.")
        #else:
            #messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
    #except Exception as e:
        #messagebox.showerror("Error", f"Error al guardar los datos: {e}")

# Interfaz principal
def interfaz_principal():
    global dashboard
    dashboard = None

    app = ttk.Window(themename="flatly")
    app.title("Software Financiero")
    app.geometry("500x300")

    ttk.Label(app, text="Bienvenido al Software Financiero", font=("Arial", 16, "bold")).pack(pady=20)
    ttk.Button(app, text="Abrir Dashboard", bootstyle=PRIMARY, command=crear_dashboard).pack(pady=10)

    app.mainloop()

if __name__ == "__main__":
    interfaz_principal()