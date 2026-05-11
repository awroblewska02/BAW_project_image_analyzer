import threading
import queue
from PIL import Image


class LoaderThread(threading.Thread):
    def __init__(self, task_queue, result_queue):
        super().__init__(daemon=True, name="LoaderThread")
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True

    def run(self):
        print("Loader thread started:", threading.current_thread().name)
        print("Loader thread id:", threading.get_ident())

        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            command = task.get("cmd")

            if command == "STOP":
                self.running = False
                break

            if command == "LOAD_IMAGE":
                file_path = task.get("path")
                index = task.get("index")

<<<<<<< HEAD
                # Dodatkowe pola używane przy przetwarzaniu całego folderu
                job_id = task.get("job_id")
                selected_filter = task.get("filter")
                mode = task.get("mode", "single")

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                try:
                    image = Image.open(file_path)
                    image.load()

                    self.result_queue.put({
                        "status": "success",
                        "path": file_path,
                        "index": index,
<<<<<<< HEAD
                        "image": image,
                        "job_id": job_id,
                        "filter": selected_filter,
                        "mode": mode
                    })

=======
                        "image": image
                    })
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                except Exception as error:
                    self.result_queue.put({
                        "status": "error",
                        "path": file_path,
                        "index": index,
<<<<<<< HEAD
                        "error": str(error),
                        "job_id": job_id,
                        "filter": selected_filter,
                        "mode": mode
=======
                        "error": str(error)
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                    })