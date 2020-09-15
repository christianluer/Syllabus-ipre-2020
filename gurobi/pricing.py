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


#############
# CONJUNTOS #
#############

# DÍAS

T = [str(k) for k in range(1,7)] # 6 dias - 1, 2, ..., 6

# PROTOCOLOS

P = [str(k) for k in range(1,4)] # 3 protocolos - 1, 2, 3
Largo_P = [9, 6, 8] #Duracion de cada protocolo en sesiones

P = [str(k) for k in range(1,4)] # 3 protocolos

Largo_P = [9,6,8] #Duracion de cada protocolo en sesiones


# SESIONES

# Sesiones del protocolo p

S = {} 

for i in P:

  S.update({i:[str(k) for k in range(1,Largo_P[int(i)-1] + 1)]})

# MÓDULOS

M = [str(k) for k in range(1,41)] 
# 40 bloques - 1, 2, ..., 40 
# 10 horas de trabajo, cada modulo consiste en 15 min


##############
# PARÁMETROS #
##############

# Variable GAMMA

γ = 0.95

# Número de enfermeras

NE = 5 

# Número de sillas

NS = 20 

# Costos por protocolo

Costos = [0.03,0.02,0.01] 

CD = dict(zip(P,Costos)) 
# Asocia los costos cada protocolo con su costo
# *** costo de derivacion por protocolo

# Duraciones de cada sesion

Modulos = [5 for k in range(1,24)] 

# Cantidad de modulos de la sesion s del tratamiento p

M_sp = {} 

for i in P:

    M_sp.update({i:{}})

    for j in S[i]:

        M_sp[i].update({j:Modulos.pop(0)})

# PARA ESTE EJEMPLO: toda sesión en todo protocolo usa 5 módulos
# Lp: maximo de días que puede esperar un paciente del protocolo p para empezar su tratamiento

lp = {}
for i in P:
      lp.update({i:{}})

# Variable aleatoria que indica numero de pacientes con protocolo p que llegan en la semana

lambdas = [5, 4, 3] 
q = dict(zip(P,np.random.poisson(lambdas)))

# k_ps indica la distancia en dias desde s=s hasta s= 1 del protocolo p

K_ps = {} 

for i in P:

  K_ps.update({i:[k for k in range(1,Largo_P[int(i)-1] + 1)]})

# PARA ESTE EJEMPLO: sesiones consecutivas


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

# Variables del satélite

# Construcción de ωpst

ω = {}

for p in P:

    for s in S[p]:

        for t in T:

            ω[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="ω[%s,%s,%s]"%(p,s,t))

ρ = {}

for p in P:

    ρ[p] = model.addVar(0,vtype=GRB.INTEGER, name="ρ[%s]"%(p))


##########
# MODELO #
##########


w = {}

y = {}

u = {}


#######################
# VARIABLES DE ESTADO #
#######################

# w [p,s,t] 
# Cantidad de protocolos -p- que tienen su sesion -s- en el día -t-

for p in P:

    for s in S[p]:

        for t in T:

            w[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="w[%s,%s,%s]"%(p,s,t))


# r [p]
# Cantidad de pacientes en la semana del protocolo p

r = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="r")


#######################
# VARIABLES DE ACCIÖN #
#######################

# x [p,t] 
# Cantiad de protocolos -p- que inician su tratamiento el dia -t-

x = model.addVars(P,T, lb=0.0, vtype=GRB.INTEGER, name="x")


# y [p,s,t,m] 
# Cantidad de protocolos -p- que comienzan su sesion -s- en modulo -m- del dia -t-

for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                y[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="y")


# z [p]
# Cantidad de protocolos -p- que son derivados a sistema privado

z = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="z")


# u [p,s,t,m] 
# Cantidad de protocolos -p- que terminan su sesion -s- en el modulo -m- del dia -t-

for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                u[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="u")


#################
# FUNCIÓN COSTO #
#################
# En informe (9)

k_as = quicksum(CD[p] * z[p] for p in P) + quicksum(u[p,s,t,m] * (m_index + 1) for p in P for s in S[p] for t in T for m_index, m in enumerate(M))


####################
# FUNCIÓN OBJETIVO #
####################
# En informe (26)

model.setObjective( (1 - γ) * β + quicksum(ω[p,s,t] * W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(ρ[p] * R[p] for p in P) - k_as, GRB.MAXIMIZE)


#################
# RESTRICCIONES #
#################

# RESTRICCIÓN 1
# Respetar cantidad de modulos de atencion
# En informe (1)

R1 = {}

# Para todo día t perteneciente a T
for t_index, t in enumerate(T):

    R1[t] = model.addConstr(quicksum(x[p,T[t_index-K_ps[p][int(s)-1]+1]] * M_sp[p][s]\

     for p in P for s in S[p] if t_index+1 >= K_ps[p][int(s)-1]) + quicksum(w[p,s,t] * M_sp[p][s]\

     for p in P for s in S[p] if t_index+1 >= K_ps[p][int(s)-1]) <= 40, name="Capacidad bloques[%s]" %t)


# RESTRICCIÓN 2
# Definifinición de y
# En informe (2)

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


# RESTRICCIÓN 3
# Conservacion de flujo de pacientes
# Definición de r_p
# En informe (3)

model.addConstrs((r[p] == q[p] for p in P), name="Realizacion de las llegadas")


# Restricción 4 
# Definicion de u, con y
# En informe (4)

R4 = {}

# Para cada protocolo
for p in P:

    # Para cada sesión
    for s in S[p]:

        # Para cada día
        for t in T:

            # Para cada módulo
            for m_index, m in enumerate(M):

                # Condición: termino en mismo día
                if m_index + M_sp[p][s] <= 40:

                    R4[p,s,t,m] = model.addConstr(y[p,s,t,m] == u[p,s,t,M[m_index - M_sp[p][s] - 1]], name="definicion u [%s, %s, %s, %s]"%(p,s,t,m))


# RESTRICCIÓN 5
# Acotar a número de sillas disponibles
# En informe (5)

model.addConstrs(( quicksum(y[p,s,t,m] + quicksum(y[p,s,t,M[m_index]] for m_index in range(max(1, m_index - M_sp[p][s])))\

 for p in P for s in S[p]) <= NS for t in T for m_index, m in enumerate(M) ), name="Capacidad sillas")


# RESTRICCIÓN 6
# Acotar a número de enfermeras
# En informe (6)

model.addConstrs((quicksum(y[p,s,t,m] for p in P for s in S[p]) + quicksum(u[p,s,t,m] for p in P for s in S[p])\

 <= NE for t in T for m in M), name="Capacidad enfermeras")


# RESTRICCIÓN 8
# Realización de llegadas - probabilidades de transición
# En informe (8)

model.addConstrs((r[p] == q[p] for p in P), name="Realizacion de las llegadas")


# RESTRICCIÓN 19
# Definición de ω
# En informe (19)

R7 = {}

# Para cada protocolo
for p in P:

    # Para cada sesión
    for s in S[p]:

        # Para cada día
        for t_index, t in enumerate(T):

            # Condición de avance de sesiones
            if t_index + 1 >= K_ps[p][int(s)-1]:

                R7[p,s,t] = model.addConstr(ω[p,s,t] == w[p,s,t] - γ * (w[p,s,T[t_index]] + x[p,T[t_index]]), name="Definicion ω")


# RESTRICCIÓN 20
# Definición de ρ
# En informe (20)

model.addConstrs((ρ[p] == r[p] for p in P), name="Definicion ρ")


##########
# FALTAN #
##########

# Restricciones que relacionan los ω y los ρ


model.update()

model.optimize()

model.printAttr("X")