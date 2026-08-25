"""System tray icon for keeping the app alive in the background.

Runs pystray's icon loop on its own daemon thread. Tray callbacks fire on
that thread, so they never touch Tkinter directly — they only push an
action string onto a thread-safe queue, which the Tk main loop polls via
`root.after(...)`. This avoids cross-thread Tkinter calls, which are not
reliably safe.
"""
from __future__ import annotations

import queue
import threading
from typing import Optional

try:
    import pystray
    from PIL import Image, ImageDraw

    TRAY_AVAILABLE = True
except Exception:
    # Covers missing packages (ImportError) as well as backend init failures
    # (e.g. pystray's Linux backend needing a GTK/AppIndicator stack that
    # isn't installed). Either way, the app should degrade gracefully
    # rather than crash on import.
    TRAY_AVAILABLE = False

from theme import BG_PANEL, ACCENT, TEXT_PRIMARY, hex_to_rgb

APP_NAME = "Today's To-Do"


def _build_icon_image():
    """Draw a small rounded-square checkmark icon matching the app theme."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [3, 3, size - 3, size - 3],
        radius=16,
        fill=hex_to_rgb(BG_PANEL) + (255,),
        outline=hex_to_rgb(ACCENT) + (255,),
        width=4,
    )
    draw.line(
        [(17, 33), (27, 45), (48, 18)],
        fill=hex_to_rgb(TEXT_PRIMARY) + (255,),
        width=6,
        joint="curve",
    )
    return img


class TrayController:
    """Owns the pystray Icon and its thread; exposes a queue for the app to poll."""

    def __init__(self):
        self.actions: "queue.Queue[str]" = queue.Queue()
        self._icon: Optional["pystray.Icon"] = None
        self._thread: Optional[threading.Thread] = None

    def _on_show(self, icon, item=None):
        self.actions.put("show")

    def _on_quit(self, icon, item=None):
        self.actions.put("quit")

    def start(self):
        if not TRAY_AVAILABLE:
            return False

        try:
            menu = pystray.Menu(
                pystray.MenuItem("Show " + APP_NAME, self._on_show, default=True),
                pystray.MenuItem("Quit", self._on_quit),
            )
            self._icon = pystray.Icon(
                "today_todo", _build_icon_image(), APP_NAME, menu
            )
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
            return True
        except Exception:
            # Tray backend failed at runtime (e.g. no system tray available).
            # Fall back to normal window behavior instead of crashing.
            self._icon = None
            self._thread = None
            return False

    def stop(self):
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
