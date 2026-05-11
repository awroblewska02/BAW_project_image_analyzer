import threading
import queue
import time
from image_filters import apply_grayscale, apply_blur, apply_edges, apply_binary


class FilterThread(threading.Thread):
    def __init__(self, task_queue, result_queue):
        super().__init__(daemon=True, name="FilterThread")
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True

    def run(self):
        print("Filter thread started:", threading.current_thread().name)
        print("Filter thread id:", threading.get_ident())

        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            command = task.get("cmd")

            if command == "STOP":
                self.running = False
                break

            if command == "APPLY_FILTER":
                image = task.get("image")
                selected_filter = task.get("filter")
                job_id = task.get("job_id")
                image_index = task.get("image_index")

                try:
                    # lekkie opóźnienie do pokazania działania i testu Abort
                    time.sleep(1.2)

                    if selected_filter == "Grayscale":
                        processed_image = apply_grayscale(image)
                    elif selected_filter == "Blur":
                        processed_image = apply_blur(image)
                    elif selected_filter == "Edges":
                        processed_image = apply_edges(image)
                    elif selected_filter == "Binary":
                        processed_image = apply_binary(image)
                    else:
                        raise ValueError("Nieznany filtr")

                    self.result_queue.put({
                        "status": "success",
                        "image": processed_image,
                        "filter": selected_filter,
                        "job_id": job_id,
                        "image_index": image_index
                    })
                except Exception as error:
                    self.result_queue.put({
                        "status": "error",
                        "error": str(error),
                        "job_id": job_id,
                        "image_index": image_index
                    })