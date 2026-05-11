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

                try:
                    image = Image.open(file_path)
                    image.load()

                    self.result_queue.put({
                        "status": "success",
                        "path": file_path,
                        "index": index,
                        "image": image
                    })
                except Exception as error:
                    self.result_queue.put({
                        "status": "error",
                        "path": file_path,
                        "index": index,
                        "error": str(error)
                    })