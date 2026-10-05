import os
import sys
import shutil
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
    while AI is streaming, thinking, or running tools!
    Renders a live Antigravity prompt box at the bottom as you type.
    ENTER queues the message. If unfinished when AI completes, preserves draft.
    ESC / Ctrl+C triggers stop_requested for immediate cancellation.
    """
    def __init__(self):
        self.stop_requested = threading.Event()
        self._thread = None
        self._running = False
        self._old_settings = None
        self._current_buffer = []
        self._box_rendered = False

    def start(self):
        if not sys.stdin.isatty():
            return
        self._running = True
        self.stop_requested.clear()
        self._current_buffer = []
        self._box_rendered = False
        try:
            fd = sys.stdin.fileno()
            self._old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
        except Exception:
            pass

    def _render_box(self):
        try:
            term_cols = shutil.get_terminal_size((80, 24)).columns
        except Exception:
            term_cols = 80
            
        div_w = max(10, term_cols - 2)
        div = f"\033[90m{'─' * div_w}\033[0m"
        text = "".join(self._current_buffer)
        
        # Max text window
        max_w = max(10, term_cols - 6)
        disp_text = text if len(text) <= max_w else text[-max_w:]
        
        cursor_block = "\033[42m \033[0m"
        input_line = f"\033[90m>\033[0m \033[1;37m{disp_text}\033[0m{cursor_block}"
        
        left_str = "esc to cancel"
        right_str = "Antrean"
        if term_cols >= 36:
            spaces = max(2, term_cols - 2 - len(left_str) - len(right_str))
            footer = f"\033[90m{left_str}\033[0m{' ' * spaces}\033[1;36m{right_str}\033[0m"
        else:
            footer = f"\033[90m{left_str}\033[0m"
            
        prefix = "\033[3A\r" if self._box_rendered else "\r\n"
        self._box_rendered = True
            
        box_str = (
            f"{prefix}\033[2K{div}\r\n"
            f"\033[2K{input_line}\r\n"
            f"\033[2K{div}\r\n"
            f"\033[2K{footer}"
        )
        sys.stdout.write(box_str)
        sys.stdout.flush()

    def _clear_box(self):
        if self._box_rendered:
            sys.stdout.write("\033[3A\r\033[2K\r\n\033[2K\r\n\033[2K\r\n\033[2K\033[3A\r")
            sys.stdout.flush()
            self._box_rendered = False

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
                        self._clear_box()
                        if line_text:
                            add_queued_message(line_text)
                            sys.stdout.write(f"\r\033[1;36m⚡ [Antrean]:\033[0m \033[1;37m\"{line_text}\"\033[0m \033[90m(akan dijalankan setelah tugas selesai)\033[0m\r\n")
                            sys.stdout.flush()
                        continue

                    # Handle Backspace
                    if raw in (b'\x7f', b'\x08'):
                        if self._current_buffer:
                            self._current_buffer.pop()
                            if self._current_buffer:
                                self._render_box()
                            else:
                                self._clear_box()
                        continue

                    # Printable text characters
                    try:
                        decoded = raw.decode('utf-8', errors='ignore')
                        printable = [c for c in decoded if c.isprintable() or c == ' ']
                        if printable:
                            self._current_buffer.extend(printable)
                            self._render_box()
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
        self._clear_box()
        if self._old_settings is not None:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass

