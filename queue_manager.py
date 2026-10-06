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
    Provides real-time visual typing feedback and preserves unsubmitted draft text when task completes.
    """
    def __init__(self, on_change=None):
        self.stop_requested = threading.Event()
        self._thread = None
        self._running = False
        self._old_settings = None
        self._current_buffer = []
        self.on_change = on_change
        self._directly_rendered = False

    def get_buffer_text(self):
        return "".join(self._current_buffer)

    def _notify_or_render(self):
        if self.on_change is not None:
            try:
                self.on_change()
            except Exception:
                pass
            return

        if not sys.stdin.isatty():
            return

        text = "".join(self._current_buffer)
        if text:
            try:
                from styles import get_current_style_settings, THEMES_MAP, get_safe_width
                _, theme_id = get_current_style_settings()
                p = THEMES_MAP.get(theme_id, THEMES_MAP["terminal"])["palette"]
                safe_w = get_safe_width()
            except Exception:
                p = {"prompt_user": "\033[1;36m"}
                safe_w = 80

            max_w = max(8, safe_w - 4)
            disp = text[-max_w:] if len(text) > max_w else text
            user_color = p.get('prompt_user', '\033[1;36m')
            prefix = f"{user_color}>\033[0m "
            sys.stdout.write(f"\r\033[2K{prefix}\033[1;37m{disp}\033[0m\033[42m \033[0m")
            sys.stdout.flush()
            self._directly_rendered = True
        else:
            if self._directly_rendered:
                sys.stdout.write("\r\033[2K")
                sys.stdout.flush()
                self._directly_rendered = False

    def start(self):
        if not sys.stdin.isatty():
            return
        self._running = True
        self.stop_requested.clear()
        self._current_buffer = []
        self._directly_rendered = False
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

                    # Handle Ctrl+C -> cancel current execution immediately
                    if raw == b'\x03':
                        self.stop_requested.set()
                        self._current_buffer = []
                        self._notify_or_render()
                        break

                    # Handle ESC key (with disambiguation for arrow escape sequences)
                    if raw == b'\x1b':
                        r_esc, _, _ = select.select([fd], [], [], 0.05)
                        if r_esc:
                            extra = os.read(fd, 32)
                            raw = raw + extra
                        if raw == b'\x1b':
                            self.stop_requested.set()
                            self._current_buffer = []
                            self._notify_or_render()
                            break

                    # Ignore arrow keys/cursor control sequences during background execution
                    if raw.startswith((b'\x1b[', b'\x1bO')):
                        continue

                    # Process input stream tokens
                    i = 0
                    while i < len(raw):
                        b = raw[i:i+1]
                        if b in (b'\r', b'\n'):
                            line_text = "".join(self._current_buffer).strip()
                            self._current_buffer = []
                            self._notify_or_render()
                            if line_text:
                                add_queued_message(line_text)
                                console.print(f"[bold cyan]⚡ [Antrean]:[/bold cyan] [bold white]\"{line_text}\"[/bold white] [dim](akan dieksekusi setelah selesai)[/dim]")
                            i += 1
                        elif b in (b'\x7f', b'\x08'):
                            if self._current_buffer:
                                self._current_buffer.pop()
                                self._notify_or_render()
                            i += 1
                        elif b == b'\x15':  # Ctrl+U
                            if self._current_buffer:
                                self._current_buffer = []
                                self._notify_or_render()
                            i += 1
                        elif b == b'\x1b':
                            i += 1
                        else:
                            char_found = False
                            for length in (1, 2, 3, 4):
                                if i + length <= len(raw):
                                    chunk = raw[i:i+length]
                                    try:
                                        decoded_c = chunk.decode('utf-8')
                                        if decoded_c.isprintable() or decoded_c == ' ':
                                            self._current_buffer.append(decoded_c)
                                            self._notify_or_render()
                                        char_found = True
                                        i += length
                                        break
                                    except UnicodeDecodeError:
                                        continue
                            if not char_found:
                                i += 1
        except Exception:
            pass

    def stop(self):
        self._running = False
        if self._current_buffer:
            leftover = "".join(self._current_buffer).strip()
            if leftover:
                set_pending_draft(leftover)
            self._current_buffer = []
        if self._directly_rendered:
            try:
                sys.stdout.write("\r\033[2K")
                sys.stdout.flush()
            except Exception:
                pass
            self._directly_rendered = False
        if self._old_settings is not None:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass
