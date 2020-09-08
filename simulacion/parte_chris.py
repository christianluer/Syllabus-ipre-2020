import numpy as np
import random
from collections import deque
from Calendario import calendario

tasa_llegada_dia = 3
tipos_de_cancer = [1, 2, 3, 4] #pueden ser nombres tambien

class Paciente:
    def __init__(self, tipo):
        self.tipo = tipo
        self.fechas_programadas = False
        #tipo refiere al tipo de cancer
    def asignar_protocolo(self):
        pass
    # poner aca como protocolo 1 o 2 o 3, cosa que puede tener un tipo de cancer, y un protocolo asignado


class Lista_pacientes:
    def __init__(self):
        self.pacientes = deque()

class Pacientes_nuevos(Lista_pacientes):
    def __init__(self):
        super().__init__()


class Pacientes_agendados(Lista_pacientes):
    def __init__(self):
        super().__init__()

def llegada_pacientes_semana(pacientes_nuevos):
    pacientes = np.random.poisson(tasa_llegada_dia, 7)
    for i in pacientes:
        for j in range(i):
            tipo = random.choice(tipos_de_cancer)
            pacientes_nuevos.pacientes.append(Paciente(tipo))

# tipo protocolo sera de la forma: (1, 2, 4, 5, "4" ),es decir,
# lunes, martes, jueves y viernes tratamiento, y 4 semanas de duracion del tratamiento
protocolo_1 = []
protocolo_2 = []
protocolo_3 = []

def agendar(pacientes_en_espera, pacientes_agendados, calendario):
    # lo que debo hacer aca es tomar pacientes en espera, agendarlos a un modulo,
    # y pasarlo a pacientes agendados
    pass

if __name__ == "__main__":
    espera = Pacientes_nuevos()
    llegada_pacientes_semana(espera)