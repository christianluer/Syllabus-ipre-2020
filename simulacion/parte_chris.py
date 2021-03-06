import numpy as np
import random
from collections import deque, defaultdict
from calendario_antiguo import calendario
import csv
import pandas as pd
import xlsxwriter

class Calendario:
    def __init__(self, calendario, enfermeras, capacidad):
        self.calendario = calendario
        self.numero_enfermeras_ocupadas = 0  # esto se actualiza por modulos.
        self.total_enfermeras = enfermeras
        self.total_pacientes_por_modulo = capacidad*self.total_enfermeras  # capacidad de las enfermeras.


    def verificar_dia(self, semana,dia, paciente): ### tiene errores para los pacientes que ya fueron agendados
        for m in range(1, len(self.calendario[semana][dias[dia]][1]) + 1):
            if self.contar_enfermeras_modulo(dia, semana, m) < self.total_enfermeras:
                # visto bueno, reviso si tmbn se cumple para el momento de la sesion
                duracion_sesion = paciente.protocolo[1][paciente.numero_sesion]
                for j in self.calendario[semana][dias[dia]]: ## revisa asientos
                    cuenta = 0
                    for i in range(m, m + duracion_sesion):  ## revisa los modulos, donde podria meterlo, me entrega la primera ocurrencia
                        if i < 41:
                            if self.contar_enfermeras_modulo(dia, semana, m + duracion_sesion) < self.total_enfermeras \
                                    and self.calendario[semana][dias[dia]][j][i].ocupado is False \
                                    and self.contar_enfermeras_modulo(dia, semana, m) < self.total_enfermeras:
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
        if modulo < 41:
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
        if self.contar_enfermeras_modulo(dia,semana,modulo_incial) < self.total_enfermeras and modulo_incial+ paciente.duracion_sesion_actual < 41 and paciente.numero_sesion <= len(paciente.protocolo[0]) and self.calendario[semana][dias[dia]][asiento][modulo_incial].ocupado == False:
            for i in range(modulo_incial, modulo_incial + paciente.duracion_sesion_actual + 1):
                self.calendario[semana][dias[dia]][asiento][i].paciente = paciente.numero_paciente
                self.calendario[semana][dias[dia]][asiento][i].ocupado = True
            self.calendario[semana][dias[dia]][asiento][modulo_incial].necesita_enfermera = True
            self.calendario[semana][dias[dia]][asiento][modulo_incial + paciente.duracion_sesion_actual].necesita_enfermera = True
            paciente.cambio_sesion()
            paciente.ultima_sesion = dia
            paciente.numero_de_sesiones += 1
            paciente.agendado_en.append([semana, dia])
            paciente.historial.append(
                [paciente.id, dia, semana, modulo_incial, asiento, paciente.tipo, paciente.numero_sesion])
            #for j in range(paciente.duracion_sesion_actual):
                #paciente.historial.append([paciente.id, dia, semana, modulo_incial + j, asiento, paciente.tipo, paciente.numero_sesion])

    def contar_horas_extra_dia(self, dia, semana):
        cuenta = 0
        for i in self.calendario[semana][dia]:
            for j in self.calendario[semana][dia][i]:
                if j > 29:
                    if self.calendario[semana][dia][i][j].paciente != None:
                        cuenta += 1
        cuenta = cuenta/4
        return cuenta
    def modulos_ocupados_por_sillas(self, dia, semana):
        porcentaje = 0
        for i in self.calendario[semana][dia]:
            for j in self.calendario[semana][dia][i]:
                if self.calendario[semana][dia][i][j].ocupado == True:
                    porcentaje += 1
        porcentaje = porcentaje/(40*14)
        cuenta = porcentaje
        return cuenta

    def generar_excel_indicador(self):
        indicador_horas_por_dia = list()
        cuenta = 1
        for i in self.calendario:
            for j in self.calendario[i]:
                hras_extra = self.contar_horas_extra_dia(j, i)
                indicador_horas_por_dia.append([i, j, hras_extra])

        with open('indicadores_simulacion.csv', mode='w') as indicador:
            indicador_writer = csv.writer(indicador, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            indicador_writer.writerow([f"numero semana", f"numero dia", f"horas extras"])
            for ñ in indicador_horas_por_dia:
                indicador_writer.writerow([f"semana: {ñ[0]}", f"dia: {ñ[1]}", f"horas extras: {ñ[2]}"])
    def simulation_indicator(self):
        indicador_horas_por_dia = list()
        cuenta = 1
        for i in self.calendario:
            for j in self.calendario[i]:
                hras_extra = self.contar_horas_extra_dia(j, i)
                modulos = self.modulos_ocupados_por_sillas(j,i)
                indicador_horas_por_dia.append([i, j, hras_extra, modulos])
        nuevo_df = pd.DataFrame(columns=["Dia", "Semana", "horas extras", "Ocupacion Sillas %"])
        for k in indicador_horas_por_dia:
            nuevo_df = nuevo_df.append(
                {"Dia": dias.index(k[1]) + 6 * k[0], "Semana": k[0], "Horas Extras": k[2], "Ocupacion Sillas %": k[3]}, ignore_index=True)
        return nuevo_df


    def generar_excel_indicador_dia(self, week, day):
        indicador_sillas_por_dia = list()
        porcentajes = self.modulos_ocupados_por_sillas(day, week)
        for i in porcentajes:
            indicador_sillas_por_dia.append([i[0], i[1]])

        with open(f'indicadores_simulacion_dia_{day}_sem_{week}.csv', mode='w') as indicador:
            indicador_writer = csv.writer(indicador, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            indicador_writer.writerow([f"silla", f"porcentaje"])
            for ñ in indicador_sillas_por_dia:
                indicador_writer.writerow([f"silla: {ñ[0]}", f"%: {ñ[1]}"])

            pass  ## trabajar el string pa pasarlo a excel
    def to_dataframe(self, semana, dia):
        columnas = []
        indices = []
        for k in range(1, len(self.calendario[semana][dias[dia]][1])+1):
            indices.append(k)
        for i in range(1, len(self.calendario[semana][dias[dia]]) + 1):
            columnas.append(f"asiento: {i}")
        columnas.append("uso enfermeras")
        df = pd.DataFrame(columns=columnas, index=indices)
        contador = 1
        for j in range(1, len(self.calendario[semana][dias[dia]][1]) + 1):
            lista = []## 40 modulos
            for i in self.calendario[semana][dias[dia]]: #14
                    lista.append(self.calendario[semana][dias[dia]][i][j].paciente)
            lista.append(self.contar_enfermeras_modulo(dia, semana, contador))
            df.loc[contador] = lista
            contador += 1
        return df

class Paciente:

    def __init__(self, tipo):
        self.tipo = tipo
        self.id = None
        # tipo refiere al tipo de cancer
        self.duracion_sesion_actual = 0  # default, se cambia dinamicamente con la lista del protocolo
        self.numero_sesion = 0  # se inicia en la sesion 0, con esta busco en el protocolo
        self.tiempo_desde_ultima_sesion = 0
        self.numero_de_sesiones = 0
        self.ultima_sesion = 0
        self.termino_sesion = False
        self.acumulado = 0
        self.protocolo = list()
        self.numero_paciente = 0
        self.agendado_en = list()
        self.historial = []
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
        if self.numero_sesion < len(self.protocolo[0]) -1:
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

class Pacientes_sesion_terminada(Lista_pacientes):
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
            tipo = random.choice(tipos_de_cancer_barbara) ### VOlver a 4 en caso necesario
            pacientes_nuevos.pacientes.append(Paciente(tipo))



# necesito una lista con las duraciones de cada sesion, se diferencian por protocolo




def agendar_prox_semana(dia_ultima_atencion, paciente, agendados, rechazados, terminados):
    if paciente.numero_sesion <= len(paciente.protocolo[0]) - 1: ## si aun no terminan su tratamiento
        if 5 - dia_ultima_atencion > paciente.protocolo[0][paciente.numero_sesion]:
            pass ## rechazo y aca deberia hacer que los pacientes se fueran de agendados.
            rechazados.pacientes.append(paciente)
            for dia in range(0, 6):
                for j in agendados.prox_semana[dia]:
                    if j.numero_paciente == paciente.numero_paciente:
                        agendados.prox_semana[dia].remove(j)
        else:
            dia = dia_ultima_atencion + paciente.protocolo[0][paciente.numero_sesion] - 5 ## deberia funcionar a priori
            agendados.prox_semana[dia].append(paciente)
            num_sesion = paciente.numero_sesion
            while dia <= 5:
                num_sesion += 1
                if num_sesion <= len(paciente.protocolo[0]) - 1:
                    dia += paciente.protocolo[0][num_sesion]
                    if dia <= 5:
                        agendados.prox_semana[dia].append(paciente)
                else:
                    break
    else:
        terminados.pacientes.append(paciente)
        for dia in range(0, 6):
            for j in agendados.prox_semana[dia]:
                if j.numero_paciente == paciente.numero_paciente:
                    agendados.prox_semana[dia].remove(j)
def posibles_dia_agendar(calendario, paciente, dia):
    pass



def simulacion(espera, pacientes_agendados, pacientes_rechazados, calendario, cuenta_paciente, all_pacientes,terminados, semanas_simulacion):
    semana = 0
    dia = 0
    # todavia es una prueba será de 5 semanas
    agendados = []
    for i in range(semanas_simulacion):
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
            ñ.id = cuenta_paciente
            cuenta_paciente += 1
            all_pacientes.pacientes.append(ñ)
        # reviso ahora mis prioridades de los que estaban agendados de la semana anterior parto con lunes, hasta sabado
        # antes de "limpiar" con el renovar cuenta pacientes, debo agendar la semana, tanto para los
        # agendados como con los nuevos
        # Falta agendar la semana nomas, aca puedo usar un for por los dias o directamente agendar
        # todo en la semana altiro


        ## limpio las listas de los dias:
        for dia in range(0, 6):
            while len(pacientes_agendados.prox_semana[dia]) > 0:
                paciente = pacientes_agendados.prox_semana[dia].popleft()
                if not paciente.termino_sesion and dia + paciente.protocolo[0][paciente.numero_sesion] <= 5:
                    if calendario.verificar_dia(i, dia, paciente):
                        modulo, asiento = calendario.verificar_dia(i, dia, paciente)
                        calendario.asignar_paciente(i, dia, modulo, asiento, paciente)
                elif not paciente.termino_sesion and dia + paciente.protocolo[0][paciente.numero_sesion] > 5:
                    if calendario.verificar_dia(i, dia, paciente):
                        modulo, asiento = calendario.verificar_dia(i, dia, paciente)
                        calendario.asignar_paciente(i, dia, modulo, asiento, paciente)
                        agendados.append([dia, paciente])
                elif paciente.termino_sesion:
                    terminados.pacientes.append(paciente)
            for p in espera.pacientes:
                if dia <= p.acumulado and p.numero_sesion == 0:
                    if calendario.verificar_dia(i, dia, p):
                        modulo, asiento = calendario.verificar_dia(i, dia, p)
                        calendario.asignar_paciente(i, dia, modulo, asiento, p)
                        p.acumulado = p.protocolo[0][p.numero_sesion]
                        if not p.termino_sesion and dia + p.protocolo[0][p.numero_sesion] > 5:
                            agendados.append([dia, p])

                elif (dia == p.acumulado or dia == p.acumulado + 1) and p.numero_sesion > 0:
                    if calendario.verificar_dia(i, dia, p):
                        modulo, asiento = calendario.verificar_dia(i, dia, p)
                        calendario.asignar_paciente(i, dia, modulo, asiento, p)
                        p.acumulado += p.protocolo[0][p.numero_sesion]
                        if not p.termino_sesion and dia + p.protocolo[0][p.numero_sesion] > 5:
                            agendados.append([dia, p])
            print(f"dia {dia}")
            calendario.printear_dia(i, dia)
        for a in agendados:
            agendar_prox_semana(a[0], a[1], pacientes_agendados, pacientes_rechazados, terminados)
        agendados = []
        print(f"semana {i}")

    #calendario.generar_excel_indicador()
    #calendario.generar_excel_indicador_dia(0,"lunes")
    #calendario.generar_excel_indicador_dia(0, "martes")
    #calendario.generar_excel_indicador_dia(0, "jueves")



def generar_excel_matricial(string):
    pass ## trabajar el string pa pasarlo a excel

def presentar(calendario):
    print("######## Simulacion asignacion pacientes ########")
    print(f"numero protocolos a evaluar: {len(tipos_de_cancer)}")
    print(f"numero total de enfermeras en la simulacion: {calendario.total_enfermeras}")
    print(f"cantidad de modulos: ")

if __name__ == "__main__":

    ##### IMPUTS ######
    cuenta_paciente = 1
    tasa_llegada_dia = 4
    tipos_de_cancer = [1, 2, 3, 4]
    tipos_de_cancer_barbara=[1,2,3]
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
    protocolo_4 = [[1, 3, 5, 6, 4], [5, 5, 5, 6, 4]] ## primer valor de la lista lista[0][0], es el
    protocolo_2 = [[1, 3, 3, 2, 2, 4], [4, 5, 5, 5, 4, 4]]
    protocolo_3 = [[0, 4, 5, 4, 4, 3, 2, 1], [4, 4, 5, 4, 4, 4, 4, 4]]
    protocolo_1 = [[2, 5, 4, 1, 1, 1, 1, 4], [3, 5, 4, 1, 1, 1, 1, 9]]
    enfermeras = 5
    capacidad_enfermeras_regular = 3
    semanas_simulacion = 11
    #### FIN IMPUTS #####
    pacientes_general = set()
    todos_los_pacientes = Lista_pacientes()
    nuevo_calendario = Calendario(calendario, enfermeras, capacidad_enfermeras_regular)
    presentar(nuevo_calendario)
    terminados = Pacientes_sesion_terminada()
    espera = Pacientes_nuevos()
    agendados = Pacientes_agendados()
    rechazados = Pacientes_rechazados()
    semana_actual = 0
    simulacion(espera, agendados, rechazados, nuevo_calendario, cuenta_paciente, todos_los_pacientes, terminados, semanas_simulacion)

    ### dataframes
    nuevo_calendario.to_dataframe(0,0)
    big_df = pd.DataFrame(columns=["ID", "Dia", "Semana", "Modulo", "Asiento", "Protocolo", "Sesion", "estado tratamiento"])
    rechazados2 = set(rechazados.pacientes)
    for i in rechazados2:
        for j in i.historial:
            big_df = big_df.append({"ID": j[0], "Dia": j[1] + 6*j[2], "Semana": j[2], "Modulo": j[3], "Asiento": j[4], "Protocolo": j[5], "Sesion": j[6], "estado tratamiento": "derivado"}, ignore_index=True)
    terminados2 = set(terminados.pacientes)
    for i in terminados2:
        for j in i.historial:
            big_df = big_df.append({"ID": j[0], "Dia": j[1] + 6*j[2], "Semana": j[2], "Modulo": j[3], "Asiento": j[4], "Protocolo": j[5], "Sesion": j[6], "estado tratamiento": "finalizado"}, ignore_index=True)
    for i in range(0,6):
        pacientes = set(agendados.prox_semana[i])
        for k in pacientes:
            for j in k.historial:
                big_df = big_df.append(
                    {"ID": j[0], "Dia": j[1] + 6*j[2], "Semana": j[2], "Modulo": j[3], "Asiento": j[4], "Protocolo": j[5],
                    "Sesion": j[6], "estado tratamiento": "En tratamiento"}, ignore_index=True)
    for l in espera.pacientes:
        for j in l.historial:
            big_df = big_df.append(
                {"ID": j[0], "Dia": j[1] + 6*j[2], "Semana": j[2], "Modulo": j[3], "Asiento": j[4], "Protocolo": j[5],
                 "Sesion": j[6], "estado tratamiento": "primera semana"}, ignore_index=True)
    print(big_df.head(100))
    xlwriter= pd.ExcelWriter("resumen_pacientes_barbara.xlsx")
    ## parte a eliminaar
    big_df=big_df[big_df['estado tratamiento'].isin(["finalizado", "En tratamiento"])]
    ##
    big_df.to_excel(xlwriter, sheet_name="resumen pacientes", index=False)
    xlwriter.close()

    writer = pd.ExcelWriter('simulacion_barbara.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Calendario')
    writer.sheets['Calendario'] = worksheet
    row = 0
    horizonte = pd.DataFrame(columns=["semana", "dia"])
    dia_hori = 0
    for i in range(semanas_simulacion):
        for j in range(6):
            df = nuevo_calendario.to_dataframe(i, j)
            df.to_excel(writer, sheet_name='Calendario', startrow=row, startcol=0)
            row += len(df.index) + 3
            horizonte = horizonte.append({"semana": i, "dia": dia_hori},ignore_index=True)
            dia_hori +=1
    horizonte.to_excel(writer, sheet_name="horizonte")
    big_df_sin_estado = big_df[["ID", "Dia", "Semana", "Modulo", "Asiento", "Protocolo", "Sesion"]]
    big_df_sin_estado.to_excel(writer, sheet_name="calendario datos")
    indicator = nuevo_calendario.simulation_indicator()
    indicator.to_excel(writer, sheet_name="indicadores")
    writer.close()


#### NUEVO DESAFIO ####



### debemos entonces guardar: el agendamiento final del dia: parecido al printear dia, no paciente por paciente, funcion printear_dia de calendario
### modulos, de todos los dias, como quedo el calendario finalmente.
### generar indicadores, segun secciones de la cantidad total de dias
### indicador de pacientes derivados por dia/semana
### plantilla con los indicadores de los dias columna indicadores, filas dias
## hojas de semana, periodo y simulacion completa
## lo que se vea sea los dias al final de la simulacion, formato igual al del terminal.

## simular por pacientes


### posible error: Tener a una enfermera atendiendo mas pacientes aun que este atendiendo al inicio a un paciente.


#### asignacion paciente mejorar
#### verificar dia tambien con lo de las horas extras
