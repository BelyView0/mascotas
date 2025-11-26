#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog
from ttkbootstrap import Style
import ttkbootstrap as tb
import sqlite3

# -----------------------------------------
#  BASE DE DATOS 
# -----------------------------------------
DB = "mascotas.db"

def db_query(query, params=(), fetch=False, many=False):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if many:
        c.executemany(query, params)
    else:
        c.execute(query, params)
    if fetch:
        data = c.fetchall()
        conn.close()
        return data
    conn.commit()
    conn.close()

def init_db():
    db_query('''
        CREATE TABLE IF NOT EXISTS duenos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            correo TEXT,
            genero TEXT,
            edad INTEGER,
            peso REAL
        )
    ''')
    db_query('''
        CREATE TABLE IF NOT EXISTS mascotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            especie TEXT,
            raza TEXT,
            edad INTEGER,
            peso REAL,
            color TEXT,
            duenio_id INTEGER,
            FOREIGN KEY(duenio_id) REFERENCES duenos(id)
        )
    ''')
    db_query('''
        CREATE TABLE IF NOT EXISTS evaluaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mascota_id INTEGER,
            duenio_nombre TEXT,
            mascota_nombre TEXT,
            calificacion REAL,
            detalle TEXT
        )
    ''')

# -----------------------------------------
#  SISTEMA
# -----------------------------------------
class App(tb.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        master.title("PetCheck")
        master.geometry("1050x650")
        master.resizable(False, False)
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):

        title = tb.Label(
            self,
            text="🐾 PetCheck",
            font=("Segoe UI", 22, "bold"),
            anchor="center"
        )
        title.pack(pady=10)

        notebook = tb.Notebook(self)
        notebook.pack(fill="both", expand=True, pady=10)

        self.tab_duenos = tb.Frame(notebook, padding=10)
        self.tab_mascotas = tb.Frame(notebook, padding=10)
        self.tab_eval = tb.Frame(notebook, padding=10)
        self.tab_reporte = tb.Frame(notebook, padding=10)

        notebook.add(self.tab_duenos, text="Dueños")
        notebook.add(self.tab_mascotas, text="Mascotas")
        notebook.add(self.tab_eval, text="Evaluaciones")
        notebook.add(self.tab_reporte, text="Reporte Mascotas")

        self.build_duenos_tab()
        self.build_mascotas_tab()
        self.build_eval_tab()
        self.build_reporte_tab()

    # --------------------------------------------------------------------
    # PANEL DUEÑOS
    # --------------------------------------------------------------------
    def build_duenos_tab(self):
        frame = tb.Frame(self.tab_duenos)
        frame.pack(fill="both", expand=True)

        form = tb.Labelframe(frame, text="Registrar Dueño", padding=10)
        form.pack(side="left", fill="y", padx=10)

        self.d_nombre = tk.StringVar()
        self.d_correo = tk.StringVar()
        self.d_genero = tk.StringVar()
        self.d_edad = tk.IntVar(value=18)
        self.d_peso = tk.DoubleVar(value=60.0)

        tb.Label(form, text="Nombre:").pack(anchor="w")
        tb.Entry(form, textvariable=self.d_nombre).pack(fill="x")

        tb.Label(form, text="Correo:").pack(anchor="w")
        tb.Entry(form, textvariable=self.d_correo).pack(fill="x")

        tb.Label(form, text="Género:").pack(anchor="w")
        tb.Combobox(form, textvariable=self.d_genero,
                    values=["Masculino", "Femenino", "Otro"]).pack(fill="x")

        tb.Label(form, text="Edad:").pack(anchor="w")
        tb.Entry(form, textvariable=self.d_edad).pack(fill="x")

        tb.Label(form, text="Peso (kg):").pack(anchor="w")
        tb.Entry(form, textvariable=self.d_peso).pack(fill="x")

        tb.Button(form, text="Agregar Dueño",
                  bootstyle="success", command=self.agregar_dueno).pack(fill="x", pady=5)

        # Botones Edit/Delete 
        tb.Button(form, text="Editar seleccionado", bootstyle="info",
                  command=self.editar_dueno_popup).pack(fill="x", pady=2)
        tb.Button(form, text="Eliminar seleccionado", bootstyle="danger",
                  command=self.eliminar_dueno).pack(fill="x", pady=2)

        listado = tb.Labelframe(frame, text="Lista de Dueños", padding=10)
        listado.pack(side="left", fill="both", expand=True, padx=10)

        self.tree_duenos = tb.Treeview(listado,
            columns=("id","nombre","correo","genero","edad","peso","mascotas"),
            show="headings", height=15)

        for col in ("id","nombre","correo","genero","edad","peso","mascotas"):
            self.tree_duenos.heading(col, text=col.capitalize())
            self.tree_duenos.column(col, anchor="center", width=120)

        self.tree_duenos.pack(fill="both", expand=True)

        self.cargar_duenos()

    def agregar_dueno(self):
        if not self.d_nombre.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        db_query(
            "INSERT INTO duenos(nombre,correo,genero,edad,peso) VALUES (?,?,?,?,?)",
            (self.d_nombre.get().strip(), self.d_correo.get().strip(), self.d_genero.get(),
             self.d_edad.get(), self.d_peso.get())
        )
        messagebox.showinfo("Éxito", "Dueño agregado")
        self.cargar_duenos()
        # actualizar menús que usan dueños
        self.actualizar_menu_duenos()
        self.cargar_mascotas_menu()

    def cargar_duenos(self):
        for row in self.tree_duenos.get_children():
            self.tree_duenos.delete(row)

        rows = db_query('''
            SELECT d.id, d.nombre, d.correo, d.genero, d.edad, d.peso,
            IFNULL(GROUP_CONCAT(m.nombre, ", "), "Sin mascotas")
            FROM duenos d
            LEFT JOIN mascotas m ON d.id=m.duenio_id
            GROUP BY d.id
        ''', fetch=True)

        for r in rows:
            self.tree_duenos.insert("", "end", values=r)

    def editar_dueno_popup(self):
        sel = self.tree_duenos.focus()
        if not sel:
            messagebox.showerror("Error", "Seleccione un dueño del listado para editar")
            return
        row = self.tree_duenos.item(sel)["values"]
        dueno_id = row[0]

        # Obtener datos del DB 
        datos = db_query("SELECT nombre, correo, genero, edad, peso FROM duenos WHERE id=?", (dueno_id,), fetch=True)
        if not datos:
            messagebox.showerror("Error", "Dueño no encontrado")
            return
        nombre, correo, genero, edad, peso = datos[0]

        popup = tk.Toplevel()
        popup.title("Editar Dueño")
        popup.geometry("350x300")
        popup.transient(self.winfo_toplevel())

        nombre_var = tk.StringVar(value=nombre)
        correo_var = tk.StringVar(value=correo)
        genero_var = tk.StringVar(value=genero)
        edad_var = tk.IntVar(value=edad if edad is not None else 0)
        peso_var = tk.DoubleVar(value=peso if peso is not None else 0.0)

        tk.Label(popup, text="Nombre:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=nombre_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Correo:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=correo_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Género:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=genero_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Edad:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=edad_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Peso:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=peso_var).pack(fill="x", padx=10)

        def guardar():
            if not nombre_var.get().strip():
                messagebox.showerror("Error", "Nombre requerido")
                return
            try:
                db_query("UPDATE duenos SET nombre=?, correo=?, genero=?, edad=?, peso=? WHERE id=?",
                         (nombre_var.get().strip(), correo_var.get().strip(), genero_var.get().strip(),
                          int(edad_var.get()), float(peso_var.get()), dueno_id))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
                return
            messagebox.showinfo("OK", "Dueño actualizado")
            popup.destroy()
            self.cargar_duenos()
            self.actualizar_menu_duenos()
            self.cargar_mascotas_menu()

        tk.Button(popup, text="Guardar", command=guardar).pack(pady=10)

    def eliminar_dueno(self):
        sel = self.tree_duenos.focus()
        if not sel:
            messagebox.showerror("Error", "Seleccione un dueño para eliminar")
            return
        row = self.tree_duenos.item(sel)["values"]
        dueno_id = row[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar dueño {row[1]}? Esto eliminará sus mascotas si las hay."):
            # eliminar mascotas relacionadas primero
            db_query("DELETE FROM mascotas WHERE duenio_id=?", (dueno_id,))
            db_query("DELETE FROM duenos WHERE id=?", (dueno_id,))
            messagebox.showinfo("Eliminado", "Dueño (y mascotas asociadas) eliminado")
            self.cargar_duenos()
            self.cargar_mascotas()
            self.actualizar_menu_duenos()
            self.cargar_mascotas_menu()

    # --------------------------------------------------------------------
    # PANEL MASCOTAS 
    # --------------------------------------------------------------------
    def build_mascotas_tab(self):
        frame = tb.Frame(self.tab_mascotas)
        frame.pack(fill="both", expand=True)

        form = tb.Labelframe(frame, text="Registrar Mascota", padding=10)
        form.pack(side="left", fill="y", padx=10)

        # DATOS DE LA MASCOTA
        self.m_nombre = tk.StringVar()
        self.m_especie = tk.StringVar()
        self.m_raza = tk.StringVar()
        self.m_edad = tk.IntVar(value=1)
        self.m_peso = tk.DoubleVar(value=1.0)
        self.m_color = tk.StringVar()

        tb.Label(form, text="Nombre Mascota:").pack(anchor="w")
        tb.Entry(form, textvariable=self.m_nombre).pack(fill="x")

        tb.Label(form, text="Especie:").pack(anchor="w")
        tb.Entry(form, textvariable=self.m_especie).pack(fill="x")

        tb.Label(form, text="Raza:").pack(anchor="w")
        tb.Entry(form, textvariable=self.m_raza).pack(fill="x")

        tb.Label(form, text="Edad Mascota:").pack(anchor="w")
        tb.Entry(form, textvariable=self.m_edad).pack(fill="x")

        tb.Label(form, text="Peso Mascota:").pack(anchor="w")
        tb.Entry(form, textvariable=self.m_peso).pack(fill="x")

        tb.Label(form, text="Color:").pack(anchor="w")
        tb.Entry(form, textvariable=self.m_color).pack(fill="x")

        # ---------- MENÚ DESPLEGABLE DUEÑOS ----------
        tb.Label(form, text="\nDueño:").pack(anchor="w")

        self.dueno_var = tk.StringVar()
        # create OptionMenu with empty initial list; actualizar_menu_duenos() will fill it
        self.dueno_menu = tk.OptionMenu(form, self.dueno_var, "")
        self.dueno_menu.pack(fill="x")
        self.actualizar_menu_duenos()

        tb.Button(form, text="Registrar Mascota",
                  bootstyle="success", command=self.agregar_mascota).pack(fill="x", pady=5)

        # Botones Edit/Delete
        tb.Button(form, text="Editar seleccionado", bootstyle="info",
                  command=self.editar_mascota_popup).pack(fill="x", pady=2)
        tb.Button(form, text="Eliminar seleccionado", bootstyle="danger",
                  command=self.eliminar_mascota).pack(fill="x", pady=2)

        # LISTADO
        listado = tb.Labelframe(frame, text="Lista de Mascotas", padding=10)
        listado.pack(side="left", fill="both", expand=True, padx=10)

        self.tree_mascotas = tb.Treeview(listado,
            columns=("id","nombre","especie","raza","edad","peso","color","duenio"),
            show="headings", height=15)

        for col in ("id","nombre","especie","raza","edad","peso","color","duenio"):
            self.tree_mascotas.heading(col, text=col.capitalize())
            self.tree_mascotas.column(col, anchor="center", width=120)

        self.tree_mascotas.pack(fill="both", expand=True)

        self.cargar_mascotas()

    def actualizar_menu_duenos(self):
        # Rebuild OptionMenu entries using current duenos from DB
        menu = self.dueno_menu["menu"]
        menu.delete(0, "end")

        duenos = db_query("SELECT id, nombre FROM duenos", fetch=True)

        for d in duenos:
            label = f"{d[0]} - {d[1]}"
            # use lambda with default arg to capture label
            menu.add_command(label=label,
                             command=lambda v=label: self.dueno_var.set(v))

        if duenos:
            self.dueno_var.set(f"{duenos[0][0]} - {duenos[0][1]}")
        else:
            self.dueno_var.set("")

    def agregar_mascota(self):
        if not self.m_nombre.get().strip():
            messagebox.showerror("Error", "El nombre de la mascota es obligatorio")
            return
        if not self.dueno_var.get():
            messagebox.showerror("Error", "Debe seleccionar un dueño")
            return

        try:
            duenio_id = int(self.dueno_var.get().split(" - ")[0])
        except:
            messagebox.showerror("Error", "Formato de dueño inválido")
            return

        db_query("""
            INSERT INTO mascotas(nombre,especie,raza,edad,peso,color,duenio_id)
            VALUES (?,?,?,?,?,?,?)
        """, (self.m_nombre.get().strip(), self.m_especie.get().strip(), self.m_raza.get().strip(),
              int(self.m_edad.get()), float(self.m_peso.get()), self.m_color.get().strip(),
              duenio_id))

        messagebox.showinfo("Éxito", "Mascota registrada correctamente")
        self.cargar_mascotas()
        self.cargar_duenos()
        # actualizar menús que dependen de mascotas/duenos
        self.actualizar_menu_duenos()
        self.cargar_mascotas_menu()

    def cargar_mascotas(self):
        for row in self.tree_mascotas.get_children():
            self.tree_mascotas.delete(row)
        rows = db_query("""
            SELECT m.id, m.nombre, m.especie, m.raza, m.edad, m.peso, m.color,
            d.nombre as duenio
            FROM mascotas m
            LEFT JOIN duenos d ON m.duenio_id = d.id
        """, fetch=True)

        for r in rows:
            self.tree_mascotas.insert("", "end", values=r)

    def editar_mascota_popup(self):
        sel = self.tree_mascotas.focus()
        if not sel:
            messagebox.showerror("Error", "Seleccione una mascota del listado para editar")
            return
        row = self.tree_mascotas.item(sel)["values"]
        mascota_id = row[0]

        datos = db_query("SELECT nombre, especie, raza, edad, peso, color, duenio_id FROM mascotas WHERE id=?", (mascota_id,), fetch=True)
        if not datos:
            messagebox.showerror("Error", "Mascota no encontrada")
            return
        nombre, especie, raza, edad, peso, color, duenio_id = datos[0]

        popup = tk.Toplevel()
        popup.title("Editar Mascota")
        popup.geometry("380x420")
        popup.transient(self.winfo_toplevel())

        nombre_var = tk.StringVar(value=nombre)
        especie_var = tk.StringVar(value=especie)
        raza_var = tk.StringVar(value=raza)
        edad_var = tk.IntVar(value=edad if edad is not None else 0)
        peso_var = tk.DoubleVar(value=peso if peso is not None else 0.0)
        color_var = tk.StringVar(value=color)

        tk.Label(popup, text="Nombre:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=nombre_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Especie:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=especie_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Raza:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=raza_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Edad:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=edad_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Peso:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=peso_var).pack(fill="x", padx=10)

        tk.Label(popup, text="Color:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(popup, textvariable=color_var).pack(fill="x", padx=10)

        # dueño selectable via OptionMenu in popup
        tk.Label(popup, text="Dueño:").pack(anchor="w", padx=10, pady=(10,0))
        duenos = db_query("SELECT id, nombre FROM duenos", fetch=True)
        opciones = [f"{d[0]} - {d[1]}" for d in duenos]
        dueño_var = tk.StringVar()
        if opciones:
            dueño_var.set(next((o for o in opciones if int(o.split(" - ")[0])==duenio_id), opciones[0]))
        else:
            dueño_var.set("")

        dueño_menu = tk.OptionMenu(popup, dueño_var, *opciones)
        dueño_menu.pack(fill="x", padx=10, pady=5)

        def guardar():
            if not nombre_var.get().strip():
                messagebox.showerror("Error", "Nombre requerido")
                return
            try:
                nuevo_duenio_id = int(dueño_var.get().split(" - ")[0]) if dueño_var.get() else None
                db_query("UPDATE mascotas SET nombre=?, especie=?, raza=?, edad=?, peso=?, color=?, duenio_id=? WHERE id=?",
                         (nombre_var.get().strip(), especie_var.get().strip(), raza_var.get().strip(),
                          int(edad_var.get()), float(peso_var.get()), color_var.get().strip(), nuevo_duenio_id, mascota_id))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar mascota: {e}")
                return
            messagebox.showinfo("OK", "Mascota actualizada")
            popup.destroy()
            self.cargar_mascotas()
            self.cargar_duenos()
            self.actualizar_menu_duenos()
            self.cargar_mascotas_menu()

        tk.Button(popup, text="Guardar", command=guardar).pack(pady=10)

    def eliminar_mascota(self):
        sel = self.tree_mascotas.focus()
        if not sel:
            messagebox.showerror("Error", "Seleccione una mascota para eliminar")
            return
        row = self.tree_mascotas.item(sel)["values"]
        mascota_id = row[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar mascota {row[1]}?"):
            db_query("DELETE FROM evaluaciones WHERE mascota_id=?", (mascota_id,))
            db_query("DELETE FROM mascotas WHERE id=?", (mascota_id,))
            messagebox.showinfo("Eliminada", "Mascota y evaluaciones asociadas eliminadas")
            self.cargar_mascotas()
            self.cargar_duenos()
            self.actualizar_menu_duenos()
            self.cargar_mascotas_menu()

    # --------------------------------------------------------------------
    # PANEL EVALUACIONES 
    # --------------------------------------------------------------------
    def build_eval_tab(self):
        frame = tb.Frame(self.tab_eval)
        frame.pack(fill="both", expand=True)

        form = tb.Labelframe(frame, text="Evaluar Mascota", padding=10)
        form.pack(side="left", fill="y", padx=10)

        self.q1 = tk.IntVar()
        self.q2 = tk.IntVar()
        self.q3 = tk.IntVar(value=1)
        self.q4 = tk.IntVar(value=1)
        self.q5 = tk.StringVar(value="Bueno")
        self.q6 = tk.StringVar(value="Limpio")

        # ------------------------------
        #  MENÚ DESPLEGABLE MASCOTAS
        # ------------------------------
        tb.Label(form, text="Mascota a evaluar:").pack(anchor="w")
        self.mascota_var = tk.StringVar()
        self.mascota_menu = tk.OptionMenu(form, self.mascota_var, "")
        self.mascota_menu.config(width=35)
        self.mascota_menu.pack(fill="x", pady=5)
        self.cargar_mascotas_menu()

        # ------------------------------
        #  PREGUNTAS
        # ------------------------------
        tb.Checkbutton(form, text="Se comporta bien en casa", variable=self.q1).pack(anchor="w")
        tb.Checkbutton(form, text="Acepta caricias", variable=self.q2).pack(anchor="w")

        tb.Label(form, text="Nivel de actividad:").pack(anchor="w")
        tb.Radiobutton(form, text="Bajo", variable=self.q3, value=1).pack(anchor="w")
        tb.Radiobutton(form, text="Alto", variable=self.q3, value=2).pack(anchor="w")

        tb.Label(form, text="Sociabilidad:").pack(anchor="w")
        tb.Radiobutton(form, text="Reservado", variable=self.q4, value=1).pack(anchor="w")
        tb.Radiobutton(form, text="Sociable", variable=self.q4, value=2).pack(anchor="w")

        tb.Label(form, text="Estado de salud:").pack(anchor="w")
        tb.Combobox(form, textvariable=self.q5, values=["Bueno","Regular","Malo"]).pack(fill="x")

        tb.Label(form, text="Higiene:").pack(anchor="w")
        tb.Combobox(form, textvariable=self.q6, values=["Limpio","Moderado","Sucio"]).pack(fill="x")

        tb.Button(form, text="Guardar Evaluación",
                  bootstyle="success", command=self.guardar_eval).pack(fill="x", pady=5)

        # Botones para editar/eliminar evaluación seleccionada
        tb.Button(form, text="Editar evaluación seleccionada", bootstyle="info",
                  command=self.editar_eval_popup).pack(fill="x", pady=2)
        tb.Button(form, text="Eliminar evaluación seleccionada", bootstyle="danger",
                  command=self.eliminar_evaluacion).pack(fill="x", pady=2)

        listado = tb.Labelframe(frame, text="Evaluaciones", padding=10)
        listado.pack(side="left", fill="both", expand=True, padx=10)

        self.tree_eval = tb.Treeview(listado,
            columns=("id","mascota","duenio","calif"),
            show="headings", height=15)

        for col in ("id","mascota","duenio","calif"):
            self.tree_eval.heading(col, text=col.capitalize())
            self.tree_eval.column(col, anchor="center", width=150)

        self.tree_eval.pack(fill="both", expand=True)

        self.cargar_evaluaciones()

    def cargar_mascotas_menu(self):
        # Rellenar OptionMenu con "id - nombre (dueño)"
        menu = self.mascota_menu["menu"]
        menu.delete(0, "end")

        rows = db_query("""
            SELECT m.id, m.nombre, d.nombre
            FROM mascotas m
            LEFT JOIN duenos d ON m.duenio_id = d.id
        """, fetch=True)

        opciones = []
        for r in rows:
            label = f"{r[0]} - {r[1]} ({r[2] if r[2] else 'Desconocido'})"
            opciones.append(label)
            menu.add_command(label=label, command=lambda v=label: self.mascota_var.set(v))

        if opciones:
            self.mascota_var.set(opciones[0])
        else:
            self.mascota_var.set("")

    def guardar_eval(self):
        # Obtener ID desde el menú desplegable
        if not self.mascota_var.get():
            messagebox.showerror("Error", "Seleccione una mascota válida")
            return

        try:
            mascota_id = int(self.mascota_var.get().split(" - ")[0])
        except:
            messagebox.showerror("Error", "Seleccione una mascota válida")
            return

        datos = db_query("""
            SELECT m.nombre, d.nombre
            FROM mascotas m
            LEFT JOIN duenos d ON m.duenio_id = d.id
            WHERE m.id=?
        """, (mascota_id,), fetch=True)

        if not datos:
            messagebox.showerror("Error", "Mascota no encontrada")
            return

        mascota_nombre, duenio_nombre = datos[0]

        # Calificación
        score = self.q1.get() + self.q2.get() + self.q3.get() + self.q4.get()
        score += {"Bueno": 2, "Regular": 1, "Malo": 0}[self.q5.get()]
        score += {"Limpio": 2, "Moderado": 1, "Sucio": 0}[self.q6.get()]
        cal = round(score / 10 * 10, 1)

        detalle = (
            f"Q1:{self.q1.get()}, Q2:{self.q2.get()}, Q3:{self.q3.get()}, "
            f"Q4:{self.q4.get()}, Salud:{self.q5.get()}, Higiene:{self.q6.get()}"
        )

        db_query("""
            INSERT INTO evaluaciones(mascota_id, duenio_nombre, mascota_nombre, calificacion, detalle)
            VALUES (?, ?, ?, ?, ?)
        """, (mascota_id, duenio_nombre, mascota_nombre, cal, detalle))

        messagebox.showinfo("Éxito", f"Evaluación guardada.\nCalificación: {cal}/10")

        self.cargar_evaluaciones()
        self.cargar_reporte()

    def cargar_evaluaciones(self):
        for r in self.tree_eval.get_children():
            self.tree_eval.delete(r)

        rows = db_query("""
            SELECT id, mascota_nombre, duenio_nombre, calificacion FROM evaluaciones
            ORDER BY id DESC
        """, fetch=True)

        for r in rows:
            self.tree_eval.insert("", "end", values=r)

    def editar_eval_popup(self):
        sel = self.tree_eval.focus()
        if not sel:
            messagebox.showerror("Error", "Seleccione una evaluación del listado para editar")
            return
        row = self.tree_eval.item(sel)["values"]
        eval_id = row[0]

        datos = db_query("SELECT mascota_id, detalle FROM evaluaciones WHERE id=?", (eval_id,), fetch=True)
        if not datos:
            messagebox.showerror("Error", "Evaluación no encontrada")
            return
        mascota_id, detalle = datos[0]

        # parse detalle for fields if possible (format we used)
        # default values
        q1 = 0; q2 = 0; q3 = 1; q4 = 1; q5 = "Bueno"; q6 = "Limpio"
        try:
            parts = detalle.split(",")
            for p in parts:
                if p.strip().startswith("Q1:"):
                    q1 = int(p.split(":")[1])
                if p.strip().startswith("Q2:"):
                    q2 = int(p.split(":")[1])
                if p.strip().startswith("Q3:"):
                    q3 = int(p.split(":")[1])
                if p.strip().startswith("Q4:"):
                    q4 = int(p.split(":")[1])
                if "Salud:" in p:
                    q5 = p.split("Salud:")[1].strip()
                if "Higiene:" in p:
                    q6 = p.split("Higiene:")[1].strip()
        except:
            pass

        popup = tk.Toplevel()
        popup.title("Editar Evaluación")
        popup.geometry("380x420")
        popup.transient(self.winfo_toplevel())

        # Mascota selector in popup
        tk.Label(popup, text="Mascota:").pack(anchor="w", padx=10, pady=(10,0))
        rows = db_query("SELECT m.id, m.nombre, d.nombre FROM mascotas m LEFT JOIN duenos d ON m.duenio_id = d.id", fetch=True)
        opciones = [f"{r[0]} - {r[1]} ({r[2] if r[2] else 'Desconocido'})" for r in rows]
        masc_var = tk.StringVar()
        if opciones:
            # set the current to match mascota_id
            cur_label = next((o for o in opciones if int(o.split(" - ")[0])==mascota_id), opciones[0])
            masc_var.set(cur_label)
        else:
            masc_var.set("")
        tk.OptionMenu(popup, masc_var, *opciones).pack(fill="x", padx=10, pady=5)

        # pregunta widgets
        q1_var = tk.IntVar(value=q1)
        q2_var = tk.IntVar(value=q2)
        q3_var = tk.IntVar(value=q3)
        q4_var = tk.IntVar(value=q4)
        q5_var = tk.StringVar(value=q5)
        q6_var = tk.StringVar(value=q6)

        tk.Checkbutton(popup, text="Se comporta bien en casa", variable=q1_var).pack(anchor="w", padx=10)
        tk.Checkbutton(popup, text="Acepta caricias", variable=q2_var).pack(anchor="w", padx=10)

        tk.Label(popup, text="Nivel de actividad:").pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Bajo", variable=q3_var, value=1).pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Alto", variable=q3_var, value=2).pack(anchor="w", padx=10)

        tk.Label(popup, text="Sociabilidad:").pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Reservado", variable=q4_var, value=1).pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Sociable", variable=q4_var, value=2).pack(anchor="w", padx=10)

        tk.Label(popup, text="Estado de salud:").pack(anchor="w", padx=10)
        tb.Combobox(popup, textvariable=q5_var, values=["Bueno","Regular","Malo"]).pack(fill="x", padx=10)

        tk.Label(popup, text="Higiene:").pack(anchor="w", padx=10)
        tb.Combobox(popup, textvariable=q6_var, values=["Limpio","Moderado","Sucio"]).pack(fill="x", padx=10)

        def guardar():
            # get selected mascota id
            if not masc_var.get():
                messagebox.showerror("Error", "Seleccione una mascota")
                return
            try:
                nuevo_mascota_id = int(masc_var.get().split(" - ")[0])
            except:
                messagebox.showerror("Error", "Mascota inválida")
                return

            # recalc calificacion
            score = q1_var.get() + q2_var.get() + q3_var.get() + q4_var.get()
            score += {"Bueno":2,"Regular":1,"Malo":0}[q5_var.get()]
            score += {"Limpio":2,"Moderado":1,"Sucio":0}[q6_var.get()]
            cal = round(score / 10 * 10, 1)

            detalle_nuevo = f"Q1:{q1_var.get()}, Q2:{q2_var.get()}, Q3:{q3_var.get()}, Q4:{q4_var.get()}, Salud:{q5_var.get()}, Higiene:{q6_var.get()}"

            # get duenio_nombre from mascotas table
            duenio_row = db_query("SELECT d.nombre FROM mascotas m LEFT JOIN duenos d ON m.duenio_id=d.id WHERE m.id=?", (nuevo_mascota_id,), fetch=True)
            duenio_nombre_nuevo = duenio_row[0][0] if duenio_row else "Desconocido"

            db_query("UPDATE evaluaciones SET mascota_id=?, duenio_nombre=?, mascota_nombre=?, calificacion=?, detalle=? WHERE id=?",
                     (nuevo_mascota_id, duenio_nombre_nuevo,
                      db_query("SELECT nombre FROM mascotas WHERE id=?", (nuevo_mascota_id,), fetch=True)[0][0],
                      cal, detalle_nuevo, eval_id))
            messagebox.showinfo("OK", "Evaluación actualizada")
            popup.destroy()
            self.cargar_evaluaciones()
            self.cargar_reporte()

        tk.Button(popup, text="Guardar", command=guardar).pack(pady=10)

    def eliminar_evaluacion(self):
        sel = self.tree_eval.focus()
        if not sel:
            messagebox.showerror("Error", "Seleccione una evaluación para eliminar")
            return
        row = self.tree_eval.item(sel)["values"]
        eval_id = row[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar evaluación #{eval_id} para {row[1]}?"):
            db_query("DELETE FROM evaluaciones WHERE id=?", (eval_id,))
            messagebox.showinfo("Eliminada", "Evaluación eliminada")
            self.cargar_evaluaciones()
            self.cargar_reporte()

    # --------------------------------------------------------------------
    # PANEL REPORTE
    # --------------------------------------------------------------------
    def build_reporte_tab(self):
        frame = tb.Frame(self.tab_reporte)
        frame.pack(fill="both", expand=True)

        tb.Label(frame, text="📊 Reporte Completo de Mascotas", font=("Segoe UI", 15, "bold")).pack(pady=10)

        self.tree_reporte = tb.Treeview(frame,
            columns=("mascota","dueno","detalle","calificacion"),
            show="headings", height=20)

        for c in ("mascota","dueno","detalle","calificacion"):
            self.tree_reporte.heading(c, text=c.capitalize())
            self.tree_reporte.column(c, anchor="center", width=220)

        self.tree_reporte.pack(fill="both", expand=True)

        self.cargar_reporte()

    def cargar_reporte(self):
        for r in self.tree_reporte.get_children():
            self.tree_reporte.delete(r)

        rows = db_query("""
            SELECT mascota_nombre, duenio_nombre, detalle, calificacion
            FROM evaluaciones
            ORDER BY id DESC
        """, fetch=True)

        for r in rows:
            self.tree_reporte.insert("", "end", values=r)

# -------------------------------------------------------------------------
# EJECUCIÓN DEL SISTEMA 
# -------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    style = Style("darkly")
    root = style.master
    App(root)
    root.mainloop()
