# pyrefly: ignore [missing-import]
import customtkinter as ctk
import sqlite3
from tkinter import filedialog, messagebox
from PIL import Image

# Configuración básica de customtkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

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
        nombre_completo = f"{p_nom} {s_nom or ''} {p_ape} {s_ape or ''}".strip()

        header_lbl = ctk.CTkLabel(main_scroll, text="Detalles del Estudiante", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1A202C")
        header_lbl.pack(anchor="w", padx=40, pady=(10, 0))

        sub_lbl = ctk.CTkLabel(main_scroll, text="Información registrada del estudiante", font=ctk.CTkFont(size=14), text_color="#718096")
        sub_lbl.pack(anchor="w", padx=40, pady=(5, 20))

        # Main Card Frame
        card_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        card_frame.pack(fill="x", padx=40, pady=(0, 30))
        card_frame.grid_columnconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")

        lbl_datos = ctk.CTkLabel(left_frame, text="Datos Personales", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C")
        lbl_datos.pack(anchor="w", pady=(0, 20))

        def create_info_row(parent, label, value):
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            lbl_key = ctk.CTkLabel(row_frame, text=label + ":", font=ctk.CTkFont(size=14, weight="bold"), text_color="#4A5568", width=150, anchor="w")
            lbl_key.pack(side="left")
            lbl_val = ctk.CTkLabel(row_frame, text=value if value else "No especificado", font=ctk.CTkFont(size=14), text_color="#1A202C", anchor="w")
            lbl_val.pack(side="left", padx=10)

        create_info_row(left_frame, "Cédula", ced)
        create_info_row(left_frame, "Nombre Completo", nombre_completo)
        create_info_row(left_frame, "Primer Nombre", p_nom)
        create_info_row(left_frame, "Segundo Nombre", s_nom)
        create_info_row(left_frame, "Primer Apellido", p_ape)
        create_info_row(left_frame, "Segundo Apellido", s_ape)
        create_info_row(left_frame, "Fecha de Nac.", f_nac)

    def show_new_student_form(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

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
                
                btn_archivo = ctk.CTkButton(row_frame, text="↑ Archivo", fg_color="#0B0F19", text_color="white", width=80, height=28, font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6, hover_color="#1F2937")
                btn_archivo.pack(side="right")

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
            if not p_nom or not p_ape or not ced:
                messagebox.showerror("Error", "Los campos: Primer Nombre, Primer Apellido y Cédula son obligatorios.")
                return

            try:
                conn = sqlite3.connect('notas.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO estudiantes (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, cedula, fecha_nacimiento, foto, grado_id)
                    VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
                ''', (p_nom, s_nom, p_ape, s_ape, ced, f_nac))
                
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
