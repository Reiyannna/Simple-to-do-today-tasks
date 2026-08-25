"""Midnight Galaxy theme: colors, fonts, and ttk style setup.

Centralizing the palette here keeps main.py focused on layout/behavior.
"""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# ---------- Palette ----------
BG_MAIN = "#1a1226"        # app background — darker than panels, easy on the eyes
BG_PANEL = "#2b1e3e"       # card / row background (even rows)
BG_PANEL_ALT = "#241a35"   # alternate row background (odd rows), subtle striping
BG_INPUT = "#241a35"       # entry / combobox field background
ACCENT = "#4a4e8f"         # cosmic blue — buttons, focus rings, header underline
ACCENT_HOVER = "#5f63b0"   # lighter blue for hover states
ACCENT_LIGHT = "#a490c2"   # lavender — secondary accent, days-left chip
TEXT_PRIMARY = "#f2f0fb"   # near-white silver — high-contrast primary text
TEXT_SECONDARY = "#c3b8dc" # lavender-silver — secondary text (chips, hints)
TEXT_MUTED = "#8b7fa8"     # muted lavender — placeholders, empty states
BORDER = "#3d2f56"         # subtle borders / dividers
WARNING = "#e0b88a"        # warm amber — task expiring soon
DANGER = "#e08a8a"         # soft red — remove button hover
SUCCESS = "#7fd9a8"        # soft green — reserved for future "done" accents

FONT_FAMILY_PRIMARY = "Segoe UI"       # crisp, native on Windows
FONT_FAMILY_FALLBACK = "Helvetica"     # sane cross-platform fallback


def resolve_font_family(root: tk.Misc) -> str:
    try:
        families = set(tkfont.families(root))
    except Exception:
        return FONT_FAMILY_FALLBACK
    return FONT_FAMILY_PRIMARY if FONT_FAMILY_PRIMARY in families else FONT_FAMILY_FALLBACK


class Fonts:
    """Font tuples, built once resolve_font_family() knows what's available."""

    def __init__(self, family: str):
        self.header = (family, 19, "bold")
        self.subheader = (family, 11)
        self.task = (family, 13)
        self.checkbox = (family, 15)
        self.meta = (family, 10)
        self.button = (family, 11, "bold")
        self.entry = (family, 12)
        self.empty_state = (family, 12)


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # noqa: E203


def apply_theme(root: tk.Tk) -> Fonts:
    """Configure the root window background and all ttk widget styles.

    Returns a Fonts instance so callers can reference font tuples by name.
    """
    family = resolve_font_family(root)
    fonts = Fonts(family)

    root.configure(bg=BG_MAIN)

    style = ttk.Style(root)
    # 'clam' is the most themeable built-in — required for real dark-mode colors.
    style.theme_use("clam")

    style.configure("TFrame", background=BG_MAIN)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("Row.TFrame", background=BG_PANEL)
    style.configure("RowAlt.TFrame", background=BG_PANEL_ALT)

    style.configure(
        "TLabel", background=BG_MAIN, foreground=TEXT_PRIMARY, font=fonts.task
    )
    style.configure(
        "Header.TLabel",
        background=BG_MAIN,
        foreground=TEXT_PRIMARY,
        font=fonts.header,
    )
    style.configure(
        "Subheader.TLabel",
        background=BG_MAIN,
        foreground=TEXT_MUTED,
        font=fonts.subheader,
    )
    style.configure(
        "Row.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=fonts.task
    )
    style.configure(
        "RowAlt.TLabel",
        background=BG_PANEL_ALT,
        foreground=TEXT_PRIMARY,
        font=fonts.task,
    )
    style.configure(
        "Meta.TLabel", background=BG_PANEL, foreground=ACCENT_LIGHT, font=fonts.meta
    )
    style.configure(
        "MetaAlt.TLabel",
        background=BG_PANEL_ALT,
        foreground=ACCENT_LIGHT,
        font=fonts.meta,
    )
    style.configure(
        "Empty.TLabel",
        background=BG_MAIN,
        foreground=TEXT_MUTED,
        font=fonts.empty_state,
    )

    # Buttons
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground=TEXT_PRIMARY,
        font=fonts.button,
        borderwidth=0,
        focusthickness=0,
        padding=(14, 8),
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER)],
    )

    # Entry
    style.configure(
        "Dark.TEntry",
        fieldbackground=BG_INPUT,
        foreground=TEXT_PRIMARY,
        insertcolor=TEXT_PRIMARY,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        borderwidth=1,
        padding=8,
    )
    style.map(
        "Dark.TEntry",
        bordercolor=[("focus", ACCENT)],
        lightcolor=[("focus", ACCENT)],
        darkcolor=[("focus", ACCENT)],
    )

    # Combobox
    style.configure(
        "Dark.TCombobox",
        fieldbackground=BG_INPUT,
        background=BG_INPUT,
        foreground=TEXT_PRIMARY,
        arrowcolor=TEXT_SECONDARY,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        borderwidth=1,
        padding=6,
    )
    style.map(
        "Dark.TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        foreground=[("readonly", TEXT_PRIMARY)],
        bordercolor=[("focus", ACCENT)],
    )
    # The dropdown listbox isn't a ttk widget — themed via the option database.
    root.option_add("*TCombobox*Listbox.background", BG_INPUT)
    root.option_add("*TCombobox*Listbox.foreground", TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", TEXT_PRIMARY)
    root.option_add("*TCombobox*Listbox.font", fonts.entry)

    # Scrollbar
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=BG_PANEL,
        troughcolor=BG_MAIN,
        bordercolor=BG_MAIN,
        arrowcolor=TEXT_SECONDARY,
        relief="flat",
    )
    style.map("Dark.Vertical.TScrollbar", background=[("active", ACCENT)])

    return fonts
