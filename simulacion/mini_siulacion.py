
import numpy as np
import random
from collections import deque, defaultdict
from calendario_antiguo import calendario

cuenta_paciente = 1
tasa_llegada_dia = 6
tipos_de_cancer = [1, 2, 3, 4]  # pueden ser nombres tambien
asientos = 14
modulos_atencion = 4 # tomara 4 modulos de 15 minutos el atender a un paciente
dias = ["lunes", "martes", "miercoles", "jueves","viernes", "sabado"]
numero_enfermeras_minimo = 6

protocolo_1 = [[2, 3, 5, 6, 4], [5, 5, 5, 6, 4]]
protocolo_2 = [[2, 3, 3, 2, 2, 4], [4, 5, 5, 5, 4, 4]]
protocolo_3 = [[1, 4, 5, 4, 4, 3, 2, 1], [4, 4, 5, 4, 4, 4, 4, 4]]
protocolo_4 = [[3, 5, 4, 1, 1, 1, 1], [3, 5, 4, 1, 1, 1, 1]]


# la segunda parte de la lista es la duracion por sesion de tratamientos, y se señala en modulos
# la primera sigue siendo la distancia entre dias de las sesiones


class Calendario:
    def __init__(self, calendario):
        self.calendario = calendario
        self.numero_enfermeras_ocupadas = 0  # esto se actualiza por modulos.
        self.total_pacientes_por_modulo = 30  # capacidad de las enfermeras.
        self.total_enfermeras = 10

    def verificar_dia(self,  semana, dia, paciente):
        print(dias[dia])### tiene errores para los pacientes que ya fueron agendados
        for m in range(1, len(self.calendario[semana][dias[dia]][1]) + 1):
            if self.contar_enfermeras_modulo(dia, semana, m) < self.total_enfermeras:
                # visto bueno, reviso si tmbn se cumple para el momento de la sesion
                duracion_sesion = paciente.protocolo[1][paciente.numero_sesion]
                for j in self.calendario[semana][dias[dia]]: ## revisa asientos
                    cuenta = 0
                    for i in range(m, m + duracion_sesion):  ## revisa los modulos, donde podria meterlo, me entrega la primera ocurrencia
                        if i < 41:
                            if self.contar_enfermeras_modulo(dia, semana,
                                                             m + duracion_sesion) < self.total_enfermeras \
                                    and self.calendario[semana][dias[dia]][j][i].ocupado is False \
                                    and self.contar_enfermeras_modulo(dia, semana, m) < self.total_enfermeras:
                                print(self.calendario[semana][dias[dia]][j][i].paciente)
                                cuenta += 1
                            elif self.calendario[semana][dias[dia]][j][i].ocupado:
                                cuenta = 0
                    if cuenta == duracion_sesion:
                        asiento_agendable = j
                        lista = [m, asiento_agendable]
                        return lista
        return False

    def contar_enfermeras_modulo(self, dia, semana, modulo):
        cuenta = 0
        for i in self.calendario[semana][dias[dia]]:
            if calendario[semana][dias[dia]][i][modulo].necesita_enfermera:
                cuenta += 1
        return cuenta
            # aca hay q revisar para cada modulo

    def printear_dia(self, semana, dia):
        contador = 1
        for j in range(1, len(self.calendario[semana][dias[dia]][1]) + 1): ## 40 modulos
            if contador < 10:
                string = f"0{contador} "
            else:
                string = f"{contador} "
            for i in self.calendario[semana][dias[dia]]:
                    string += f"{self.calendario[semana][dias[dia]][i][j].paciente}  "
            contador += 1
            print(string)
    def asignar_paciente(self, semana, dia, modulo_incial, asiento, paciente):
        if self.contar_enfermeras_modulo(dia,semana,modulo_incial) < self.total_enfermeras:
            for i in range(modulo_incial, modulo_incial + paciente.duracion_sesion_actual + 1):
                self.calendario[semana][dias[dia]][asiento][i].paciente = paciente.numero_paciente
                self.calendario[semana][dias[dia]][asiento][i].ocupado = True
            self.calendario[semana][dias[dia]][asiento][modulo_incial].necesita_enfermera = True
            self.calendario[semana][dias[dia]][asiento][modulo_incial + paciente.duracion_sesion_actual].necesita_enfermera = True
            paciente.cambio_sesion()
            paciente.ultima_sesion = dia

class Paciente:

    def __init__(self, tipo):
        self.tipo = tipo
        # tipo refiere al tipo de cancer
        self.duracion_sesion_actual = 0  # default, se cambia dinamicamente con la lista del protocolo
        self.numero_sesion = 0  # se inicia en la sesion 0, con esta busco en el protocolo
        self.tiempo_desde_ultima_sesion = 0
        self.ultima_sesion = 0
        self.termino_sesion = False
        self.acumulado = 0
        self.protocolo = list()
        self.numero_paciente = 0
        if self.tipo == 1:
            self.asignar_protocolo(protocolo_1)
        elif self.tipo == 2:
            self.asignar_protocolo(protocolo_2)
        elif self.tipo == 3:
            self.asignar_protocolo(protocolo_3)
        elif self.tipo == 4:
            self.asignar_protocolo(protocolo_4)

    def asignar_protocolo(self, lista):
        self.protocolo = lista
        self.duracion_sesion_actual = self.protocolo[1][0]
        self.acumulado = self.protocolo[0][0]
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




def agendar_prox_semana(dia_ultima_atencion, paciente, agendados):
    if paciente.numero_sesion <= len(paciente.protocolo[0]) - 1:
        if 6 - dia_ultima_atencion < paciente.protocolo[0][paciente.numero_sesion]:
            pass ## rechazo y aca deberia hacer que los pacientes se fueran de agendados.
        else:
            dia = dia_ultima_atencion + paciente.protocolo[0][paciente.numero_sesion] - 6 ## deberia funcionar a priori
            agendados.prox_semana[dia].appendright(paciente)
            num_sesion = paciente.numero_sesion
            while dia <= 6:
                num_sesion += 1
                if num_sesion <= len(paciente.protocolo[0]) - 1:
                    dia += paciente.protocolo[0][num_sesion]
                    if dia <= 6:
                        agendados.prox_semana[dia].appendright(paciente)
    else:
        pass # termino el tratamiento.

def posibles_dia_agendar(calendario, paciente, dia):
    pass



def simulacion(espera, pacientes_agendados, pacientes_rechazados, calendario, cuenta_paciente):
    semana = 0
    dia = 0
    # todavia es una prueba será de 5 semanas

    espera.pacientes = list()
    # cada i que pase será nueva semana, por lo tanto necesíto que me llegue nueva gente.
    llegada_pacientes_semana(espera)
    ## se me llenan los pacientes en espera, los ordeno
    espera.ordenar()
    espera.pacientes.reverse()
    for ñ in espera.pacientes:
        if cuenta_paciente < 10:
            ñ.numero_paciente = f"p00{cuenta_paciente}"
        elif cuenta_paciente >= 10 and cuenta_paciente < 100:
            ñ.numero_paciente = f"p0{cuenta_paciente}"
        else:
            ñ.numero_paciente = f"p{cuenta_paciente}"
        cuenta_paciente += 1
    paciente_1 = espera.pacientes[0]
    #modulo, asiento = calendario.verificar_dia(0,0, paciente_1)
    #calendario.asignar_paciente(0, 0, modulo, asiento, paciente_1)
    modulo, asiento = calendario.verificar_dia(0, 3, paciente_1)
    calendario.asignar_paciente(0, 3, modulo, asiento, paciente_1)
    print(calendario.calendario[0]["jueves"][1][1].paciente)
    paciente_2 = espera.pacientes[1]
    #modulo, asiento = calendario.verificar_dia(0, 0, paciente_2)
    #calendario.asignar_paciente(0, 0, modulo, asiento, paciente_2)
    modulo, asiento = calendario.verificar_dia(0, 3, paciente_2)
    calendario.asignar_paciente(0, 3, modulo, asiento, paciente_2)
    print(calendario.calendario[0]["jueves"][1][1].paciente)
    calendario.asignar_paciente(0, 3, modulo, asiento, paciente_2)
    #calendario.printear_dia(0, 0)
    calendario.printear_dia(0, 3)
    print(dias[3])
            ## debo limpiar los dias, las personas de los dias. en agendados


        #agendar_prox_semana()

if __name__ == "__main__":
    nuevo_calendario = Calendario(calendario)
    espera = Pacientes_nuevos()
    agendados = Pacientes_agendados()
    rechazados = Pacientes_rechazados()
    semana_actual = 0
    llegada_pacientes_semana(espera)
    espera.ordenar()
    simulacion(espera, agendados, rechazados, nuevo_calendario, cuenta_paciente)