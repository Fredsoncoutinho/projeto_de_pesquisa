import tkinter as tk

def open_popup(msg, width, root):
    top = tk.Toplevel(root)
    top.geometry(f"{width}x100")
    top.title("Erro de porta")
    tk.Label(top, text=msg, font=('Arial 14 bold')).place(x=20, y=30)