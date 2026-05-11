import threading
import queue
import os


class SaverThread(threading.Thread):
    def __init__(self, task_queue, result_queue):
        super().__init__(daemon=True, name="SaverThread")
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True

    def run(self):
        print("Saver thread started:", threading.current_thread().name)
        print("Saver thread id:", threading.get_ident())

        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            command = task.get("cmd")

            if command == "STOP":
                self.running = False
                break

            if command == "SAVE_IMAGE":
                image = task.get("image")
                output_path = task.get("output_path")

<<<<<<< HEAD
                # Dodatkowe pola używane przy przetwarzaniu całego folderu
                job_id = task.get("job_id")
                image_index = task.get("image_index")
                mode = task.get("mode", "single")

=======
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                try:
                    folder = os.path.dirname(output_path)
                    if folder:
                        os.makedirs(folder, exist_ok=True)

                    image.save(output_path)

                    self.result_queue.put({
                        "status": "success",
<<<<<<< HEAD
                        "output_path": output_path,
                        "job_id": job_id,
                        "image_index": image_index,
                        "mode": mode
                    })

                except Exception as error:
                    self.result_queue.put({
                        "status": "error",
                        "error": str(error),
                        "job_id": job_id,
                        "image_index": image_index,
                        "mode": mode
=======
                        "output_path": output_path
                    })
                except Exception as error:
                    self.result_queue.put({
                        "status": "error",
                        "error": str(error)
>>>>>>> 7ef02b2bd1b2bfa4279f95537273f15b108b01dd
                    })