import os
import sys
import threading
import termios
import tty
import select
from collections import deque
from ui import console

_MESSAGE_QUEUE = deque()
_QUEUE_LOCK = threading.Lock()
_PENDING_DRAFT = ""

def get_next_queued_message():
    with _QUEUE_LOCK:
        if _MESSAGE_QUEUE:
            return _MESSAGE_QUEUE.popleft()
        return None

def has_queued_messages():
    with _QUEUE_LOCK:
        return len(_MESSAGE_QUEUE) > 0

def add_queued_message(msg):
    if msg and msg.strip():
        with _QUEUE_LOCK:
            _MESSAGE_QUEUE.append(msg.strip())

def set_pending_draft(text):
    global _PENDING_DRAFT
    _PENDING_DRAFT = text

def get_and_clear_pending_draft():
    global _PENDING_DRAFT
    draft = _PENDING_DRAFT
    _PENDING_DRAFT = ""
    return draft

class AsyncInputQueueWatcher:
    """
    Background listener that lets user type & press ENTER to queue messages
    or press ESC/Ctrl+C to cancel while AI is streaming, thinking, or running tools.
    Preserves unsubmitted draft text when task completes.
    """
    def __init__(self):
        self.stop_requested = threading.Event()
        self._thread = None
        self._running = False
        self._old_settings = None
        self._current_buffer = []

    def start(self):
        if not sys.stdin.isatty():
            return
        self._running = True
        self.stop_requested.clear()
        self._current_buffer = []
        try:
            fd = sys.stdin.fileno()
            self._old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
        except Exception:
            pass

    def _listen(self):
        try:
            fd = sys.stdin.fileno()
            while self._running and not self.stop_requested.is_set():
                r, _, _ = select.select([fd], [], [], 0.05)
                if r:
                    try:
                        raw = os.read(fd, 1024)
                    except Exception:
                        break
                    if not raw:
                        continue

                    # Handle ESC or Ctrl+C -> cancel current AI execution
                    if raw in (b'\x1b', b'\x03'):
                        self.stop_requested.set()
                        break

                    # Handle Enter -> queue message
                    if b'\r' in raw or b'\n' in raw:
                        line_text = "".join(self._current_buffer).strip()
                        self._current_buffer = []
                        if line_text:
                            add_queued_message(line_text)
                            console.print(f"\n[bold cyan]⚡ [Antrean]:[/bold cyan] [bold white]\"{line_text}\"[/bold white] [dim](akan dieksekusi setelah selesai)[/dim]")
                        continue

                    # Handle Backspace
                    if raw in (b'\x7f', b'\x08'):
                        if self._current_buffer:
                            self._current_buffer.pop()
                        continue

                    # Printable text characters
                    try:
                        decoded = raw.decode('utf-8', errors='ignore')
                        printable = [c for c in decoded if c.isprintable() or c == ' ']
                        if printable:
                            self._current_buffer.extend(printable)
                    except Exception:
                        pass
        except Exception:
            pass

    def stop(self):
        self._running = False
        if self._current_buffer:
            leftover = "".join(self._current_buffer).strip()
            if leftover:
                set_pending_draft(leftover)
            self._current_buffer = []
        if self._old_settings is not None:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass
