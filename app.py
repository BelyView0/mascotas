#!/usr/bin/env python3
"""Sistema de opinión de mascotas - Interfaz de Usuario (Tkinter + SQLite)
Instrucciones: ejecutar `python app.py` (requiere Python 3). Crea una base de datos local 'mascotas.db'.
Autor: Generado por ChatGPT (ejemplo educativo)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

DB = "mascotas.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS duenos (' 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' 'nombre TEXT, ' 'correo TEXT, ' 'genero TEXT, ' 'edad INTEGER, ' 'peso REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS mascotas (' 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' 'nombre TEXT, ' 'especie TEXT, ' 'raza TEXT, ' 'edad INTEGER, ' 'peso REAL, ' 'color TEXT, ' 'duenio_id INTEGER, ' 'FOREIGN KEY(duenio_id) REFERENCES duenos(id))')
    c.execute('CREATE TABLE IF NOT EXISTS evaluaciones (' 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' 'mascota_id INTEGER, ' 'duenio_nombre TEXT, ' 'mascota_nombre TEXT, ' 'calificacion REAL, ' 'detalle TEXT)')
    conn.commit()
    conn.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Sistema de opinión de mascotas - Demo')
        self.geometry('900x600')
        self.create_widgets()

    def create_widgets(self):
        tabControl = ttk.Notebook(self)

        self.tab_duenos = ttk.Frame(tabControl)
        self.tab_mascotas = ttk.Frame(tabControl)
        self.tab_evaluacion = ttk.Frame(tabControl)

        tabControl.add(self.tab_duenos, text='Dueñ@s')
        tabControl.add(self.tab_mascotas, text='Mascotas')
        tabControl.add(self.tab_evaluacion, text='Evaluación')
        tabControl.pack(expand=1, fill='both')

        self.build_duenos_tab()
        self.build_mascotas_tab()
        self.build_evaluacion_tab()

    def build_duenos_tab(self):
        frame = self.tab_duenos
        left = ttk.Frame(frame, padding=10)
        left.pack(side='left', fill='y')

        ttk.Label(left, text='Formulario Dueñ@').pack(anchor='w')
        self.dueno_nombre = tk.StringVar()
        self.dueno_correo = tk.StringVar()
        self.dueno_genero = tk.StringVar()
        self.dueno_edad = tk.IntVar(value=18)
        self.dueno_peso = tk.DoubleVar(value=60.0)

        ttk.Label(left, text='Nombre:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.dueno_nombre).pack(fill='x')
        ttk.Label(left, text='Correo:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.dueno_correo).pack(fill='x')
        ttk.Label(left, text='Género:').pack(anchor='w')
        ttk.Combobox(left, textvariable=self.dueno_genero, values=['Masculino','Femenino','Otro']).pack(fill='x')
        ttk.Label(left, text='Edad:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.dueno_edad).pack(fill='x')
        ttk.Label(left, text='Peso (kg):').pack(anchor='w')
        ttk.Entry(left, textvariable=self.dueno_peso).pack(fill='x')

        ttk.Button(left, text='Agregar Dueñ@', command=self.agregar_dueno).pack(fill='x', pady=5)
        ttk.Button(left, text='Actualizar Dueñ@', command=self.actualizar_dueno).pack(fill='x', pady=5)
        ttk.Button(left, text='Eliminar Dueñ@', command=self.eliminar_dueno).pack(fill='x', pady=5)
        ttk.Button(left, text='Refrescar Listado', command=self.cargar_lista_duenos).pack(fill='x', pady=5)

        right = ttk.Frame(frame, padding=10)
        right.pack(side='left', fill='both', expand=True)

        ttk.Label(right, text='Listado de Dueñ@s (con nombre de mascota)').pack(anchor='w')
        self.tree_duenos = ttk.Treeview(right, columns=('id','nombre','correo','genero','edad','peso','mascotas'), show='headings')
        for col in ('id','nombre','correo','genero','edad','peso','mascotas'):
            self.tree_duenos.heading(col, text=col.capitalize())
            self.tree_duenos.column(col, width=100)
        self.tree_duenos.pack(fill='both', expand=True)
        self.cargar_lista_duenos()

    def agregar_dueno(self):
        nombre = self.dueno_nombre.get().strip()
        correo = self.dueno_correo.get().strip()
        genero = self.dueno_genero.get().strip()
        try:
            edad = int(self.dueno_edad.get())
            peso = float(self.dueno_peso.get())
        except:
            messagebox.showerror('Error', 'Edad y peso deben ser numéricos')
            return
        if not nombre:
            messagebox.showerror('Error', 'Nombre requerido')
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('INSERT INTO duenos (nombre,correo,genero,edad,peso) VALUES (?,?,?,?,?)', (nombre,correo,genero,edad,peso))
        conn.commit(); conn.close()
        messagebox.showinfo('Éxito', 'Dueñ@ agregado')
        self.cargar_lista_duenos()

    def cargar_lista_duenos(self):
        for i in self.tree_duenos.get_children(): self.tree_duenos.delete(i)
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('SELECT d.id,d.nombre,d.correo,d.genero,d.edad,d.peso, ' 'GROUP_CONCAT(m.nombre, ", ") as mascotas ' 'FROM duenos d LEFT JOIN mascotas m ON d.id=m.duenio_id ' 'GROUP BY d.id')
        for row in c.fetchall():
            self.tree_duenos.insert('', 'end', values=row)
        conn.close()

    def actualizar_dueno(self):
        sel = self.tree_duenos.focus()
        if not sel:
            messagebox.showerror('Error', 'Seleccione un dueñ@ del listado para actualizar')
            return
        values = self.tree_duenos.item(sel,'values')
        idd = values[0]
        nuevo = simpledialog.askstring('Actualizar', 'Nuevo nombre:', initialvalue=values[1])
        if nuevo:
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute('UPDATE duenos SET nombre=? WHERE id=?', (nuevo,idd))
            conn.commit(); conn.close()
            self.cargar_lista_duenos()

    def eliminar_dueno(self):
        sel = self.tree_duenos.focus()
        if not sel:
            messagebox.showerror('Error', 'Seleccione un dueñ@ del listado para eliminar')
            return
        values = self.tree_duenos.item(sel,'values')
        idd = values[0]
        if messagebox.askyesno('Confirmar', f'Eliminar dueñ@ {values[1]}?'):
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute('DELETE FROM duenos WHERE id=?', (idd,))
            conn.commit(); conn.close()
            self.cargar_lista_duenos()

    def build_mascotas_tab(self):
        frame = self.tab_mascotas
        left = ttk.Frame(frame, padding=10)
        left.pack(side='left', fill='y')

        ttk.Label(left, text='Formulario Mascota').pack(anchor='w')
        self.m_nombre = tk.StringVar()
        self.m_especie = tk.StringVar()
        self.m_raza = tk.StringVar()
        self.m_edad = tk.IntVar(value=1)
        self.m_peso = tk.DoubleVar(value=1.0)
        self.m_color = tk.StringVar()
        self.m_duenio = tk.IntVar()

        ttk.Label(left, text='Nombre:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_nombre).pack(fill='x')
        ttk.Label(left, text='Especie:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_especie).pack(fill='x')
        ttk.Label(left, text='Raza:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_raza).pack(fill='x')
        ttk.Label(left, text='Edad:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_edad).pack(fill='x')
        ttk.Label(left, text='Peso (kg):').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_peso).pack(fill='x')
        ttk.Label(left, text='Color:').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_color).pack(fill='x')
        ttk.Label(left, text='Dueñ@ (ID):').pack(anchor='w')
        ttk.Entry(left, textvariable=self.m_duenio).pack(fill='x')

        ttk.Button(left, text='Agregar Mascota', command=self.agregar_mascota).pack(fill='x', pady=5)
        ttk.Button(left, text='Actualizar Mascota', command=self.actualizar_mascota).pack(fill='x', pady=5)
        ttk.Button(left, text='Eliminar Mascota', command=self.eliminar_mascota).pack(fill='x', pady=5)
        ttk.Button(left, text='Reporte de Mascotas', command=self.reporte_mascotas).pack(fill='x', pady=5)

        right = ttk.Frame(frame, padding=10)
        right.pack(side='left', fill='both', expand=True)
        ttk.Label(right, text='Listado de Mascotas').pack(anchor='w')
        self.tree_mascotas = ttk.Treeview(right, columns=('id','nombre','especie','raza','edad','peso','color','duenio_id'), show='headings')
        for col in ('id','nombre','especie','raza','edad','peso','color','duenio_id'):
            self.tree_mascotas.heading(col, text=col.capitalize())
            self.tree_mascotas.column(col, width=100)
        self.tree_mascotas.pack(fill='both', expand=True)
        self.cargar_lista_mascotas()

    def agregar_mascota(self):
        nombre = self.m_nombre.get().strip()
        especie = self.m_especie.get().strip()
        raza = self.m_raza.get().strip()
        try:
            edad = int(self.m_edad.get()); peso = float(self.m_peso.get()); duenio_id = int(self.m_duenio.get())
        except:
            messagebox.showerror('Error', 'Edad, peso y dueñ@ (ID) deben ser numéricos')
            return
        if not nombre:
            messagebox.showerror('Error', 'Nombre requerido')
            return
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('INSERT INTO mascotas (nombre,especie,raza,edad,peso,color,duenio_id) VALUES (?,?,?,?,?,?,?)',
                  (nombre,especie,raza,edad,peso,self.m_color.get().strip(),duenio_id))
        conn.commit(); conn.close()
        messagebox.showinfo('Éxito', 'Mascota agregada')
        self.cargar_lista_mascotas()

    def cargar_lista_mascotas(self):
        for i in self.tree_mascotas.get_children(): self.tree_mascotas.delete(i)
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('SELECT id,nombre,especie,raza,edad,peso,color,duenio_id FROM mascotas')
        for row in c.fetchall():
            self.tree_mascotas.insert('', 'end', values=row)
        conn.close()

    def actualizar_mascota(self):
        sel = self.tree_mascotas.focus()
        if not sel:
            messagebox.showerror('Error', 'Seleccione una mascota para actualizar')
            return
        values = self.tree_mascotas.item(sel,'values')
        idd = values[0]
        nuevo = simpledialog.askstring('Actualizar', 'Nuevo nombre:', initialvalue=values[1])
        if nuevo:
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute('UPDATE mascotas SET nombre=? WHERE id=?', (nuevo,idd))
            conn.commit(); conn.close()
            self.cargar_lista_mascotas()

    def eliminar_mascota(self):
        sel = self.tree_mascotas.focus()
        if not sel:
            messagebox.showerror('Error', 'Seleccione una mascota para eliminar')
            return
        values = self.tree_mascotas.item(sel,'values')
        idd = values[0]
        if messagebox.askyesno('Confirmar', f'Eliminar mascota {values[1]}?'):
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute('DELETE FROM mascotas WHERE id=?', (idd,))
            conn.commit(); conn.close()
            self.cargar_lista_mascotas()

    def reporte_mascotas(self):
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('SELECT m.id,m.nombre,m.especie,m.raza,m.edad,m.peso,m.color, d.nombre as duenio FROM mascotas m LEFT JOIN duenos d ON m.duenio_id=d.id')
        rows = c.fetchall(); conn.close()
        s = 'Reporte de mascotas:\n\n'
        for r in rows:
            s += f'ID:{r[0]} Nombre:{r[1]} Especie:{r[2]} Raza:{r[3]} Edad:{r[4]} Peso:{r[5]} Color:{r[6]} Dueñ@:{r[7]}\n'
        messagebox.showinfo('Reporte', s[:2000])

    def build_evaluacion_tab(self):
        frame = self.tab_evaluacion
        left = ttk.Frame(frame, padding=10)
        left.pack(side='left', fill='y')

        ttk.Label(left, text='Evaluación de Mascota').pack(anchor='w')
        self.q1 = tk.IntVar()
        self.q2 = tk.IntVar()
        ttk.Checkbutton(left, text='Pregunta 1: Se comporta bien en casa', variable=self.q1).pack(anchor='w')
        ttk.Checkbutton(left, text='Pregunta 2: Acepta caricias', variable=self.q2).pack(anchor='w')
        self.q3 = tk.IntVar(value=1)
        ttk.Label(left, text='Pregunta 3: Nivel de actividad').pack(anchor='w')
        ttk.Radiobutton(left, text='Bajo', variable=self.q3, value=1).pack(anchor='w')
        ttk.Radiobutton(left, text='Alto', variable=self.q3, value=2).pack(anchor='w')
        self.q4 = tk.IntVar(value=1)
        ttk.Label(left, text='Pregunta 4: Sociabilidad').pack(anchor='w')
        ttk.Radiobutton(left, text='Reservado', variable=self.q4, value=1).pack(anchor='w')
        ttk.Radiobutton(left, text='Sociable', variable=self.q4, value=2).pack(anchor='w')
        ttk.Label(left, text='Pregunta 5: Estado de salud').pack(anchor='w')
        self.q5 = tk.StringVar(value='Bueno')
        ttk.Combobox(left, textvariable=self.q5, values=['Bueno','Regular','Malo']).pack(fill='x')
        ttk.Label(left, text='Pregunta 6: Higiene').pack(anchor='w')
        self.q6 = tk.StringVar(value='Limpio')
        ttk.Combobox(left, textvariable=self.q6, values=['Limpio','Moderado','Sucio']).pack(fill='x')

        ttk.Label(left, text='Mascota ID a evaluar:').pack(anchor='w')
        self.eval_mascota_id = tk.IntVar(value=1)
        ttk.Entry(left, textvariable=self.eval_mascota_id).pack(fill='x', pady=3)

        ttk.Button(left, text='Calcular y Guardar Evaluación', command=self.calcular_evaluacion).pack(fill='x', pady=5)
        ttk.Button(left, text='Reporte Evaluaciones', command=self.reporte_evaluaciones).pack(fill='x', pady=5)

        right = ttk.Frame(frame, padding=10)
        right.pack(side='left', fill='both', expand=True)
        ttk.Label(right, text='Últimas evaluaciones').pack(anchor='w')
        self.tree_eval = ttk.Treeview(right, columns=('id','mascota','duenio','calificacion'), show='headings')
        for col in ('id','mascota','duenio','calificacion'):
            self.tree_eval.heading(col, text=col.capitalize())
            self.tree_eval.column(col, width=120)
        self.tree_eval.pack(fill='both', expand=True)
        self.cargar_evaluaciones()

    def calcular_evaluacion(self):
        score = 0
        score += int(self.q1.get())
        score += int(self.q2.get())
        score += int(self.q3.get())
        score += int(self.q4.get())
        score += {'Bueno':2,'Regular':1,'Malo':0}.get(self.q5.get(),0)
        score += {'Limpio':2,'Moderado':1,'Sucio':0}.get(self.q6.get(),0)
        cal = round((score / 10.0) * 10,1)
        try:
            mascota_id = int(self.eval_mascota_id.get())
        except:
            messagebox.showerror('Error', 'ID inválido')
            return
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('SELECT nombre, duenio_id FROM mascotas WHERE id=?', (mascota_id,))
        row = c.fetchone()
        if not row:
            messagebox.showerror('Error', 'Mascota no encontrada')
            conn.close(); return
        nombre_mascota = row[0]
        duenio_id = row[1]
        c.execute('SELECT nombre FROM duenos WHERE id=?', (duenio_id,))
        duenio = c.fetchone()
        duenio_nombre = duenio[0] if duenio else 'Desconocido'
        detalle = f'q1:{self.q1.get()},q2:{self.q2.get()},q3:{self.q3.get()},q4:{self.q4.get()},q5:{self.q5.get()},q6:{self.q6.get()}'
        c.execute('INSERT INTO evaluaciones (mascota_id, duenio_nombre, mascota_nombre, calificacion, detalle) VALUES (?,?,?,?,?)',
                  (mascota_id, duenio_nombre, nombre_mascota, cal, detalle))
        conn.commit(); conn.close()
        messagebox.showinfo('Evaluación guardada', f'Calificación: {cal} /10 para {nombre_mascota}')
        self.cargar_evaluaciones()

    def cargar_evaluaciones(self):
        for i in self.tree_eval.get_children(): self.tree_eval.delete(i)
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('SELECT id, mascota_nombre, duenio_nombre, calificacion FROM evaluaciones ORDER BY id DESC LIMIT 50')
        for row in c.fetchall():
            self.tree_eval.insert('', 'end', values=row)
        conn.close()

    def reporte_evaluaciones(self):
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute('SELECT mascota_nombre, calificacion, duenio_nombre FROM evaluaciones ORDER BY id DESC')
        rows = c.fetchall(); conn.close()
        s = 'Reporte de evaluaciones:\n\n'
        for r in rows:
            s += f'Mascota:{r[0]} Calificación:{r[1]} Dueñ@:{r[2]}\n'
        messagebox.showinfo('Reporte Evaluaciones', s[:2000])

if __name__ == '__main__':
    init_db()
    app = App()
    app.mainloop()