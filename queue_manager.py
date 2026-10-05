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

class AsyncInputQueueWatcher:
    """
    Background listener that lets user type & press ENTER to queue messages
    while AI is streaming, thinking, or running tools!
    ESC / Ctrl+C triggers stop_requested for cancellation.
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
                            sys.stdout.write(f"\r\n\033[1;36m⚡ Message queued:\033[0m \033[1;37m\"{line_text}\"\033[0m \033[90m(will execute when AI completes)\033[0m\r\n")
                            sys.stdout.flush()
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
        if self._old_settings is not None:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass
