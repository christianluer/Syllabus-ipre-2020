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

T = [str(k) for k in range(1,7)] #6 dias

P = [str(k) for k in range(1,4)] # 3 protocolos

M = [str(k) for k in range(1,41)] # 40 bloques

Largo_P = [9,6,8] #Duracion de cada protocolo

S = {} #Sesiones del protocolo p

for i in P:

  S.update({i:[str(k) for k in range(1,Largo_P[int(i)-1] + 1)]})





#Parametros

γ = 0.95

NE = 5 #Número de enfermeras

NS = 20 #Número sillas



Costos = [0.03,0.02,0.01] #Costos por protocolo

CD = dict(zip(P,Costos))

Modulos = [5 for k in range(1,24)] #Duraciones de cada sesion

M_sp = {} #Modulos de la sesion s del tratamiento p

for i in P:

    M_sp.update({i:{}})

    for j in S[i]:

        M_sp[i].update({j:Modulos.pop(0)})



lambdas = [5,4,3] # promedio de llegada protocolo p

q = dict(zip(P,np.random.poisson(lambdas)))

K_ps = {} #Sesiones del protocolo p

for i in P:

  K_ps.update({i:[k for k in range(1,Largo_P[int(i)-1] + 1)]})



model = Model("Asignacion")

#Para el satelite

β = 1

W = {}

for p in P:

    for s in S[p]:

        for t in T:

            W[p,s,t] = 1

R = {}

for p in P:

    R[p] = 5



ω = {}

for p in P:

    for s in S[p]:

        for t in T:

            ω[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="ω[%s,%s,%s]"%(p,s,t))

ρ = {}

for p in P:

    ρ[p] = model.addVar(0,vtype=GRB.INTEGER, name="ρ[%s]"%(p))

#Modelo



w = {}

y = {}

u = {}

#Variables de estado

for p in P:

    for s in S[p]:

        for t in T:

            w[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="w[%s,%s,%s]"%(p,s,t))

r = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="r")



#Variables de accion

x = model.addVars(P,T, lb=0.0, vtype=GRB.INTEGER, name="x")

for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                y[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="y")

z = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="z")

for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                u[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="u")



#Funcion costos

k_as = quicksum(CD[p] * z[p] for p in P) + quicksum(u[p,s,t,m] * (m_index + 1) for p in P for s in S[p] for t in T for m_index, m in enumerate(M))



model.setObjective( (1 - γ) * β + quicksum(ω[p,s,t] * W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(ρ[p] * R[p] for p in P) - k_as, GRB.MAXIMIZE)



#Restricciones

R1 = {}

for p in P:

    for s in S[p]:

        for t_index, t in enumerate(T):

            if t_index+1 >= K_ps[p][int(s)-1]:

                R1[p,s,t] = model.addConstr(quicksum(y[p,s,t,m] for m in M) == x[p,T[t_index-K_ps[p][int(s)-1]+1]] + w[p,s,t]\

                , name="definicion y [%s, %s, %s]"%(p,s,t))



R2 = {}

for t_index, t in enumerate(T):

    R2[t] = model.addConstr(quicksum(x[p,T[t_index-K_ps[p][int(s)-1]+1]] * M_sp[p][s]\

     for p in P for s in S[p] if t_index+1 >= K_ps[p][int(s)-1]) + quicksum(w[p,s,t] * M_sp[p][s]\

     for p in P for s in S[p] if t_index+1 >= K_ps[p][int(s)-1]) <= 40, name="capacidad bloques[%s]" %t)





model.addConstrs((r[p] == q[p] for p in P), name="Realizacion de las llegadas")

model.addConstrs((r[p] == z[p] + quicksum(x[p,t] for t in T) for p in P), name="conservacion de flujo")

model.addConstrs((quicksum(y[p,s,t,m] for p in P for s in S[p]) + quicksum(u[p,s,t,m] for p in P for s in S[p])\

 <= NE for t in T for m in M), name="Capacidad enfermeras")





R3 = {}

for p in P:

    for s in S[p]:

        for t in T:

            for m_index, m in enumerate(M):

                if m_index + M_sp[p][s] <= 40:

                    R3[p,s,t,m] = model.addConstr(y[p,s,t,m] == u[p,s,t,M[m_index - M_sp[p][s] - 1]], name="definicion u [%s, %s, %s, %s]"%(p,s,t,m))



model.addConstrs(( quicksum(y[p,s,t,m] + quicksum(y[p,s,t,M[m_index]] for m_index in range(max(1, m_index - M_sp[p][s])))\

 for p in P for s in S[p]) <= NS for t in T for m_index, m in enumerate(M) ), name="capacidad sillas")







R4 = {}

for p in P:

    for s in S[p]:

        for t_index, t in enumerate(T):

            if t_index + 1 >= K_ps[p][int(s)-1]:

                R4[p,s,t] = model.addConstr(ω[p,s,t] == w[p,s,t] - γ * (w[p,s,T[t_index]] + x[p,T[t_index]]), name="definicion ω")



model.addConstrs((ρ[p] == r[p] for p in P), name="definicion ρ")



#Resrticciones que relacionan los ω y los ρ



model.update()



model.optimize()

model.printAttr("X")