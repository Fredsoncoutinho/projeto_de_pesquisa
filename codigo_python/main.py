import tkinter as tk
from time import sleep
from serial.tools import list_ports
from warnings import simplefilter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog
from numpy import array, append, float_, arange, amax, amin, vectorize
from pandas import DataFrame, read_csv
from datetime import datetime
from serial import Serial

simplefilter(action='ignore', category=FutureWarning)

# ------Variaveis globais
arrayDadosTermopar = [0]                 # Lista com os dados recebidos do termopar
arrayDadosPirometro = [0]                # Lista com os dados recebidos do pirômetro
cols = ['Termopar', 'Pirometro(real)']   # Variável com os rótulos do dataframe
dat = DataFrame(columns=cols)            # Variável dataframe do pandas
sensores = 0                             # Variável que vai receber os sensores
cond = False                             # Variável que controlao início do plot

# ------Variável de data para armazenar o tempo 
now = datetime.now()
data = now.strftime("%d/%m/%Y %H:%M:%S")#tempo

# -----Funcoes ------
def plot_start(sensores):
    """
    Função para iniciar o plot
    :param sensores: os sensores que recebem os dados
    """
    global cond
    cond = True
    try:
        sensores.reset_input_buffer()
        plot_data()
    except:
        temp = "Não foi possível ligar os sensores"
        widt = 11 * len(temp)
        open_popup(temp, widt, root)


def plot_stop():
    """
    Função para parar o plot
    """
    global cond
    print(arrayDadosPirometro)
    print(arrayDadosTermopar)
    cond = False


def update_status():
    global data, arrayDadosPirometro, arrayDadosTermopar

    # Obter a mensagem atual
    current_status_pirometro = statusPirometro["text"]

    arrayDadosPirometro_lenght = len(arrayDadosPirometro)
    current_status_pirometro = arrayDadosPirometro[arrayDadosPirometro_lenght - 1]

    # Atualiza a mensagem
    statusPirometro["text"] = f"{current_status_pirometro:3.2f}"

    # Get the current message
    current_status_termopar = statusTermopar["text"]

    # If the message is "Working...", start over with "Working"

    arrayDadosTermopar_lenght = len(arrayDadosTermopar)
    current_status_termopar = arrayDadosTermopar[arrayDadosTermopar_lenght - 1]

    # Update the message
    statusTermopar["text"] = f"{current_status_termopar:3.2f}"

    # After 1 second, update the status
    root.after(200, update_status)


# Função para configurar a comunicação serial com a porta selecionada
def connect():
    """
    Função para conectar a comunicação serial do arduino com a interface
    """
    global sensores
    port = selected_port.get()
    try:
        sensores = Serial(port, baudrate=9600, timeout=1) # Estabelece a conexão com o Arduino
    except:
        temp = f"Não foi possível se conectar a porta {port}"
        widt = 11 * len(temp)
        open_popup(temp, widt, root)
    else:
        porta = tk.Label(root, text="Conectado a porta: ", font=("Arial", 20))
        porta["text"] += port
        porta.pack()


def primeiroGrafico(dadoTermopar):
    """
    Função para gerar o gráfico do Termopar
    :param dadoTermopar: os dados recebidos pelo termopar
    """
    global arrayDadosTermopar
    if len(arrayDadosTermopar) < 40:
        arrayDadosTermopar.append(dadoTermopar)
        limiteMaximo = round(amax(arrayDadosTermopar, axis=0))
        limiteMinimo = round(amin(arrayDadosTermopar, axis=0))
        ax1.set_ylim(limiteMinimo - 10, limiteMaximo + 10)
    else:
        limiteMaximo = round(amax(arrayDadosTermopar, axis=0))
        limiteMinimo = round(amin(arrayDadosTermopar, axis=0))
        ax1.set_ylim(limiteMinimo - 10, limiteMaximo + 10)
        arrayDadosTermopar[0:39] = arrayDadosTermopar[1:40]
        arrayDadosTermopar[39] = float(dadoTermopar)
    lines1.set_xdata(arange(0, len(arrayDadosTermopar)))
    lines1.set_ydata(arrayDadosTermopar)


def segundoGrafico(dadoPirometro):
    """
    Função para gerar o gráfico do Pirometro
    :param dadoPirometro: os dados recebidos pelo pirometro
    """
    global arrayDadosPirometro
    if len(arrayDadosPirometro) < 40:
        arrayDadosPirometro.append(dadoPirometro)
        limiteMaximo = round(amax(arrayDadosPirometro, axis=0))
        limiteMinimo = round(amin(arrayDadosPirometro, axis=0))
        ax2.set_ylim(limiteMinimo - 10, limiteMaximo + 10)
    else:
        limiteMaximo = round(amax(arrayDadosPirometro, axis=0))
        limiteMinimo = round(amin(arrayDadosPirometro, axis=0))
        ax2.set_ylim(limiteMinimo - 10, limiteMaximo + 10)
        arrayDadosPirometro[0:39] = arrayDadosPirometro[1:40]
        arrayDadosPirometro[39] = float(dadoPirometro)
    lines2.set_xdata(arange(0, len(arrayDadosPirometro)))
    lines2.set_ydata(arrayDadosPirometro)


def plot_data():
    """
    Função para mostrar os gráficos na tela
    """
    global cond, data, dat

    if cond:
        # -----------Variáveis dos que recebem os dados dos sensores---------
        try:
            primeiroDado = sensores.readline()
            segundoDado = sensores.readline()
        except:
            temp = "Não foi possível iniciar"
            print(temp)
            larg = 11 * len(temp)
            open_popup(temp, larg, root)
        else:
            # -----------Decodificando as variáveis---------
            dadoTermopar = primeiroDado.decode('utf')
            dadoPirometro = segundoDado.decode('utf')
            dadoTermopar = float(dadoTermopar)
            dadoPirometro = float(dadoPirometro)
            #print(f'termopar: {dadoTermopar}')
            #print(f'pirometro: {dadoPirometro}')
            primeiroGrafico(dadoTermopar)
            segundoGrafico(dadoPirometro)
            # ----------Acessa a função pandas para plotar as strings com os dados dos sensores--------
            novos_dados = {
                'Termopar': [dadoTermopar],
                'Pirometro(real)': [dadoPirometro]
            }
            dat._append(novos_dados, ignore_index=True)
            canvas.draw()
            root.after(200, plot_data)



def salvar_arquivo(root):
    """
    Função para salvar os dados em um arquivo
    :param root: tela onde o popup será mostrado
    """
    file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    try:
        dat.to_csv(file_path, index=False, sep=" ")
    except:
        temp = "Não foi possível salvar! Tente novamente"
        widt = 11 * len(temp)
        open_popup(temp, widt, root)

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
    'calbiri', 12), command=lambda: plot_start(sensores))
start.pack(side=tk.LEFT)

root.update()
stop = tk.Button(root, text="Parar", font=(
    'calbiri', 12), command=lambda: plot_stop())
stop.pack(side=tk.LEFT)

salvar = tk.Button(root, text="Salvar", font=(
    'calbiri', 12), command=lambda: salvar_arquivo(root))
salvar.pack(side=tk.LEFT)

statusTermopar = tk.Label(root, text="Termopar: C°", font=("Arial", 20))
statusTermopar.pack(side=tk.LEFT)

statusTermopar = tk.Label(root, text="Esperando dados", font=("Arial", 20))
statusTermopar.pack(side=tk.LEFT)

statusPirometro = tk.Label(root, text="Pirômetro: C°", font=("Arial", 20))
statusPirometro.pack(side=tk.LEFT)

statusPirometro = tk.Label(root, text="Esperando dados", font=("Arial", 20))
statusPirometro.pack(side=tk.LEFT)

root.after(1, update_status)
root.after(1, plot_data)
root.mainloop()