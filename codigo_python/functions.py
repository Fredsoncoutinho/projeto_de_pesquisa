import tkinter as tk
from serial.tools import list_ports
from time import sleep

def check_ports():
    """
    Função para checar se existem portas conectadas
    :return: Retorna a lista das portas conectadas
    """
    ports = list(list_ports.comports())
    if len(ports) != 0:
        ports_list = [port.device for port in ports]
    else:
        ports_list = ["---"]
    return ports_list


def open_popup(msg, width, root):
    """
    Função para mostrar um popup na tela
    :param msg: Texto apresentado no popup
    :param width: Tamanho usado para dimensionar a tela
    :param root: Janela onde vai ser apresentada
    """
    top = tk.Toplevel(root)
    top.geometry(f"{width}x100")
    top.title("Erro de porta")
    tk.Label(top, text=msg, font=('Arial 14 bold')).place(x=20, y=30)
