from gurobipy import *

import numpy as np


# Conjuntos

contador_de_columnas = 1

C = [k for k in range(1, contador_de_columnas + 1)] # Número de columnas

# Otros conjuntos 

T = [k for k in range(1, 13)] # 2 semanas sin contar los domingos
# Buen punto inicial para revisar factibilidad

P = [k for k in range(1, 4)] #3 protocolos  
# Buena simplificación  

M = [k for k in range(1, 53)] #52 módulos incluídas horas extra
# 13 horas en total
##esta distinto al pricing, cual tomar?

S = {1: [0,1,2,3,4,5,6,7,8], 2: [0,1,2,3,4,5], 3: [0,1,2,3,4,5,6,7]} 
# Duración de las sesiones por protocolo p sin contar los días de descanso
# quizas hacer la construcción de los parámetros igual que en el pricing?

# Parámetros utilizados en el modelo, modificables

CD_p = [1, 1, 1] # Costo derivación por protocolo (también están distintos a los del pricing)

BR = 32 # Bloques regulares efectivos
# Jornada de 8 horas

BE = 9 # Bloques extra efectivos
# 1,5 horas

BR2 = 40 # Bloques regulares nominales

BE2 = [k for k in range(1, 13)] # Bloques extra nominales

CE = 250 # Costo hora extra #arreglar con respecto al pricing

CR = 100 # Costo hora regular

CM = (CE - CR)/4 # Costo marginal por bloque extra de atención #???

K_ps = {1: [0,1,2,5,6,7,13,14,15], 2: [0,1,8,9,16,18], 3: [0,2,4,6,8,10,12,14]} 
# Días desde que un paciente con protocolo p inicia su tratamiento hasta que está en la sesión s 
#quizas deberíamos ocupar los mismos que en el pricing

M_ps = {1: [2,2 ,2,4,4,4,2,2,2], 2: [22,22,22,22,22,18], 3: [12,8,12,8,12,8,12,8]} 
# Corresponde a la duración en módulos de la sesión s del protocolo p

gamma = 0.99

lambdas = [1.6, 1.1, 2.1] # tasa de llegada dist. poisson


# Variables iniciales arbitrarias

# Variables de estado (parámetros obtenidos del pricing)

# Variable de estado W-p,s,t
# Cantidad de pacientes con protocolo p que tienen agendada su sesión s en el día t

w_pst_dada = {} #cantididad de pacientes con protocolo p que tiene su sesión s el día t

for p in P:
# Para cada protocolo

    for s in S[p]: 
    #Para cada sesión

        for t in T: 
        #Para cada día

            w_pst_dada[p,s,t] = 0
            # Variable de estado
            # Cantidad de protocolos p en sesión s en día t

#Valores iniciales

w_pst_dada[1,1,1]=0

w_pst_dada[2,1,1]=0

w_pst_dada[3,1,1]=0

w_pst_dada[2,1,2]=0

w_pst_dada[1,2,2]=0

w_pst_dada[2,2,2]=0

w_pst_dada[1,1,3]=0

w_pst_dada[1,3,3]=0

w_pst_dada[3,2,3]=0

w_pst_dada[2,2,3]=0

w_pst_dada[1,2,4]=0

w_pst_dada[1,1,5]=0

w_pst_dada[1,3,5]=0

w_pst_dada[2,1,5]=0

w_pst_dada[3,3,5]=0

w_pst_dada[1,2,6]=0

w_pst_dada[1,4,6]=0

w_pst_dada[2,2,6]=0

w_pst_dada[1,3,7]=0

w_pst_dada[1,5,7]=0

w_pst_dada[2,1,7]=0

w_pst_dada[3,4,7]=0

w_pst_dada[1,4,8]=0

w_pst_dada[1,6,8]=0

w_pst_dada[2,2,8]=0

w_pst_dada[1,5,9]=0

w_pst_dada[2,3,9]=0

w_pst_dada[3,5,9]=0

w_pst_dada[1,4,10]=0

w_pst_dada[1,6,10]=0

w_pst_dada[2,3,10]=0

w_pst_dada[2,4,10]=0

w_pst_dada[1,5,11]=0

w_pst_dada[2,4,11]=0

w_pst_dada[3,6,11]=0

w_pst_dada[1,6,12]=0

w_pst_dada[3,1,12]=0


# Variable de estado R-p
# Cantidad de pacientes con protocolo p que llegaron en el último periodo

r_p_dada = {}

for p in P:

    r_p_dada[p] = 0

# Valores Iniciales

r_p_dada[1] = 5

r_p_dada[2] = 3

r_p_dada[3] = 4


# Variables de estado acción (parámetros obtenidos del pricing)

# Variable de estado Z-p
# Cantidad de protocolos p derivados a sistema privado

z_p_dada = {}

for p in P:

    z_p_dada[p] = 0

# Valores Iniciales

z_p_dada[1] = 5

z_p_dada[2] = 3

z_p_dada[3] = 4
#No debeían ser 0?

# Variable de estado X-p,t
# Cantidad de pacientes con protocolo p con sesión agendada en día t
# Permite realizar calendarización interdía

x_pt_dada = {}

for p in P:

    for t in T: 

        x_pt_dada[p,t] = 0

# Valores Iniciales

x_pt_dada[1,1] = 0

x_pt_dada[2,1] = 0

x_pt_dada[3,1] = 0

x_pt_dada[2,2] = 0

x_pt_dada[1,3] = 0

x_pt_dada[1,5] = 0

x_pt_dada[2,5] = 0

x_pt_dada[2,7] = 0

x_pt_dada[3,12] =0


# Variable de estado Y-p,t,s,m
# Cantidad de pacientes protocolo p, sesión s, día t, módulo m
# Variable a cargo de caldarización intradía

y_pstm_dada = {}

for p in P:

    for s in S[p]:

        for t in T: 

            for m in M: 

                y_pstm_dada[p,s,t,m] = 0


# Variable de estado U-p,t,s,m
# Cantidad de pacientes con protocolo p que en el día t terminan 
# su sesión s en el módulo m

u_pstm_dada = {}

for p in P:

    for s in S[p]:

        for t in T: 

            for m in M:

                u_pstm_dada[p,s,t,m] = 0


# Valores Iniciales

y_pstm_dada[1,1,1,1] =  0

y_pstm_dada[1,1,1,3] =  0

y_pstm_dada[1,1,1,5] =  0

y_pstm_dada[2,1,1,7] =  0

y_pstm_dada[3,1,1,29] = 0

u_pstm_dada[1,1,1,2] =  0

u_pstm_dada[1,1,1,4] =  0

u_pstm_dada[1,1,1,6] =  0

u_pstm_dada[2,1,1,28] = 0

u_pstm_dada[3,1,1,52] = 0

y_pstm_dada[1,2,2,1] =  0

y_pstm_dada[1,2,2,3] =  0

y_pstm_dada[1,2,2,5] =  0

y_pstm_dada[2,2,2,7] =  0

y_pstm_dada[2,2,2,29] = 0

u_pstm_dada[1,2,2,2] =  0

u_pstm_dada[1,2,2,4] =  0

u_pstm_dada[1,2,2,6] =  0

u_pstm_dada[2,2,2,28] = 0

u_pstm_dada[2,2,2,50] = 0

y_pstm_dada[1,3,3,1] =  0

y_pstm_dada[1,3,3,3] =  0

y_pstm_dada[1,3,3,5] =  0

y_pstm_dada[1,1,3,45] = 0

y_pstm_dada[2,2,3,23] = 0

y_pstm_dada[3,2,3,7] =  0

y_pstm_dada[3,2,3,15] = 0

u_pstm_dada[1,3,3,2] =  0

u_pstm_dada[1,3,3,4] =  0

u_pstm_dada[1,3,3,6] =  0

u_pstm_dada[1,1,3,46] = 0

u_pstm_dada[2,2,3,44] = 0

u_pstm_dada[3,2,3,14] = 0

u_pstm_dada[3,2,3,22] = 0

y_pstm_dada[1,2,4,1] =  0

u_pstm_dada[1,2,4,2] =  0

y_pstm_dada[1,1,5,27] = 0

y_pstm_dada[1,3,5,25] = 0

y_pstm_dada[2,1,5,29] = 0

y_pstm_dada[3,3,5,1] =  0

y_pstm_dada[3,3,5,13] = 0

u_pstm_dada[1,1,5,28] = 0

u_pstm_dada[1,3,5,26] = 0

u_pstm_dada[2,1,5,50] = 0

u_pstm_dada[3,3,5,12] = 0

u_pstm_dada[3,3,5,14] = 0

y_pstm_dada[1,2,6,13] = 0

y_pstm_dada[1,4,6,1] =  0

y_pstm_dada[1,4,6,5] =  0

y_pstm_dada[1,4,6,9] =  0

y_pstm_dada[2,2,6,15] = 0

u_pstm_dada[1,2,6,14] = 0

u_pstm_dada[1,4,6,4] =  0

u_pstm_dada[1,4,6,8] =  0

u_pstm_dada[1,4,6,12] = 0

u_pstm_dada[2,2,6,46] = 0

y_pstm_dada[1,5,7,1] =  0

y_pstm_dada[1,5,7,5] =  0

y_pstm_dada[1,5,7,9] =  0

y_pstm_dada[1,3,7,29] = 0

y_pstm_dada[2,1,7,31] = 0

y_pstm_dada[3,4,7,13] = 0

y_pstm_dada[3,4,7,21] = 0

u_pstm_dada[1,5,7,4] =  0

u_pstm_dada[1,5,7,8] =  0

u_pstm_dada[1,5,7,12] = 0

u_pstm_dada[1,3,7,30] = 0

u_pstm_dada[2,1,7,52] = 0

u_pstm_dada[3,4,7,20] = 0

u_pstm_dada[3,4,7,28] = 0

y_pstm_dada[1,4,8,13] = 0

y_pstm_dada[1,6,8,1] =  0

y_pstm_dada[1,6,8,5] =  0

y_pstm_dada[1,6,8,9] =  0

y_pstm_dada[2,2,8,17] = 0

u_pstm_dada[1,4,8,16] = 0

u_pstm_dada[1,6,8,4] =  0

u_pstm_dada[1,6,8,8] =  0

u_pstm_dada[1,6,8,12] = 0

u_pstm_dada[2,2,8,38] = 0

y_pstm_dada[1,5,9,47] = 0

y_pstm_dada[2,3,9,1] =  0

y_pstm_dada[3,5,9,23] = 0

y_pstm_dada[3,5,9,31] = 0

u_pstm_dada[1,5,9,50] = 0

u_pstm_dada[2,3,9,22] = 0

u_pstm_dada[3,5,9,30] = 0

u_pstm_dada[3,5,9,38] = 0

y_pstm_dada[1,4,10,49] = 0

y_pstm_dada[1,6,10,45] = 0

y_pstm_dada[2,4,10,1] = 0

y_pstm_dada[2,3,10,23] = 0

u_pstm_dada[1,4,10,52] = 0

u_pstm_dada[1,6,10,48] = 0

u_pstm_dada[2,4,10,22] = 0

u_pstm_dada[2,3,10,44] = 0

y_pstm_dada[1,5,11,39] = 0

y_pstm_dada[2,4,11,17] = 0

y_pstm_dada[3,6,11,1] = 0

y_pstm_dada[3,6,11,9] = 0

u_pstm_dada[1,5,11,42] = 0

u_pstm_dada[2,4,11,38] = 0

u_pstm_dada[3,6,11,8] = 0

u_pstm_dada[3,6,11,16] = 0

y_pstm_dada[1,6,12,1] = 0

y_pstm_dada[3,1,12,5] = 0

y_pstm_dada[3,1,12,17] = 0

u_pstm_dada[1,6,12,4] = 0

u_pstm_dada[3,1,12,16] = 0

u_pstm_dada[3,1,12,28] = 0