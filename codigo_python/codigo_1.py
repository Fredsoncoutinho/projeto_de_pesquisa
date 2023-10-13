import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import filedialog
import numpy as np
import serial as sr
import serial.tools.list_ports
import pandas as pd
import win32com.client as win32
from datetime import datetime
from functions import *

# ------Variaveis globais
arrayDadosTermopar = np.array([0])
arrayDadosPirometro = np.array([0])
cols = ['Termopar','Pirometro(real)', 'Pirômetro(simulado)','Data/Hora']
dat = pd.DataFrame(columns=cols)
sensores = 0
cond = False

# ------Variável de data para armazenar o tempo 
now = datetime.now()
data = now.strftime("%d/%m/%Y %H:%M:%S")

# -----plot data-----

fig = Figure()

ax1 = fig.add_subplot(211)
ax1.set_title('Termopar (MAX6675)')
ax1.set_xlabel('Tempo')
ax1.set_ylabel('Temperadura °C')
ax1.set_xlim(0, 40)
ax1.grid()

fig.subplots_adjust(hspace=0.5)
ax2 = fig.add_subplot(212)
ax2.set_title('Pirômetro (MLX90614)')
ax2.set_xlabel('Tempo')
ax2.set_ylabel('Temperadura °C')
ax2.set_xlim(0, 40)
ax2.grid()

lines1 = ax1.plot([], [])[0]  # variaveis que recebe os valores de x e de y
lines2 = ax2.plot([], [])[0]
lines2 = ax2.plot([], [], color="r")[0]

# -----------Salvar os dados em arquivo csv----------
# dat.to_csv("termopar",index = True, sep =" ")
1
# -----Main GUI code-----
root = tk.Tk()
root.title('Plotagem em tempo real')

# cria menu suspenso com as portas disponíveis
ports = list(serial.tools.list_ports.comports())
ports_list = [port.device for port in ports]
selected_port = tk.StringVar(root)
selected_port.set(ports_list[0])  # seleciona a primeira porta por padrão
port_menu = tk.OptionMenu(root, selected_port, *ports_list)
port_menu.pack()

# cria botão para conectar
connect_button = tk.Button(root, text="Conectar",font=("Arial", 12), command=connect)
connect_button.pack()

# ------Cria o objeto de plotagem na  GUI----------

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.get_tk_widget().pack(side="bottom", fill=tk.BOTH, expand=1)
canvas.draw()


# ----------Criação dos botões---------
root.update()
start = tk.Button(root, text="Iniciar", font=(
    'calbiri', 12), command=lambda: plot_start())

start.pack(side=tk.LEFT)

root.update()
stop = tk.Button(root, text="Parar", font=(
    'calbiri', 12), command=lambda: plot_stop())
stop.pack(side=tk.LEFT)

salvar = tk.Button(root, text="Salvar", font=(
    'calbiri', 12), command=lambda: salvar())
salvar.pack(side=tk.LEFT)


statusTermopar = tk.Label(root, text="Termopar: C°", font=("Arial", 20))
statusTermopar.pack(side=tk.LEFT)

statusTermopar = tk.Label(root, text="Esperando dados", font=("Arial", 20))
statusTermopar.pack(side=tk.LEFT)

statusPirometro = tk.Label(root, text="Pirômetro: C°", font=("Arial", 20))
statusPirometro.pack(side=tk.LEFT)

statusPirometro = tk.Label(root, text="Esperando dados", font=("Arial", 20))
statusPirometro.pack(side=tk.LEFT)


# ----Inicia a porta serial----
'''''''''''''''''''''
try:
    sensores = sr.Serial('COM11', 9600)
    sensores.reset_input_buffer()

except sr.serialutil.SerialException:
    error = tk.Label(
        root, text="Arduino não conectado, por favor verifique a porta", font=("Arial", 20))
    error.pack(side=tk.TOP)
    print("Arduino não conectado, por favor verifique a porta")

'''''''''''''''''''''

#posição = motor.readline()

root.after(1, update_status)
root.after(1, plot_data)
root.mainloop()