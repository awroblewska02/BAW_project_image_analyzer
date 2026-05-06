from PIL import Image


def loader_worker(file_path, result_queue):
    """
    Funkcja wykonywana w osobnym wątku.
    Odpowiada tylko za wczytanie obrazu z dysku.

    Ważne:
    - ta funkcja NIE aktualizuje GUI,
    - wynik przekazuje do kolejki result_queue,
    - GUI odbierze wynik później w głównym wątku.
    """
    try:
        image = Image.open(file_path)
        image.load()

        result_queue.put({
            "status": "success",
            "path": file_path,
            "image": image
        })

    except Exception as error:
        result_queue.put({
            "status": "error",
            "path": file_path,
            "error": str(error)
        })