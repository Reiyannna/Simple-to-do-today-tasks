# Today's To-Do

A dark-themed ("Midnight Galaxy") daily habit checklist. Tasks have a
duration (today only / 1 week / 1 month / 1 year); checking one off resets
automatically the next day, and it silently drops off the list once its
duration ends.

## Files

| File | Purpose |
|---|---|
| `main.py` | The app itself. Run this in VS Code for normal development. |
| `theme.py` | Colors, fonts, and ttk styling (Midnight Galaxy palette). |
| `task.py` | Pure task logic — reset/expiry rules, no GUI or file I/O. |
| `storage.py` | Loads/saves tasks to `tasks.json` next to the script. |
| `tray.py` | System tray icon (uses `pystray` + `Pillow`). |
| `run_hidden.pyw` | Double-click to launch with **no console window**, independent of any editor. |
| `add_to_startup.ps1` | Run once to make the app auto-launch (hidden) at Windows login. |
| `requirements.txt` | Optional tray dependencies. |
| `test_task.py` | Unit tests for the reset/expiry logic. |

## Setup

```
pip install -r requirements.txt
```

This installs `pystray` and `Pillow`, which power the tray icon. The app
still runs fine without them — closing the window just quits normally
instead of minimizing to the tray.

## Running it

- **While developing in VS Code:** `python main.py` as usual.
- **Standalone, no console window:** double-click `run_hidden.pyw`
  (works because `.pyw` files launch via `pythonw.exe` on Windows).
- **Auto-start at login:** right-click `add_to_startup.ps1` → *Run with
  PowerShell*, once. It creates a shortcut in your Startup folder pointing
  at `run_hidden.pyw`. Delete the shortcut from `shell:startup` to undo.

## How the background behavior works

- Closing the window (✕) **minimizes to the system tray** instead of
  quitting, as long as the tray started successfully. Double-click the
  tray icon (or right-click → *Show*) to bring it back. Right-click →
  *Quit* fully exits.
- While running, the app checks every minute whether the date has rolled
  over past midnight, and resets any checked-off tasks automatically —
  no restart required.
- Because it's launched independent of VS Code (via `run_hidden.pyw` or
  the Startup shortcut), closing VS Code has no effect on it.

## Tests

```
pip install pytest
pytest test_task.py -v
```
