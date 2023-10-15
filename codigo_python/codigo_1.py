# import win32com.client as win32
# import serial as sr
import tkinter as tk
from serial.tools import list_ports
from warnings import simplefilter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from tkinter import filedialog
from numpy import array, append, float_, arange, amax, amin, vectorize
from pandas import DataFrame, read_csv
from datetime import datetime
from serial import Serial

simplefilter(action='ignore', category=FutureWarning)

# ------Variaveis globais
arrayDadosTermopar = array([0])
arrayDadosPirometro = array([0])
cols = ['Termopar', 'Pirometro(real)', 'Pirômetro(simulado)', 'Data/Hora']
dat = DataFrame(columns=cols)
sensores = 0
cond = False

# ------Variável de data para armazenar o tempo 
now = datetime.now()
data = now.strftime("%d/%m/%Y %H:%M:%S")


# -----Funcoes ------


def plot_start():
    global cond, sensores
    cond = True
    try:
        sensores.reset_input_buffer()
    except:
        temp = "Não foi possível ligar os sensores"
        widt = 11 * len(temp)
        open_popup(temp, widt)


def plot_stop():
    global cond
    cond = False


def update_status():
    global data, arrayDadosPirometro, arrayDadosTermopar

    # Obter a mensagem atual
    current_status_pirometro = statusPirometro["text"]

    # Se a mensagem for "Trabalhando...", recomece com "trabalhando"

    arrayDadosPirometro_lenght = len(arrayDadosPirometro)
    current_status_pirometro = arrayDadosPirometro[arrayDadosPirometro_lenght - 1]

    # Atualiza a mensagem
    statusPirometro["text"] = current_status_pirometro

    # Get the current message
    current_status_termopar = statusTermopar["text"]

    # If the message is "Working...", start over with "Working"

    arrayDadosTermopar_lenght = len(arrayDadosTermopar)
    current_status_termopar = arrayDadosTermopar[arrayDadosTermopar_lenght - 1]

    # Update the message
    statusTermopar["text"] = current_status_termopar

    # After 1 second, update the status
    root.after(200, update_status)


# Função para configurar a comunicação serial com a porta selecionada
def connect():
    global sensores
    port = selected_port.get()
    try:
        sensores = Serial(port, baudrate=9600, timeout=1)
    except:
        temp = f"Não foi possível se conectar a porta {port}"
        widt = 11 * len(temp)
        open_popup(temp, widt)
    else:
        porta = tk.Label(root, text="Conectado a porta: ", font=("Arial", 20))
        porta.pack()


def primeiroGrafico(dadoTermopar):
    global arrayDadosTermopar

    if len(arrayDadosTermopar) < 40:
        arrayDadosTermopar = append(arrayDadosTermopar, float(dadoTermopar))
        limiteMaximo = round(amax(arrayDadosTermopar, axis=0))
        limiteMinimo = round(amin(arrayDadosTermopar, axis=0))
        ax1.set_ylim(limiteMinimo - 20, limiteMaximo + 20)

    else:
        limiteMaximo = round(amax(arrayDadosTermopar, axis=0))
        limiteMinimo = round(amin(arrayDadosTermopar, axis=0))
        ax1.set_ylim(limiteMinimo - 20, limiteMaximo + 20)

        arrayDadosTermopar[0:39] = arrayDadosTermopar[1:40]
        arrayDadosTermopar[39] = float(dadoTermopar)

    lines1.set_xdata(arange(0, len(arrayDadosTermopar)))
    lines1.set_ydata(arrayDadosTermopar)


def segundoGrafico(dadoPirometro):
    global arrayDadosPirometro
    if len(arrayDadosPirometro) < 40:
        arrayDadosPirometro = append(
            arrayDadosPirometro, float(dadoPirometro))

        limiteMaximo = round(amax(arrayDadosPirometro, axis=0))
        limiteMinimo = round(amin(arrayDadosPirometro, axis=0))

        ax2.set_ylim(limiteMinimo - 20, limiteMaximo + 20)

    else:
        limiteMaximo = round(amax(arrayDadosPirometro, axis=0))
        limiteMinimo = round(amin(arrayDadosPirometro, axis=0))
        ax2.set_ylim(limiteMinimo - 20, limiteMaximo + 20)

        arrayDadosPirometro[0:39] = arrayDadosPirometro[1:40]
        arrayDadosPirometro[39] = float(dadoPirometro)
    lines2.set_xdata(arange(0, len(arrayDadosPirometro)))
    lines2.set_ydata(arrayDadosPirometro)


def plot_data():
    global cond, data, dat

    if cond:
        # -----------Variáveis dos que recebem os dados dos sensores---------
        try:
            primeiroDado = sensores.readline()
            segundoDado = sensores.readline()
        except:
            temp = "Não foi possível iniciar"
            larg = 11 * len(temp)
            open_popup(temp, larg)
        else:
            # -----------Decodificando as variáveis---------
            dadoTermopar = primeiroDado.decode('utf')
            dadoPirometro = segundoDado.decode('utf')

            # print('termopar: ', (dadoTermopar))
            # print('pirometro: ', (dadoPirometro))

            # Abre o aqquivo de solução
            z = read_csv('solucao', sep=' ', index_col=False)
            vector = vectorize(float_)
            y = z.to_numpy()
            solucao = vector(y)

            pos = 1.0
            sens = float(dadoPirometro)
            # sens = 27,5
            # Implementa a correção
            F = lambda pos, sens: array([1, pos, sens, pos ** 2, sens ** 2, pos * sens]) @ solucao
            correcao = F(pos, sens)

            # print("%.2f"%correcao)
            primeiroGrafico(dadoTermopar)
            segundoGrafico("%.2f" % correcao)

            # ----------Acessa a função pandas para plotar as strings com os dados dos sensores--------
            dat = dat.append({'Termopar': dadoTermopar[0:5], 'Pirometro(real)': dadoPirometro[0:5],
                              'Pirometro(simulado)': "%.2f" % correcao, 'Data/Hora': data}, ignore_index=True)

            # print(dat)

            canvas.draw()

            root.after(200, plot_data)


def salvar_arquivo():
    file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    try:
        dat.to_csv(file_path, index=False, sep=" ")
    except:
        temp = "Não foi possível salvar! Tente novamente"
        widt = 11 * len(temp)
        open_popup(temp, widt)


def open_popup(msg, width):
    global root
    top = tk.Toplevel(root)
    top.geometry(f"{width}x100")
    top.title("Erro de porta")
    tk.Label(top, text=msg, font=('Arial 14 bold')).place(x=20, y=30)


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
lines2 = ax2.plot([], [], color="r")[0]

# -----------Salvar os dados em arquivo csv----------
# dat.to_csv("termopar",index = True, sep =" ")

# -----Main GUI code-----
root = tk.Tk()
root.title('Plotagem em tempo real')

# cria menu suspenso com as portas disponíveis
ports = list(list_ports.comports())
if len(ports) != 0:
    ports_list = [port.device for port in ports]
else:
    ports_list = ["---"]
selected_port = tk.StringVar(root)
selected_port.set(ports_list[0])  # seleciona a primeira porta por padrão
port_menu = tk.OptionMenu(root, selected_port, *ports_list)
port_menu.pack()

# cria botão para conectar
connect_button = tk.Button(root, text="Conectar", font=("Arial", 12), command=connect)
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
    'calbiri', 12), command=lambda: salvar_arquivo())
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

# posição = motor.readline()

root.after(1, update_status)
root.after(1, plot_data)
root.mainloop()
