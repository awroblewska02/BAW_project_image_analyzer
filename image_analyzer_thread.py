import threading
import queue
import time
from image_filters import apply_grayscale, apply_blur, apply_edges, apply_binary


class ImageAnalyzerThread(threading.Thread):
    """
    Analizator obrazu działający jako maszyna stanów.

<<<<<<< HEAD
    W projekcie można uruchomić dwa obiekty tej klasy:
    - ImageAnalyzerThread-1
    - ImageAnalyzerThread-2

    Oba analizatory pobierają zadania z tej samej kolejki task_queue
    i zwracają wyniki do tej samej kolejki result_queue.
=======
    Ten wątek odpowiada za wykonanie wybranego algorytmu przetwarzania obrazu.
    Nie aktualizuje GUI bezpośrednio. Informacje o stanie i wyniku pracy
    przekazuje do GUI przez kolejkę wyników.
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
    """

    VALID_STATES = {
        "WAITING",
        "PREPARING",
        "ANALYZING",
        "FINISHED",
        "ERROR",
        "STOPPED"
    }

<<<<<<< HEAD
    def __init__(self, task_queue, result_queue, name="ImageAnalyzerThread"):
        super().__init__(daemon=True, name=name)
=======
    def __init__(self, task_queue, result_queue):
        super().__init__(daemon=True, name="ImageAnalyzerThread")
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.state = "WAITING"

    def run(self):
        print("Image analyzer thread started:", threading.current_thread().name)
        print("Image analyzer thread id:", threading.get_ident())

        self.send_state_update("INIT")

        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            command = task.get("cmd")

            if command == "STOP":
                self.change_state("STOPPED", "Zamykanie analizatora obrazu")
                self.running = False
                break

            if command == "ANALYZE_IMAGE":
                image = task.get("image")
                selected_filter = task.get("filter")
                job_id = task.get("job_id")
                image_index = task.get("image_index")
<<<<<<< HEAD
                mode = task.get("mode", "single")
                worker = threading.current_thread().name

                try:
                    self.change_state("PREPARING", f"{worker}: przygotowanie obrazu do analizy")

                    image_to_process = image.copy()

                    self.change_state("ANALYZING", f"{worker}: wykonywanie algorytmu {selected_filter}")

                    # Lekkie opóźnienie do pokazania działania maszyny stanów i testu Abort
=======

                try:
                    self.change_state("PREPARING", "Przygotowanie obrazu do analizy")

                    image_to_process = image.copy()

                    self.change_state("ANALYZING", f"Wykonywanie algorytmu: {selected_filter}")

                    # lekkie opóźnienie do pokazania działania maszyny stanów i testu Abort
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                    time.sleep(1.2)

                    if selected_filter == "Grayscale":
                        processed_image = apply_grayscale(image_to_process)
                    elif selected_filter == "Blur":
                        processed_image = apply_blur(image_to_process)
                    elif selected_filter == "Edges":
                        processed_image = apply_edges(image_to_process)
                    elif selected_filter == "Binary":
                        processed_image = apply_binary(image_to_process)
                    else:
                        raise ValueError("Nieznany filtr")

<<<<<<< HEAD
                    self.change_state("FINISHED", f"{worker}: analiza obrazu zakończona")
=======
                    self.change_state("FINISHED", "Analiza obrazu zakończona")
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

                    self.result_queue.put({
                        "type": "result",
                        "status": "success",
                        "image": processed_image,
                        "filter": selected_filter,
                        "job_id": job_id,
<<<<<<< HEAD
                        "image_index": image_index,
                        "mode": mode,
                        "worker": worker
                    })

                    self.change_state("WAITING", f"{worker}: oczekiwanie na kolejne zadanie")

                except Exception as error:
                    self.change_state("ERROR", f"{worker}: {error}")
=======
                        "image_index": image_index
                    })

                    self.change_state("WAITING", "Oczekiwanie na kolejne zadanie")

                except Exception as error:
                    self.change_state("ERROR", str(error))
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

                    self.result_queue.put({
                        "type": "result",
                        "status": "error",
                        "error": str(error),
                        "job_id": job_id,
<<<<<<< HEAD
                        "image_index": image_index,
                        "mode": mode,
                        "worker": worker
                    })

                    self.change_state("WAITING", f"{worker}: oczekiwanie po błędzie")

    def change_state(self, new_state, event):
        if new_state not in self.VALID_STATES:
            event = f"Nieznany stan analizatora: {new_state}"
            new_state = "ERROR"
=======
                        "image_index": image_index
                    })

                    self.change_state("WAITING", "Oczekiwanie po błędzie")

    def change_state(self, new_state, event):
        if new_state not in self.VALID_STATES:
            new_state = "ERROR"
            event = f"Nieznany stan analizatora: {new_state}"
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd

        old_state = self.state
        self.state = new_state

        self.result_queue.put({
            "type": "state",
            "status": "state_changed",
            "old_state": old_state,
            "new_state": new_state,
<<<<<<< HEAD
            "event": event,
            "worker": threading.current_thread().name
=======
            "event": event
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
        })

    def send_state_update(self, event):
        self.result_queue.put({
            "type": "state",
            "status": "state_changed",
            "old_state": self.state,
            "new_state": self.state,
<<<<<<< HEAD
            "event": event,
            "worker": threading.current_thread().name
        })
=======
            "event": event
        })
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
