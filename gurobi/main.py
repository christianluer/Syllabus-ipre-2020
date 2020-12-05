from gurobipy import *

from parametros import *

import numpy as np



# GENERACIÓN DE COLUMNAS

contador_de_columnas = 1

C = [k for k in range(1, contador_de_columnas + 1)] # Número de columnas


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





###########
# Maestro #
###########

maestro = Model("main")

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

#el hora extra estaría multiplicando como 1*u+2*u+3*u???

# OMEGA

omega_cpst = {}

for c in C: 

    if c == contador_de_columnas:

        for p in P: 

            for s in S[p]:

                for t in T:

                    if (int(t) + 6 - K_ps[p][s]) > 0 and (int(t) + 6) < 13:

                        omega_cpst[c,p,s,t] = w_pst_dada[p,s,t] - γ * (w_pst_dada[p,s,(t + 6)] + x_pt_dada[p,(t + 6 - K_ps[p][s])])

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

#maestro.computeIIS()

#maestro.write("output_maestro.ilp")

maestro.printAttr("X")

