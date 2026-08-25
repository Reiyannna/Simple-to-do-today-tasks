"""Today's To-Do — a dark-themed habit checklist app with tray support.

Run directly:      python main.py
Run hidden:         double-click run_hidden.pyw (no console window)
Run on login:       see add_to_startup.ps1
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk, messagebox

from task import Task, DURATION_PRESETS, process_tasks
from storage import load_tasks, save_tasks
from theme import (
    apply_theme,
    BG_MAIN,
    BG_PANEL,
    BG_PANEL_ALT,
    ACCENT,
    ACCENT_LIGHT,
    TEXT_MUTED,
    TEXT_SECONDARY,
    WARNING,
    DANGER,
)
from tray import TrayController, TRAY_AVAILABLE

# Make text crisp on high-DPI Windows displays.
if sys.platform.startswith("win"):
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

MIDNIGHT_CHECK_INTERVAL_MS = 60_000  # re-check for day rollover once a minute
TRAY_POLL_INTERVAL_MS = 150


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Today's To-Do")
        self.geometry("460x580")
        self.minsize(360, 360)

        self.fonts = apply_theme(self)

        self.tasks: list[Task] = process_tasks(load_tasks())
        save_tasks(self.tasks)

        self._build_layout()
        self._render_tasks()

        self.tray = TrayController()
        self.tray_active = self.tray.start()
        if self.tray_active:
            self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)
            self.after(TRAY_POLL_INTERVAL_MS, self._poll_tray_queue)
        else:
            # No pystray/Pillow installed — fall back to a normal quit-on-close app.
            self.protocol("WM_DELETE_WINDOW", self._quit_app)

        self.after(MIDNIGHT_CHECK_INTERVAL_MS, self._check_for_day_rollover)

    # ---------- UI construction ----------

    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        header = ttk.Frame(self, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Today's Habits", style="Header.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Check off what you've done today",
            style="Subheader.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        underline = tk.Frame(header, bg=ACCENT, height=2)
        underline.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        # Scrollable checklist card
        list_outer = ttk.Frame(self, style="TFrame")
        list_outer.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        list_outer.columnconfigure(0, weight=1)
        list_outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            list_outer, highlightthickness=0, bg=BG_MAIN, bd=0
        )
        scrollbar = ttk.Scrollbar(
            list_outer,
            orient="vertical",
            command=canvas.yview,
            style="Dark.Vertical.TScrollbar",
        )
        self.tasks_container = ttk.Frame(canvas, style="TFrame")

        self.tasks_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.tasks_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas = canvas

        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        canvas.bind_all("<Button-4>", self._on_mousewheel)
        canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Bottom bar: add a task
        add_frame = ttk.Frame(self, style="TFrame")
        add_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(6, 20))
        add_frame.columnconfigure(0, weight=1)

        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(
            add_frame, textvariable=self.name_var, style="Dark.TEntry",
            font=self.fonts.entry,
        )
        name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=3)
        name_entry.bind("<Return>", lambda e: self._add_task())

        self.duration_var = tk.StringVar(value=DURATION_PRESETS[0][0])
        duration_menu = ttk.Combobox(
            add_frame,
            textvariable=self.duration_var,
            values=[label for label, _ in DURATION_PRESETS],
            state="readonly",
            width=11,
            style="Dark.TCombobox",
            font=self.fonts.entry,
        )
        duration_menu.grid(row=0, column=1, padx=(0, 8))

        add_btn = ttk.Button(
            add_frame, text="+ Add", command=self._add_task, style="Accent.TButton"
        )
        add_btn.grid(row=0, column=2)

        if not TRAY_AVAILABLE:
            hint = ttk.Label(
                self,
                text="Tip: install pystray + Pillow for a tray icon (see requirements.txt)",
                style="Subheader.TLabel",
            )
            hint.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 10))

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    # ---------- Rendering ----------

    def _render_tasks(self):
        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        self.tasks_container.columnconfigure(1, weight=1)

        if not self.tasks:
            ttk.Label(
                self.tasks_container,
                text="No habits yet — add one below to get started.",
                style="Empty.TLabel",
            ).grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=16)
            return

        for row, task in enumerate(self.tasks):
            self._render_task_row(row, task)

    def _render_task_row(self, row: int, task: Task):
        alt = row % 2 == 1
        row_bg = BG_PANEL_ALT if alt else BG_PANEL
        row_style = "RowAlt.TFrame" if alt else "Row.TFrame"
        label_style = "RowAlt.TLabel" if alt else "Row.TLabel"

        row_frame = ttk.Frame(self.tasks_container, style=row_style)
        row_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=1)
        row_frame.columnconfigure(1, weight=1)
        self.tasks_container.columnconfigure(0, weight=1)

        # Custom checkbox glyph (full color control vs. native ttk indicator)
        checked = task.done_today
        check_var = tk.StringVar(value="\u2611" if checked else "\u2610")
        check_lbl = tk.Label(
            row_frame,
            textvariable=check_var,
            font=self.fonts.checkbox,
            bg=row_bg,
            fg=ACCENT_LIGHT if checked else TEXT_SECONDARY,
            cursor="hand2",
            padx=10,
            pady=8,
        )
        check_lbl.grid(row=0, column=0, sticky="w")

        def toggle(event=None, t=task, var=check_var, lbl=check_lbl):
            t.done_today = not t.done_today
            var.set("\u2611" if t.done_today else "\u2610")
            lbl.configure(fg=ACCENT_LIGHT if t.done_today else TEXT_SECONDARY)
            save_tasks(self.tasks)

        check_lbl.bind("<Button-1>", toggle)

        name_lbl = ttk.Label(row_frame, text=task.name, style=label_style)
        name_lbl.grid(row=0, column=1, sticky="w", pady=8)

        days_left = task.days_left()
        if days_left <= 0:
            expiry_text, expiry_color = "expires today", DANGER
        elif days_left <= 2:
            expiry_text, expiry_color = f"{days_left}d left", WARNING
        else:
            expiry_text, expiry_color = f"{days_left}d left", ACCENT_LIGHT

        expiry_lbl = tk.Label(
            row_frame,
            text=expiry_text,
            font=self.fonts.meta,
            bg=row_bg,
            fg=expiry_color,
            padx=8,
        )
        expiry_lbl.grid(row=0, column=2, sticky="e")

        remove_lbl = tk.Label(
            row_frame,
            text="\u2715",
            font=self.fonts.meta,
            bg=row_bg,
            fg=TEXT_MUTED,
            cursor="hand2",
            padx=10,
            pady=8,
        )
        remove_lbl.grid(row=0, column=3, sticky="e")
        remove_lbl.bind("<Button-1>", lambda e, t=task: self._remove_task(t))
        remove_lbl.bind("<Enter>", lambda e, lbl=remove_lbl: lbl.configure(fg=DANGER))
        remove_lbl.bind(
            "<Leave>", lambda e, lbl=remove_lbl: lbl.configure(fg=TEXT_MUTED)
        )

    # ---------- Actions ----------

    def _add_task(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showinfo("Task name needed", "Type a task name before adding.")
            return

        label = self.duration_var.get()
        duration_days = dict(DURATION_PRESETS).get(label, 1)

        self.tasks.append(Task.new(name, duration_days))
        save_tasks(self.tasks)
        self.name_var.set("")
        self._render_tasks()

    def _remove_task(self, task: Task):
        self.tasks = [t for t in self.tasks if t.id != task.id]
        save_tasks(self.tasks)
        self._render_tasks()

    # ---------- Background behavior: midnight rollover while running ----------

    def _check_for_day_rollover(self):
        before = [(t.id, t.done_today) for t in self.tasks]
        self.tasks = process_tasks(self.tasks)
        after = [(t.id, t.done_today) for t in self.tasks]
        if before != after:
            save_tasks(self.tasks)
            self._render_tasks()
        self.after(MIDNIGHT_CHECK_INTERVAL_MS, self._check_for_day_rollover)

    # ---------- Tray integration ----------

    def _hide_to_tray(self):
        self.withdraw()

    def _show_from_tray(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _poll_tray_queue(self):
        try:
            while True:
                action = self.tray.actions.get_nowait()
                if action == "show":
                    self._show_from_tray()
                elif action == "quit":
                    self._quit_app()
                    return  # app is shutting down; stop polling
        except Exception:
            pass  # queue.Empty is expected most cycles
        self.after(TRAY_POLL_INTERVAL_MS, self._poll_tray_queue)

    def _quit_app(self):
        if self.tray_active:
            self.tray.stop()
        self.destroy()


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
