import numpy as np
import random
from collections import deque
from calendario_antiguo import calendario

tasa_llegada_dia = 3
tipos_de_cancer = [1, 2, 3, 4]  # pueden ser nombres tambien
asientos = 4
modulos_atencion = 4 # tomara 4 modulos de 15 minutos el atender a un paciente
dias = ["lunes", "martes", "miercoles", "jueves","viernes", "sabado"]
numero_enfermeras_minimo = 6

protocolo_1 = [[2, 3, 5, 6, 4], [5, 5, 5, 6, 4]]
protocolo_2 = [[2, 3, 3, 2, 2, 4], [4, 5, 5, 5, 4, 4]]
protocolo_3 = [[1, 4, 5, 4 , 4, 3, 2, 1], [4, 4, 5, 4 , 4, 4, 4, 4]]
protocolo_4 = [[3, 5, 4, 1, 1, 1, 1] , [3, 5, 4, 1, 1, 1, 1]]

# la segunda parte de la lista es la duracion por sesion de tratamientos, y se señala en modulos
# la primera sigue siendo la distancia entre dias de las sesiones

class Enfermera:
    def __init__(self):
        self.atendiendo = False


class Calendario:
    def __init__(self, calendario):
        self.calendario = calendario
        self.numero_enfermeras_ocupadas = 0 # esto se actualiza por modulos.
        self.total_pacientes_por_modulo = 30 # capacidad de las enfermeras.
        self.total_enfermeras = 5

    def verificar_cupo_modulo(self, dia, semana, modulo, paciente):
        if self.numero_enfermeras_ocupadas < self.total_enfermeras:
          # visto bueno, reviso si tmbn se cumple para el momento de la sesion
            duracion_sesion = paciente.protocolo[1][paciente.numero_sesion]
            asiento_agendable = 0
            for j in self.calendario[semana][dia]:
                cuenta = 0
                for i in range(modulo, duracion_sesion + 1):
                    if i < 41:
                        if self.contar_enfermeras_modulo(dia, semana, i) < self.total_enfermeras\
                                and self.calendario[semana][dia][j][i].ocupado == False:
                            cuenta += 1
                if cuenta == duracion_sesion and asiento_agendable == 0:
                    asiento_agendable = j
                    return asiento_agendable
        return False

    def renovar_cuenta_pacientes(self, dia, semana):
        for i in self.calendario[semana][dia]:
            for j in self.calendario[semana][dia][i]:
                if self.calendario[semana][dia][i][j].ocupado:
                    self.calendario[semana][dia][i][j].paciente.tiempo_desde_ultima_sesion = 0

    def contar_enfermeras_modulo(self, dia, semana, modulo):
        cuenta = 0
        for i in self.calendario[semana][dia]:
            if calendario[semana][dia][i][modulo].necesita_enfermera:
                cuenta += 1
        return cuenta
            # aca hay q revisar para cada modulo

    def printear_dia(self, semana, dia):
        contador = 1
        for j in range(len(self.calendario[0]["lunes"][1])):
            string = f"{contador} "
            for i in calendario[0]["lunes"]:
                string += f"{calendario[0]['lunes'][i][1].paciente}  "
            contador += 1
            print(string)

class Paciente:

    def __init__(self, tipo):
        self.tipo = tipo
        self.fechas_programadas = False
        # tipo refiere al tipo de cancer
        self.duracion_sesion_actual = 4 # default, se cambia dinamicamente con la lista del protocolo
        self.numero_sesion = 0 # se inicia en la sesion 0, con esta busco en el protocolo
        self.tiempo_desde_ultima_sesion = 0
    def asignar_protocolo(self, lista):
        self.protocolo = lista
    # poner aca como protocolo 1 o 2 o 3, cosa que puede tener un tipo de cancer,


def sortear(dato):
    return dato.tipo


class Lista_pacientes:
    def __init__(self):
        self.pacientes = list()

    def ordenar(self):
        self.pacientes.sort(key=sortear, reverse=True)



class Pacientes_nuevos(Lista_pacientes):
    def __init__(self):
        super().__init__()


class Pacientes_agendados(Lista_pacientes):
    def __init__(self):
        super().__init__()
        self.lunes = deque()
        self.martes = deque()
        self.miercoles = deque()
        self.jueves = deque()
        self.viernes = deque()
        self.sabado = deque()
class Pacientes_rechazados(Lista_pacientes):
    def __init__(self):
        super().__init__()

def llegada_pacientes_semana(pacientes_nuevos):
    pacientes = np.random.poisson(tasa_llegada_dia, 7)
    for i in pacientes:
        for j in range(i):
            tipo = random.choice(tipos_de_cancer)
            pacientes_nuevos.pacientes.append(Paciente(tipo))



# necesito una lista con las duraciones de cada sesion, se diferencian por protocolo


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
    print(semana_actual)
    for i in pacientes_agendados.pacientes:
        asignar(semana_actual, calendario, i)
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
        elif estado[0] == False:
            pacientes_rechazados.pacientes.append(paciente)





def simulacion(espera, pacientes_agendados, pacientes_rechazados, calendario):
    semana = 0
    dia = 0
    # todavia es una prueba será de 5 semanas
    for i in range(5):

        # cada i que pase será nueva semana, por lo tanto necesíto que me llegue nueva gente.
        llegada_pacientes_semana(espera)
        ## se me llenan los pacientes en espera, los ordeno
        espera.ordenar()
        ## reviso ahora mis prioridades de los que estaban agendados de la semana anterior
        for k in range(8):## dias
            calendario.renovar_cuenta_pacientes(k, i)
            # politica de ahora, agendar por orden de importancia en el tipo de cancer

            for i in pacientes_agendados:
                for j in calendario[semana][dias[dia]]:
                    pass
            # deberia agendarlos en sus dias, aca iria politica de que si hay pacientes nuevos que requieran tratamiento antes
            # ademas de ver lo de las enfermeras, ya se tiene una idea de como  hacerlo.
            # se harian listas sobre los dias que hay que agendar a los pacientes.

        semana += 1



if __name__ == "__main__":
    nuevo_calendario = Calendario(calendario)
    espera = Pacientes_nuevos()
    agendados = Pacientes_agendados()
    rechazados = Pacientes_rechazados()
    semana_actual = 0
    llegada_pacientes_semana(espera)
    espera.ordenar()
    nuevo_calendario.printear_dia(0, "lunes")

    ####simulacion_semana_nueva(espera, agendados, rechazados, calendario)



    #desde aca abajo se simularia por semana
    #for i in range(1, 5):
     #  llegada_pacientes_semana(espera)
     #  simular_semana(espera, agendados, rechazados, calendario, semana_actual)
      # semana_actual += 1


    #for i in calendario[0]["lunes"]:
     #   if len(calendario[0]["lunes"][i]) == 0:
      #      print(f"en el modulo {i} no hay pacientes")