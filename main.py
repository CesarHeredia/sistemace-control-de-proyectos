# pyrefly: ignore [missing-import]
import customtkinter as ctk
import sqlite3
import re
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image

# Configuración básica de customtkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # Configurar ventana principal
        self.title("Sistema de Notas")
        self.geometry("1200x750")
        self.configure(fg_color="#F3F4F6") # Fondo general claro
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#0B0F19")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Sistema de Notas", font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 0), sticky="w")
        
        self.subtitle_label = ctk.CTkLabel(self.sidebar_frame, text="Gestión Educativa", font=ctk.CTkFont(size=13), text_color="#A0AEC0")
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 40), sticky="w")

        # Opciones del Menú
        self.btn_estudiantes = ctk.CTkButton(self.sidebar_frame, text="👥  Estudiantes", fg_color="#374151", text_color="white", anchor="w", height=45, font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, command=self.show_student_list)
        self.btn_estudiantes.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_calificaciones = ctk.CTkButton(self.sidebar_frame, text="📖  Calificaciones", fg_color="transparent", text_color="#A0AEC0", anchor="w", height=45, hover_color="#1F2937", font=ctk.CTkFont(size=14))
        self.btn_calificaciones.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📄  Reportes", fg_color="transparent", text_color="#A0AEC0", anchor="w", height=45, hover_color="#1F2937", font=ctk.CTkFont(size=14))
        self.btn_reportes.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.btn_configuracion = ctk.CTkButton(self.sidebar_frame, text="⚙️  Configuración", fg_color="transparent", text_color="#A0AEC0", anchor="w", height=45, hover_color="#1F2937", font=ctk.CTkFont(size=14))
        self.btn_configuracion.grid(row=5, column=0, padx=15, pady=5, sticky="nwe")

        # Footer Sidebar
        self.footer_label1 = ctk.CTkLabel(self.sidebar_frame, text="Servicio Comunitario", font=ctk.CTkFont(size=12), text_color="#A0AEC0")
        self.footer_label1.grid(row=6, column=0, padx=20, pady=(0, 0), sticky="w")
        self.footer_label2 = ctk.CTkLabel(self.sidebar_frame, text="© 2026", font=ctk.CTkFont(size=12), text_color="#A0AEC0")
        self.footer_label2.grid(row=7, column=0, padx=20, pady=(0, 30), sticky="w")

        # --- Contenedor Principal Dinamico ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=40, pady=30, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Cargar vista por defecto
        self.show_student_list()

    def _bind_mouse_scroll(self, scrollable_frame):
        def scroll_up(event):
            if scrollable_frame.winfo_exists():
                try:
                    scrollable_frame._parent_canvas.yview("scroll", -1, "units")
                except:
                    pass
        def scroll_down(event):
            if scrollable_frame.winfo_exists():
                try:
                    scrollable_frame._parent_canvas.yview("scroll", 1, "units")
                except:
                    pass
        self.bind_all("<Button-4>", scroll_up)
        self.bind_all("<Button-5>", scroll_down)

    def validar_datos_estudiante(self, p_nombre, p_apellido, cedula, fecha_nacimiento):
        if not p_nombre.strip():
            messagebox.showerror("Error de Validación", "El Primer Nombre es obligatorio.")
            return False
        if not p_apellido.strip():
            messagebox.showerror("Error de Validación", "El Primer Apellido es obligatorio.")
            return False
        if not cedula.strip():
            messagebox.showerror("Error de Validación", "La Cédula es obligatoria.")
            return False
            
        if not re.match(r'^[VvEeGg]-[0-9]+$', cedula.strip()):
            messagebox.showerror("Error de Validación", "La Cédula debe tener el formato V-12345678 o E-12345678.")
            return False
            
        if fecha_nacimiento.strip():
            try:
                datetime.strptime(fecha_nacimiento.strip(), "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error de Validación", "La Fecha de Nacimiento debe tener el formato dd/mm/aaaa (ej. 15/03/2015) y ser una fecha válida.")
                return False
        else:
            messagebox.showerror("Error de Validación", "La Fecha de Nacimiento es obligatoria.")
            return False
            
        return True

    def eliminar_estudiante(self, student_id):
        confirm = messagebox.askyesno("Confirmar Eliminación", "¿Estás completamente seguro de que deseas eliminar este estudiante y todos sus documentos cargados?")
        if not confirm:
            return

        try:
            conn = sqlite3.connect('notas.db')
            cursor = conn.cursor()
            
            # Obtener rutas de archivos para borrarlos físicamente
            cursor.execute('SELECT ruta_archivo FROM documentos_estudiante WHERE estudiante_id = ?', (student_id,))
            files = cursor.fetchall()
            
            import os
            for (filepath,) in files:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as ex:
                        print(f"No se pudo borrar el archivo {filepath}: {ex}")
            
            # Borrar registros de documentos
            cursor.execute('DELETE FROM documentos_estudiante WHERE estudiante_id = ?', (student_id,))
            
            # Borrar estudiante
            cursor.execute('DELETE FROM estudiantes WHERE id = ?', (student_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Estudiante y todos sus documentos eliminados correctamente.")
            self.show_student_list()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar el estudiante: {e}")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        # Resetear pesos del grid
        self.main_frame.grid_rowconfigure((0,1,2,3), weight=0)

    def show_student_list(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Encabezado (Header)
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.header_frame, text="Gestión de Estudiantes", font=ctk.CTkFont(size=26, weight="bold"), text_color="#1A202C")
        self.title_label.grid(row=0, column=0, sticky="w")
        self.subtitle_main_label = ctk.CTkLabel(self.header_frame, text="Administra los datos de los estudiantes", font=ctk.CTkFont(size=15), text_color="#718096")
        self.subtitle_main_label.grid(row=1, column=0, sticky="w")

        self.btn_nuevo = ctk.CTkButton(self.header_frame, text="+ Nuevo Estudiante", fg_color="#0B0F19", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, hover_color="#1F2937", command=self.show_new_student_form)
        self.btn_nuevo.grid(row=0, column=1, rowspan=2, sticky="e")

        # Buscador y Filtro
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10, height=65, border_width=1, border_color="#E2E8F0")
        self.search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="🔍 Buscar estudiante...", border_width=0, fg_color="#F8FAFC", height=45, corner_radius=8, font=ctk.CTkFont(size=14))
        self.search_entry.grid(row=0, column=0, padx=15, pady=10, sticky="ew")

        self.filter_option = ctk.CTkOptionMenu(self.search_frame, values=["Todos los niveles", "Primaria", "Bachillerato", "Preescolar"], fg_color="#F8FAFC", text_color="#1A202C", button_color="#F8FAFC", button_hover_color="#E2E8F0", dropdown_hover_color="#E2E8F0", dropdown_text_color="#1A202C", dropdown_fg_color="white", height=45, corner_radius=8, font=ctk.CTkFont(size=14))
        self.filter_option.grid(row=0, column=1, padx=15, pady=10)

        # Tabla Principal
        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        self.table_frame.grid(row=2, column=0, sticky="nsew")
        self.table_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # Encabezados de la Tabla
        headers = ["ID", "Cédula", "Nombre", "Acciones"]
        for i, h in enumerate(headers):
            # Usando un frame gris claro para cada encabezado de columna
            header_bg = ctk.CTkFrame(self.table_frame, fg_color="#F3F4F6", corner_radius=0, height=45)
            header_bg.grid(row=0, column=i, sticky="nsew")
            header_bg.grid_propagate(False)
            lbl = ctk.CTkLabel(header_bg, text=h, font=ctk.CTkFont(weight="bold", size=14), text_color="#4A5568")
            lbl.place(relx=0.5 if i==3 else 0.15, rely=0.5, anchor="center" if i==3 else "w")

        self.cargar_estudiantes()

    def cargar_estudiantes(self):
        # Limpiar la tabla antes de recargar, manteniendo solo la primera fila (los encabezados)
        if not hasattr(self, 'table_frame') or not self.table_frame.winfo_exists():
            return
            
        for widget in self.table_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()
                
        try:
            conn = sqlite3.connect('notas.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, cedula, primer_nombre, primer_apellido FROM estudiantes')
            estudiantes = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("Error al cargar:", e)
            estudiantes = []

        for row, data in enumerate(estudiantes, start=1):
            nombre_completo = f"{data[2]} {data[3]}"
            ctk.CTkLabel(self.table_frame, text=str(data[0]), text_color="#1A202C", anchor="w", font=ctk.CTkFont(size=13)).grid(row=row, column=0, padx=15, pady=15, sticky="ew")
            ctk.CTkLabel(self.table_frame, text=data[1], text_color="#1A202C", anchor="w", font=ctk.CTkFont(size=13)).grid(row=row, column=1, padx=15, pady=15, sticky="ew")
            ctk.CTkLabel(self.table_frame, text=nombre_completo, text_color="#1A202C", anchor="w", font=ctk.CTkFont(size=13)).grid(row=row, column=2, padx=15, pady=15, sticky="ew")
            
            # Botones Acciones
            acciones_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            acciones_frame.grid(row=row, column=3, padx=15, pady=15)
            
            btn_view = ctk.CTkButton(acciones_frame, text="👁️", width=32, height=32, fg_color="transparent", text_color="#3182CE", hover_color="#EBF8FF", font=ctk.CTkFont(size=16), command=lambda s_id=data[0]: self.show_student_details(s_id))
            btn_view.pack(side="left", padx=5)
            
            # Línea separadora horizontal para cada fila
            if row < len(estudiantes):
                sep = ctk.CTkFrame(self.table_frame, height=1, fg_color="#EDF2F7")
                sep.grid(row=row, column=0, columnspan=4, sticky="sew", padx=10)

    def show_student_details(self, student_id):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        main_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_scroll.grid(row=0, column=0, sticky="nsew")
        self._bind_mouse_scroll(main_scroll)

        # Botón Volver
        header_frame_back = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_frame_back.pack(fill="x", padx=40, pady=(30, 0))
        btn_volver = ctk.CTkButton(header_frame_back, text="← Volver a la lista", fg_color="transparent", text_color="#4A5568", font=ctk.CTkFont(weight="bold", size=14), width=80, hover_color="#E2E8F0", command=self.show_student_list)
        btn_volver.pack(side="left")

        try:
            conn = sqlite3.connect('notas.db')
            cursor = conn.cursor()
            cursor.execute('SELECT primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, cedula, fecha_nacimiento FROM estudiantes WHERE id = ?', (student_id,))
            estudiante = cursor.fetchone()
            
            cursor.execute('SELECT ano_bachillerato, ruta_archivo FROM documentos_estudiante WHERE estudiante_id = ?', (student_id,))
            documentos = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar el estudiante: {e}")
            self.show_student_list()
            return

        if not estudiante:
            messagebox.showerror("Error", "Estudiante no encontrado.")
            self.show_student_list()
            return

        p_nom, s_nom, p_ape, s_ape, ced, f_nac = estudiante

        header_lbl = ctk.CTkLabel(main_scroll, text="Datos del Estudiante", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1A202C")
        header_lbl.pack(anchor="w", padx=40, pady=(10, 0))

        sub_lbl = ctk.CTkLabel(main_scroll, text="Información registrada", font=ctk.CTkFont(size=14), text_color="#718096")
        sub_lbl.pack(anchor="w", padx=40, pady=(5, 20))

        # Card 1: Datos Personales
        card_datos = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        card_datos.pack(fill="x", padx=40, pady=(0, 20))
        card_datos.grid_columnconfigure((0, 1), weight=1)

        lbl_tit_datos = ctk.CTkLabel(card_datos, text="Datos Personales", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C")
        lbl_tit_datos.grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(25, 20))

        def create_form_entry(parent, row, col, label_text, value_text):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=col, sticky="ew", padx=30, pady=(0, 15))
            lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), text_color="#718096")
            lbl.pack(anchor="w", pady=(0, 5))
            entry = ctk.CTkEntry(frame, height=40, fg_color="#F3F4F6", border_width=0, text_color="#1A202C", font=ctk.CTkFont(size=14))
            entry.pack(fill="x")
            entry.insert(0, value_text if value_text else "")
            entry.configure(state="readonly")

        create_form_entry(card_datos, 1, 0, "Nombre", p_nom)
        create_form_entry(card_datos, 1, 1, "Apellido", p_ape)
        create_form_entry(card_datos, 2, 0, "Cédula", ced)
        create_form_entry(card_datos, 2, 1, "Fecha de Nacimiento", f_nac)

        # Card 2: Bachillerato
        card_bach = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        card_bach.pack(fill="x", padx=40, pady=(0, 20))
        card_bach.grid_columnconfigure(0, weight=1)

        lbl_tit_bach = ctk.CTkLabel(card_bach, text="Bachillerato", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C")
        lbl_tit_bach.pack(anchor="w", padx=30, pady=(25, 15))

        anos = ["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"]
        for ano in anos:
            row_frame = ctk.CTkFrame(card_bach, fg_color="transparent", border_width=1, border_color="#E2E8F0", corner_radius=8)
            row_frame.pack(fill="x", padx=30, pady=(0, 10))
            
            lbl_ano = ctk.CTkLabel(row_frame, text=ano, font=ctk.CTkFont(size=14), text_color="#1A202C")
            lbl_ano.pack(side="left", padx=(15, 0), pady=12)
            
            if ano in documentos:
                def open_file(path=documentos[ano]):
                    import os, sys, subprocess
                    if sys.platform == "win32":
                        os.startfile(path)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", path])
                    else:
                        subprocess.Popen(["xdg-open", path])

                btn_ver = ctk.CTkButton(row_frame, text="Abrir Archivo", fg_color="#3182CE", hover_color="#2B6CB0", text_color="white", width=100, height=28, font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6, command=open_file)
                btn_ver.pack(side="right", padx=15, pady=10)

        # Botones de Acción (Editar y Eliminar)
        btn_action_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        btn_action_frame.pack(fill="x", padx=40, pady=(0, 40))
        
        btn_eliminar = ctk.CTkButton(btn_action_frame, text="Eliminar Estudiante", fg_color="#E53E3E", hover_color="#C53030", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, command=lambda: self.eliminar_estudiante(student_id))
        btn_eliminar.pack(side="left", padx=(0, 10))
        
        btn_editar = ctk.CTkButton(btn_action_frame, text="Editar Estudiante", fg_color="#3182CE", hover_color="#2B6CB0", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, command=lambda: self.show_edit_student_form(student_id))
        btn_editar.pack(side="right")

    def show_edit_student_form(self, student_id):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.archivos_seleccionados = {}
        self.archivos_originales = {}

        try:
            conn = sqlite3.connect('notas.db')
            cursor = conn.cursor()
            cursor.execute('SELECT primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, cedula, fecha_nacimiento FROM estudiantes WHERE id = ?', (student_id,))
            estudiante = cursor.fetchone()
            
            cursor.execute('SELECT ano_bachillerato, ruta_archivo FROM documentos_estudiante WHERE estudiante_id = ?', (student_id,))
            for row in cursor.fetchall():
                self.archivos_originales[row[0]] = row[1]
                self.archivos_seleccionados[row[0]] = row[1]
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar los datos del estudiante: {e}")
            self.show_student_list()
            return

        if not estudiante:
            messagebox.showerror("Error", "Estudiante no encontrado.")
            self.show_student_list()
            return

        p_nom, s_nom, p_ape, s_ape, ced, f_nac = estudiante

        main_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_scroll.grid(row=0, column=0, sticky="nsew")
        self._bind_mouse_scroll(main_scroll)

        # Botón Volver
        header_frame_back = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_frame_back.pack(fill="x", padx=40, pady=(30, 0))
        btn_volver = ctk.CTkButton(header_frame_back, text="← Volver a detalles", fg_color="transparent", text_color="#4A5568", font=ctk.CTkFont(weight="bold", size=14), width=80, hover_color="#E2E8F0", command=lambda: self.show_student_details(student_id))
        btn_volver.pack(side="left")

        header_lbl = ctk.CTkLabel(main_scroll, text="Editar Estudiante", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1A202C")
        header_lbl.pack(anchor="w", padx=40, pady=(10, 0))
        
        sub_lbl = ctk.CTkLabel(main_scroll, text="Modifica los datos del estudiante", font=ctk.CTkFont(size=14), text_color="#718096")
        sub_lbl.pack(anchor="w", padx=40, pady=(5, 20))

        # Main Card Frame (Datos Personales)
        card_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        card_frame.pack(fill="x", padx=40, pady=(0, 30))
        card_frame.grid_columnconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")

        lbl_datos = ctk.CTkLabel(left_frame, text="Datos Personales", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C")
        lbl_datos.pack(anchor="w", pady=(0, 20))

        def create_field(parent, label_text, placeholder, default_val=""):
            lbl = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), text_color="#4A5568")
            lbl.pack(anchor="w", pady=(10, 5))
            entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=40, fg_color="#F8FAFC", border_color="#E2E8F0", text_color="#1A202C")
            entry.pack(fill="x")
            if default_val:
                entry.insert(0, default_val)
            return entry

        self.entry_p_nombre = create_field(left_frame, "Primer Nombre", "Ej: Juan", p_nom)
        self.entry_s_nombre = create_field(left_frame, "Segundo Nombre", "Ej: Carlos", s_nom)
        self.entry_p_apellido = create_field(left_frame, "Primer Apellido", "Ej: Perez", p_ape)
        self.entry_s_apellido = create_field(left_frame, "Segundo Apellido", "Ej: Gomez", s_ape)
        self.entry_cedula = create_field(left_frame, "Cédula", "V-12345678", ced)
        self.entry_fecha = create_field(left_frame, "Fecha de Nacimiento", "dd/mm/aaaa", f_nac)

        # --- Seccion: Nivel Educativo y Grado ---
        nivel_lbl = ctk.CTkLabel(main_scroll, text="Nivel Educativo y Grado", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1A202C")
        nivel_lbl.pack(anchor="w", padx=40, pady=(10, 20))

        def create_accordion(parent, title, options):
            acc_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E2E8F0")
            acc_frame.pack(fill="x", padx=40, pady=(0, 20))

            header_frame = ctk.CTkFrame(acc_frame, fg_color="#F3F4F6", corner_radius=0, height=45, cursor="hand2")
            header_frame.pack(fill="x")
            header_frame.grid_propagate(False)
            
            lbl_title = ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#1A202C", cursor="hand2")
            lbl_title.pack(side="left", padx=15)
            
            lbl_arrow = ctk.CTkLabel(header_frame, text="⌃", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C", cursor="hand2")
            lbl_arrow.pack(side="right", padx=15)

            content_frame = ctk.CTkFrame(acc_frame, fg_color="transparent")
            content_frame.pack(fill="x", pady=(0, 10))

            for opt in options:
                row_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                row_frame.pack(fill="x", padx=15, pady=8)
                
                lbl_opt = ctk.CTkLabel(row_frame, text=opt, font=ctk.CTkFont(size=13), text_color="#4A5568")
                lbl_opt.pack(side="left")
                
                # Label to show the selected file name
                initial_filename = ""
                if opt in self.archivos_originales:
                    import os
                    initial_filename = os.path.basename(self.archivos_originales[opt])
                    if len(initial_filename) > 20:
                        initial_filename = initial_filename[:17] + "..."
                        
                lbl_filename = ctk.CTkLabel(row_frame, text=initial_filename, font=ctk.CTkFont(size=11), text_color="#3182CE")
                lbl_filename.pack(side="right", padx=(10, 0))

                def select_pdf(lbl=lbl_filename, opt_key=opt):
                    filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
                    if filepath:
                        import os
                        filename = os.path.basename(filepath)
                        if len(filename) > 20:
                            filename = filename[:17] + "..."
                        lbl.configure(text=filename)
                        self.archivos_seleccionados[opt_key] = filepath

                btn_archivo = ctk.CTkButton(row_frame, text="↑ Archivo", fg_color="#0B0F19", text_color="white", width=80, height=28, font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6, hover_color="#1F2937", command=select_pdf)
                btn_archivo.pack(side="right")
                
                # Drag and Drop support
                def on_drop(event, lbl=lbl_filename, opt_key=opt):
                    filepath = event.data
                    if filepath:
                        if filepath.startswith('{') and filepath.endswith('}'):
                            filepath = filepath[1:-1]
                        if filepath.lower().endswith('.pdf'):
                            import os
                            filename = os.path.basename(filepath)
                            if len(filename) > 20:
                                filename = filename[:17] + "..."
                            lbl.configure(text=filename)
                            self.archivos_seleccionados[opt_key] = filepath
                        else:
                            messagebox.showerror("Error", "Por favor, selecciona un archivo PDF.")
                            
                row_frame.drop_target_register(DND_FILES)
                row_frame.dnd_bind('<<Drop>>', on_drop)
                btn_archivo.drop_target_register(DND_FILES)
                btn_archivo.dnd_bind('<<Drop>>', on_drop)

            # Estado del acordeón
            acc_frame.is_expanded = True

            def toggle_accordion(event=None):
                if acc_frame.is_expanded:
                    content_frame.pack_forget()
                    lbl_arrow.configure(text="⌄")
                    acc_frame.is_expanded = False
                else:
                    content_frame.pack(fill="x", pady=(0, 10))
                    lbl_arrow.configure(text="⌃")
                    acc_frame.is_expanded = True

            header_frame.bind("<Button-1>", toggle_accordion)
            lbl_title.bind("<Button-1>", toggle_accordion)
            lbl_arrow.bind("<Button-1>", toggle_accordion)

        create_accordion(main_scroll, "Bachillerato", ["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"])

        # Guardar / Acciones Finales
        save_btn_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        save_btn_frame.pack(fill="x", padx=40, pady=(10, 40))
        
        def guardar_cambios():
            p_nom = self.entry_p_nombre.get()
            s_nom = self.entry_s_nombre.get()
            p_ape = self.entry_p_apellido.get()
            s_ape = self.entry_s_apellido.get()
            ced = self.entry_cedula.get()
            f_nac = self.entry_fecha.get()
            
            # Validación robusta
            if not self.validar_datos_estudiante(p_nom, p_ape, ced, f_nac):
                return

            try:
                conn = sqlite3.connect('notas.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE estudiantes 
                    SET primer_nombre = ?, segundo_nombre = ?, primer_apellido = ?, segundo_apellido = ?, cedula = ?, fecha_nacimiento = ?
                    WHERE id = ?
                ''', (p_nom, s_nom, p_ape, s_ape, ced, f_nac, student_id))
                
                # Procesar archivos
                import os, shutil
                os.makedirs('documentos_estudiantes', exist_ok=True)
                
                anos = ["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"]
                for ano in anos:
                    original_path = self.archivos_originales.get(ano)
                    current_path = self.archivos_seleccionados.get(ano)
                    
                    if current_path != original_path:
                        # Si cambió el archivo
                        if original_path and os.path.exists(original_path):
                            try:
                                os.remove(original_path)
                            except Exception as ex:
                                print(f"No se pudo eliminar el archivo original {original_path}: {ex}")
                        
                        if current_path:
                            # Copiar el nuevo archivo
                            ext = os.path.splitext(current_path)[1]
                            nuevo_nombre = f"estudiante_{student_id}_{ano.replace(' ', '_')}{ext}"
                            nueva_ruta = os.path.join('documentos_estudiantes', nuevo_nombre)
                            shutil.copy2(current_path, nueva_ruta)
                            
                            # Actualizar o insertar en BD
                            if original_path:
                                cursor.execute('''
                                    UPDATE documentos_estudiante 
                                    SET ruta_archivo = ? 
                                    WHERE estudiante_id = ? AND ano_bachillerato = ?
                                ''', (nueva_ruta, student_id, ano))
                            else:
                                cursor.execute('''
                                    INSERT INTO documentos_estudiante (estudiante_id, ano_bachillerato, ruta_archivo)
                                    VALUES (?, ?, ?)
                                ''', (student_id, ano, nueva_ruta))
                        else:
                            # Si se borró el archivo
                            cursor.execute('''
                                DELETE FROM documentos_estudiante 
                                WHERE estudiante_id = ? AND ano_bachillerato = ?
                            ''', (student_id, ano))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Éxito", "Estudiante actualizado correctamente.")
                self.show_student_details(student_id)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Ya existe un estudiante registrado con esta cédula.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al guardar los cambios: {e}")

        btn_guardar = ctk.CTkButton(save_btn_frame, text="Guardar Cambios", fg_color="#0B0F19", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, hover_color="#1F2937", command=guardar_cambios)
        btn_guardar.pack(side="right")

    def show_new_student_form(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.archivos_seleccionados = {}

        # Scrollable Frame
        main_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_scroll.grid(row=0, column=0, sticky="nsew")
        self._bind_mouse_scroll(main_scroll)

        # Boton "Volver"
        header_frame_back = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_frame_back.pack(fill="x", padx=40, pady=(30, 0))
        btn_volver = ctk.CTkButton(header_frame_back, text="← Volver a la lista", fg_color="transparent", text_color="#4A5568", font=ctk.CTkFont(weight="bold", size=14), width=80, hover_color="#E2E8F0", command=self.show_student_list)
        btn_volver.pack(side="left")

        header_lbl = ctk.CTkLabel(main_scroll, text="Nuevo Estudiante", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1A202C")
        header_lbl.pack(anchor="w", padx=40, pady=(10, 0))
        
        sub_lbl = ctk.CTkLabel(main_scroll, text="Registra los datos del nuevo estudiante", font=ctk.CTkFont(size=14), text_color="#718096")
        sub_lbl.pack(anchor="w", padx=40, pady=(5, 20))

        # Main Card Frame (Datos Personales)
        card_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        card_frame.pack(fill="x", padx=40, pady=(0, 30))
        card_frame.grid_columnconfigure(0, weight=1)

        # --- Datos Personales ---
        left_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")

        lbl_datos = ctk.CTkLabel(left_frame, text="Datos Personales", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C")
        lbl_datos.pack(anchor="w", pady=(0, 20))

        def create_field(parent, label_text, placeholder):
            lbl = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), text_color="#4A5568")
            lbl.pack(anchor="w", pady=(10, 5))
            entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=40, fg_color="#F8FAFC", border_color="#E2E8F0", text_color="#1A202C")
            entry.pack(fill="x")
            return entry

        self.entry_p_nombre = create_field(left_frame, "Primer Nombre", "Ej: Juan")
        self.entry_s_nombre = create_field(left_frame, "Segundo Nombre", "Ej: Carlos")
        self.entry_p_apellido = create_field(left_frame, "Primer Apellido", "Ej: Perez")
        self.entry_s_apellido = create_field(left_frame, "Segundo Apellido", "Ej: Gomez")
        self.entry_cedula = create_field(left_frame, "Cédula", "V-12345678")
        self.entry_fecha = create_field(left_frame, "Fecha de Nacimiento", "dd/mm/aaaa")

        # --- Seccion: Nivel Educativo y Grado ---
        nivel_lbl = ctk.CTkLabel(main_scroll, text="Nivel Educativo y Grado", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1A202C")
        nivel_lbl.pack(anchor="w", padx=40, pady=(10, 20))

        def create_accordion(parent, title, options):
            acc_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E2E8F0")
            acc_frame.pack(fill="x", padx=40, pady=(0, 20))

            header_frame = ctk.CTkFrame(acc_frame, fg_color="#F3F4F6", corner_radius=0, height=45, cursor="hand2")
            header_frame.pack(fill="x")
            header_frame.grid_propagate(False)
            
            lbl_title = ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#1A202C", cursor="hand2")
            lbl_title.pack(side="left", padx=15)
            
            lbl_arrow = ctk.CTkLabel(header_frame, text="⌃", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C", cursor="hand2")
            lbl_arrow.pack(side="right", padx=15)

            content_frame = ctk.CTkFrame(acc_frame, fg_color="transparent")
            content_frame.pack(fill="x", pady=(0, 10))

            for opt in options:
                row_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                row_frame.pack(fill="x", padx=15, pady=8)
                
                lbl_opt = ctk.CTkLabel(row_frame, text=opt, font=ctk.CTkFont(size=13), text_color="#4A5568")
                lbl_opt.pack(side="left")
                
                # Label to show the selected file name
                lbl_filename = ctk.CTkLabel(row_frame, text="", font=ctk.CTkFont(size=11), text_color="#3182CE")
                lbl_filename.pack(side="right", padx=(10, 0))

                def select_pdf(lbl=lbl_filename, opt_key=opt):
                    filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
                    if filepath:
                        # Extract just the filename from the path
                        import os
                        filename = os.path.basename(filepath)
                        # Truncate if too long
                        if len(filename) > 20:
                            filename = filename[:17] + "..."
                        lbl.configure(text=filename)
                        self.archivos_seleccionados[opt_key] = filepath

                btn_archivo = ctk.CTkButton(row_frame, text="↑ Archivo", fg_color="#0B0F19", text_color="white", width=80, height=28, font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6, hover_color="#1F2937", command=select_pdf)
                btn_archivo.pack(side="right")
                
                # Drag and Drop support
                def on_drop(event, lbl=lbl_filename, opt_key=opt):
                    filepath = event.data
                    if filepath:
                        if filepath.startswith('{') and filepath.endswith('}'):
                            filepath = filepath[1:-1]
                        if filepath.lower().endswith('.pdf'):
                            import os
                            filename = os.path.basename(filepath)
                            if len(filename) > 20:
                                filename = filename[:17] + "..."
                            lbl.configure(text=filename)
                            self.archivos_seleccionados[opt_key] = filepath
                        else:
                            messagebox.showerror("Error", "Por favor, selecciona un archivo PDF.")
                            
                row_frame.drop_target_register(DND_FILES)
                row_frame.dnd_bind('<<Drop>>', on_drop)
                btn_archivo.drop_target_register(DND_FILES)
                btn_archivo.dnd_bind('<<Drop>>', on_drop)

            # Estado del acordeón
            acc_frame.is_expanded = True

            def toggle_accordion(event=None):
                if acc_frame.is_expanded:
                    content_frame.pack_forget()
                    lbl_arrow.configure(text="⌄")
                    acc_frame.is_expanded = False
                else:
                    content_frame.pack(fill="x", pady=(0, 10))
                    lbl_arrow.configure(text="⌃")
                    acc_frame.is_expanded = True

            header_frame.bind("<Button-1>", toggle_accordion)
            lbl_title.bind("<Button-1>", toggle_accordion)
            lbl_arrow.bind("<Button-1>", toggle_accordion)

        create_accordion(main_scroll, "Bachillerato", ["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"])
        
        # Guardar / Acciones Finales
        save_btn_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        save_btn_frame.pack(fill="x", padx=40, pady=(10, 40))
        
        def guardar_estudiante():
            p_nom = self.entry_p_nombre.get()
            s_nom = self.entry_s_nombre.get()
            p_ape = self.entry_p_apellido.get()
            s_ape = self.entry_s_apellido.get()
            ced = self.entry_cedula.get()
            f_nac = self.entry_fecha.get()
            
            # Validación robusta
            if not self.validar_datos_estudiante(p_nom, p_ape, ced, f_nac):
                return

            try:
                conn = sqlite3.connect('notas.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO estudiantes (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, cedula, fecha_nacimiento, foto, grado_id)
                    VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
                ''', (p_nom, s_nom, p_ape, s_ape, ced, f_nac))
                
                estudiante_id = cursor.lastrowid
                
                # Guardar archivos
                import os, shutil
                os.makedirs('documentos_estudiantes', exist_ok=True)
                
                for ano, filepath in getattr(self, 'archivos_seleccionados', {}).items():
                    if os.path.exists(filepath):
                        ext = os.path.splitext(filepath)[1]
                        nuevo_nombre = f"estudiante_{estudiante_id}_{ano.replace(' ', '_')}{ext}"
                        nueva_ruta = os.path.join('documentos_estudiantes', nuevo_nombre)
                        shutil.copy2(filepath, nueva_ruta)
                        
                        cursor.execute('''
                            INSERT INTO documentos_estudiante (estudiante_id, ano_bachillerato, ruta_archivo)
                            VALUES (?, ?, ?)
                        ''', (estudiante_id, ano, nueva_ruta))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Éxito", "Estudiante guardado correctamente.")
                self.show_student_list()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Ya existe un estudiante registrado con esta cédula.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")

        btn_guardar = ctk.CTkButton(save_btn_frame, text="Guardar Estudiante", fg_color="#0B0F19", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, hover_color="#1F2937", command=guardar_estudiante)
        btn_guardar.pack(side="right")

if __name__ == "__main__":
    app = App()
    app.mainloop()
