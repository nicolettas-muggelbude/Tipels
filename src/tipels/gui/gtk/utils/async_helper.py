"""
Tipels GTK GUI - Async Helper

Threading-Infrastruktur für asynchrone Operationen in GTK3
"""

import threading
from typing import Callable, Any, Optional
from gi.repository import GLib


class AsyncTask:
    """
    Wrapper für asynchrone Operationen mit thread-sicheren GTK-Updates.

    Verwendet GLib.idle_add für thread-sichere UI-Updates, da GTK3 nicht
    thread-safe ist.

    Beispiel:
        def scan_hardware():
            detector = HardwareDetector()
            return detector.scan_all()

        def on_complete(result, error=None):
            if error:
                show_error(error)
            else:
                display_devices(result)

        task = AsyncTask(scan_hardware, on_complete)
        task.run()
    """

    def __init__(
        self,
        task_func: Callable,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ):
        """
        Initialisiert AsyncTask.

        Args:
            task_func: Funktion die asynchron ausgeführt wird
            callback: Wird mit Ergebnis aufgerufen (im GTK-Main-Thread)
            error_callback: Wird bei Fehler aufgerufen (im GTK-Main-Thread)
        """
        self.task_func = task_func
        self.callback = callback
        self.error_callback = error_callback
        self._thread = None

    def run(self, *args, **kwargs):
        """
        Führt Task in separatem Thread aus.

        Args:
            *args: Positionsargumente für task_func
            **kwargs: Keyword-Argumente für task_func
        """
        def thread_func():
            try:
                result = self.task_func(*args, **kwargs)
                if self.callback:
                    GLib.idle_add(self.callback, result, None)
            except Exception as e:
                if self.error_callback:
                    GLib.idle_add(self.error_callback, e)
                elif self.callback:
                    # Fallback: Error als zweites Argument
                    GLib.idle_add(self.callback, None, e)

        self._thread = threading.Thread(target=thread_func, daemon=True)
        self._thread.start()

    def is_running(self) -> bool:
        """Prüft ob Task noch läuft."""
        return self._thread is not None and self._thread.is_alive()


def run_in_thread(func: Callable) -> Callable:
    """
    Decorator um Funktion asynchron auszuführen.

    Beispiel:
        @run_in_thread
        def long_operation():
            time.sleep(10)
            return "done"

        long_operation()  # Läuft in separatem Thread
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(
            target=func,
            args=args,
            kwargs=kwargs,
            daemon=True
        )
        thread.start()
        return thread
    return wrapper


def idle_add(func: Callable, *args) -> int:
    """
    Wrapper für GLib.idle_add mit besserer API.

    Args:
        func: Funktion die im GTK-Main-Thread ausgeführt wird
        *args: Argumente für func

    Returns:
        Source ID (für g_source_remove)
    """
    return GLib.idle_add(func, *args)
