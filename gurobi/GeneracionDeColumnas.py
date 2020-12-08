import pandas as pd
import numpy as np
import gurobipy as gu
from parametros import *


contador_de_columnas = 1
C = [k for k in range(1, contador_de_columnas + 1)]

########################
# DEFINICIÓN DE CLASES #
########################

# PROBLEMA MAESTRO #

class MasterProblem:
    def __init__(self, input):

        self.model = gu.Model('MasterProblem')
        #input proveniente del pricing
        #deje solo las que utiliza el maestro
        self.columnas = C
        self.omega = {}
        self.rho = {}
        self.w = {}
        self.r = {}
        self.r_prima = {}
        
        #añadir la nueva columna
        for c in C:

            for p in P:
                    for s in S[p]:
                        for t in T:
                            self.omega[c,p,s,t] = input[c]['Omega'][p,s,t]

            for p in P:
                self.rho[c,p] = input[c]['Rho'][p]
            
            for p in P:
                for s in S[p]:
                    for t in T:
                        self.w[c,p,s,t] = input[c]['w'][p,s,t]
            
            for p in P:
                for s in S[p]:
                    for t in T:
                        self.w_prima[c,p,s,t] = input[c]['w_prima'][p,s,t]
            
            for p in P:
                self.r[c,p] = input[c]['r'][p]
            
            for p in P:
                self.r_prima[c,p] = input[c]['r_prima'][p]
            
            self.k_as[c] = input[c]['k_as']

        #definicion de la esperanza de w
        self.E_w = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.E_w[p,s,t] = quicksum(self.w[c,p,s,t] for c in C) / contador_de_columnas
       
        # esperanza de r
        self.E_r = {}
        for p in P: 
            self.E_r[p] = quicksum(self.r[c,p] for c in C) / contador_de_columnas

    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()

    def generateVariables(self):

        self.pi = {}
        self.pi = model.addVars(C, lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name="Columna ingresada")

    def generateConstraints(self):

        # Restricción 1
        self.R1 = {}
        self.R1= self.model.addConstr((1 - γ) * sum(self.pi[c] for c in C) == 1, name= "beta")

        # Restricción 2
        self.R2 = {}
        for p in P: 
            for s in S[p]:
                for t in T:     
                    self.R1 = self.model.addConstr(sum((self.omega[c,p,s,t] * self.pi[c]) for c in C) >= self.E_w[p,s,t], name= "W")

        # Restricción 3
        self.R3 = {}
        for p in P: 
            self.R3 = self.model.addConstr(sum((self.rho[c,p] * self.pi[c]) for c in C) >= self.E_r[p], name = "R")

    def generateObjective(self):
        self.model.setObjective(sum((self.k_c[c] * self.pi[c]) for c in C), GRB.MINIMIZE)

    def generateDuals (self):
        beta_dado = {}
        beta_dado = self.R1.Pi

        W_dados = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    W_dados[p,s,t] = self.R2.Pi

        R_dados = {}
        for p in P:
            R_dados[p] = self.R3.Pi

        duales = {"Beta": beta_dado, "W" : W_dados, "R": "R_dados"}

        return duales

    def solveModel(self):
        self.model.optimize()


# PRICING #

class SubProblem:
    def __init__(self, input):
        self.model = gu.Model('Pricing')
        self.W = input["Omega"] # obtenido a partir del dual del maestro
        self.Rho = input["Rho"] # obtenido a partir del dual del maestro
        self.Beta = input["Beta"] # obtenido a partir del dual del maestro
        self.llegadas = input['Llegadas']

    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()

    def generateVariables(self):
        # VARIABLES DE ESTADO #
        self.w = {}
        # Cantidad de protocolos -p- que tienen su sesion -s- en el día -t-
        for p in P:
            for s in S[p]:
                for t in T:
                    self.w[p,s,t] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="w[%s,%s,%s]"%(p,s,t))

        self.w_prima= {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.w_prima[p,s,t] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="w_prima[%s,%s,%s]"%(p,s,t))

        self.r= {}
        # Cantidad de pacientes en la semana del protocolo p
        for p in P:
            self.r[p] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="r[%s]"%(p))

        self.r_prima= {}
        for p in P:
            self.r_prima[p] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="r_prima[%s]"%(p))

        # VARIABLES DE ACCIÓN #
        self.x = {}
        #Cantiad de protocolos -p- que inician su tratamiento el dia -t-
        for p in P:
            for t in T:
                self.x[p,t] = self.model.addVar(lb=0,  vtype=GRB.INTEGER,  name="x[%s,%s]"%(p,t))

        self.y = {}
        # Cantidad de protocolos -p- que comienzan su sesion -s- en modulo -m- del dia -t-
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in M:
                        self.y[p,s,t,m] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="y[%s,%s,%s,%s]"%(p,s,t,m))

        self.z =  {}
        # Cantidad de protocolos -p- que son derivados a sistema privado
        for p in P:
            self.z[p] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="z[%s]"%(p))

        self.u = {}
        # Cantidad de protocolos -p- que terminan su sesion -s- en el modulo -m- del dia -t-
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in M:
                        self.u[p,s,t,m] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="u[%s,%s,%s,%s]"%(p,s,t,m))

        # VARIABLES ADICIONALES #
        self.omega = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.omega[p,s,t] = self.model.addVar(lb=0,  vtype=GRB.CONTINUOUS, name="omega[%s,%s,%s]"%(p,s,t))

        self.rho = {}
        for p in P:
            self.rho[p] = self.model.addVar(lb=0,   vtype=GRB.CONTINUOUS, name="rho[%s]"%(p))
        

    def generateConstraints(self):
        
        self.R1 = {}
        # Respetar cantidad de modulos de atencion
        for t in T:
                self.R1[t] = self.model.addConstr(quicksum(self.x[p,T[t-K_ps[p][s]-1]] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])\
                    + quicksum(self.w[p,s,t] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])  <= BR + BE, name="Capacidad bloques[%s]" %t)
        
        self.R2 = {}
        # Definifinición de y
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t >= K_ps[p][s]:

                        self.R2[p,s,t] = self.model.addConstr(quicksum(self.y[p,s,t,m] for m in range(1, BR+1)) == self.x[p,T[t - K_ps[p][s] - 1]] + self.w[p,s,t]\

                        , name="Definicion y [%s, %s, %s]"%(p,s,t))
                    else: 
                        self.R2[p,s,t] = self.model.addConstr( self.w[p,s,t]==0)

        self.R3 = {}
        # Conservacion de flujo de pacientes
        for p in P:
            self.R3[p] = self.model.addConstr( (self.r[p] == self.z[p] + quicksum(self.x[p, d]   for d in range(1, (Lp[p]+1))) ), 
        name="Conservacion de flujo")

        self.R4 = {}
        # Definicion de u, con y
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in range(1, BR+1):
                        # Condición: termino en mismo día
                        if m + M_sp[p][s] - 2 <= BR + BE:

                            self.R4[p,s,t,m] = self.model.addConstr(self.y[p,s,t,m] == self.u[p,s,t,M[m + M_sp[p][s] - 2]],
                                name="Definicion u [%s, %s, %s, %s]"%(p,s,t,m))

        self.R5 = {}
        # Acotar a número de sillas disponibles
        for t in T:
            for m in range(1, BR+1):
                self.R5[m,t] =   self.model.addConstr(( quicksum(self.y[p,s,t,m] + 

                            quicksum(self.y[p,s,t, m - M_sp[p][s]] for m in M if  m - M_sp[p][s] >= 1)\

                            for p in P for s in S[p]) <= NS), name="Capacidad sillas")
       
        self.R6 = {}
        # Acotar a número de enfermeras
        for t in T:

            for m in M:

                self.R6[m,t] = self.model.addConstr((quicksum(self.y[p,s,t,m] + self.u[p,s,t,m] for p in P for s in S[p]) <= NE), 
                                            name="Capacidad enfermeras")
        
        self.R7 = {}
        #"Definición w"
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t + 7 >= K_ps[p][s]:
                        if t+7 < len(T):

                            self.R7[p,s,t] = self.model.addConstr(self.w_prima[p,s,t] == 
                                self.w[p,s,T[t-K_ps[p][s]+7]] + self.x[p,T[t+7]],
                                        name="Definición w'")

        self.R8 = {}
        # Realización de llegadas - probabilidades de transición
        for p in P:
            self.R8[p] = self.model.addConstr((self.r_prima[p] == q[p]), name="Realizacion de las llegadas")
        
        self.R19 = {}
        # Definición de omega
        for p in P:
            for s in S[p]:
                for t in T:
                    if t+7 <len(T): 
                        # Condición de avance de sesiones
                        if t + 1 >= K_ps[p][s]:

                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t] == self.w[p,s,t] - γ * (self.w[p,s,T[t+7]] 
                                + self.x[p,T[t+7]]), name="Definicion omega")
                        else: 
                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)
                    else: 

                        self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)       
        
        self.R20 = {}
        # Definición de rho
        for p in P:

            self.R20[p] = self.model.addConstr((self.rho[p] == self.r[p] - (γ *self.r_prima[p])), name="Definicion rho")

        
    def generateObjective(self):
        k_as = quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR + l] * l  for p in P for s in S[p] for t in T for l in range(1, BE + 1))*(CE-CR)
        self.f_obj_pr = (1 - γ) * self.beta + quicksum(self.omega[p,s,t] * self.W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(self.rho[p] * self.R[p] for p in P)
        self.model.setObjective(self.f_obj_pr, GRB.MAXIMIZE)
    
    #def getNewPattern(self):
        #return self.model.gettAtr('X', self.model.getVars())

    def entregarInformacion(self):
        # Rho
        info_rho = {}
        for p in P:
            info_rho[p] = self.rho[p].x
        # Omega
        info_omega = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    info_omega[p,s,t] = self.omega[p,s,t].x
        # w
        info_w = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    info_w[p,s,t] = self.w[p,s,t].x
        # w prima
        info_w_prima = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    info_w_prima[p,s,t] = self.w_prima[p,s,t].x
        # r
        info_r = {}
        for p in P:
            info_r[p] = self.r[p]
        # r_prima
        info_r_prima = {}
        for p in P:
            info_r_prima[p] = self.r_prima[p]
        # z
        info_z =  {}
        for p in P:
            info_z[p] = self.z[p].x
        # u
        info_u = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in M:
                        info_u[p,s,t,m] = self.u[p,s,t,m].x
        columna_actual = {'Rho': info_rho, 'Omega': info_omega, 'w': info_w, 'w_prima': info_w_prima, 'r': info_r, 'r_prima': info_r_prima, 'z': info_z, 'u': info_u, 'k_as': self.k_as}
        informacion[contador_de_columnas] = columna_actual 


    def solveModel(self):
        self.model.optimize()

##########
# FASE 1 #
##########

class FaseUnoMasterProblem:
    def __init__(self, input):
        self.model = gu.Model('MasterProblem Fase Uno')
        self.columnas = C

        self.omega = {}
        self.rho = {}
        self.w = {}
        self.w_prima = {}
        self.r = {}
        self.r_prima = {}
        self.z = {}
        self.u = {}
        self.k_as = {}
        
        for c in C:

            for p in P:
                    for s in S[p]:
                        for t in T:
                            self.omega[c,p,s,t] = input[c]['Omega'][p,s,t]

            for p in P:
                self.rho[c,p] = input[c]['Rho'][p]
            
            for p in P:
                for s in S[p]:
                    for t in T:
                        self.w[c,p,s,t] = input[c]['w'][p,s,t]
            
            for p in P:
                for s in S[p]:
                    for t in T:
                        self.w_prima[c,p,s,t] = input[c]['w_prima'][p,s,t]
            
            for p in P:
                self.r[c,p] = input[c]['r'][p]
            
            for p in P:
                self.r_prima[c,p] = input[c]['r_prima'][p]
            
            for p in P:
                self.z[c,p] = input[c]['z'][p]
            
            for p in P:
                for s in S[p]:
                    for t in T:
                        for m in M:
                            self.u[c,p,s,t,m] = input[c]['u'][p,s,t,m]
            
            self.k_as[c] = input[c]['k_as']


    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()

    def generateVariables(self):
        # VARIABLES #
        self.pi = {}
        self.pi = self.model.addVars(C, lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name="Columna ingresada")

        # VARIABLES ARTIFICIALES #
        self.a_beta = {}
        for c in C:
            self.a_beta[c] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="a_beta[%s]"%(c))

        self.a_omega = {}
        for c in C:
            self.a_omega[c] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="a_omega[%s]"%(c))

        self.a_rho = {}
        for c in C:
            self.a_rho[c] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="a_rho[%s]"%(c))

        # ESPERANZAS #
        # w
        self.E_w = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.E_w[p,s,t] = quicksum(self.w[c,p,s,t] for c in C) / contador_de_columnas
        # r
        self.E_r = {}
        for p in P: 
            self.E_r[p] = quicksum(self.r[c,p] for c in C) / contador_de_columnas


    def generateConstraints(self):
        # Restricción 1
        self.model.addConstr((1 - γ) * quicksum(self.pi[c] + self.a_beta[c] for c in C) == 1, name= "Beta")

        # Restricción 2
        for p in P: 
            for s in S[p]:
                for t in T:     
                    self.model.addConstr(quicksum((self.omega[c,p,s,t] * self.pi[c]) + self.a_omega[c] for c in C) >= self.E_w[p,s,t], name= "Omega")

        # Restricción 3
        for p in P: 
            self.model.addConstr(quicksum((self.rho[c,p] * self.pi[c]) + self.a_rho[c] for c in C) >= self.E_r[p], name = "Rho")

    def generateObjective(self):
        self.model.setObjective(quicksum(self.a_beta[c] + self.a_omega[c] + self.a_rho[c] for c in C), GRB.MINIMIZE)

    def solveModel(self):
        self.model.optimize()


class FaseUnoPricing:
    def __init__(self, input):
        self.model = gu.Model('FaseUno Pricing')
        self.Omega = input["Omega"] # obtenido a partir del dual del maestro
        self.Rho = input["Rho"] # obtenido a partir del dual del maestro
        self.Beta = input["Beta"] # obtenido a partir del dual del maestro
        self.llegadas = input['Llegadas']

    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()

    def generateVariables(self):
        # VARIABLES DE ESTADO #
        self.w = {}
        # Cantidad de protocolos -p- que tienen su sesion -s- en el día -t-
        for p in P:
            for s in S[p]:
                for t in T:
                    self.w[p,s,t] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="w[%s,%s,%s]"%(p,s,t))

        self.w_prima= {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.w_prima[p,s,t] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="w_prima[%s,%s,%s]"%(p,s,t))

        self.r = {}
        # Cantidad de pacientes en la semana del protocolo p
        for p in P:
            #self.r[p] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="r[%s]"%(p))
            self.r[p] = self.llegadas[p]

        self.r_prima = {}
        for p in P:
            #self.r_prima[p] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="r_prima[%s]"%(p))
            self.r_prima[p] = self.llegadas[p]

        # VARIABLES DE ACCIÓN #
        self.x = {}
        #Cantiad de protocolos -p- que inician su tratamiento el dia -t-
        for p in P:
            for t in T:
                self.x[p,t] = self.model.addVar(lb=0,  vtype=GRB.INTEGER,  name="x[%s,%s]"%(p,t))

        self.y = {}
        # Cantidad de protocolos -p- que comienzan su sesion -s- en modulo -m- del dia -t-
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in M:
                        self.y[p,s,t,m] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="y[%s,%s,%s,%s]"%(p,s,t,m))

        self.z =  {}
        # Cantidad de protocolos -p- que son derivados a sistema privado
        for p in P:
            self.z[p] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="z[%s]"%(p))

        self.u = {}
        # Cantidad de protocolos -p- que terminan su sesion -s- en el modulo -m- del dia -t-
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in M:
                        self.u[p,s,t,m] = self.model.addVar(lb=0, vtype=GRB.INTEGER, name="u[%s,%s,%s,%s]"%(p,s,t,m))

        # VARIABLES ADICIONALES #
        self.omega = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.omega[p,s,t] = self.model.addVar(lb=0,  vtype=GRB.CONTINUOUS, name="omega[%s,%s,%s]"%(p,s,t))

        self.rho = {}
        for p in P:
            self.rho[p] = self.model.addVar(lb=0,   vtype=GRB.CONTINUOUS, name="rho[%s]"%(p))
        

    def generateConstraints(self):
        
        self.R1 = {}
        # Respetar cantidad de modulos de atencion
        for t in T:
                self.R1[t] = self.model.addConstr(quicksum(self.x[p,T[t-K_ps[p][s]-1]] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])\
                    + quicksum(self.w[p,s,t] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])  <= BR + BE, name="Capacidad bloques[%s]" %t)
        
        self.R2 = {}
        # Definifinición de y
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t >= K_ps[p][s]:

                        self.R2[p,s,t] = self.model.addConstr(quicksum(self.y[p,s,t,m] for m in range(1, BR+1)) == self.x[p,T[t - K_ps[p][s] - 1]] + self.w[p,s,t]\

                        , name="Definicion y [%s, %s, %s]"%(p,s,t))
                    else: 
                        self.R2[p,s,t] = self.model.addConstr( self.w[p,s,t]==0)

        self.R3 = {}
        # Conservacion de flujo de pacientes
        for p in P:
            self.R3[p] = self.model.addConstr( (self.r[p] == self.z[p] + quicksum(self.x[p, d]   for d in range(1, (Lp[p]+1))) ), 
        name="Conservacion de flujo")

        self.R4 = {}
        # Definicion de u, con y
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in range(1, BR+1):
                        # Condición: termino en mismo día
                        if m + M_sp[p][s] - 2 <= BR + BE:

                            self.R4[p,s,t,m] = self.model.addConstr(self.y[p,s,t,m] == self.u[p,s,t,M[m + M_sp[p][s] - 2]],
                                name="Definicion u [%s, %s, %s, %s]"%(p,s,t,m))

        self.R5 = {}
        # Acotar a número de sillas disponibles
        for t in T:
            for m in range(1, BR+1):
                self.R5[m,t] =   self.model.addConstr(( quicksum(self.y[p,s,t,m] + 

                            quicksum(self.y[p,s,t, m - M_sp[p][s]] for m in M if  m - M_sp[p][s] >= 1)\

                            for p in P for s in S[p]) <= NS), name="Capacidad sillas")
       
        self.R6 = {}
        # Acotar a número de enfermeras
        for t in T:

            for m in M:

                self.R6[m,t] = self.model.addConstr((quicksum(self.y[p,s,t,m] + self.u[p,s,t,m] for p in P for s in S[p]) <= NE), 
                                            name="Capacidad enfermeras")
        
        self.R7 = {}
        #"Definición w"
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t + 7 >= K_ps[p][s]:
                        if t+7 < len(T):

                            self.R7[p,s,t] = self.model.addConstr(self.w_prima[p,s,t] == 
                                self.w[p,s,T[t-K_ps[p][s]+7]] + self.x[p,T[t+7]],
                                        name="Definición w'")

        self.R8 = {}
        # Realización de llegadas - probabilidades de transición
        for p in P:
            self.R8[p] = self.model.addConstr((self.r_prima[p] == q[p]), name="Realizacion de las llegadas")
        
        self.R19 = {}
        # Definición de omega
        for p in P:
            for s in S[p]:
                for t in T:
                    if t+7 <len(T): 
                        # Condición de avance de sesiones
                        if t + 1 >= K_ps[p][s]:

                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t] == self.w[p,s,t] - γ * (self.w[p,s,T[t+7]] 
                                + self.x[p,T[t+7]]), name="Definicion omega")
                        else: 
                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)
                    else: 

                        self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)       
        
        self.R20 = {}
        # Definición de rho
        for p in P:

            self.R20[p] = self.model.addConstr((self.rho[p] == self.r[p] - (γ *self.r_prima[p])), name="Definicion rho")

        
    def generateObjective(self):
        # Funcion costos para k pricing
        self.k_as = quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR + l] * l  for p in P for s in S[p] for t in T for l in range(1, BE + 1))*(CE-CR)
        self.f_obj_pr = (1 - γ) * self.Beta + quicksum(self.omega[p,s,t] * self.w[p,s,t] for p in P for s in S[p] for t in T) + quicksum(self.rho[p] * self.r[p] for p in P)
        self.model.setObjective(self.f_obj_pr, GRB.MAXIMIZE)
    
    #def getNewPattern(self):
        #return self.model.gettAtr('X', self.model.getVars())

    def solveModel(self):
        self.model.params.NonConvex = 2
        self.model.optimize()
        #self.model.printAttr("X")
        #self.model.gettAtr('X', self.model.getVars())

    def entregarInformacion(self):
        # Rho
        info_rho = {}
        for p in P:
            info_rho[p] = self.rho[p].x
        # Omega
        info_omega = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    info_omega[p,s,t] = self.omega[p,s,t].x
        # w
        info_w = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    info_w[p,s,t] = self.w[p,s,t].x
        # w prima
        info_w_prima = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    info_w_prima[p,s,t] = self.w_prima[p,s,t].x
        # r
        info_r = {}
        for p in P:
            info_r[p] = self.r[p]
        # r_prima
        info_r_prima = {}
        for p in P:
            info_r_prima[p] = self.r_prima[p]
        # z
        info_z =  {}
        for p in P:
            info_z[p] = self.z[p].x
        # u
        info_u = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in M:
                        info_u[p,s,t,m] = self.u[p,s,t,m].x
        # k_as
        #info_k_as = k_as

        columna_actual = {'Rho': info_rho, 'Omega': info_omega, 'w': info_w, 'w_prima': info_w_prima, 'r': info_r, 'r_prima': info_r_prima, 'z': info_z, 'u': info_u, 'k_as': self.k_as}
        informacion[contador_de_columnas] = columna_actual 



##########################
# GENERACIÓN DE COLUMNAS #
##########################

# Definamos el siguiente caso:
# Llegada Protocolo 1 - 5 pacientes - Poisson lamda=5
# Llegada Protocolo 2 - 5 pacientes - Poisson lamda=5
# Llegada Protocolo 3 - 5 pacientes - Poisson lamda=5

informacion = {}

# Contruimos la primera columna
diccionario = {'Llegadas': q, 'Omega': 1, 'Rho': 1, 'Beta': 1}
Fase1Pricing = FaseUnoPricing(diccionario)
Fase1Pricing.buildModel()
Fase1Pricing.solveModel()
Fase1Pricing.entregarInformacion()

# Inicializamos el Maestro con  la columna generada
Fase1Maestro = FaseUnoMasterProblem(informacion)
Fase1Maestro.buildModel()
Fase1Maestro.solveModel()

contador_de_columnas += 1
C = [k for k in range(1, contador_de_columnas + 1)]

while (Fase1Maestro.model.ObjVal != 0 and contador_de_columnas < 1000):
    print('ITERANDO')
    break
print('LISTOCO')

###############
# ITERACIONES #
###############

modelImprovable = True
while (modelImprovable and contador_de_columnas < 1000):
  
    last_obj_master = actual_obj_master
    
    #los aux son para agrega nuevas columnas
    aux_omega = {}
    aux_rho = {}
    aux_w = {}
    aux_y = {}
    aux_r= {}
    aux_x= {}
    #Optimizamos el master con valores de entrada (fase I)
      
    master_solution = MasterProblem({"columnas": columnas, "omega_dado": omega_dado, "rho_dado": rho_dado, "w_dados": w_dados, "r_dados": r_dados, "r_prima_dados": r_prima_dados})
    master_solution.buildModel()
    master_solution.model.optimize()

    #Actualizamos resultado
    actual_obj_master = master_solution.model.objVal
    #print("RESULTADO MASTER:", actual_obj_master)
    
    master_solution.model.printAttr('X')
    print("RESULTADOS PI")
    print(master_solution.model.getVars())
    rest = master_solution.model.getConstrs()
    beta_dado, W_dados, R_dados = {}, {}, {}

    ##generando variables duales y asignandoles los nombres correspondientes
    for r in rest:
        if r.constrName == "beta":
            beta_dado = r.Pi
        elif r.constrName[0] == "W":
           W_dados[r.constrName] = r.Pi
        elif r.constrName[0] == "R":
            R_dados[r.constrName] = r.Pi  

    # Una vez resuelto el Master, usamos estos datos como input para el pricing, para resolver este
     
    pricing_solution = PricingProblem({"beta_dado": beta_dado, "W_dados": W_dados, "R_dados": R_dados})

    pricing_solution.buildModel()
    pricing_solution.model.optimize()
    lista_variables_pricing = pricing_solution.model.getVars()

    actual_pricing_value = pricing_solution.model.objVal
    pricing_solution.model.printAttr('X')

    # REVISAR LO DE LOS INDICES
    for v in lista_variables_pricing: 
        name = v.varName
        if name[0] == "w": 
            w_aux[name] = v.x # Key del dict será "chi_pr[indicex,indicey]"
        elif name[0] == "omega": 
            omega_aux[name] = v.x
        elif name[0] == "rho":
            rho_aux = v.x
        elif name[0] == "y": 
            y_aux = v.x
        elif name[0] == "r": 
            r_aux = v.x    
        elif name[0] == "x": 
            x_aux = v.x 
    
    #if actual_pricing_value > 0:
    print("Veamos pricing_valur:" + str(actual_pricing_value))
    if actual_pricing_value < 0:
        columnas.append(column_to_enter)
        #print(columnas)
        omega.append(omega_aux)
        rho.append(rho_aux)
        w.append(w_aux)
        x.append(x_aux)
        r.append(r_aux)
        y.append(y_aux)
    column_to_enter += 1
    #print("Número de iteraciones" + str(column_to_enter))
    if column_to_enter == 30:
        break

# imprimo valores resultantes del master
#print("Llega hasta iteración: ", column_to_enter - 1)


#OTRA FORMA DE HACERLO
modelImprovable = True

while modelImprovable:
    # Solved relaxed Master
    master.solveRelaxedModel()
    duals = master.getDuals()
    #duals de nuestro problema serian W, R Y beta
    # luego se construye el pricing con los valores entregados por el master
    subproblem = SubProblem(inputDF, rollWidth, duals)
    subproblem.buildModel()
    subproblem.solveModel(120, 0.05)
    # iterar hasta que el resultado del pricing se vuelva negativo
    modelImprovable = (subproblem.getObjectiveValue()) > 0
    # Add new generated pattern to master and iterate

