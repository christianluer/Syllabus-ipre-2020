import numpy as np
import random
from collections import deque
from calendario_antiguo import calendario

tasa_llegada_dia = 3
tipos_de_cancer = [1, 2, 3, 4]  # pueden ser nombres tambien
asientos = 4
modulos_atencion = 4 # tomara 4 modulos de 15 minutos el atender a un paciente
dias = ["lunes", "martes", "miercoles", "jueves","viernes", "sabado"]
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

class Pacientes_rechazados(Lista_pacientes):
    def __init__(self):
        super().__init__()

def llegada_pacientes_semana(pacientes_nuevos):
    pacientes = np.random.poisson(tasa_llegada_dia, 7)
    for i in pacientes:
        for j in range(i):
            tipo = random.choice(tipos_de_cancer)
            pacientes_nuevos.pacientes.append(Paciente(tipo))

# tipo protocolo sera de la forma: (separacion de dias, 4 ),es decir,
# lista de la separacion entre dias, y 4 semanas de duracion del tratamiento

protocolo_1 = [2, 4]
protocolo_2 = [2, 3]
protocolo_3 = [1, 4]
protocolo_4 = [3, 5]



def disponibilidad_semana(semana_acutal, calendario):
    disponibilidad = False
    modulo = 0
    dia = ""
    encontre_uno = False
    for i in calendario[semana_acutal]:
        for j in range(len(calendario[semana_acutal][i])):
            if j <= 37:
                if len(calendario[semana_acutal][i][j]) < asientos and j <= 38 and encontre_uno == False:
                    inicio = 0
                    for k in range(1, modulos_atencion):
                        if len(calendario[semana_acutal][i][j + k]) < asientos:
                            disponibilidad = True
                            inicio += 1
                        elif len(calendario[semana_acutal][i][j + k]) >= asientos:
                            disponibilidad = False
                    if disponibilidad and inicio == 3:
                        modulo = j
                        dia = i
                        encontre_uno = True
    estado = [disponibilidad, modulo, dia]
    return estado

def disponibilidad_dia(dia, semana_actual, calendario):
    encontre_uno = False
    disponibilidad = False
    modulo = 0
    for i in range(len(calendario[semana_actual][dia])):
        if len(calendario[semana_actual][dia][i]) < asientos and i <= 38 and encontre_uno == False:
            inicio = 0
            for k in range(1, modulos_atencion):
                if len(calendario[semana_actual][dia][i + k]) < asientos:
                    disponibilidad = True
                    inicio += 1
                elif len(calendario[semana_actual][dia][i + k]) >= asientos:
                    disponibilidad = False
            if disponibilidad and inicio == 3:
                modulo = i
                encontre_uno = True
    estado = [disponibilidad, dia, modulo]
    return estado

def asignar_protocolo(paciente):
    if paciente.tipo == 1:
        paciente.asignar_protocolo(protocolo_1)
    elif paciente.tipo == 2:
        paciente.asignar_protocolo(protocolo_2)
    elif paciente.tipo == 3:
        paciente.asignar_protocolo(protocolo_3)
    elif paciente.tipo == 4:
        paciente.asignar_protocolo(protocolo_4)

def simular_semana(pacientes_en_espera, pacientes_agendados, pacientes_rechazados, calendario, semana_actual):
    semana_actual = semana_actual
    while len(pacientes_en_espera.pacientes) != 0:
        paciente = pacientes_en_espera.pacientes.popleft()
        estado = disponibilidad_semana(semana_actual, calendario)
        if estado[0]:
            # asigno primer dia y le asigno un protocolo
            asignar_protocolo(paciente)
            for i in range(modulos_atencion):
                calendario[semana_actual][estado[2]][estado[1] + i].append(paciente)

            numero_dia_inicial = dias.index(estado[2])
            if numero_dia_inicial + paciente.protocolo[0] < 6 and disponibilidad_dia(estado[1],
                                                                                     semana_actual,
                                                                                     calendario)[0]:
                nuevo_dia = disponibilidad_dia(estado[1], semana_actual, calendario)
                for i in range(modulos_atencion):
                    calendario[semana_actual][nuevo_dia[1]][nuevo_dia[2] + i].append(paciente)
            pacientes_agendados.pacientes.append(paciente)


if __name__ == "__main__":
    espera = Pacientes_nuevos()
    agendados = Pacientes_agendados()
    rechazados = Pacientes_rechazados()
    semana_acutal = 0
    # desde aca abajo se simularia por semana
    llegada_pacientes_semana(espera)
    simular_semana(espera, agendados, rechazados, calendario, semana_acutal)
    


