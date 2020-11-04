import numpy as np
import random
from collections import deque, defaultdict
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


class Calendario:
    def __init__(self, calendario):
        self.calendario = calendario
        self.numero_enfermeras_ocupadas = 0  # esto se actualiza por modulos.
        self.total_pacientes_por_modulo = 30  # capacidad de las enfermeras.
        self.total_enfermeras = 5

    def verificar_dia(self, dia, semana, paciente):
        for m in range(0, len(self.calendario[semana][dia][0])):
            if self.numero_enfermeras_ocupadas < self.total_enfermeras:
                # visto bueno, reviso si tmbn se cumple para el momento de la sesion
                duracion_sesion = paciente.protocolo[1][paciente.numero_sesion]
                asiento_agendable = 0
                for j in self.calendario[semana][dia]: ## revisa asientos
                    cuenta = 0
                    for i in range(m, m + duracion_sesion + 1):  ## revisa los modulos, donde podria meterlo, me entrega la primera ocurrencia
                        if i < 41:
                            if self.contar_enfermeras_modulo(dia, semana,
                                                             m + duracion_sesion) < self.total_enfermeras \
                                    and self.calendario[semana][dia][j][i].ocupado == False \
                                    and self.contar_enfermeras_modulo(dia, semana, m) < self.total_enfermeras:
                                cuenta += 1
                    print(f"duracion sesion: {duracion_sesion}")
                    print(f"cuenta: {cuenta}")
                    if cuenta == duracion_sesion:
                        asiento_agendable = j
                        lista = [m, asiento_agendable]
                        return lista
            return False

    def verificar_cupo_modulo(self, dia, semana, modulo, paciente):
        if self.numero_enfermeras_ocupadas < self.total_enfermeras:
          # visto bueno, reviso si tmbn se cumple para el momento de la sesion
            duracion_sesion = paciente.protocolo[1][paciente.numero_sesion]
            asiento_agendable = 0
            for j in self.calendario[semana][dia]:
                cuenta = 0
                for i in range(modulo, modulo + duracion_sesion + 1):
                    if i < 41:
                        if self.contar_enfermeras_modulo(dia, semana, modulo + duracion_sesion) < self.total_enfermeras\
                                and self.calendario[semana][dia][j][i].ocupado == False\
                                and self.contar_enfermeras_modulo(dia, semana, modulo)< self.total_enfermeras:
                            cuenta += 1
                print(f"duracion sesion: {duracion_sesion}")
                print(f"cuenta: {cuenta}")
                if cuenta == duracion_sesion:
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
    def asignar_paciente(self, semana, dia, modulo_incial, asiento, paciente):
        for i in range(modulo_incial, modulo_incial + paciente.duracion_sesion_actual + 1):
            self.calendario[semana][dia][asiento][i].paciente = paciente
            self.calendario[semana][dia][asiento][i].ocupado = True
        self.calendario[semana][dia][asiento][modulo_incial].necesita_enfermera = True
        self.calendario[semana][dia][asiento][modulo_incial + paciente.duracion_sesion_actual].necesita_enfermera = True
        paciente.cambio_sesion()

class Paciente:

    def __init__(self, tipo):
        self.tipo = tipo
        # tipo refiere al tipo de cancer
        self.duracion_sesion_actual = 0  # default, se cambia dinamicamente con la lista del protocolo
        self.numero_sesion = 0  # se inicia en la sesion 0, con esta busco en el protocolo
        self.tiempo_desde_ultima_sesion = 0
        self.termino_sesion = False

    def asignar_protocolo(self, lista):
        self.protocolo = lista
        self.duracion_sesion_actual = self.protocolo[1][0]
    # poner aca como protocolo 1 o 2 o 3, cosa que puede tener un tipo de cancer,

    def cambio_sesion(self):
        #### se debe poner una vez se agenda a un paciente
        if self.numero_sesion <= len(self.protocolo[0]):
            self.numero_sesion += 1
            self.duracion_sesion_actual = self.protocolo[1][self.numero_sesion]
            self.tiempo_desde_ultima_sesion = 0
        else:
            self.termino_sesion = True ## puedo revisar antes de agendar los pacientes si ya terminaron su sesion



### primera politica ordenar por importancia de tipo de cancer

def sortear(dato):
    return dato.protocolo[0][dato.numero_sesion]


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
        self.prox_semana = defaultdict(deque)
        self.prox_semana[0] = self.lunes
        self.prox_semana[1] = self.martes
        self.prox_semana[2] = self.miercoles
        self.prox_semana[3] = self.jueves
        self.prox_semana[4] = self.viernes
        self.prox_semana[5] = self.sabado
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

def agendar_prox_semana(dia_ultima_atencion, paciente, agendados):
    if 6 - dia_ultima_atencion < paciente.protocolo[0][paciente.numero_sesion]:
        pass ## rechazo
    else:
        dia = dia_ultima_atencion + paciente.protocolo[0][paciente.numero_sesion] - 6 ## deberia funcionar a priori
        agendados.prox_semana[dia].appendright(paciente)
        num_sesion = paciente.numero_sesion
        while dia <= 6:
            num_sesion += 1
            dia += paciente.protocolo[0][num_sesion]
            if dia <= 6:
                agendados.prox_semana[dia].appendright(paciente)

def posibles_dia_agendar(calendario, paciente, dia):
    pass



def simulacion(espera, pacientes_agendados, pacientes_rechazados, calendario):
    semana = 0
    dia = 0
    # todavia es una prueba será de 5 semanas
    for i in range(5):

        # cada i que pase será nueva semana, por lo tanto necesíto que me llegue nueva gente.
        llegada_pacientes_semana(espera)
        ## se me llenan los pacientes en espera, los ordeno
        espera.ordenar()
        # reviso ahora mis prioridades de los que estaban agendados de la semana anterior parto con lunes, hasta sabado
        # antes de "limpiar" con el renovar cuenta pacientes, debo agendar la semana, tanto para los
        # agendados como con los nuevos
        # Falta agendar la semana nomas, aca puedo usar un for por los dias o directamente agendar
        # todo en la semana altiro


        ## limpio las listas de los dias:
        for dia in range(0,6):
            while len(pacientes_agendados.prox_semana[dia]) > 0:
                paciente = pacientes_agendados.prox_semana[dia].popleft()
                if not paciente.termino_sesion and paciente.tiempo_desde_ultima_sesion\
                        <= paciente.protocolo[1][paciente.numero_sesion]:
                    if calendario.verificar_dia(i, dia, paciente):
                        modulo, asiento = calendario.verificar_dia(i, dia, paciente)
                        calendario.asignar_paciente(i, dia, modulo, asiento, paciente)
            for p in espera:
                acumulado = p.protocolo[0][p.numero_sesion]
                while dia < acumulado:
                    if calendario.verificar_dia(i, dia, p):
                        if dia == acumulado:
                            modulo, asiento = calendario.verificar_dia(i, dia, p)
                            calendario.asignar_paciente(i, dia, modulo, asiento, p)
                            acumulado += p.protocolo[0][p.numero_sesion]
                            ultima_sesion = dia
        agendar_prox_semana()

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