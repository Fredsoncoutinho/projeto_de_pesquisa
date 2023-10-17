from serial.tools import list_ports
from time import sleep

def check_ports():
    ports = list(list_ports.comports())
    if len(ports) != 0:
        ports_list = [port.device for port in ports]
    else:
        ports_list = ["---"]
    return ports_list

ports_list = check_ports()
mostrou = False
while True:
    ports_list = check_ports()
    if ports_list == ["---"]:
        print("Não conectado")
        mostrou = True
        sleep(0.5)
    else:
        print(f"Conectado a porta: {ports_list[0]}")
        sleep(0.5)