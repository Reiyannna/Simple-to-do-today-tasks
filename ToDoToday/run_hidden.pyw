"""Double-click this file to launch Today's To-Do with no console window.

On Windows, .pyw files run via pythonw.exe automatically (no terminal),
and the process is independent of whatever started it — closing VS Code,
or any editor, will not affect it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import TodoApp  # noqa: E402

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
