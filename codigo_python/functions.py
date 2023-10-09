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
    print(port)
    sensores = serial.Serial(port, baudrate=9600, timeout=1)
    porta = tk.Label(root, text="Conectado a porta: ", font=("Arial", 20))
    porta.pack()

def primeiroGrafico(dadoTermopar):
    global arrayDadosTermopar

    if (len(arrayDadosTermopar) < 40):
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
    if (len(arrayDadosPirometro) < 40):
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
        arrayDadosPirometro[39] =float(dadoPirometro)
    lines2.set_xdata(np.arange(0, len(arrayDadosPirometro)))
    lines2.set_ydata(arrayDadosPirometro)


def plot_data():
    global cond, data, dat

    if (cond == True):
        # -----------Variáveis dos que recebem os dados dos sensores---------
        primeiroDado = sensores.readline()
        segundoDado = sensores.readline()
        # -----------Decodificando as variáveis---------
        dadoTermopar = primeiroDado.decode('utf')
        dadoPirometro = segundoDado.decode('utf')
    
        #print('termopar: ', (dadoTermopar))
        #print('pirometro: ', (dadoPirometro))
        
        #Abre o aqquivo de solução
        z = pd.read_csv('solucao', sep=' ', index_col= False )
        vector = np.vectorize(np.float_)
        y = z.to_numpy()
        solucao = vector(y)
        
        pos = 1.0
        sens = float(dadoPirometro)
        #sens = 27.5
        #Implementa a correção
        F = lambda pos,sens: np.array([1,pos,sens, pos**2,sens**2,pos*sens])@solucao
        correcao = F(pos, sens)
        
        #print("%.2f"%correcao)
        primeiroGrafico(dadoTermopar)
        segundoGrafico("%.2f"%correcao)

# ----------Acessa a função pandas para plotar as strings com os dados dos sensores--------
        dat = dat.append({'Termopar': dadoTermopar[0:5],'Pirometro(real)':dadoPirometro[0:5], 'Pirometro(simulado)': "%.2f"%correcao,'Data/Hora': data}, ignore_index=True)

        # print(dat)

        canvas.draw()

    root.after(200, plot_data)


def salvar():
    file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    dat.to_csv(file_path, index=False, sep=" ")
