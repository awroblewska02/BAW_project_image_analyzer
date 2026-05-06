import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from image_filters import apply_grayscale, apply_blur, apply_edges, apply_binary
from loader_thread import loader_worker


class ImageApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analizator obrazów")
        self.root.geometry("1320x760")
        self.root.minsize(1180, 700)

        self.bg_main = "#dff4ff"
        self.bg_panel = "#cfefff"
        self.bg_canvas = "#eef9ff"
        self.button_bg = "#b9e6ff"
        self.button_active = "#9fdcff"
        self.text_color = "#1f4e79"

        self.root.configure(bg=self.bg_main)

        self.current_image = None
        self.processed_image = None
        self.original_photo = None
        self.processed_photo = None

        self.image_paths = []
        self.current_index = -1

        self.preview_width = 430
        self.preview_height = 280

        # ===== WIELOWĄTKOWOŚĆ - LOADER THREAD =====
        self.loader_queue = queue.Queue()
        self.loader_thread = None

        self._build_ui()

    def _build_ui(self):
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        title_label = tk.Label(
            self.root,
            text="Analizator obrazów",
            font=("Arial", 22, "bold"),
            bg=self.bg_main,
            fg=self.text_color
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(12, 10))

        # ===== LEWY PANEL =====
        left_panel = tk.Frame(
            self.root,
            bg=self.bg_panel,
            bd=2,
            relief="groove",
            padx=18,
            pady=18
        )
        left_panel.grid(row=1, column=0, sticky="nsw", padx=(18, 14), pady=(0, 12))

        left_title = tk.Label(
            left_panel,
            text="Ustawienia początkowe",
            font=("Arial", 12, "bold"),
            bg=self.bg_panel,
            fg=self.text_color
        )
        left_title.pack(pady=(0, 14))

        self.load_button = tk.Button(
            left_panel,
            text="Wczytaj obraz",
            command=self.load_image,
            bg=self.button_bg,
            activebackground=self.button_active,
            width=18,
            font=("Arial", 10)
        )
        self.load_button.pack(pady=4)

        self.load_folder_button = tk.Button(
            left_panel,
            text="Wczytaj folder",
            command=self.load_folder,
            bg=self.button_bg,
            activebackground=self.button_active,
            width=18,
            font=("Arial", 10)
        )
        self.load_folder_button.pack(pady=4)

        self.process_all_button = tk.Button(
            left_panel,
            text="Przetwórz cały folder",
            command=self.process_entire_folder,
            bg=self.button_bg,
            activebackground=self.button_active,
            width=18,
            font=("Arial", 10)
        )
        self.process_all_button.pack(pady=4)

        filter_label = tk.Label(
            left_panel,
            text="Wybierz filtr:",
            font=("Arial", 10, "bold"),
            bg=self.bg_panel,
            fg=self.text_color
        )
        filter_label.pack(pady=(18, 6))

        self.filter_box = ttk.Combobox(
            left_panel,
            values=["Grayscale", "Blur", "Edges", "Binary"],
            state="readonly",
            width=16,
            font=("Arial", 10)
        )
        self.filter_box.pack(pady=4)
        self.filter_box.set("Grayscale")

        self.info_label = tk.Label(
            left_panel,
            text="Brak folderu",
            bg=self.bg_panel,
            fg=self.text_color,
            font=("Arial", 10),
            wraplength=180,
            justify="center"
        )
        self.info_label.pack(pady=(18, 0))

        # ===== PRAWA GŁÓWNA CZĘŚĆ =====
        main_area = tk.Frame(self.root, bg=self.bg_main)
        main_area.grid(row=1, column=1, sticky="nsew", padx=(0, 18), pady=(0, 12))

        main_area.grid_rowconfigure(0, weight=0)
        main_area.grid_rowconfigure(1, weight=1)
        main_area.grid_columnconfigure(0, weight=1)

        # ===== GÓRNA BELKA =====
        top_bar = tk.Frame(main_area, bg=self.bg_main)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        top_bar.grid_columnconfigure(0, minsize=240)
        top_bar.grid_columnconfigure(1, weight=1)
        top_bar.grid_columnconfigure(2, minsize=240)

        left_spacer = tk.Frame(top_bar, bg=self.bg_main)
        left_spacer.grid(row=0, column=0, sticky="w")

        # ===== NAWIGACJA NA ŚRODKU =====
        nav_panel = tk.Frame(
            top_bar,
            bg=self.bg_panel,
            bd=2,
            relief="groove",
            padx=20,
            pady=14
        )
        nav_panel.grid(row=0, column=1)

        nav_title = tk.Label(
            nav_panel,
            text="Nawigacja i sterowanie",
            font=("Arial", 12, "bold"),
            bg=self.bg_panel,
            fg=self.text_color
        )
        nav_title.pack(pady=(0, 12))

        nav_buttons = tk.Frame(nav_panel, bg=self.bg_panel)
        nav_buttons.pack()

        self.prev_button = tk.Button(
            nav_buttons,
            text="← Poprzedni",
            command=self.show_previous_image,
            bg=self.button_bg,
            activebackground=self.button_active,
            width=13,
            font=("Arial", 10)
        )
        self.prev_button.grid(row=0, column=0, padx=6)

        self.start_button = tk.Button(
            nav_buttons,
            text="START",
            command=self.start_processing,
            bg="#8fd3ff",
            activebackground="#70c5ff",
            width=13,
            font=("Arial", 10, "bold")
        )
        self.start_button.grid(row=0, column=1, padx=6)

        self.next_button = tk.Button(
            nav_buttons,
            text="Następny →",
            command=self.show_next_image,
            bg=self.button_bg,
            activebackground=self.button_active,
            width=13,
            font=("Arial", 10)
        )
        self.next_button.grid(row=0, column=2, padx=6)

        # ===== ZAPIS PO PRAWEJ =====
        save_panel = tk.Frame(
            top_bar,
            bg=self.bg_panel,
            bd=2,
            relief="groove",
            padx=18,
            pady=14
        )
        save_panel.grid(row=0, column=2, sticky="e")

        save_title = tk.Label(
            save_panel,
            text="Zapis i akcje",
            font=("Arial", 12, "bold"),
            bg=self.bg_panel,
            fg=self.text_color
        )
        save_title.pack(pady=(0, 12))

        self.save_button = tk.Button(
            save_panel,
            text="Zapisz wynik",
            command=self.save_result,
            bg=self.button_bg,
            activebackground=self.button_active,
            width=18,
            font=("Arial", 10)
        )
        self.save_button.pack(pady=4)

        self.abort_button = tk.Button(
            save_panel,
            text="Abort",
            command=self.abort_processing,
            bg="#ffcad4",
            activebackground="#ffb3c1",
            width=18,
            font=("Arial", 10, "bold")
        )
        self.abort_button.pack(pady=4)

        # ===== PANELE Z OBRAZAMI =====
        images_frame = tk.Frame(main_area, bg=self.bg_main)
        images_frame.grid(row=1, column=0, sticky="nsew")

        images_frame.grid_columnconfigure(0, weight=1)
        images_frame.grid_columnconfigure(1, weight=1)
        images_frame.grid_rowconfigure(0, weight=1)

        original_frame = tk.Frame(
            images_frame,
            bg=self.bg_panel,
            bd=2,
            relief="groove",
            padx=10,
            pady=8
        )
        original_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        processed_frame = tk.Frame(
            images_frame,
            bg=self.bg_panel,
            bd=2,
            relief="groove",
            padx=10,
            pady=8
        )
        processed_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        original_title = tk.Label(
            original_frame,
            text="Obraz oryginalny",
            font=("Arial", 12, "bold"),
            bg=self.bg_panel,
            fg=self.text_color
        )
        original_title.pack(pady=(0, 8))

        self.original_canvas = tk.Canvas(
            original_frame,
            width=self.preview_width,
            height=self.preview_height,
            bg=self.bg_canvas,
            highlightthickness=1,
            highlightbackground="#7fbfe6"
        )
        self.original_canvas.pack(fill="both", expand=True)
        self.original_canvas.create_text(
            self.preview_width // 2,
            self.preview_height // 2,
            text="Brak obrazu",
            font=("Arial", 13)
        )

        processed_title = tk.Label(
            processed_frame,
            text="Obraz przetworzony",
            font=("Arial", 12, "bold"),
            bg=self.bg_panel,
            fg=self.text_color
        )
        processed_title.pack(pady=(0, 8))

        self.processed_canvas = tk.Canvas(
            processed_frame,
            width=self.preview_width,
            height=self.preview_height,
            bg=self.bg_canvas,
            highlightthickness=1,
            highlightbackground="#7fbfe6"
        )
        self.processed_canvas.pack(fill="both", expand=True)
        self.processed_canvas.create_text(
            self.preview_width // 2,
            self.preview_height // 2,
            text="Brak obrazu",
            font=("Arial", 13)
        )

        # ===== DÓŁ: PASEK + NAPIS =====
        bottom_frame = tk.Frame(self.root, bg=self.bg_main)
        bottom_frame.grid(row=2, column=0, columnspan=2, pady=(0, 14))

        self.progress = ttk.Progressbar(
            bottom_frame,
            length=420,
            mode="determinate"
        )
        self.progress.pack(pady=(0, 6))

        self.bottom_status_label = tk.Label(
            bottom_frame,
            text="Status: gotowy",
            bg=self.bg_main,
            fg=self.text_color,
            font=("Arial", 10, "bold")
        )
        self.bottom_status_label.pack()

    def set_status(self, text):
        self.bottom_status_label.config(text=text)

    def apply_selected_filter(self, image, selected_filter):
        if selected_filter == "Grayscale":
            return apply_grayscale(image)
        elif selected_filter == "Blur":
            return apply_blur(image)
        elif selected_filter == "Edges":
            return apply_edges(image)
        elif selected_filter == "Binary":
            return apply_binary(image)
        else:
            raise ValueError("Nieznany filtr")

    # ============================================================
    # LOADER THREAD - URUCHAMIANIE WĄTKU WCZYTUJĄCEGO OBRAZ
    # ============================================================

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz obraz",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )

        if not file_path:
            return

        self.image_paths = [file_path]
        self.current_index = 0

        self.current_image = None
        self.processed_image = None
        self.processed_photo = None

        self.processed_canvas.delete("all")
        self.processed_canvas.create_text(
            int(self.processed_canvas["width"]) // 2,
            int(self.processed_canvas["height"]) // 2,
            text="Brak obrazu",
            font=("Arial", 13)
        )

        self.progress["value"] = 0
        self.set_status("Status: uruchamianie Loader Thread...")

        self.load_button.config(state="disabled")

        self.loader_thread = threading.Thread(
            target=loader_worker,
            args=(file_path, self.loader_queue),
            daemon=True
        )
        self.loader_thread.start()

        self.root.after(100, self.check_loader_queue)

    def check_loader_queue(self):
        """
        Ta metoda działa w głównym wątku GUI.
        Odbiera wynik pracy Loader Thread z kolejki i dopiero tutaj aktualizuje interfejs.
        """
        try:
            result = self.loader_queue.get_nowait()
        except queue.Empty:
            self.root.after(100, self.check_loader_queue)
            return

        self.load_button.config(state="normal")

        if result["status"] == "success":
            self.current_image = result["image"]

            self.display_image(self.current_image, "original")

            self.processed_canvas.delete("all")
            self.processed_canvas.create_text(
                int(self.processed_canvas["width"]) // 2,
                int(self.processed_canvas["height"]) // 2,
                text="Brak obrazu",
                font=("Arial", 13)
            )

            self.processed_image = None
            self.processed_photo = None
            self.progress["value"] = 0

            file_name = os.path.basename(result["path"])
            self.info_label.config(
                text=f"Obraz {self.current_index + 1} z {len(self.image_paths)}\n{file_name}"
            )

            self.set_status("Status: obraz wczytany przez Loader Thread")

        else:
            messagebox.showerror(
                "Błąd",
                f"Nie udało się wczytać obrazu:\n{result['error']}"
            )
            self.set_status("Status: błąd w Loader Thread")

    # ============================================================
    # POZOSTAŁE FUNKCJE - NA RAZIE DZIAŁAJĄ JAK WCZEŚNIEJ
    # ============================================================

    def load_folder(self):
        folder_path = filedialog.askdirectory(title="Wybierz folder ze zdjęciami")

        if not folder_path:
            return

        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp")
        files = []

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(supported_extensions):
                files.append(os.path.join(folder_path, file_name))

        files.sort()

        if not files:
            messagebox.showwarning("Brak obrazów", "W wybranym folderze nie ma obrazów.")
            return

        self.image_paths = files
        self.current_index = 0
        self._load_image_from_index()
        self.set_status(f"Status: wczytano folder ({len(files)} obrazów)")

    def _load_image_from_index(self):
        if not self.image_paths or self.current_index < 0 or self.current_index >= len(self.image_paths):
            return

        try:
            path = self.image_paths[self.current_index]
            self.current_image = Image.open(path)
            self.display_image(self.current_image, "original")

            self.processed_canvas.delete("all")
            self.processed_canvas.create_text(
                int(self.processed_canvas["width"]) // 2,
                int(self.processed_canvas["height"]) // 2,
                text="Brak obrazu",
                font=("Arial", 13)
            )

            self.processed_image = None
            self.processed_photo = None
            self.progress["value"] = 0

            file_name = os.path.basename(path)
            self.info_label.config(
                text=f"Obraz {self.current_index + 1} z {len(self.image_paths)}\n{file_name}"
            )
            self.set_status("Status: obraz wczytany")
        except Exception as error:
            messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu:\n{error}")

    def show_previous_image(self):
        if not self.image_paths:
            return

        if self.current_index > 0:
            self.current_index -= 1
            self._load_image_from_index()

    def show_next_image(self):
        if not self.image_paths:
            return

        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self._load_image_from_index()

    def start_processing(self):
        if self.current_image is None:
            self.set_status("Status: najpierw wczytaj obraz lub folder")
            return

        selected_filter = self.filter_box.get()
        self.progress["value"] = 20
        self.root.update_idletasks()

        try:
            self.processed_image = self.apply_selected_filter(self.current_image, selected_filter)

            self.progress["value"] = 80
            self.display_image(self.processed_image, "processed")
            self.progress["value"] = 100
            self.set_status(f"Status: zastosowano filtr {selected_filter}")

        except Exception as error:
            messagebox.showerror("Błąd", f"Nie udało się przetworzyć obrazu:\n{error}")
            self.set_status("Status: błąd przetwarzania")
            self.progress["value"] = 0

    def process_entire_folder(self):
        if not self.image_paths or len(self.image_paths) == 0:
            self.set_status("Status: najpierw wczytaj folder")
            return

        output_folder = filedialog.askdirectory(title="Wybierz folder do zapisu wyników")

        if not output_folder:
            return

        selected_filter = self.filter_box.get()
        total_files = len(self.image_paths)

        try:
            for index, path in enumerate(self.image_paths):
                image = Image.open(path)
                processed = self.apply_selected_filter(image, selected_filter)

                base_name = os.path.basename(path)
                name, ext = os.path.splitext(base_name)
                output_path = os.path.join(
                    output_folder,
                    f"{name}_{selected_filter.lower()}{ext}"
                )

                processed.save(output_path)

                self.progress["value"] = ((index + 1) / total_files) * 100
                self.root.update_idletasks()

            self.set_status(f"Status: przetworzono cały folder filtrem {selected_filter}")
            messagebox.showinfo(
                "Gotowe",
                f"Przetworzono {total_files} obrazów.\nWyniki zapisano w:\n{output_folder}"
            )

        except Exception as error:
            messagebox.showerror("Błąd", f"Nie udało się przetworzyć folderu:\n{error}")
            self.set_status("Status: błąd przetwarzania folderu")
            self.progress["value"] = 0

    def save_result(self):
        if self.processed_image is None:
            self.set_status("Status: brak wyniku do zapisania")
            return

        answer = messagebox.askyesnocancel(
            "Zapis wyniku",
            "Czy zapisać wynik do domyślnego folderu 'results'?\n\n"
            "Tak = zapisz do folderu results\n"
            "Nie = wybierz inne miejsce\n"
            "Anuluj = przerwij"
        )

        if answer is None:
            self.set_status("Status: zapis anulowany")
            return

        try:
            if answer is True:
                project_dir = os.path.dirname(os.path.abspath(__file__))
                results_dir = os.path.join(project_dir, "results")
                os.makedirs(results_dir, exist_ok=True)

                if self.image_paths and 0 <= self.current_index < len(self.image_paths):
                    base_name = os.path.basename(self.image_paths[self.current_index])
                    name, ext = os.path.splitext(base_name)
                else:
                    name, ext = "processed_image", ".png"

                selected_filter = self.filter_box.get().lower()
                output_path = os.path.join(results_dir, f"{name}_{selected_filter}{ext}")

                self.processed_image.save(output_path)
                self.set_status("Status: zapisano do folderu results")
                messagebox.showinfo("Zapisano", f"Plik zapisano w:\n{output_path}")

            else:
                file_path = filedialog.asksaveasfilename(
                    title="Zapisz wynik",
                    defaultextension=".png",
                    filetypes=[
                        ("PNG file", "*.png"),
                        ("JPEG file", "*.jpg"),
                        ("BMP file", "*.bmp")
                    ]
                )

                if not file_path:
                    self.set_status("Status: zapis anulowany")
                    return

                self.processed_image.save(file_path)
                self.set_status("Status: wynik zapisany")
                messagebox.showinfo("Zapisano", f"Plik zapisano w:\n{file_path}")

        except Exception as error:
            messagebox.showerror("Błąd", f"Nie udało się zapisać obrazu:\n{error}")

    def abort_processing(self):
        self.progress["value"] = 0
        self.set_status("Status: przerwano")

    def display_image(self, image, target):
        preview = image.copy()
        preview.thumbnail((self.preview_width, self.preview_height))

        photo = ImageTk.PhotoImage(preview)

        if target == "original":
            self.original_photo = photo
            canvas = self.original_canvas
        else:
            self.processed_photo = photo
            canvas = self.processed_canvas

        canvas.delete("all")
        canvas_width = int(canvas["width"])
        canvas_height = int(canvas["height"])
        canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=photo,
            anchor="center"
        )

    def run(self):
        self.root.mainloop()