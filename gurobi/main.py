from gurobipy import *

from parametros import *

import numpy as np


#############
# CONJUNTOS #
#############

# DÍAS

T = [int(k) for k in range(1,13)] 
# 14 dias - 1, 2, ..., 13


#K_ps = {1: [0,1,2,5,6,7,12,13,14], 2: [0,1,8,9,16,18], 3: [0,2,4,6,8,10,12,14]} 
# Días desde que un paciente con protocolo p inicia su tratamiento hasta que está en la sesión s 
#quizas deberíamos ocupar los mismos que en el pricing


# GENERACIÓN DE COLUMNAS

contador_de_columnas = 1

C = [k for k in range(1, contador_de_columnas + 1)] # Número de columnas

K_ps = {1: [0,1,2,5,6,7,12,13,14], 2: [0,1,8,9,16,18], 3: [0,2,4,6,8,10,12,14]} 
###################################
# VARIABLES INICIALES ARBITRARIAS #
###################################

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

#w_pst_dada[1,1,1]=3
#
#w_pst_dada[2,1,1]=1
#
#w_pst_dada[3,1,1]=2
#
#w_pst_dada[2,1,2]=1
#
#w_pst_dada[1,2,2]=3
#
#w_pst_dada[2,2,2]=1
#
#w_pst_dada[1,1,3]=1
#
#w_pst_dada[1,3,3]=3
#
#w_pst_dada[3,2,3]=2
#
#w_pst_dada[2,2,3]=1
#
#w_pst_dada[1,2,4]=1
#
#w_pst_dada[1,1,5]=1
#
#w_pst_dada[1,3,5]=1
#
#w_pst_dada[2,1,5]=1
#
#w_pst_dada[3,3,5]=2
#
#w_pst_dada[1,2,6]=1
#
#w_pst_dada[1,4,6]=3
#
#w_pst_dada[2,2,6]=1
#
#w_pst_dada[1,3,7]=1
#
#w_pst_dada[1,5,7]=3
#
#w_pst_dada[2,1,7]=1
#
#w_pst_dada[3,4,7]=2
#
#w_pst_dada[1,4,8]=1
#
#w_pst_dada[1,6,8]=3
#
#w_pst_dada[2,2,8]=1
#
#w_pst_dada[1,5,9]=1
#
#w_pst_dada[2,3,9]=1
#
#w_pst_dada[3,5,9]=2
#
#w_pst_dada[1,4,10]=1
#
#w_pst_dada[1,6,10]=1
#
#w_pst_dada[2,3,10]=1
#
#w_pst_dada[2,4,10]=1
#
#w_pst_dada[1,5,11]=1
#
#w_pst_dada[2,4,11]=1
#
#w_pst_dada[3,6,11]=2
#
#w_pst_dada[1,6,12]=1
#
#w_pst_dada[3,1,12]=2


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



# Variable de estado X-p,t
# Cantidad de pacientes con protocolo p con sesión agendada en día t
# Permite realizar calendarización interdía

x_pt_dada = {}

for p in P:

    for t in T: 

        x_pt_dada[p,t] = 0

# Valores Iniciales

#x_pt_dada[1,1] = 3
#
#x_pt_dada[2,1] = 1
#
#x_pt_dada[3,1] = 2
#
#x_pt_dada[2,2] = 1
#
#x_pt_dada[1,3] = 1
#
#x_pt_dada[1,5] = 1
#
#x_pt_dada[2,5] = 1
#
#x_pt_dada[2,7] = 1
#
#x_pt_dada[3,12] = 2


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

#y_pstm_dada[1,1,1,1] = 1
#
#y_pstm_dada[1,1,1,3] = 1
#
#y_pstm_dada[1,1,1,5] = 1
#
#y_pstm_dada[2,1,1,7] = 1
#
#y_pstm_dada[3,1,1,29] = 1
#
#u_pstm_dada[1,1,1,2] = 1
#
#u_pstm_dada[1,1,1,4] = 1
#
#u_pstm_dada[1,1,1,6] = 1
#
#u_pstm_dada[2,1,1,28] = 1
#
#u_pstm_dada[3,1,1,52] = 1
#
#y_pstm_dada[1,2,2,1] = 1
#
#y_pstm_dada[1,2,2,3] = 1
#
#y_pstm_dada[1,2,2,5] = 1
#
#y_pstm_dada[2,2,2,7] = 1
#
#y_pstm_dada[2,2,2,29] = 1
#
#u_pstm_dada[1,2,2,2] = 1
#
#u_pstm_dada[1,2,2,4] = 1
#
#u_pstm_dada[1,2,2,6] = 1
#
#u_pstm_dada[2,2,2,28] = 1
#
#u_pstm_dada[2,2,2,50] = 1
#
#y_pstm_dada[1,3,3,1] = 1
#
#y_pstm_dada[1,3,3,3] = 1
#
#y_pstm_dada[1,3,3,5] = 1
#
#y_pstm_dada[1,1,3,45] = 1
#
#y_pstm_dada[2,2,3,23] = 1
#
#y_pstm_dada[3,2,3,7] = 1
#
#y_pstm_dada[3,2,3,15] = 1
#
#u_pstm_dada[1,3,3,2] = 1
#
#u_pstm_dada[1,3,3,4] = 1
#
#u_pstm_dada[1,3,3,6] = 1
#
#u_pstm_dada[1,1,3,46] = 1
#
#u_pstm_dada[2,2,3,44] = 1
#
#u_pstm_dada[3,2,3,14] = 1
#
#u_pstm_dada[3,2,3,22] = 1
#
#y_pstm_dada[1,2,4,1] = 1
#
#u_pstm_dada[1,2,4,2] = 1
#
#y_pstm_dada[1,1,5,27] = 1
#
#y_pstm_dada[1,3,5,25] = 1
#
#y_pstm_dada[2,1,5,29] = 1
#
#y_pstm_dada[3,3,5,1] = 1
#
#y_pstm_dada[3,3,5,13] = 1
#
#u_pstm_dada[1,1,5,28] = 1
#
#u_pstm_dada[1,3,5,26] = 1
#
#u_pstm_dada[2,1,5,50] = 1
#
#u_pstm_dada[3,3,5,12] = 1
#
#u_pstm_dada[3,3,5,14] = 1
#
#y_pstm_dada[1,2,6,13] = 1
#
#y_pstm_dada[1,4,6,1] = 1
#
#y_pstm_dada[1,4,6,5] = 1
#
#y_pstm_dada[1,4,6,9] = 1
#
#y_pstm_dada[2,2,6,15] = 1
#
#u_pstm_dada[1,2,6,14] = 1
#
#u_pstm_dada[1,4,6,4] = 1
#
#u_pstm_dada[1,4,6,8] = 1
#
#u_pstm_dada[1,4,6,12] = 1
#
#u_pstm_dada[2,2,6,46] = 1
#
#y_pstm_dada[1,5,7,1] = 1
#
#y_pstm_dada[1,5,7,5] = 1
#
#y_pstm_dada[1,5,7,9] = 1
#
#y_pstm_dada[1,3,7,29] = 1
#
#y_pstm_dada[2,1,7,31] = 1
#
#y_pstm_dada[3,4,7,13] = 1
#
#y_pstm_dada[3,4,7,21] = 1
#
#u_pstm_dada[1,5,7,4] = 1
#
#u_pstm_dada[1,5,7,8] = 1
#
#u_pstm_dada[1,5,7,12] = 1
#
#u_pstm_dada[1,3,7,30] = 1
#
#u_pstm_dada[2,1,7,52] = 1
#
#u_pstm_dada[3,4,7,20] = 1
#
#u_pstm_dada[3,4,7,28] = 1
#
#y_pstm_dada[1,4,8,13] = 1
#
#y_pstm_dada[1,6,8,1] = 1
#
#y_pstm_dada[1,6,8,5] = 1
#
#y_pstm_dada[1,6,8,9] = 1
#
#y_pstm_dada[2,2,8,17] = 1
#
#u_pstm_dada[1,4,8,16] = 1
#
#u_pstm_dada[1,6,8,4] = 1
#
#u_pstm_dada[1,6,8,8] = 1
#
#u_pstm_dada[1,6,8,12] = 1
#
#u_pstm_dada[2,2,8,38] = 1
#
#y_pstm_dada[1,5,9,47] = 1
#
#y_pstm_dada[2,3,9,1] = 1
#
#y_pstm_dada[3,5,9,23] = 1
#
#y_pstm_dada[3,5,9,31] = 1
#
#u_pstm_dada[1,5,9,50] = 1
#
#u_pstm_dada[2,3,9,22] = 1
#
#u_pstm_dada[3,5,9,30] = 1
#
#u_pstm_dada[3,5,9,38] = 1
#
#y_pstm_dada[1,4,10,49] = 1
#
#y_pstm_dada[1,6,10,45] = 1
#
#y_pstm_dada[2,4,10,1] = 1
#
#y_pstm_dada[2,3,10,23] = 1
#
#u_pstm_dada[1,4,10,52] = 1
#
#u_pstm_dada[1,6,10,48] = 1
#
#u_pstm_dada[2,4,10,22] = 1
#
#u_pstm_dada[2,3,10,44] = 1
#
#y_pstm_dada[1,5,11,39] = 1
#
#y_pstm_dada[2,4,11,17] = 1
#
#y_pstm_dada[3,6,11,1] = 1
#
#y_pstm_dada[3,6,11,9] = 1
#
#u_pstm_dada[1,5,11,42] = 1
#
#u_pstm_dada[2,4,11,38] = 1
#
#u_pstm_dada[3,6,11,8] = 1
#
#u_pstm_dada[3,6,11,16] = 1
#
#y_pstm_dada[1,6,12,1] = 1
#
#y_pstm_dada[3,1,12,5] = 1
#
#y_pstm_dada[3,1,12,17] = 1
#
#u_pstm_dada[1,6,12,4] = 1
#
#u_pstm_dada[3,1,12,16] = 1
#
#u_pstm_dada[3,1,12,28] = 1


###########
# Maestro #
###########

maestro = Model("Asignacion")

# Variable generación de columnas

pi = {}

pi = maestro.addVars(C, lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name="Columna ingresada")

################
# DEFINICIONES #
################

#################
# FUNCIÓN COSTO #
#################
# En informe (9)

k_c = {}

for c in C: 

    if c == contador_de_columnas:

        k_c[c] = quicksum(z_p_dada[p]*CD[p] for p in P) + quicksum(hora_extra * u_pstm_dada[p,s,t,m] * CM for hora_extra in BE2 for p in P for s in S[p] for t in T for m in range(BR2 + hora_extra, 41))

# ¿Porque p-1 en cdp? Para alinear protocolos (1,2,3) con índice de búsqueda (0,1,2)
#pero es un diccionario
#el hora extra estaría multiplicando como 1*u+2*u+3*u???
#aparecía hasta 51, deberia ser 43 o no?
# OMEGA

omega_cpst = {}

for c in C: 

    if c == contador_de_columnas:

        for p in P: 

            for s in S[p]:

                for t in T:

                    if (int(t) + 6 - K_ps[p][s-1]) > 0 and (int(t) + 6) < 13:

                        omega_cpst[c,p,s,t] = w_pst_dada[p,s,t] - γ * (w_pst_dada[p,s,(t + 6)] + x_pt_dada[p,(t + 6 - K_ps[p][s-1])])

                    else:

                        omega_cpst[c,p,s,t] = w_pst_dada[p,s,t]


# RHO

rho_cp = {}

for c in C: 

    if c == contador_de_columnas:

        for p in P: 

            rho_cp[c,p] = r_p_dada[p] - γ * lambdas[p-1]


# Esperanza de W

E_alpha_w = {}

for p in P:

    for s in S[p]:

        for t in T:

            E_alpha_w[p,s,t] = w_pst_dada[p,s,t] 


# Esperanza de R

E_alpha_r = {}

for p in P: 

    E_alpha_r[p] = lambdas[p-1]                   


#################
# RESTRICCIONES #
#################

# Restricción 1

maestro.addConstr((1 - γ) * sum(pi[c] for c in C) == 1)

# Restricción 2

for p in P: 

    for s in S[p]:

        for t in T:
            
            maestro.addConstr(sum((omega_cpst[c,p,s,t] * pi[c]) for c in C) >= E_alpha_w[p,s,t])

# Restricción 3

for p in P: 

    maestro.addConstr(sum((rho_cp[c,p] * pi[c]) for c in C) >= E_alpha_r[p])

# Restricción 4

for c in C: 

    maestro.addConstr(pi[c] >= 0)


####################
# FUNCIÓN OBJETIVO #
####################

maestro.setObjective(sum((k_c[c] * pi[c]) for c in C), GRB.MINIMIZE)

#Probar funcionamiento del modelo

maestro.optimize()

maestro.computeIIS()

maestro.write("output_maestro.ilp")

