import warnings
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import filedialog
import numpy as np
import pandas as pd
from datetime import datetime
import serial as sr  # Rename the 'serial' module to 'sr'
import serial.tools.list_ports
warnings.simplefilter(action='ignore', category=FutureWarning)

# ------global variables
arrayDadosTermopar = np.array([0])
arrayDadosPirometro = np.array([0])
cols = ['Termopar', 'Pirômetro', 'Data/Hora']
dat = pd.DataFrame(columns=cols)
sensores = 0
cond = False
# Vaiável de data para armazenar o tempo
now = datetime.now()
data = now.strftime("%d/%m/%Y %H:%M:%S")

# -----plot data-----

fig = Figure(figsize=(8, 6))  # Adjust the figure size to fit the entire GUI window

ax1 = fig.add_subplot(211)

ax1.set_title('Termopar (MAX6675)', fontsize=18)
ax1.set_xlabel('Tempo', fontsize=18)
ax1.set_ylabel('Temperadura °C', fontsize=18)
ax1.set_xlim(0, 40)
ax1.grid()

fig.subplots_adjust(hspace=0.5)

ax2 = fig.add_subplot(212)

ax2.set_title('Pirômetro (MLX90614)', fontsize=18)
ax2.set_xlabel('Tempo', fontsize=18)
ax2.set_ylabel('Temperadura °C', fontsize=18)
ax2.set_xlim(0, 40)
ax2.grid()

lines1 = ax1.plot([], [])[0]  # variaveis que recebe os valores de x e de y
lines2 = ax2.plot([], [], color="r")[0]


def primeiroGrafico(dadoTermopar):
    global arrayDadosTermopar

    if len(arrayDadosTermopar) < 40:
        arrayDadosTermopar = np.append(arrayDadosTermopar, float(dadoTermopar))
        limiteMaximo = round(np.amax(arrayDadosTermopar, axis=0))
        limiteMinimo = round(np.amin(arrayDadosTermopar, axis=0))
        ax1.set_ylim(limiteMinimo-20, limiteMaximo+20)

    else:
        limiteMaximo = round(np.amax(arrayDadosTermopar, axis=0))
        limiteMinimo = round(np.amin(arrayDadosTermopar, axis=0))
        ax1.set_ylim(limiteMinimo-20, limiteMaximo+20)

        arrayDadosTermopar[0:39] = arrayDadosTermopar[1:40]
        arrayDadosTermopar[39] = float(dadoTermopar)

    lines1.set_xdata(np.arange(0, len(arrayDadosTermopar)))
    lines1.set_ydata(arrayDadosTermopar)


def segundoGrafico(dadoPirometro):
    global arrayDadosPirometro
    if len(arrayDadosPirometro) < 40:
        arrayDadosPirometro = np.append(
            arrayDadosPirometro, float(dadoPirometro))

        limiteMaximo = round(np.amax(arrayDadosPirometro, axis=0))
        limiteMinimo = round(np.amin(arrayDadosPirometro, axis=0))

        ax2.set_ylim(limiteMinimo-20, limiteMaximo+20)

    else:
        limiteMaximo = round(np.amax(arrayDadosPirometro, axis=0))
        limiteMinimo = round(np.amin(arrayDadosPirometro, axis=0))
        ax2.set_ylim(limiteMinimo-20, limiteMaximo+20)

        arrayDadosPirometro[0:39] = arrayDadosPirometro[1:40]
        arrayDadosPirometro[39] = float(dadoPirometro)
    lines2.set_xdata(np.arange(0, len(arrayDadosPirometro)))
    lines2.set_ydata(arrayDadosPirometro)


def plot_data():
    global cond, data, dat

    if cond:
        # -----------Variáveis dos que recebem os dados dos sensores---------
        primeiroDado = sensores.readline()
        segundoDado = sensores.readline()
# -----------Decodificando as variáveis---------
        dadoTermopar = primeiroDado.decode('utf')
        dadoPirometro = segundoDado.decode('utf')
    
        # print('termopar: ', (dadoTermopar))
        # print('pirometro: ', (dadoPirometro))

        # print("%.2f"%correcao)
        primeiroGrafico(dadoPirometro)
        segundoGrafico(dadoTermopar)

# ----------Acessa a função pandas para plotar as strings com os dados dos sensores--------
        dat = dat.append({'Termopar': dadoTermopar[0:5], 'Pirômetro': dadoPirometro[0:5], 'Data/Hora': data}, ignore_index=True)

        # print(dat)

        canvas.draw()

    root.after(200, plot_data)

# -----------Salvar os dados em arquivo csv----------
    # dat.to_csv("termopar",index = True, sep =" ")


# -----------Criação das funções------
def plot_start():
    global cond
    cond = True
    sensores.reset_input_buffer()


def plot_stop():
    global cond
    cond = False


def update_status():
    global data, arrayDadosPirometro, arrayDadosTermopar

    # Obter a mensagem atual
    # current_status_pirometro = statusPirometro["text"]  # Pra que serve isso ?

    # Se a mensagem for "Trabalhando...", recomece com "trabalhando"

    arrayDadosPirometro_lenght = len(arrayDadosPirometro)
    current_status_pirometro = arrayDadosPirometro[arrayDadosPirometro_lenght - 1]

    # Atualiza a mensagem
    statusPirometro["text"] = current_status_pirometro

    # Get the current message
    # current_status_termopar = statusTermopar["text"]  # Pra que serve isso ?

    # If the message is "Working...", start over with "Working"

    arrayDadosTermopar_lenght = len(arrayDadosTermopar)
    current_status_termopar = arrayDadosTermopar[arrayDadosTermopar_lenght - 1]

    # Update the message
    statusTermopar["text"] = current_status_termopar

    # After 1 second, update the status
    root.after(200, update_status)


# -----Main GUI code-----
root = tk.Tk()
root.title('Plotagem em tempo real')

pid = "0043"
com_port = None


def connect():
    global sensores, pid, com_port
    ports = list(sr.tools.list_ports.comports())

    for p in ports:
        if pid in p.hwid:
            com_port = p.device
    print("porta atual: ", com_port)
    sensores = sr.Serial(com_port, baudrate=9600, timeout=1)
    porta = tk.Label(root, text=f"Conectado a porta: {com_port}", font=("Arial", 20))
    porta.pack()


connect()

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.get_tk_widget().pack(side="bottom", fill=tk.BOTH, expand=1)
canvas.draw()

start = tk.Button(root, text="Iniciar", font=(
    'calbiri', 12), command=plot_start)
start.pack(side=tk.LEFT)

stop = tk.Button(root, text="Parar", font=(
    'calbiri', 12), command=plot_stop)
stop.pack(side=tk.LEFT)

salvar_dados = tk.Button(root, text="Salvar Dados", font=(
    'calbiri', 12), command=lambda: salvar())
salvar_dados.pack(side=tk.LEFT)

# Função para salvar a imagem


def save_image():
    file_path = filedialog.asksaveasfilename(defaultextension='.png')
    canvas.print_figure(file_path, dpi=1200)  # Set the desired dpi (resolution)


salvar_imagem = tk.Button(root, text="Salvar Imagem", font=(
    'calbiri', 12), command=save_image)
salvar_imagem.pack(side=tk.LEFT)

statusTermopar = tk.Label(root, text="Termopar: C°", font=("Arial", 20))
statusTermopar.pack(side=tk.LEFT)

statusTermopar = tk.Label(root, text="Esperando dados", font=("Arial", 20))
statusTermopar.pack(side=tk.LEFT)

statusPirometro = tk.Label(root, text="Pirômetro: C°", font=("Arial", 20))
statusPirometro.pack(side=tk.LEFT)

statusPirometro = tk.Label(root, text="Esperando dados", font=("Arial", 20))
statusPirometro.pack(side=tk.LEFT)


def salvar():
    file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    dat.to_csv(file_path, index=False, sep=" ")


root.after(1, update_status)
root.after(1, plot_data)
root.mainloop()
