import threading
import queue


class ControllerThread(threading.Thread):
    """
    Kontroler aplikacji działający jako maszyna stanów.

    Ten wątek nie przetwarza obrazów i nie aktualizuje GUI bezpośrednio.
    Jego zadaniem jest przechowywanie aktualnego stanu aplikacji
    oraz przekazywanie informacji o zmianach stanu do GUI przez kolejkę wyników.
    """

    VALID_STATES = {
        "IDLE",
        "LOADING",
        "READY",
        "PROCESSING",
        "SAVING",
        "ABORTED",
        "ERROR",
        "CLOSING"
    }

    def __init__(self, task_queue, result_queue):
        super().__init__(daemon=True, name="ControllerThread")
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.state = "IDLE"

    def run(self):
        print("Controller thread started:", threading.current_thread().name)
        print("Controller thread id:", threading.get_ident())

        self.send_state_update("INIT")

        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            command = task.get("cmd")

            if command == "STOP":
                self.change_state("CLOSING", "Zamykanie aplikacji")
                self.running = False
                break

            if command == "SET_STATE":
                new_state = task.get("state")
                event = task.get("event", "")

                if new_state in self.VALID_STATES:
                    self.change_state(new_state, event)
                else:
                    self.change_state("ERROR", f"Nieznany stan: {new_state}")

    def change_state(self, new_state, event):
        old_state = self.state
        self.state = new_state

        self.result_queue.put({
            "status": "state_changed",
            "old_state": old_state,
            "new_state": new_state,
            "event": event
        })

    def send_state_update(self, event):
        self.result_queue.put({
            "status": "state_changed",
            "old_state": self.state,
            "new_state": self.state,
            "event": event
        })