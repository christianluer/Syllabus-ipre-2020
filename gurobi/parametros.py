from gurobipy import *

import numpy as np

#############
# CONJUNTOS #
#############


# PROTOCOLOS

P = [k for k in range(1,4)] 
# 3 protocolos - 1, 2, 3

Largo_P = [7, 5, 7] 
# Duracion de cada protocolo en sesiones

# SESIONES

# Sesiones del protocolo p

S = {} 

for i in P:

  S.update({i:[k for k in range(1,Largo_P[int(i)-1] + 1)]})

# MÓDULOS - maestro usaba 53

M = [k for k in range(1,41)] 
# 40 bloques - 1, 2, ..., 40 
# 10 horas de trabajo, cada modulo consiste en 15 min

#Días

T = [int(k) for k in range(1, 42)]

##############
# PARÁMETROS #
##############


# Variable GAMMA 

γ = 0.95

# Costos por protocolo
#estimados

Costos = [1000000,1000000,1000000]

CD = dict(zip(P,Costos)) 
# Asocia los costos cada protocolo con su costo de derivación

# Costo bloque regular

CR = 1000 

# Costo bloque extra

CE = 2000

CM = (CE - CR)/4 # Costo marginal por bloque extra de atención 


# Cantidad de modulos de la sesion s del tratamiento p

M_sp = {} 

for i in P:

    M_sp.update({i:{}})

    for j in S[i]:

        M_sp[i].update({j:5})


# Bloques regulares efectivos
# Jornada de 8 horas

BR = 32 

# Bloques extra efectivos
# 1,5 horas

BE = 8 

# Maestro

BR2 = 40 # Bloques regulares nominales

BE2 = [k for k in range(1, 13)] # Bloques extra nominales

# Variable  que indica numero de pacientes con protocolo p que llegan en la semana

q = {1: 10, 2: 10, 3: 10}



#tiempo entre la sesion s y su primera sesion
#escrita como diccionario para que no hayan errores en los indices
K_ps = \
{1: {1: 0, 2: 5, 3: 10, 4: 11, 5: 12, 6: 13, 7: 14}, \
2: {1: 0, 2: 3, 3: 7, 4: 9, 5: 11}, \
3: {1: 0, 2: 4, 3: 10, 4: 15, 5: 20, 6: 23, 7: 26}}


##############
# PARÁMETROS #
##############

# Variable GAMMA

# Número de enfermeras

NE = 10

# Número de sillas

NS = 10

# Lp: maximo de días que puede esperar un paciente del protocolo p para empezar su tratamiento

Lp = {1: 15, 2: 15, 3: 15}

