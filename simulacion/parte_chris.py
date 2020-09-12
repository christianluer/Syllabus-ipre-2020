import numpy as np
import random
from collections import deque
from Calendario import calendario

tasa_llegada_dia = 3
tipos_de_cancer = [1, 2, 3, 4]  # pueden ser nombres tambien


class Paciente:

    def __init__(self, tipo):
        self.tipo = tipo
        self.fechas_programadas = False
        # tipo refiere al tipo de cancer

    def asignar_protocolo(self, lista):
        self.protocolo = lista
    # poner aca como protocolo 1 o 2 o 3, cosa que puede tener un tipo de cancer,


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

# tipo protocolo sera de la forma: (dias, 4 ),es decir,
# lista de los dias, y 4 semanas de duracion del tratamiento

protocolo_1 = ["lunes", "miercoles", "viernes", 4]
protocolo_2 = ["martes", "jueves", "sabado", 3]
protocolo_3 = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", 4]
protocolo_4 = ["lunes", "jueves", 5]


def agendar(pacientes_en_espera, pacientes_agendados, calendario, semana_acutal):
    # lo que debo hacer aca es tomar pacientes en espera, agendarlos a un modulo,
    # y pasarlo a pacientes agendados
    while len(pacientes_en_espera.pacientes) != 0:
        paciente = pacientes_en_espera.pacientes.popleft()
        if paciente.tipo == 1:
            # con protocolo 1 asigno a los pacientes en el calendario, reviso si se puede
            # en caso que no no lo agrego a los pacientes agendados.
            paciente.asignar_protocolo(protocolo_1)
            for i in paciente.protocolo:
                if type(i) != int:
                    cupo = 0
                    for j in calendario[semana_acutal][i]:
                        if cupo == 0 and calendario[semana_acutal][i][j] == True:
                            # es que esta libre debo poner ese valor en falso
                            calendario[semana_acutal][i][j] = False
                            cupo += 1
                    if cupo == 0:
                        # paciente queda en el olvido, ya que no hay cupos para ese dia
                        pass
        elif paciente.tipo == 2:
            paciente.asignar_protocolo(protocolo_2)
            pass
        elif paciente.tipo == 3:
            paciente.asignar_protocolo(protocolo_3)
            pass
        elif paciente.tipo == 4:
            paciente.asignar_protocolo(protocolo_4)
            pass


if __name__ == "__main__":
    espera = Pacientes_nuevos()
    agendados = Pacientes_agendados()
    semana_acutal = 0
    # desde aca abajo se simularia por semana
    llegada_pacientes_semana(espera)
    agendar(espera, agendados, calendario, semana_acutal)