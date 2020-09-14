import numpy as np

from openpyxl import load_workbook

from gurobipy import *


# datos = load_workbook(filename="libro.xlsx",data_only=True)

# datos.active = 0

# sheet = datos.active

# Modulos = []

# for row in sheet.iter_rows(min_col=2,max_col=8,min_row=2,max_row=6):

#     for i in row:

#         Modulos.append(float(i.value))





#Conjuntos

# Días
T = [str(k) for k in range(1,7)] # 6 dias - 1, 2, ..., 6

# Protocolos
P = [str(k) for k in range(1,4)] # 3 protocolos - 1, 2, 3
Largo_P = [9, 6, 8] #Duracion de cada protocolo en sesiones

# Sesiones
S = {} #Sesiones del protocolo p

for i in P:

  S.update({i:[str(k) for k in range(1,Largo_P[int(i)-1] + 1)]}) #***

# Módulos
M = [str(k) for k in range(1,41)] # 40 bloques - 1, 2, ..., 40 
# 10 horas de trabajo, cada modulo consiste en 15 min

#Parametros

γ = 0.95

NE = 5 # Número de enfermeras

NS = 20 # Número sillas


Costos = [0.03,0.02,0.01] #Costos por protocolo

CD = dict(zip(P,Costos)) # Asocia los costos cada protocolo con su costo
# *** costo de derivacion por protocolo

Modulos = [5 for k in range(1,24)] # Duraciones de cada sesion

M_sp = {} # Cantidad de modulos de la sesion s del tratamiento p

for i in P:

    M_sp.update({i:{}})

    for j in S[i]:

        M_sp[i].update({j:Modulos.pop(0)})

# Todos las sesiones de todos los protocolos están usando 5 modulos cada uno

# Variable aleatoria que indica numero de pacientes con protocolo p que llegan en la semana
lambdas = [5, 4, 3] 
q = dict(zip(P,np.random.poisson(lambdas)))

# k_ps indica la distancia en dias desde s=s hasta s= 1 del protocolo p
K_ps = {} 

for i in P:

  K_ps.update({i:[k for k in range(1,Largo_P[int(i)-1] + 1)]})
# EN ESTE CASO  está considera que todas las sesiones se hacen consecutivas


model = Model("Asignacion")

# Para el satelite

β = 1

# Construccion de Wpst 
W = {}

for p in P:

    for s in S[p]:

        for t in T:

            W[p,s,t] = 1

# Construcción de Rp
R = {}

for p in P:

    R[p] = 5

# Construcción de ωpst

# Variables del satélite

ω = {}

for p in P:

    for s in S[p]:

        for t in T:

            ω[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="ω[%s,%s,%s]"%(p,s,t))

ρ = {}

for p in P:

    ρ[p] = model.addVar(0,vtype=GRB.INTEGER, name="ρ[%s]"%(p))


# Modelo

w = {}

y = {}

u = {}

# Variables de estado

# wpst cantidad de pacientes p que tienen su sesion s en el día t
for p in P:

    for s in S[p]:

        for t in T:

            w[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="w[%s,%s,%s]"%(p,s,t))

# Cantidad de pacientes en la semana del protocolo p
r = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="r")



# Variables de accion

# xpt cantiad de pacientes del protocolo p que inician su tratamiento el dia t
x = model.addVars(P,T, lb=0.0, vtype=GRB.INTEGER, name="x")

# ypstm cantidad de pacientes de p que comienzan su sesion s en modulo m del dia t
for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                y[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="y")

# z cantidad de pacientes de p que son derivados 
z = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="z")

# upstm terminan su sesion en elmodulo m del dia t
for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                u[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="u")



# Funcion costos

k_as = quicksum(CD[p] * z[p] for p in P) + quicksum(u[p,s,t,m] * (m_index + 1) for p in P for s in S[p] for t in T for m_index, m in enumerate(M))



model.setObjective( (1 - γ) * β + quicksum(ω[p,s,t] * W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(ρ[p] * R[p] for p in P) - k_as, GRB.MAXIMIZE)



# Restricciones

# Restricción 1: respetar cantidad de modulos de atencion

R1 = {}

# Para todo día t perteneciente a T
for t_index, t in enumerate(T):

    R1[t] = model.addConstr(quicksum(x[p,T[t_index-K_ps[p][int(s)-1]+1]] * M_sp[p][s]\

     for p in P for s in S[p] if t_index+1 >= K_ps[p][int(s)-1]) + quicksum(w[p,s,t] * M_sp[p][s]\

     for p in P for s in S[p] if t_index+1 >= K_ps[p][int(s)-1]) <= 40, name="Capacidad bloques[%s]" %t)


# Restricción 2: definifinición de y

R2 = {}

# Para cada p en P
for p in P:
    # Para cada sesión s en S(p
    for s in S[p]:
        # Para cada t en T
        for t_index, t in enumerate(T):
            # Condicion para evitar exponente igual a 0
            if t_index+1 >= K_ps[p][int(s)-1]:

                R2[p,s,t] = model.addConstr(quicksum(y[p,s,t,m] for m in M) == x[p,T[t_index-K_ps[p][int(s)-1]+1]] + w[p,s,t]\

                , name="Definicion y [%s, %s, %s]"%(p,s,t))


# Restricción 3: conservacion de flujo de pacientes
# Definición de r_p

model.addConstrs((r[p] == z[p] + quicksum(x[p,t] for t in T) for p in P), name="Conservacion de flujo")

# Restriccion 4: definicion de u, con y

R4 = {}

for p in P:

    for s in S[p]:

        for t in T:

            for m_index, m in enumerate(M):

                if m_index + M_sp[p][s] <= 40:

                    R4[p,s,t,m] = model.addConstr(y[p,s,t,m] == u[p,s,t,M[m_index - M_sp[p][s] - 1]], name="definicion u [%s, %s, %s, %s]"%(p,s,t,m))

# Restriccion 5: capacidad sillas

model.addConstrs(( quicksum(y[p,s,t,m] + quicksum(y[p,s,t,M[m_index]] for m_index in range(max(1, m_index - M_sp[p][s])))\

 for p in P for s in S[p]) <= NS for t in T for m_index, m in enumerate(M) ), name="Capacidad sillas")

# Restriccion 6: enfermeras

model.addConstrs((quicksum(y[p,s,t,m] for p in P for s in S[p]) + quicksum(u[p,s,t,m] for p in P for s in S[p])\

 <= NE for t in T for m in M), name="Capacidad enfermeras")

# Restricción 7: definicion ω

R7 = {}

for p in P:

    for s in S[p]:

        for t_index, t in enumerate(T):

            if t_index + 1 >= K_ps[p][int(s)-1]:

                R7[p,s,t] = model.addConstr(ω[p,s,t] == w[p,s,t] - γ * (w[p,s,T[t_index]] + x[p,T[t_index]]), name="Definicion ω")

# Restricción 8

model.addConstrs((r[p] == q[p] for p in P), name="Realizacion de las llegadas")


# Definicion ρ

model.addConstrs((ρ[p] == r[p] for p in P), name="Definicion ρ")

#Restricciones que relacionan los ω y los ρ



model.update()

model.optimize()

model.printAttr("X")