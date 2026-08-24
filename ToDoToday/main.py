"""Today's To-Do — a simple habit checklist app.

Run: python main.py
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from task import Task, DURATION_PRESETS, process_tasks
from storage import load_tasks, save_tasks


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Today's To-Do")
        self.geometry("420x480")
        self.minsize(320, 320)

        self.tasks: list[Task] = process_tasks(load_tasks())
        save_tasks(self.tasks)  # persist any resets/expirations immediately

        self._build_layout()
        self._render_tasks()

    # ---------- UI construction ----------

    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Scrollable checklist area
        list_frame = ttk.Frame(self)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.tasks_container = ttk.Frame(canvas)

        self.tasks_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.tasks_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas = canvas

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)       # Windows/macOS
        canvas.bind_all("<Button-4>", self._on_mousewheel)          # Linux scroll up
        canvas.bind_all("<Button-5>", self._on_mousewheel)          # Linux scroll down

        # Bottom bar: add a task
        add_frame = ttk.Frame(self)
        add_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))
        add_frame.columnconfigure(0, weight=1)

        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(add_frame, textvariable=self.name_var)
        name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        name_entry.bind("<Return>", lambda e: self._add_task())

        self.duration_var = tk.StringVar(value=DURATION_PRESETS[0][0])
        duration_menu = ttk.Combobox(
            add_frame,
            textvariable=self.duration_var,
            values=[label for label, _ in DURATION_PRESETS],
            state="readonly",
            width=12,
        )
        duration_menu.grid(row=0, column=1, padx=4)

        add_btn = ttk.Button(add_frame, text="Add", command=self._add_task)
        add_btn.grid(row=0, column=2, padx=(4, 0))

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

        if not self.tasks:
            ttk.Label(
                self.tasks_container,
                text="No tasks yet — add one below.",
                foreground="#888",
            ).grid(row=0, column=0, sticky="w", padx=4, pady=8)
            return

        for row, task in enumerate(self.tasks):
            self._render_task_row(row, task)

    def _render_task_row(self, row: int, task: Task):
        var = tk.BooleanVar(value=task.done_today)

        def on_toggle():
            task.done_today = var.get()
            save_tasks(self.tasks)

        cb = ttk.Checkbutton(self.tasks_container, variable=var, command=on_toggle)
        cb.grid(row=row, column=0, sticky="w", padx=(4, 2), pady=2)

        name_lbl = ttk.Label(self.tasks_container, text=task.name)
        name_lbl.grid(row=row, column=1, sticky="w", padx=2, pady=2)

        days_left = task.days_left()
        expiry_text = "expires today" if days_left <= 0 else f"{days_left}d left"
        expiry_lbl = ttk.Label(
            self.tasks_container, text=expiry_text, foreground="#888"
        )
        expiry_lbl.grid(row=row, column=2, sticky="w", padx=6, pady=2)

        remove_btn = ttk.Button(
            self.tasks_container,
            text="\u2715",
            width=3,
            command=lambda t=task: self._remove_task(t),
        )
        remove_btn.grid(row=row, column=3, sticky="e", padx=(2, 4), pady=2)

        self.tasks_container.columnconfigure(1, weight=1)

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


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
