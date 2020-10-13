import numpy as np

from openpyxl import load_workbook

from gurobipy import *

from parametros import *


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

T = [str(k) for k in range(1,7)] 
# 6 dias - 1, 2, ..., 6

# PROTOCOLOS - usaba string en los k

# SESIONES - usaba string en los k

# MÓDULOS - usaba string en k


##############
# PARÁMETROS #
##############

# Variable GAMMA

# Número de enfermeras

NE = 5 

# Número de sillas

NS = 20 

# Costos por protocolo

# Costo bloque regular

# Costo bloque extra

# Duraciones de cada sesion

# Bloques regulares efectivos
# Jornada de 8 horas

# Bloques extra efectivos
# 1,5 horas

# Lp: maximo de días que puede esperar un paciente del protocolo p para empezar su tratamiento

Lp = {}
for i in P:
      Lp.update({i: [k for k in range(5)] })


# Variable aleatoria que indica numero de pacientes con protocolo p que llegan en la semana

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


# Construcción de ρ p

ρ = {}

for p in P:

    ρ[p] = model.addVar(0,vtype=GRB.INTEGER, name="ρ[%s]"%(p))


##########
# MODELO #
##########


w = {}

w_prima = {}

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


for p in P:

    for s in S[p]:

        for t in T:

            w_prima[p,s,t] = model.addVar(0,vtype=GRB.INTEGER, name="w_prima[%s,%s,%s]"%(p,s,t))

# w[p,s,t] = model.addVar(P, S, T, lb=0.0, vtype=GRB.INTEGER, name="w[%s,%s,%s]"%(p,s,t))


# r [p]
# Cantidad de pacientes en la semana del protocolo p

r = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="r[%s]"%(p))


# r_prima [p]

r_prima = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="r_prima[%s]"%(p))


#######################
# VARIABLES DE ACCIÖN #
#######################

# x [p,t] 
# Cantiad de protocolos -p- que inician su tratamiento el dia -t-

x = model.addVars(P,T, lb=0.0, vtype=GRB.INTEGER, name="x[%s,%s]"%(p,t))


# y [p,s,t,m] 
# Cantidad de protocolos -p- que comienzan su sesion -s- en modulo -m- del dia -t-

for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                y[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="y[%s,%s,%s,%s]"%(p,s,t,m))


# z [p]
# Cantidad de protocolos -p- que son derivados a sistema privado

z = model.addVars(P, lb=0.0, vtype=GRB.INTEGER, name="z[%s]"%(p))

for p in P:

    z[p] = 0


# u [p,s,t,m] 
# Cantidad de protocolos -p- que terminan su sesion -s- en el modulo -m- del dia -t-

for p in P:

    for s in S[p]:

        for t in T:

            for m in M:

                u[p,s,t,m] = model.addVar(0,vtype=GRB.INTEGER, name="u[%s,%s,%s,%s]"%(p,s,t,m))


#################
# FUNCIÓN COSTO #
#################
# En informe (9)

# Faltan los costos

k_as = quicksum(CD[p] * z[p] for p in P) + quicksum(u[p,s,t,m] * (m_index + 1) for p in P for s in S[p] for t in T for m_index, m in enumerate(M))*(CE-CR)


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
# t_index + 1 = t

for t in T:

    R1[t] = model.addConstr(quicksum(x[p,T[(int(t)-1)-K_ps[p][int(s)-1]+1]] * M_sp[p][s]\

     for p in P for s in S[p] if int(t) >= K_ps[p][int(s)-1]) + quicksum(w[p,s,t] * M_sp[p][s]\

     for p in P for s in S[p] if int(t) >= K_ps[p][int(s)-1]) <= 40, name="Capacidad bloques[%s]" %t)


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

R3 = {}

# Para todo protocolo p
for p in P:

    R3[p] = model.addConstr( (r[p] == z[p] + quicksum(x[p, str(d+1)] for d in Lp[p]) ), 
        name="Conservacion de flujo")

# Funciona sólo con el tiempo en string, no entiendo


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
                if m_index + M_sp[p][s] - 1 <= BR + BE:

                    R4[p,s,t,m] = model.addConstr(y[p,s,t,m] == u[p,s,t,M[m_index - M_sp[p][s] - 1]],
                        name="Definicion u [%s, %s, %s, %s]"%(p,s,t,m))


# RESTRICCIÓN 5
# Acotar a número de sillas disponibles
# En informe (5)

R5 = {}

for t in T:

    for m_index, m in enumerate(M):

        R5[m,t] =   model.addConstr(( quicksum(y[p,s,t,m] + 

                    quicksum(y[p,s,t,M[m_index]] for m_index in range(max(1, m_index - M_sp[p][s])))\

                    for p in P for s in S[p]) <= NS), name="Capacidad sillas")


# RESTRICCIÓN 6
# Acotar a número de enfermeras
# En informe (6)

R6 = {}

for t in T:

    for m in M:

        R6[m,t] = model.addConstr((quicksum(y[p,s,t,m] for p in P for s in S[p]) + 
                                    quicksum(u[p,s,t,m] for p in P for s in S[p]) <= NE), 
                                    name="Capacidad enfermeras")


# RESTRICCIÓN 7
# En informe (7)

R7 = {}

for p in P:

    for s in S[p]:

        for t_index, t in enumerate(T):

            if t_index + 7 <= len(T):

                # Condicion para evitar exponente igual a 0
                if t_index + 7 >= K_ps[p][int(s)-1]:

                    R7[p,s,t] = model.addConstr(w_prima[p,s,t] == 
                        w[p,s,T[t_index-K_ps[p][int(s)-1]+7]] + x[p,T[t_index+7]],
                                 name="Definición w'")


# RESTRICCIÓN 8
# Realización de llegadas - probabilidades de transición
# En informe (8)

# ¿Qué es r prima?

R8 = {}

for p in P:

    R8[p] = model.addConstr((r_prima[p] == q[p]), name="Realizacion de las llegadas")


# RESTRICCIÓN 19
# Definición de ω
# En informe (19)

R19 = {}

# Para cada protocolo
for p in P:

    # Para cada sesión
    for s in S[p]:

        # Para cada día
        for t_index, t in enumerate(T):

            if t_index + 7 <= len(T):

                # Condición de avance de sesiones
                if t_index + 1 >= K_ps[p][int(s)-1]:

                    R19[p,s,t] = model.addConstr(ω[p,s,t] == w[p,s,t] - γ * (w[p,s,T[t_index+7]] 
                        + x[p,T[t_index+7]]), name="Definicion ω")


# RESTRICCIÓN 20
# Definición de ρ
# En informe (20)

R20 = {}

for p in P:

    R20[p] = model.addConstr((ρ[p] == r[p] - (γ * r_prima[p])), name="Definicion ρ")


model.update()

model.optimize()

model.computeIIS()

model.write("output_pricing.ilp")

model.printAttr("X")