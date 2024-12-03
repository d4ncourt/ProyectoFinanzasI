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
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import tempfile
import os


valores_calculados = {}

combo_parametros = None

global fig

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

        # Calcular el apalancamiento operativo
        ventas_totales = punto_equilibrio * precio_venta
        contribucion_marginal_total = ventas_totales - costo_variable_total

        if contribucion_marginal_total == 0:
            apalancamiento = "No válido, no hay contribución marginal."
        else:
            apalancamiento = (ventas_totales - costos_fijos) / contribucion_marginal_total

        # Guardar los valores en la variable global `valores_calculados`
        valores_calculados.update({
            "punto_equilibrio": punto_equilibrio,
            "ingresos_totales": ingresos_totales,
            "costos_totales": costos_totales,
            "ganancias": ganancias,
            "apalancamiento": apalancamiento,
            "precio_unitario": precio_venta,
            "costo_variable_unitario": costo_variable,
            "costos_fijos": costos_fijos
        })

        return punto_equilibrio, ingresos_totales, costos_totales, ganancias, apalancamiento

    except Exception as e:
        print(f"Error en el cálculo: {e}")
        return None, None, None, None, None



# Función para crear el dashboard
# Función para crear el dashboard
def crear_dashboard():
    global dashboard, lbl_pe, lbl_ventas, lbl_apalancamiento, entry_costos_fijos, entry_precio_unitario, entry_costo_variable_unitario, panel_graficos, combo_parametros

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
        entry_costos_fijos, entry_precio_unitario, entry_costo_variable_unitario, lbl_pe, lbl_ventas, lbl_apalancamiento, panel_graficos)
    ).pack(anchor=W, pady=10)

    # Llamar a la función de exportación después de calcular
    
# Botón para exportar a Excel
    # Generar gráfico y exportar a Excel
# Generar gráfico y exportar a Excel
    ttk.Button(panel_izquierdo, text="Exportar a Excel", bootstyle=INFO, 
        command=lambda: exportar_a_excel(figura_grafico=generar_grafico(panel_izquierdo,
            float(entry_precio_unitario.get()), 
            float(entry_costos_fijos.get()), 
            float(entry_costo_variable_unitario.get()))
        )
    ).pack(anchor=W, pady=5)

# Generar gráfico y exportar a PDF
    ttk.Button(panel_izquierdo, text="Exportar a PDF", bootstyle=INFO, 
        command=lambda: exportar_a_pdf(figura_grafico=generar_grafico(panel_izquierdo,
            float(entry_precio_unitario.get()), 
            float(entry_costos_fijos.get()), 
            float(entry_costo_variable_unitario.get()))
        )
    ).pack(anchor=W, pady=5)


    ttk.Button(panel_izquierdo, text="Guardar Parámetros", bootstyle=SUCCESS, 
    command=lambda: guardar_parametros(
        float(entry_costos_fijos.get()), 
        float(entry_precio_unitario.get()), 
        float(entry_costo_variable_unitario.get())
    )
    ).pack(anchor=W, pady=5)

    combo_parametros = ttk.Combobox(panel_izquierdo, state="readonly", width=25, values=["Cargando..."])  # Replace 'root' with your actual Tkinter root window
    combo_parametros.pack(anchor=W, pady=5)
    
    # Asignar la función que manejará la selección del ComboBox
    combo_parametros.bind("<<ComboboxSelected>>", lambda event: cargar_parametros())

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

def generar_grafico(panel, precio_venta, costos_fijos, costo_variable_unitario):
    fig = None  # Inicializamos `fig` localmente en la función

    punto_equilibrio, ingresos_totales_pe, costos_totales_pe, ganancias_pe, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_venta, costo_variable_unitario)

    if punto_equilibrio is None:
        print("Error en los cálculos. No se puede generar la gráfica.")
        return None

    max_unidades = min(int(punto_equilibrio * 2), 1000)  
    unidades = list(range(0, max_unidades))

    for widget in panel.winfo_children():
        widget.destroy()

    canvas_grafico = ttk.Canvas(panel, width=800, height=400)
    canvas_grafico.pack(fill=ttk.BOTH, expand=True)

    ancho = max(9, len(unidades) / 100)  
    fig = Figure(figsize=(ancho, 4), dpi=100)  # Asignamos `fig` localmente
    ax1 = fig.add_subplot(111)

    ingresos = [u * precio_venta for u in unidades]
    costos_variables = [u * costo_variable_unitario for u in unidades]
    costos_totales = [costos_fijos + cv for cv in costos_variables]
    ganancias = [i - c for i, c in zip(ingresos, costos_totales)]
    ingresos_constantes_totales = [ingresos_totales_pe] * len(unidades)

    ax1.plot(unidades, ingresos, label='Ingresos', color='#458ec1', linewidth=2)
    ax1.plot(unidades, costos_totales, label='Costos Totales', color='#ff9437', linewidth=2)
    ax1.plot(unidades, ganancias, label='Ganancias', color='#4cae4c', linestyle='-', linewidth=2)
    ax1.plot(unidades, ingresos_constantes_totales, label='Ingresos Constantes Totales', color='black', linestyle='--', linewidth=2)
    ax1.axvline(punto_equilibrio, color='black', linestyle='--', label=f'Punto de Equilibrio ({punto_equilibrio:.2f} unidades)')

    ax1.set_title('Gráfica de Análisis', fontsize=14)
    ax1.set_xlabel('Unidades Vendidas', fontsize=12)
    ax1.set_ylabel('Monto ($)', fontsize=12)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, frameon=True, shadow=True)
    ax1.grid(alpha=0.3)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=canvas_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)

    return fig  # Devolvemos `fig` para usarla en la exportación


def exportar_a_excel(figura_grafico=None):
    try:
        # Acceder a los valores calculados
        punto_equilibrio = valores_calculados["punto_equilibrio"]
        ingresos_totales = valores_calculados["ingresos_totales"]
        costos_totales = valores_calculados["costos_totales"]
        ganancias = valores_calculados["ganancias"]
        apalancamiento = valores_calculados["apalancamiento"]
        unidades_vendidas = valores_calculados.get("unidades_vendidas", 0)  # Asegúrate de tener este valor
        precio_unitario = valores_calculados["precio_unitario"]
        costo_variable_unitario = valores_calculados["costo_variable_unitario"]
        costos_fijos = valores_calculados["costos_fijos"]

        folder = 'exportaciones'
        if not os.path.exists(folder):
            os.makedirs(folder)

        nombre_archivo = f"exportaciones/Resultados_Financieros_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Calcular ganancias dinámicamente para las unidades vendidas
        ganancias_dinamicas = (
            (precio_unitario * unidades_vendidas) -
            (costo_variable_unitario * unidades_vendidas) -
            costos_fijos
        )

        # Análisis dinámico
        if unidades_vendidas >= punto_equilibrio:
            status = "obtendría ganancias"
        else:
            status = "incurriría en pérdidas"

        analisis_texto = (
            f"Se necesitan vender {punto_equilibrio:.2f} unidades para lograr el punto de equilibrio.\n"
            f"Al vender {unidades_vendidas} unidades, la empresa {status}.\n"
            f"La ganancia exacta al vender esta cantidad es de ${ganancias_dinamicas:,.2f}."
        )
        
        # Crear el archivo Excel
        workbook = xlsxwriter.Workbook(nombre_archivo)
        worksheet = workbook.add_worksheet("Resultados")

        # Formatos
        formato_encabezado = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#4F81BD',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        formato_monetario = workbook.add_format({'num_format': '$#,##0.00', 'border': 1, 'align': 'center'})
        formato_decimal = workbook.add_format({'num_format': '0.00', 'border': 1, 'align': 'center'})

        # Encabezados de la tabla
        worksheet.merge_range('A1:B1', 'Resultados Financieros', formato_encabezado)
        worksheet.write('A2', 'Indicador', formato_encabezado)
        worksheet.write('B2', 'Valor', formato_encabezado)

        # Datos
        datos = [
            ["Punto de Equilibrio (unidades)", punto_equilibrio],
            ["Ingresos Totales ($)", ingresos_totales],
            ["Costos Totales ($)", costos_totales],
            ["Ganancias ($)", ganancias],
            ["Apalancamiento Operativo", apalancamiento],
        ]
        for i, fila in enumerate(datos, start=2):
            worksheet.write(i, 0, fila[0], formato_encabezado)
            if "($)" in fila[0]:
                worksheet.write(i, 1, fila[1], formato_monetario)
            else:
                worksheet.write(i, 1, fila[1], formato_decimal)

        # Agregar análisis dinámico
        worksheet.write(i + 2, 0, "Análisis:", formato_encabezado)
        worksheet.merge_range(f'A{i + 3}:B{i + 5}', analisis_texto, formato_decimal)

        # Ajustar el tamaño de las columnas
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 20)

        # Insertar gráfica (si es necesario)
        if figura_grafico is not None:
            imagen_stream = BytesIO()
            figura_grafico.savefig(imagen_stream, format='png', bbox_inches='tight')
            imagen_stream.seek(0)
            worksheet.insert_image("D2", "grafico.png", {'image_data': imagen_stream, 'x_scale': 0.8, 'y_scale': 0.8})

        # Guardar el archivo
        workbook.close()
        messagebox.showinfo("Éxito", f"Archivo Excel exportado correctamente como '{nombre_archivo}'.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")



def exportar_a_pdf(figura_grafico=None):
    try:
        # Acceder a los valores calculados
        punto_equilibrio = valores_calculados["punto_equilibrio"]
        ingresos_totales = valores_calculados["ingresos_totales"]
        costos_totales = valores_calculados["costos_totales"]
        ganancias = valores_calculados["ganancias"]
        apalancamiento = valores_calculados["apalancamiento"]
        unidades_vendidas = valores_calculados.get("unidades_vendidas", 0)
        precio_unitario = valores_calculados["precio_unitario"]
        costo_variable_unitario = valores_calculados["costo_variable_unitario"]
        costos_fijos = valores_calculados["costos_fijos"]

        folder = 'exportaciones'
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Nombre del archivo con fecha y hora
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"exportaciones/Resultados_Financieros_{fecha_hora_actual}.pdf"
        

        # Calcular ganancias dinámicamente para las unidades vendidas
        ganancias_dinamicas = (
            (precio_unitario * unidades_vendidas) -
            (costo_variable_unitario * unidades_vendidas) -
            costos_fijos
        )

        # Análisis dinámico
        if unidades_vendidas >= punto_equilibrio:
            status = "obtendría ganancias"
        else:
            status = "incurriría en pérdidas"

        analisis_texto = (
            f"Se necesitan vender {punto_equilibrio:.2f} unidades para lograr el punto de equilibrio.\n"
            f"Al vender {unidades_vendidas} unidades, la empresa {status}.\n"
            f"La ganancia exacta al vender esta cantidad es de ${ganancias_dinamicas:,.2f}."
        )

        # Nombre del archivo con fecha y hora
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"Resultados_Financieros_{fecha_hora_actual}.pdf"
        
        # Crear el archivo PDF
        pdf_file = canvas.Canvas(nombre_archivo, pagesize=letter)
        width, height = letter

        # Título del documento
        pdf_file.setFont("Helvetica-Bold", 16)
        pdf_file.drawString(30, height - 40, "Resultados Financieros")

        # Subtítulo y espacio para los datos
        pdf_file.setFont("Helvetica-Bold", 12)
        pdf_file.drawString(30, height - 80, "Indicadores Financieros:")

        # Datos a incluir
        data = [
            ("Punto de Equilibrio (unidades):", punto_equilibrio),
            ("Ingresos Totales ($):", ingresos_totales),
            ("Costos Totales ($):", costos_totales),
            ("Ganancias ($):", ganancias),
            ("Apalancamiento Operativo:", apalancamiento),
        ]

        y_position = height - 120  # Posición inicial para las filas de datos
        for label, value in data:
            pdf_file.setFont("Helvetica", 10)
            pdf_file.drawString(30, y_position, label)
            pdf_file.drawString(300, y_position, f"{value:,.2f}" if isinstance(value, (int, float)) else str(value))
            y_position -= 20

        # Agregar análisis dinámico al PDF
        pdf_file.setFont("Helvetica-Bold", 12)
        pdf_file.drawString(30, y_position - 20, "Análisis:")
        pdf_file.setFont("Helvetica", 10)
        pdf_file.drawString(30, y_position - 40, analisis_texto)

        # Ajustar posición para el gráfico (si es necesario)
        y_position -= 100

        # Insertar gráfico si se proporciona
        if figura_grafico is not None:
            # Guardar el gráfico en un archivo temporal
            temp_image_path = os.path.join(tempfile.gettempdir(), "grafico_temporal.png")
            figura_grafico.savefig(temp_image_path, format='png', bbox_inches='tight')

            # Insertar la imagen en el PDF
            pdf_file.drawImage(temp_image_path, 30, y_position - 200, width=500, height=200)

        # Guardar el archivo PDF
        pdf_file.save()

        # Mensaje de éxito
        messagebox.showinfo("Éxito", f"Archivo PDF exportado correctamente como '{nombre_archivo}'.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a PDF: {e}")

# Fudnción para calcular y actualizar KPIs# Función para calcular y actualizar los KPIs y la gráfica
# Función para calcular y actualizar los KPIs y la gráfica
def calcular_y_actualizar_kpis(entry_costos_fijos, entry_precio_unitario, entry_costo_variable_unitario, lbl_pe, lbl_ventas, lbl_apalancamiento, panel_graficos):
    try:
        # Obtener los valores de entrada
        costos_fijos = float(entry_costos_fijos.get())
        precio_unitario = float(entry_precio_unitario.get())
        costo_variable_unitario = float(entry_costo_variable_unitario.get())

        # Calcular los KPIs
        punto_equilibrio, ingresos_totales, costos_totales, ganancias, apalancamiento = calcular_punto_equilibrio(
            costos_fijos, precio_unitario, costo_variable_unitario
        )

        valores_calculados.update({
            "punto_equilibrio": punto_equilibrio,
            "ingresos_totales": ingresos_totales,
            "costos_totales": costos_totales,
            "ganancias": ganancias,
            "apalancamiento": apalancamiento,
            "precio_unitario": precio_unitario,
            "costo_variable_unitario": costo_variable_unitario,
            "costos_fijos": costos_fijos
        })

        if punto_equilibrio is not None:
            lbl_pe.config(text=f"Punto de Equilibrio: {punto_equilibrio:.2f} unidades")
            lbl_ventas.config(text=f"Ventas Totales: ${ingresos_totales:,.2f}")
            lbl_apalancamiento.config(text=f"Apalancamiento Operativo: {apalancamiento:.2f}")

            # Generar la gráfica utilizando la función generar_grafico
            generar_grafico(panel_graficos, precio_unitario, costos_fijos, costo_variable_unitario)

    except Exception as e:
        messagebox.showerror("Error", f"Error al calcular los KPIs: {e}")




# Función para cargar los parámetros en el combobox
def cargar_parametros(event=None):
    global combo_parametros  # Aseguramos que se usa la variable global

    conexion = conectar_bd()

    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad FROM Parametros ORDER BY FechaRegistro DESC")
            parametros = cursor.fetchall()
            print("Datos obtenidos:", parametros)

            if parametros:  # Verificar que no sea None ni vacío
                opciones = [f"CostosFijos: {p[0]}, Precio: {p[1]}, Costo Variable: {p[2]}" for p in parametros]
                combo_parametros['values'] = opciones
                combo_parametros.current(0)  # Establece el primer elemento como seleccionado

                # Asignamos valores de la primera fila de parametros
                costos_fijos, precio_unitario, costo_variable_unitario = parametros[0]  # Esto accede al primer elemento de la lista

                # Actualizamos los campos de entrada
                entry_costos_fijos.delete(0, ttk.END)
                entry_costos_fijos.insert(0, costos_fijos)
                entry_precio_unitario.delete(0, ttk.END)
                entry_precio_unitario.insert(0, precio_unitario)
                entry_costo_variable_unitario.delete(0, ttk.END)
                entry_costo_variable_unitario.insert(0, costo_variable_unitario)

                # Calculamos los KPIs
                punto_equilibrio, ingresos_totales, costos_totales, ganancias, apalancamiento = calcular_punto_equilibrio(costos_fijos, precio_unitario, costo_variable_unitario)

                if punto_equilibrio is not None:
                    lbl_pe.config(text=f"Punto de Equilibrio: {punto_equilibrio:.2f} unidades")
                    lbl_ventas.config(text=f"Ventas Totales: ${ingresos_totales:,.2f}")
                    lbl_apalancamiento.config(text=f"Apalancamiento Operativo: {apalancamiento:.2f}")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron datos en la tabla Parametros.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {e}")
        
        finally:
            cursor.close()
            conexion.close()
    else:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")

# Llamar a la función cuando se seleccione un item del combobox



def guardar_parametros(costos_fijos, precio_unitario, costo_variable_unitario):
    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO Parametros (CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad) VALUES (?, ?, ?)",
                           (costos_fijos, precio_unitario, costo_variable_unitario))
            conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Parámetros guardados correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron guardar los parámetros: {e}")


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