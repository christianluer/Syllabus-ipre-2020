from gurobipy import *

from parametros import *

import numpy as np


#Maestro

maestro = Model("Asignacion")

# Variable generación de columnas

pi = {}

pi = maestro.addVars(C, lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name="Columna ingresada")


# Definiciones

# Función costo

k_c = {}

for c in C: 

    if c == contador_de_columnas:

        k_c[c] = quicksum(z_p_dada[p]*CD_p[p-1] for p in P) + quicksum(hora_extra * u_pstm_dada[p,s,t,m] * CM for hora_extra in BE2 for p in P for s in S[p] for t in T for m in range(BR2 + hora_extra, 53))

#porque p-1 en cdp?
# Omega 

omega_cpst = {}

for c in C: 

    if c == contador_de_columnas:

        for p in P: 

            for s in S[p]:

                for t in T:

                    if (t + 6 - K_ps[p][s]) > 0 and (t + 6) < 13:

                        omega_cpst[c,p,s,t] = w_pst_dada[p,s,t] - gamma * (w_pst_dada[p,s,(t + 6)] + x_pt_dada[p,(t + 6 - K_ps[p][s])])

                    else:

                        omega_cpst[c,p,s,t] = w_pst_dada[p,s,t]


# Rho

rho_cp = {}

for c in C: 

    if c == contador_de_columnas:

        for p in P: 

            rho_cp[c,p] = r_p_dada[p] - gamma * lambdas[p-1]


#Esperanza de W.

E_alpha_w = {}

for p in P:

    for s in S[p]:

        for t in T:

            E_alpha_w[p,s,t] = w_pst_dada[p,s,t] 


#Esperanza de R.

E_alpha_r = {}

for p in P: 

    E_alpha_r[p] = lambdas[p-1]                   


#Restricciones

#Restricción 1

maestro.addConstr((1 - gamma) * sum(pi[c] for c in C) == 1)

#Restricción 2

for p in P: 

    for s in S[p]:

        for t in T:
            
            maestro.addConstr(sum((omega_cpst[c,p,s,t] * pi[c]) for c in C) >= E_alpha_w[p,s,t])

#Restricción 3

for p in P: 

    maestro.addConstr(sum((rho_cp[c,p] * pi[c]) for c in C) >= E_alpha_r[p])

#Restricción 4

for c in C: 

    maestro.addConstr(pi[c] >= 0)


#Fijar F.O. 

maestro.setObjective(sum((k_c[c] * pi[c]) for c in C), GRB.MINIMIZE)


#Probar funcionamiento del modelo

maestro.optimize()