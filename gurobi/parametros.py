from gurobipy import *

import numpy as np

#############
# CONJUNTOS #
#############


# PROTOCOLOS

P = [k for k in range(1,4)] 
# 3 protocolos - 1, 2, 3

Largo_P = [8, 6, 8] 
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

T = [int(k) for k in range(1,21)]

##############
# PARÁMETROS #
##############


# Variable GAMMA - maestro dice "gamma"

γ = 0.95

# Costos por protocolo

Costos = [10000000,10000000,10000000]

CD = dict(zip(P,Costos)) 
# Asocia los costos cada protocolo con su costo de derivación

# Costo bloque regular

CR = 10000 

# Costo bloque extra

CE = 25000 

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

# Variable aleatoria que indica numero de pacientes con protocolo p que llegan en la semana

lambdas = [5, 5, 5] 
q = {1: 5, 2: 5, 3: 5}
#CAMBIO PARA QUE NO SEA ALEATORIO


#tiempo entre la sesion s y su primera sesion
#escrita como diccionario para que no hayan errores en los indices
K_ps = \
{1: {1: 0, 2: 1, 3: 2, 4: 4, 5: 6, 6: 8, 7: 10, 8: 11}, \
2: {1: 0, 2: 1, 3: 8, 4: 9, 5: 10, 6: 12}, \
3: {1: 0, 2: 2, 3: 4, 4: 6, 5: 8, 6: 10, 7: 11, 8: 12}}


##############
# PARÁMETROS #
##############

# Variable GAMMA

# Número de enfermeras

NE = 1000000

# Número de sillas

NS = 500000

# Lp: maximo de días que puede esperar un paciente del protocolo p para empezar su tratamiento

Lp = {1: 5, 2: 5, 3: 5}
