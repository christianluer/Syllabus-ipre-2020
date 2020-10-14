from gurobipy import *

import numpy as np

#############
# CONJUNTOS #
#############

# PROTOCOLOS

P = [k for k in range(1,4)] 
# 3 protocolos - 1, 2, 3

Largo_P = [9, 6, 8] 
# Duracion de cada protocolo en sesiones

# SESIONES

# Sesiones del protocolo p

S = {} 

for i in P:

  S.update({i:[k for k in range(1,Largo_P[int(i)-1] + 1)]})
print(S)

# MÓDULOS - maestro usaba 53

M = [k for k in range(1,41)] 
# 40 bloques - 1, 2, ..., 40 
# 10 horas de trabajo, cada modulo consiste en 15 min


##############
# PARÁMETROS #
##############


# Variable GAMMA - maestro dice "gamma"

γ = 0.95

# Costos por protocolo

Costos = [100,100,100] #porque son estos???

CD = dict(zip(P,Costos)) 
# Asocia los costos cada protocolo con su costo de derivación

# Costo bloque regular

CR = 100 

# Costo bloque extra

CE = 200 

CM = (CE - CR)/4 # Costo marginal por bloque extra de atención #???


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

BE = 9 

# Maestro

BR2 = 40 # Bloques regulares nominales

BE2 = [k for k in range(1, 13)] # Bloques extra nominales

# Variable aleatoria que indica numero de pacientes con protocolo p que llegan en la semana

lambdas = [5, 4, 3] ##lambdas derbería coincidir con las llegadas
q = dict(zip(P,np.random.poisson(lambdas)))






