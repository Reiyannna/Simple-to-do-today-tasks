# tech stack:
# 	python 
# 	GUI

# Purpose:
# 	build a to-do-today only app
# 	for maintaining a habit

# features:
# 	simple resizeable window panel
# 	checklist bullet form
# 	can add and remove tasks
# 	adds duration for tasks (example one task is set for one week, one year)

# future features:
# 	tracks data and pattern
# 	analyze users consistency
# 	recommends solutions to maintain consistency


import tkinter as tk
from tkinter import messagebox

# 1. Create the main application window
root = tk.Tk()
root.title("My Python GUI")
root.geometry("300x200")

# 2. Define an action for the button click
def on_button_click():
    messagebox.showinfo("Success", "You clicked the button!")

# 3. Create a label widget
label = tk.Label(root, text="Welcome to your GUI App!", font=("Arial", 12))
label.pack(pady=20)  # Add padding to top and bottom

# 4. Create a button widget and link it to the action
button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=10)

# 5. Start the application
root.mainloop()