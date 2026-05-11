import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from image_filters import apply_grayscale, apply_blur, apply_edges, apply_binary
from loader_thread import LoaderThread
from image_analyzer_thread import ImageAnalyzerThread
from saver_thread import SaverThread
from controller_thread import ControllerThread


class ImageApp:
    def __init__(self):
        print("GUI thread:", threading.current_thread().name)
        print("GUI thread id:", threading.get_ident())

        self.root = tk.Tk()
        self.root.title("Analizator obrazów")
        self.root.geometry("1320x860")
        self.root.minsize(1180, 800)

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

        self.loader_task_queue = queue.Queue()
        self.loader_result_queue = queue.Queue()

        self.analyzer_task_queue = queue.Queue()
        self.analyzer_result_queue = queue.Queue()
        self.analyzer_state = "WAITING"

        self.saver_task_queue = queue.Queue()
        self.saver_result_queue = queue.Queue()

        self.controller_task_queue = queue.Queue()
        self.controller_result_queue = queue.Queue()
        self.controller_state = "IDLE"

        self.loaded_images = {}
        self.loading_requested = set()
        self.processed_results = {}

        self.next_job_id = 1
        self.active_job_id = None
        self.cancelled_jobs = set()
        self.processing_in_progress = False
        self.save_in_progress = False

<<<<<<< HEAD
        # Tryb przetwarzania całego folderu przez kolejki Producer-Consumer
        self.batch_processing = False
        self.batch_output_folder = None
        self.batch_filter = None
        self.batch_total = 0
        self.batch_saved = 0
        self.batch_job_ids = set()
        self.batch_output_paths = {}

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        self.loader_thread = LoaderThread(
            self.loader_task_queue,
            self.loader_result_queue
        )

<<<<<<< HEAD
        self.image_analyzer_thread_1 = ImageAnalyzerThread(
            self.analyzer_task_queue,
            self.analyzer_result_queue,
            name="ImageAnalyzerThread-1"
        )

        self.image_analyzer_thread_2 = ImageAnalyzerThread(
            self.analyzer_task_queue,
            self.analyzer_result_queue,
            name="ImageAnalyzerThread-2"
=======
        self.image_analyzer_thread = ImageAnalyzerThread(
            self.analyzer_task_queue,
            self.analyzer_result_queue
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        )

        self.saver_thread = SaverThread(
            self.saver_task_queue,
            self.saver_result_queue
        )

        self.controller_thread = ControllerThread(
            self.controller_task_queue,
            self.controller_result_queue
        )

        self.loader_thread.start()
<<<<<<< HEAD
        self.image_analyzer_thread_1.start()
        self.image_analyzer_thread_2.start()
=======
        self.image_analyzer_thread.start()
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        self.saver_thread.start()
        self.controller_thread.start()

        self._build_ui()

        self.root.after(100, self.check_loader_queue)
        self.root.after(100, self.check_analyzer_queue)
        self.root.after(100, self.check_saver_queue)
        self.root.after(100, self.check_controller_queue)
        self.root.after(300, self.update_debug_info)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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
        self.info_label.pack(pady=(18, 4))

        self.image_index_progress = ttk.Progressbar(
            left_panel,
            length=180,
            mode="determinate"
        )
        self.image_index_progress.pack(pady=(0, 4))

        main_area = tk.Frame(self.root, bg=self.bg_main)
        main_area.grid(row=1, column=1, sticky="nsew", padx=(0, 18), pady=(0, 12))

        main_area.grid_rowconfigure(0, weight=0)
        main_area.grid_rowconfigure(1, weight=1)
        main_area.grid_columnconfigure(0, weight=1)

        top_bar = tk.Frame(main_area, bg=self.bg_main)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        top_bar.grid_columnconfigure(0, minsize=240)
        top_bar.grid_columnconfigure(1, weight=1)
        top_bar.grid_columnconfigure(2, minsize=240)

        left_spacer = tk.Frame(top_bar, bg=self.bg_main)
        left_spacer.grid(row=0, column=0, sticky="w")

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

        self.controller_state_label = tk.Label(
            bottom_frame,
            text="Stan kontrolera: IDLE",
            bg=self.bg_main,
            fg=self.text_color,
            font=("Arial", 10, "bold")
        )
        self.controller_state_label.pack(pady=(4, 0))

        self.analyzer_state_label = tk.Label(
            bottom_frame,
            text="Stan analizatora: WAITING",
            bg=self.bg_main,
            fg=self.text_color,
            font=("Arial", 10, "bold")
        )
        self.analyzer_state_label.pack(pady=(4, 0))

        self.debug_label = tk.Label(
            bottom_frame,
<<<<<<< HEAD
            text="Załadowane=0 | Przetworzone=0 | Indeks=0/0 | Analiza=nie | Zapis=nie | Analizatory=2",
=======
            text="Załadowane=0 | Przetworzone=0 | Indeks=0/0 | Analiza=nie | Zapis=nie",
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
            bg=self.bg_main,
            fg=self.text_color,
            font=("Arial", 9)
        )
        self.debug_label.pack(pady=(6, 0))

    def set_status(self, text):
        self.bottom_status_label.config(text=text)

    def request_controller_state(self, new_state, event=""):
        self.controller_task_queue.put({
            "cmd": "SET_STATE",
            "state": new_state,
            "event": event
        })

    def check_controller_queue(self):
        try:
            while True:
                result = self.controller_result_queue.get_nowait()

                if result["status"] == "state_changed":
                    self.controller_state = result["new_state"]
                    event = result.get("event", "")

                    self.controller_state_label.config(
                        text=f"Stan kontrolera: {self.controller_state}"
                    )

                    if event:
                        print(
                            f"Controller state: {result['old_state']} -> "
                            f"{result['new_state']} | event: {event}"
                        )

        except queue.Empty:
            pass

        self.root.after(100, self.check_controller_queue)

    def check_analyzer_queue(self):
        try:
            while True:
                result = self.analyzer_result_queue.get_nowait()

                result_type = result.get("type")

                if result_type == "state":
                    self.analyzer_state = result["new_state"]
                    event = result.get("event", "")
<<<<<<< HEAD
                    worker = result.get("worker", "ImageAnalyzerThread")

                    self.analyzer_state_label.config(
                        text=f"Stan analizatora: {self.analyzer_state} ({worker})"
=======

                    self.analyzer_state_label.config(
                        text=f"Stan analizatora: {self.analyzer_state}"
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                    )

                    if event:
                        print(
                            f"Analyzer state: {result['old_state']} -> "
<<<<<<< HEAD
                            f"{result['new_state']} | worker: {worker} | event: {event}"
=======
                            f"{result['new_state']} | event: {event}"
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                        )

                    continue

                if result_type == "result":
                    result_job_id = result.get("job_id")
                    result_index = result.get("image_index")
<<<<<<< HEAD
                    result_mode = result.get("mode", "single")
                    worker = result.get("worker", "ImageAnalyzerThread")

                    # Jeżeli użytkownik przerwał batch, ignorujemy spóźnione wyniki.
                    if result_mode == "batch" and not self.batch_processing:
                        continue
=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

                    if result_job_id in self.cancelled_jobs:
                        self.cancelled_jobs.discard(result_job_id)
                        continue

<<<<<<< HEAD
                    # Dla pojedynczego obrazu pilnujemy aktywnego job_id.
                    # Dla folderu jobów jest wiele, więc nie stosujemy active_job_id.
                    if result_mode != "batch":
                        if self.active_job_id is not None and result_job_id != self.active_job_id:
                            continue

                    if result["status"] == "success":
                        if result_mode == "batch":
                            output_path = self.batch_output_paths.get(result_index)

                            if output_path is None:
                                self.batch_processing = False
                                self.processing_in_progress = False
                                self.start_button.config(state="normal")
                                self.process_all_button.config(state="normal")
                                self.set_status("Status: błąd ścieżki zapisu w trybie folderu")
                                self.request_controller_state("ERROR", "Brak ścieżki zapisu dla obrazu")
                                continue

                            self.saver_task_queue.put({
                                "cmd": "SAVE_IMAGE",
                                "image": result["image"].copy(),
                                "output_path": output_path,
                                "job_id": result_job_id,
                                "image_index": result_index,
                                "mode": "batch"
                            })

                            self.set_status(
                                f"Status: obraz {result_index + 1}/{self.batch_total} "
                                f"przeanalizowany przez {worker}, przekazany do SaverThread"
                            )
                            continue

                        self.processing_in_progress = False
                        self.start_button.config(state="normal")
                        self.active_job_id = None

=======
                    if self.active_job_id is not None and result_job_id != self.active_job_id:
                        continue

                    self.processing_in_progress = False
                    self.start_button.config(state="normal")
                    self.active_job_id = None

                    if result["status"] == "success":
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                        self.processed_results[result_index] = {
                            "image": result["image"].copy(),
                            "filter": result["filter"]
                        }

                        self.update_image_index_progress()

                        if result_index == self.current_index:
                            self.processed_image = result["image"]
                            self.display_image(self.processed_image, "processed")
                            self.progress["value"] = 100
                            self.set_status(
<<<<<<< HEAD
                                f"Status: zastosowano algorytm {result['filter']} przez {worker}"
=======
                                f"Status: zastosowano algorytm {result['filter']} przez ImageAnalyzerThread"
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                            )
                            self.request_controller_state("READY", "Analiza obrazu zakończona")
                        else:
                            self.progress["value"] = 0
                            self.set_status("Status: wynik zapisany dla innego zdjęcia")
                            self.request_controller_state("READY", "Analiza zakończona dla innego obrazu")

                        if result_index in self.loaded_images and result_index == self.current_index:
                            path, _ = self.loaded_images[result_index]
                            file_name = os.path.basename(path)
                            processed_count = len(self.processed_results)
                            self.info_label.config(
                                text=(
                                    f"Obraz {self.current_index + 1} z {len(self.image_paths)}\n"
                                    f"{file_name}\n"
                                    f"Przetworzone: {processed_count} z {len(self.image_paths)}"
                                )
                            )

                    else:
<<<<<<< HEAD
                        if result_mode == "batch":
                            self.batch_processing = False
                            self.processing_in_progress = False
                            self.start_button.config(state="normal")
                            self.process_all_button.config(state="normal")

                            self.set_status(f"Status: błąd analizy w trybie folderu ({worker})")
                            self.request_controller_state("ERROR", "Błąd analizy folderu")
                            messagebox.showerror(
                                "Błąd",
                                f"Nie udało się przeanalizować jednego z obrazów:\n{result['error']}"
                            )
                            continue

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                        if result_index == self.current_index:
                            self.progress["value"] = 0

                        self.processing_in_progress = False
                        self.start_button.config(state="normal")
                        self.active_job_id = None

<<<<<<< HEAD
                        self.set_status(f"Status: błąd w {worker}")
=======
                        self.set_status("Status: błąd w ImageAnalyzerThread")
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                        self.request_controller_state("ERROR", "Błąd analizy obrazu")
                        messagebox.showerror(
                            "Błąd",
                            f"Nie udało się przeanalizować obrazu:\n{result['error']}"
                        )

        except queue.Empty:
            pass

        self.root.after(100, self.check_analyzer_queue)

    def update_debug_info(self):
        loaded_count = len(self.loaded_images)
        processed_count = len(self.processed_results)

<<<<<<< HEAD
        if self.batch_processing:
            mode_text = f"Batch={self.batch_saved}/{self.batch_total}"
        else:
            mode_text = "Batch=nie"

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        debug_text = (
            f"Załadowane={loaded_count} | "
            f"Przetworzone={processed_count} | "
            f"Indeks={self.current_index + 1 if self.current_index >= 0 else 0}/"
            f"{len(self.image_paths)} | "
            f"Analiza={'tak' if self.processing_in_progress else 'nie'} | "
<<<<<<< HEAD
            f"Zapis={'tak' if self.save_in_progress else 'nie'} | "
            f"Analizatory=2 | "
            f"{mode_text}"
=======
            f"Zapis={'tak' if self.save_in_progress else 'nie'}"
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        )

        self.debug_label.config(text=debug_text)
        self.root.after(300, self.update_debug_info)

    def update_image_index_progress(self):
        if not self.image_paths:
            self.image_index_progress["value"] = 0
            return

        total = len(self.image_paths)
        processed = len(self.processed_results)
        self.image_index_progress["value"] = (processed / total) * 100

    def request_load_for_index(self, index):
        if index < 0 or index >= len(self.image_paths):
            return
        if index in self.loaded_images:
            return
        if index in self.loading_requested:
            return

        self.loading_requested.add(index)
        self.loader_task_queue.put({
            "cmd": "LOAD_IMAGE",
            "path": self.image_paths[index],
<<<<<<< HEAD
            "index": index,
            "mode": "single"
=======
            "index": index
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        })

    def show_image_from_cache(self, index):
        if index not in self.loaded_images:
            return False

        path, image = self.loaded_images[index]
        self.current_image = image.copy()
        self.display_image(self.current_image, "original")

        if index in self.processed_results:
            saved_result = self.processed_results[index]
            self.processed_image = saved_result["image"].copy()
            self.display_image(self.processed_image, "processed")
        else:
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
        processed_count = len(self.processed_results)

        self.info_label.config(
            text=(
                f"Obraz {index + 1} z {len(self.image_paths)}\n"
                f"{file_name}\n"
                f"Przetworzone: {processed_count} z {len(self.image_paths)}"
            )
        )

        self.update_image_index_progress()
        self.set_status("Status: obraz pobrany z kolejki")

        if not self.processing_in_progress and not self.save_in_progress:
            self.request_controller_state("READY", "Obraz gotowy do analizy")

        return True

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz obraz",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )

        if not file_path:
            return

        self.image_paths = [file_path]
        self.current_index = 0
        self.loaded_images.clear()
        self.loading_requested.clear()
        self.processed_results.clear()

        self.current_image = None
        self.processed_image = None
        self.processed_photo = None

        self.processing_in_progress = False
        self.save_in_progress = False
        self.active_job_id = None
        self.cancelled_jobs.clear()

<<<<<<< HEAD
        self.batch_processing = False
        self.batch_output_folder = None
        self.batch_filter = None
        self.batch_total = 0
        self.batch_saved = 0
        self.batch_job_ids.clear()
        self.batch_output_paths.clear()

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        self.processed_canvas.delete("all")
        self.processed_canvas.create_text(
            int(self.processed_canvas["width"]) // 2,
            int(self.processed_canvas["height"]) // 2,
            text="Brak obrazu",
            font=("Arial", 13)
        )

        self.progress["value"] = 0
        self.set_status("Status: dodano 1 obraz do LoaderThread")
        self.request_controller_state("LOADING", "Wczytywanie pojedynczego obrazu")

        self.load_button.config(state="disabled")

        self.request_load_for_index(0)
        self.update_image_index_progress()

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
        self.loaded_images.clear()
        self.loading_requested.clear()
        self.processed_results.clear()

        self.current_image = None
        self.processed_image = None
        self.processed_photo = None

        self.processing_in_progress = False
        self.save_in_progress = False
        self.active_job_id = None
        self.cancelled_jobs.clear()

<<<<<<< HEAD
        self.batch_processing = False
        self.batch_output_folder = None
        self.batch_filter = None
        self.batch_total = 0
        self.batch_saved = 0
        self.batch_job_ids.clear()
        self.batch_output_paths.clear()

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        self.progress["value"] = 0

        self.processed_canvas.delete("all")
        self.processed_canvas.create_text(
            int(self.processed_canvas["width"]) // 2,
            int(self.processed_canvas["height"]) // 2,
            text="Brak obrazu",
            font=("Arial", 13)
        )

        self.set_status(f"Status: folder dodany ({len(files)} obrazów), ładowanie kolejki...")
        self.request_controller_state("LOADING", "Wczytywanie folderu obrazów")

        self.request_load_for_index(0)
        self.request_load_for_index(1)
        self.update_image_index_progress()

    def check_loader_queue(self):
        try:
            while True:
                result = self.loader_result_queue.get_nowait()

                self.load_button.config(state="normal")
                index = result.get("index")
<<<<<<< HEAD
                result_mode = result.get("mode", "single")
=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

                if result["status"] == "success":
                    self.loaded_images[index] = (result["path"], result["image"])

<<<<<<< HEAD
                    if result_mode == "batch":
                        if not self.batch_processing:
                            continue

                        self.analyzer_task_queue.put({
                            "cmd": "ANALYZE_IMAGE",
                            "image": result["image"].copy(),
                            "filter": result["filter"],
                            "job_id": result["job_id"],
                            "image_index": index,
                            "mode": "batch"
                        })
                    else:
                        if index == self.current_index and self.current_image is None:
                            self.show_image_from_cache(index)

                        self.request_load_for_index(index + 1)
                else:
                    if result_mode == "batch":
                        self.batch_processing = False
                        self.processing_in_progress = False
                        self.start_button.config(state="normal")
                        self.process_all_button.config(state="normal")
                        self.set_status("Status: błąd ładowania w trybie folderu")
                        self.request_controller_state("ERROR", "Błąd ładowania folderu")
                    else:
                        self.set_status("Status: błąd w LoaderThread")
                        self.request_controller_state("ERROR", "Błąd wczytywania obrazu")

                    messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu:\n{result['error']}")
=======
                    if index == self.current_index and self.current_image is None:
                        self.show_image_from_cache(index)

                    self.request_load_for_index(index + 1)
                else:
                    messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu:\n{result['error']}")
                    self.set_status("Status: błąd w LoaderThread")
                    self.request_controller_state("ERROR", "Błąd wczytywania obrazu")
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

        except queue.Empty:
            pass

        self.root.after(100, self.check_loader_queue)

    def start_processing(self):
        if self.current_image is None:
            self.set_status("Status: najpierw wczytaj obraz lub folder")
            return

        if self.processing_in_progress:
            self.set_status("Status: trwa już analiza obrazu")
            return

        selected_filter = self.filter_box.get()

        job_id = self.next_job_id
        self.next_job_id += 1
        self.active_job_id = job_id
        self.processing_in_progress = True

        self.progress["value"] = 20
        self.set_status(f"Status: dodano zadanie do ImageAnalyzerThread ({selected_filter})")
        self.request_controller_state("PROCESSING", f"Analiza filtrem {selected_filter}")

        self.start_button.config(state="disabled")

        self.analyzer_task_queue.put({
            "cmd": "ANALYZE_IMAGE",
            "image": self.current_image.copy(),
            "filter": selected_filter,
            "job_id": job_id,
<<<<<<< HEAD
            "image_index": self.current_index,
            "mode": "single"
=======
            "image_index": self.current_index
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        })

    def check_saver_queue(self):
        try:
            while True:
                result = self.saver_result_queue.get_nowait()
<<<<<<< HEAD
                result_mode = result.get("mode", "single")

                if result_mode == "batch" and not self.batch_processing:
                    continue

                if result["status"] == "success":
                    if result_mode == "batch":
                        self.batch_saved += 1

                        progress_value = (self.batch_saved / self.batch_total) * 100
                        self.progress["value"] = progress_value
                        self.image_index_progress["value"] = progress_value

                        self.set_status(
                            f"Status: zapisano {self.batch_saved}/{self.batch_total} obrazów przez SaverThread"
                        )

                        if self.batch_saved >= self.batch_total:
                            self.batch_processing = False
                            self.processing_in_progress = False
                            self.start_button.config(state="normal")
                            self.process_all_button.config(state="normal")

                            self.request_controller_state("READY", "Przetwarzanie folderu zakończone")

                            messagebox.showinfo(
                                "Gotowe",
                                f"Przetworzono i zapisano {self.batch_total} obrazów.\n"
                                f"Wyniki zapisano w:\n{self.batch_output_folder}"
                            )
                    else:
                        self.save_in_progress = False
                        self.save_button.config(state="normal")
                        self.set_status("Status: zapis zakończony przez SaverThread")
                        self.request_controller_state("READY", "Zapis zakończony")
                        messagebox.showinfo("Zapisano", f"Plik zapisano w:\n{result['output_path']}")
                else:
                    if result_mode == "batch":
                        self.batch_processing = False
                        self.processing_in_progress = False
                        self.start_button.config(state="normal")
                        self.process_all_button.config(state="normal")

                        self.set_status("Status: błąd zapisu w trybie folderu")
                        self.request_controller_state("ERROR", "Błąd zapisu folderu")
                        messagebox.showerror(
                            "Błąd",
                            f"Nie udało się zapisać jednego z obrazów:\n{result['error']}"
                        )
                    else:
                        self.save_in_progress = False
                        self.save_button.config(state="normal")
                        self.set_status("Status: błąd w SaverThread")
                        self.request_controller_state("ERROR", "Błąd zapisu obrazu")
                        messagebox.showerror("Błąd", f"Nie udało się zapisać obrazu:\n{result['error']}")
=======
                self.save_in_progress = False
                self.save_button.config(state="normal")

                if result["status"] == "success":
                    self.set_status("Status: zapis zakończony przez SaverThread")
                    self.request_controller_state("READY", "Zapis zakończony")
                    messagebox.showinfo("Zapisano", f"Plik zapisano w:\n{result['output_path']}")
                else:
                    self.set_status("Status: błąd w SaverThread")
                    self.request_controller_state("ERROR", "Błąd zapisu obrazu")
                    messagebox.showerror("Błąd", f"Nie udało się zapisać obrazu:\n{result['error']}")
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

        except queue.Empty:
            pass

        self.root.after(100, self.check_saver_queue)

    def show_previous_image(self):
        if not self.image_paths:
            return

        if self.current_index > 0:
            self.current_index -= 1
            if not self.show_image_from_cache(self.current_index):
                self.current_image = None
                self.set_status("Status: czekam na załadowanie obrazu...")
                self.request_controller_state("LOADING", "Oczekiwanie na poprzedni obraz")
                self.request_load_for_index(self.current_index)

    def show_next_image(self):
        if not self.image_paths:
            return

        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            if not self.show_image_from_cache(self.current_index):
                self.current_image = None
                self.set_status("Status: czekam na załadowanie obrazu...")
                self.request_controller_state("LOADING", "Oczekiwanie na następny obraz")
                self.request_load_for_index(self.current_index)

            self.request_load_for_index(self.current_index + 1)

    def process_entire_folder(self):
        if not self.image_paths:
            self.set_status("Status: najpierw wczytaj folder")
            return

<<<<<<< HEAD
        if self.batch_processing:
            self.set_status("Status: folder jest już przetwarzany")
            return

        selected_filter = self.filter_box.get()

        # Automatyczny folder zapisu wyników całego folderu
        project_dir = os.path.dirname(os.path.abspath(__file__))
        output_folder = os.path.join(project_dir, "results_caly")
        os.makedirs(output_folder, exist_ok=True)

        self.batch_processing = True
        self.processing_in_progress = True
        self.batch_output_folder = output_folder
        self.batch_filter = selected_filter
        self.batch_total = len(self.image_paths)
        self.batch_saved = 0
        self.batch_job_ids.clear()
        self.batch_output_paths.clear()

        self.progress["value"] = 0
        self.image_index_progress["value"] = 0

        self.start_button.config(state="disabled")
        self.process_all_button.config(state="disabled")

        self.set_status(
            f"Status: dodano folder do kolejek Producer–Consumer "
            f"({self.batch_total} obrazów), zapis do results_caly"
        )
        self.request_controller_state(
            "PROCESSING",
            "Przetwarzanie całego folderu przez wątki, zapis do results_caly"
        )

        for index, path in enumerate(self.image_paths):
            job_id = self.next_job_id
            self.next_job_id += 1
            self.batch_job_ids.add(job_id)

            base_name = os.path.basename(path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(
                output_folder,
                f"{name}_{selected_filter.lower()}{ext}"
            )
            self.batch_output_paths[index] = output_path

            if index in self.loaded_images:
                _, image = self.loaded_images[index]

                self.analyzer_task_queue.put({
                    "cmd": "ANALYZE_IMAGE",
                    "image": image.copy(),
                    "filter": selected_filter,
                    "job_id": job_id,
                    "image_index": index,
                    "mode": "batch"
                })
            else:
                self.loading_requested.add(index)

                self.loader_task_queue.put({
                    "cmd": "LOAD_IMAGE",
                    "path": path,
                    "index": index,
                    "job_id": job_id,
                    "filter": selected_filter,
                    "mode": "batch"
                })
=======
        output_folder = filedialog.askdirectory(title="Wybierz folder do zapisu wyników")
        if not output_folder:
            return

        selected_filter = self.filter_box.get()
        total_files = len(self.image_paths)

        self.request_controller_state("PROCESSING", "Przetwarzanie całego folderu")

        try:
            for index, path in enumerate(self.image_paths):
                image = Image.open(path)

                if selected_filter == "Grayscale":
                    processed = apply_grayscale(image)
                elif selected_filter == "Blur":
                    processed = apply_blur(image)
                elif selected_filter == "Edges":
                    processed = apply_edges(image)
                elif selected_filter == "Binary":
                    processed = apply_binary(image)
                else:
                    raise ValueError("Nieznany filtr")

                base_name = os.path.basename(path)
                name, ext = os.path.splitext(base_name)
                output_path = os.path.join(output_folder, f"{name}_{selected_filter.lower()}{ext}")

                processed.save(output_path)

                self.progress["value"] = ((index + 1) / total_files) * 100
                self.root.update_idletasks()

            self.set_status(f"Status: przetworzono cały folder filtrem {selected_filter}")
            self.request_controller_state("READY", "Przetwarzanie folderu zakończone")
            messagebox.showinfo(
                "Gotowe",
                f"Przetworzono {total_files} obrazów.\nWyniki zapisano w:\n{output_folder}"
            )

        except Exception as error:
            messagebox.showerror("Błąd", f"Nie udało się przetworzyć folderu:\n{error}")
            self.set_status("Status: błąd przetwarzania folderu")
            self.request_controller_state("ERROR", "Błąd przetwarzania folderu")
            self.progress["value"] = 0
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

    def save_result(self):
        if self.processed_image is None:
            self.set_status("Status: brak wyniku do zapisania")
            return

        if self.save_in_progress:
            self.set_status("Status: trwa już zapis")
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
            else:
                output_path = filedialog.asksaveasfilename(
                    title="Zapisz wynik",
                    defaultextension=".png",
                    filetypes=[
                        ("PNG file", "*.png"),
                        ("JPEG file", "*.jpg"),
                        ("BMP file", "*.bmp")
                    ]
                )
                if not output_path:
                    self.set_status("Status: zapis anulowany")
                    return

            self.save_in_progress = True
            self.save_button.config(state="disabled")
            self.set_status("Status: dodano zadanie do SaverThread")
            self.request_controller_state("SAVING", "Zapisywanie wyniku")

            self.saver_task_queue.put({
                "cmd": "SAVE_IMAGE",
                "image": self.processed_image.copy(),
<<<<<<< HEAD
                "output_path": output_path,
                "mode": "single"
=======
                "output_path": output_path
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
            })

        except Exception as error:
            self.save_in_progress = False
            self.request_controller_state("ERROR", "Błąd przygotowania zapisu")
            messagebox.showerror("Błąd", f"Nie udało się przygotować zapisu:\n{error}")

    def abort_processing(self):
<<<<<<< HEAD
        if self.batch_processing:
            self.batch_processing = False
            self.processing_in_progress = False
            self.batch_job_ids.clear()
            self.batch_output_paths.clear()

            self.start_button.config(state="normal")
            self.process_all_button.config(state="normal")

            self.progress["value"] = 0
            self.image_index_progress["value"] = 0

            self.set_status("Status: anulowano przetwarzanie folderu")
            self.request_controller_state("ABORTED", "Anulowano przetwarzanie całego folderu")
            return

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        if not self.processing_in_progress or self.active_job_id is None:
            self.set_status("Status: brak aktywnej operacji do anulowania")
            self.progress["value"] = 0
            return

        self.cancelled_jobs.add(self.active_job_id)
        self.active_job_id = None
        self.processing_in_progress = False
        self.start_button.config(state="normal")
        self.progress["value"] = 0
        self.set_status("Status: anulowano operację")
        self.request_controller_state("ABORTED", "Anulowano aktywną analizę obrazu")

    def on_close(self):
        self.loader_task_queue.put({"cmd": "STOP"})
<<<<<<< HEAD

        # Dwa komunikaty STOP, bo działają dwa wątki analizatora.
        self.analyzer_task_queue.put({"cmd": "STOP"})
        self.analyzer_task_queue.put({"cmd": "STOP"})

=======
        self.analyzer_task_queue.put({"cmd": "STOP"})
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        self.saver_task_queue.put({"cmd": "STOP"})
        self.controller_task_queue.put({"cmd": "STOP"})
        self.root.destroy()

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