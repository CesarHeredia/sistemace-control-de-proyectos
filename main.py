import customtkinter as ctk

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
        self.btn_estudiantes = ctk.CTkButton(self.sidebar_frame, text="👥  Estudiantes", fg_color="#374151", text_color="white", anchor="w", height=45, font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8)
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


        # --- Contenido Principal ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=40, pady=30, sticky="nsew")
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

        self.btn_nuevo = ctk.CTkButton(self.header_frame, text="+ Nuevo Estudiante", fg_color="#0B0F19", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, hover_color="#1F2937", command=self.open_new_student_window)
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

        # Lista vacía para los estudiantes (se pueden cargar desde una base de datos más adelante)
        estudiantes = []

        # Llenar las filas de la tabla
        for row, data in enumerate(estudiantes, start=1):
            ctk.CTkLabel(self.table_frame, text=str(data[0]), text_color="#1A202C", anchor="w", font=ctk.CTkFont(size=13)).grid(row=row, column=0, padx=15, pady=15, sticky="ew")
            ctk.CTkLabel(self.table_frame, text=data[1], text_color="#1A202C", anchor="w", font=ctk.CTkFont(size=13)).grid(row=row, column=1, padx=15, pady=15, sticky="ew")
            ctk.CTkLabel(self.table_frame, text=data[2], text_color="#1A202C", anchor="w", font=ctk.CTkFont(size=13)).grid(row=row, column=2, padx=15, pady=15, sticky="ew")
            
            # Botones Acciones
            acciones_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            acciones_frame.grid(row=row, column=3, padx=15, pady=15)
            
            btn_edit = ctk.CTkButton(acciones_frame, text="📝", width=32, height=32, fg_color="transparent", text_color="#718096", hover_color="#F3F4F6", font=ctk.CTkFont(size=16))
            btn_edit.pack(side="left", padx=5)
            btn_del = ctk.CTkButton(acciones_frame, text="🗑️", width=32, height=32, fg_color="transparent", text_color="#E53E3E", hover_color="#FED7D7", font=ctk.CTkFont(size=16))
            btn_del.pack(side="left", padx=5)
            
            # Línea separadora horizontal para cada fila
            if row < len(estudiantes):
                sep = ctk.CTkFrame(self.table_frame, height=1, fg_color="#EDF2F7")
                sep.grid(row=row, column=0, columnspan=4, sticky="sew", padx=10)

    def open_new_student_window(self):
        new_window = ctk.CTkToplevel(self)
        new_window.title("Nuevo Estudiante")
        new_window.geometry("900x700")
        new_window.configure(fg_color="#F9FAFB")
        new_window.attributes("-topmost", True)
        new_window.after(10, new_window.lift)

        # Scrollable Frame
        main_scroll = ctk.CTkScrollableFrame(new_window, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)

        header_lbl = ctk.CTkLabel(main_scroll, text="Nuevo Estudiante", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1A202C")
        header_lbl.pack(anchor="w", padx=40, pady=(30, 0))
        
        sub_lbl = ctk.CTkLabel(main_scroll, text="Registra los datos del nuevo estudiante", font=ctk.CTkFont(size=14), text_color="#718096")
        sub_lbl.pack(anchor="w", padx=40, pady=(5, 20))

        # Main Card Frame (Datos Personales y Foto)
        card_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#E2E8F0")
        card_frame.pack(fill="x", padx=40, pady=(0, 30))
        card_frame.grid_columnconfigure(0, weight=1)
        card_frame.grid_columnconfigure(1, weight=1)

        # --- Left Column - Datos Personales ---
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

        create_field(left_frame, "Nombre", "Ingrese el nombre")
        create_field(left_frame, "Apellido", "Ingrese el apellido")
        create_field(left_frame, "Cédula", "V-12345678")
        create_field(left_frame, "Fecha de Nacimiento", "dd/mm/aaaa")

        # --- Right Column - Foto ---
        right_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")

        lbl_foto = ctk.CTkLabel(right_frame, text="Foto del Estudiante (Tamaño Carta)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1A202C")
        lbl_foto.pack(anchor="w", pady=(0, 10))

        # Photo Preview Area
        preview_border = ctk.CTkFrame(right_frame, fg_color="transparent", corner_radius=10, border_width=2, border_color="#E2E8F0")
        preview_border.pack(fill="both", expand=True)

        preview_bg = ctk.CTkFrame(preview_border, fg_color="#F3F4F6", corner_radius=8)
        preview_bg.pack(fill="both", expand=True, padx=10, pady=10)

        # Inner content of preview
        preview_inner = ctk.CTkFrame(preview_bg, fg_color="transparent")
        preview_inner.place(relx=0.5, rely=0.4, anchor="center")

        icon_lbl = ctk.CTkLabel(preview_inner, text="👥", font=ctk.CTkFont(size=60), text_color="#9CA3AF")
        icon_lbl.pack()

        text_lbl1 = ctk.CTkLabel(preview_inner, text="Vista previa de la foto", font=ctk.CTkFont(size=14), text_color="#718096")
        text_lbl1.pack(pady=(10,0))
        text_lbl2 = ctk.CTkLabel(preview_inner, text="Tamaño carta recomendado", font=ctk.CTkFont(size=12), text_color="#A0AEC0")
        text_lbl2.pack()

        # Select Photo Button
        btn_foto = ctk.CTkButton(preview_bg, text="Seleccionar Foto", fg_color="#0B0F19", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, hover_color="#1F2937", width=200)
        btn_foto.place(relx=0.5, rely=0.8, anchor="center")

        lbl_formato = ctk.CTkLabel(preview_bg, text="Formatos: JPG, PNG", font=ctk.CTkFont(size=11), text_color="#A0AEC0")
        lbl_formato.place(relx=0.5, rely=0.92, anchor="center")

        # --- Seccion: Nivel Educativo y Grado ---
        nivel_lbl = ctk.CTkLabel(main_scroll, text="Nivel Educativo y Grado", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1A202C")
        nivel_lbl.pack(anchor="w", padx=40, pady=(10, 20))

        radio_var = ctk.StringVar(value="")

        def create_accordion(parent, title, options):
            acc_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E2E8F0")
            acc_frame.pack(fill="x", padx=40, pady=(0, 20))

            header_frame = ctk.CTkFrame(acc_frame, fg_color="#F3F4F6", corner_radius=0, height=45)
            header_frame.pack(fill="x")
            header_frame.grid_propagate(False)
            
            lbl_title = ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#1A202C")
            lbl_title.pack(side="left", padx=15)
            
            lbl_arrow = ctk.CTkLabel(header_frame, text="⌃", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1A202C")
            lbl_arrow.pack(side="right", padx=15)

            for opt in options:
                row_frame = ctk.CTkFrame(acc_frame, fg_color="transparent")
                row_frame.pack(fill="x", padx=15, pady=8)
                
                rb = ctk.CTkRadioButton(row_frame, text=opt, variable=radio_var, value=opt, font=ctk.CTkFont(size=13), text_color="#4A5568", border_color="#CBD5E1", hover_color="#94A3B8")
                rb.pack(side="left")
                
                btn_archivo = ctk.CTkButton(row_frame, text="↑ Archivo", fg_color="#0B0F19", text_color="white", width=80, height=28, font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6, hover_color="#1F2937")
                btn_archivo.pack(side="right")

        create_accordion(main_scroll, "Maternal", ["Segundo Nivel", "Tercer Nivel"])
        create_accordion(main_scroll, "Primaria", ["1er Grado", "2do Grado", "3er Grado", "4to Grado", "5to Grado", "6to Grado"])
        create_accordion(main_scroll, "Bachillerato", ["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"])
        
        # Guardar / Acciones Finales
        save_btn_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        save_btn_frame.pack(fill="x", padx=40, pady=(10, 40))
        
        btn_guardar = ctk.CTkButton(save_btn_frame, text="Guardar Estudiante", fg_color="#0B0F19", text_color="white", font=ctk.CTkFont(weight="bold", size=14), corner_radius=8, height=45, hover_color="#1F2937")
        btn_guardar.pack(side="right")

if __name__ == "__main__":
    app = App()
    app.mainloop()
