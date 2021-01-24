import pandas as pd
import numpy as np
import gurobipy as gu
from parametros import *

########################
# DEFINICIÓN DE CLASES #
########################

# PROBLEMA MAESTRO #

class MasterProblem:
    def __init__(self, input):

        self.model = gu.Model('MasterProblem')
        #input proveniente del pricing
        self.columnas = C
        self.omega = {}
        self.rho = {}
        self.w = {}
        self.r = {}
        self.r_prima = {}
        self.w_prima = {}
        self.k_as= {}
        
        #añadir la nueva columna
        for c in self.columnas:

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
                for s in S[p]:
                    for t in T:
                        self.w_prima[c,p,s,t] = input[c]['w_prima'][p,s,t]           
            
            self.k_as[c] = input[c]['k_as']

        # Definicion de la esperanza de w
        # Por ahora = 0 para que corra
        self.E_w = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.E_w[p,s,t] = 0
       
        # Esperanza de r
        self.E_r = {}
        for p in P: 
            self.E_r[p] = q[p]

    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()

    def generateVariables(self):

        self.pi = {}
        for c in self.columnas: 
            self.pi[c] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="pi[%s]"%(c))

    def generateConstraints(self):

        # Restricción 1
        self.R1 = {}
        self.R1= self.model.addConstr((1 - γ) * sum(self.pi[c] for c in C) == 1, name= "beta")

        # Restricción 2
        self.R2 = {}
        for p in P: 
            for s in S[p]:
                for t in T:     
                    self.R2 = self.model.addConstr(sum((self.omega[c,p,s,t] * self.pi[c]) for c in C) >= self.E_w[p,s,t], name= "W")

        # Restricción 3
        self.R3 = {}
        for p in P: 
            self.R3 = self.model.addConstr(sum((self.rho[c,p] * self.pi[c]) for c in C) >= self.E_r[p], name = "R")

    def generateObjective(self):
        self.model.setObjective(quicksum((self.k_as[c] * self.pi[c]) for c in self.columnas), GRB.MINIMIZE)

    def entregarDuales(self): 
        #entrega las duales de cada una de las restricciones
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

        self.duales = {'Beta': beta_dado, 'W' : W_dados, 'R': R_dados}
        return(self.duales)

    def solveModel(self):
        self.model.optimize()


# PRICING #

class SubProblem:
    def __init__(self, input):
        self.model = gu.Model('Pricing')
        self.W = input['W'] # obtenido a partir del dual del maestro
        self.R = input['R'] # obtenido a partir del dual del maestro
        self.Beta = input['Beta'] # obtenido a partir del dual del maestro

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
        
        self.k_as = {}
        self.k_as = self.model.addVar(lb = 0, vtype=GRB.CONTINUOUS, name="k")

    def generateConstraints(self):
        
        self.R1 = {}
        # Respetar cantidad de modulos de atencion
        for t in T:
                self.R1[t] = self.model.addConstr(quicksum(self.x[p,T[t-K_ps[p][s]-1]] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])\
                    + quicksum(self.w[p,s,t] * M_sp[p][s] for p in P for s in S[p])  <= BR + BE, name="Capacidad bloques[%s]" %t)
        
        
        self.R2 = {}
        # Definifinición de y
        for p in P:
            for s in S[p]:
                for t in range(1, 7):
                #for t in T:
                # Condicion para evitar exponente igual a 0
                    if t >= K_ps[p][s]:
                        self.R2[p,s,t] = self.model.addConstr(quicksum(self.y[p,s,t,m] for m in range(1, BR+1)) == self.x[p,T[t - K_ps[p][s] - 1]] + self.w[p,s,t]\
                            , name="Definicion y [%s, %s, %s]"%(p,s,t))
                    #else: 
                        #self.R2[p,s,t] = self.model.addConstr( self.w[p,s,t]==0)

        self.R3 = {}
        # Conservacion de flujo de pacientes
        for p in P:
            self.R3[p] = self.model.addConstr( (self.r[p] == self.z[p] + quicksum(self.x[p, d]   for d in range(1, (Lp[p]+1))) ), 
        name="Conservacion de flujo")

        self.R4 = {}
        # Definicion de u, con y
        for p in P:
            for s in S[p]:
                for t in range(1, 7):
                #for t in T:
                    for m in range(1, BR+1):
                        # Condición: termino en mismo día
                        if m + M_sp[p][s] - 2  <= BR + BE:

                            self.R4[p,s,t,m] = self.model.addConstr(self.y[p,s,t,m] == self.u[p,s,t,M[m + M_sp[p][s] - 2]],
                                name="Definicion u [%s, %s, %s, %s]"%(p,s,t,m))

        self.R5 = {}
        # Acotar a número de sillas disponibles
        #for t in T:
        for t in range(1, 7):
            for m in range(1, BR+1):
                self.R5[m,t] =   self.model.addConstr(( quicksum(self.y[p,s,t,m] + 

                            quicksum(self.y[p,s,t, m - M_sp[p][s]] for m in M if  m - M_sp[p][s] >= 1)\

                            for p in P for s in S[p]) <= NS), name="Capacidad sillas")
       
        self.R6 = {}
        # Acotar a número de enfermeras
        #for t in T:
        for t in range(1, 7):
            for m in M:

                self.R6[m,t] = self.model.addConstr((quicksum(self.y[p,s,t,m] + self.u[p,s,t,m] for p in P for s in S[p]) <= NE), 
                                            name="Capacidad enfermeras")
        
        self.R7 = {}
        #"Definición w"
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t + 7 >= K_ps[p][s] +1 :
                        if t+7 < len(T):

                            self.R7[p,s,t] = self.model.addConstr(self.w_prima[p,s,t] == 
                                self.w[p,s,t+7] + self.x[p,t-K_ps[p][s]+7],
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

                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t] == self.w[p,s,t] - γ * (self.w_prima[p,s,t]), name="Definicion omega")
                        #else: 
                            #self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)
                    #else: 

                        #elf.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)       
        
        self.R20 = {}
        # Definición de rho
        for p in P:

            self.R20[p] = self.model.addConstr((self.rho[p] == self.r[p] - (γ *self.r_prima[p])), name="Definicion rho")
        


        #DEF
        self.Rx = {}
        self.Rx = self.model.addConstr(self.k_as == quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR + l] * l  for p in P for s in S[p] for t in range(1, 7) for l in range(1, BE + 1))*(CE-CR))
        
    def generateObjective(self):
       
        self.f_obj_pr = (1 - γ) * self.Beta + quicksum(self.omega[p,s,t] * self.W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(self.rho[p] * self.R[p] for p in P)- self.k_as
        self.model.setObjective(self.f_obj_pr, GRB.MAXIMIZE)
    

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
            info_r[p] = self.r[p].x
        # r_prima
        info_r_prima = {}
        for p in P:
            info_r_prima[p] = self.r_prima[p].x
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

        info_k_as = {}
        info_k_as= self.k_as.x

        columna_actual = {'Rho': info_rho, 'Omega': info_omega, 'w': info_w, 'w_prima': info_w_prima, 'r': info_r, 'r_prima': info_r_prima, 'z': info_z, 'u': info_u, 'k_as': info_k_as}
        for c in C:
            informacion[c] = columna_actual 



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
            
            
            self.k_as[c] = input[c]['k_as']


    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()

    def generateVariables(self):
        # VARIABLES #
        self.pi = {}
        for c in C: 
            self.pi[c] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="pi[%s]"%(c))
        
        # VARIABLES ARTIFICIALES #
        #SON POR CADA RESTRICCION
    
        self.a_beta = {}
        self.a_beta= self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="a_beta")

        self.a_omega = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.a_omega[p,s,t] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="a_omega[%s,%s,%s]"%(p,s,t))

        self.a_rho = {}
        for p in P:
            self.a_rho[p] = self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="a_rho[%s]"%(p))

        # ESPERANZAS #
        # w
        self.E_w = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.E_w[p,s,t] = 0
        # r
        self.E_r = {}
        for p in P: 
            self.E_r[p] = q[p]


    def generateConstraints(self):
        # Restricción 1
        self.R1 = {}
        self.R1 = self.model.addConstr((1 - γ) * quicksum(self.pi[c]  for c in C) + self.a_beta == 1, name= "Beta")

        # Restricción 2
        self.R2 = {}
        for p in P: 
            for s in S[p]:
                for t in T:     
                    self.R2 = self.model.addConstr(quicksum((self.omega[c,p,s,t] * self.pi[c])  for c in C) + self.a_omega[p,s,t]>= self.E_w[p,s,t], name= "Omega")

        # Restricción 3
        self.R3 = {}
        for p in P: 
            self.R3 = self.model.addConstr(quicksum((self.rho[c,p] * self.pi[c])  for c in C) + self.a_rho[p] >= self.E_r[p], name = "Rho")

    def generateObjective(self):
        self.model.setObjective(self.a_beta+ quicksum(self.a_omega[p,s,t] for p in P for s in S[p] for t in T) +  quicksum(self.a_rho[p] for p in P), GRB.MINIMIZE)

    def solveModel(self):
        self.model.optimize()
        

    def entregarDuales(self):
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

        self.duales = {'Beta': beta_dado, 'W' : W_dados, 'R': R_dados}
        return(self.duales)

class FaseUnoPricing:
    def __init__(self, input):
        self.model = gu.Model('FaseUno Pricing')
        self.W = input["W"] # obtenido a partir del dual del maestro
        self.R = input["R"] # obtenido a partir del dual del maestro
        self.Beta = input["Beta"] # obtenido a partir del dual del maestro

    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()
        self.model.params.NonConvex = 2

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
            self.r[p] = q[p]

        self.r_prima = {}
        for p in P:
            #self.r_prima[p] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="r_prima[%s]"%(p))
            self.r_prima[p] = q[p]
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

        self.k_as = {}
        self.k_as = self.model.addVar(lb = 0, vtype=GRB.CONTINUOUS, name="k")


    def generateConstraints(self):
        
        self.R1 = {}
        # Respetar cantidad de modulos de atencion
        for t in T:
                self.R1[t] = self.model.addConstr(quicksum(self.x[p,T[t-K_ps[p][s]-1]] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])\
                    + quicksum(self.w[p,s,t] * M_sp[p][s] for p in P for s in S[p])  <= (BR + BE), name="Capacidad bloques[%s]" %t)
        
        self.R2 = {}
        # Definifinición de y
        for p in P:
            for s in S[p]:
                #for t in T:
                for t in range(1, 7):
                    # Condicion para evitar exponente igual a 0
                    if t >= K_ps[p][s]:

                        self.R2[p,s,t] = self.model.addConstr(quicksum(self.y[p,s,t,m] for m in range(1, BR+1)) == self.x[p,T[t - K_ps[p][s] - 1]] + self.w[p,s,t]\
                            , name="Definicion y [%s, %s, %s]"%(p,s,t))
                    

        self.R3 = {}
        # Conservacion de flujo de pacientes
        for p in P:
            self.R3[p] = self.model.addConstr( (self.r[p] == self.z[p] + quicksum(self.x[p, d]   for d in range(1, (Lp[p]+1))) ), 
        name="Conservacion de flujo")

        self.R4 = {}
        # Definicion de u, con y
        for p in P:
            for s in S[p]:
                #for t in T:
                for t in range(1, 7):
                    for m in range(1, BR+1):
                        # Condición: termino en mismo día
                        if m + M_sp[p][s] - 2 <= BR + BE:

                            self.R4[p,s,t,m] = self.model.addConstr(self.y[p,s,t,m] == self.u[p,s,t,M[m + M_sp[p][s] - 2]],
                                name="Definicion u [%s, %s, %s, %s]"%(p,s,t,m))

        self.R5 = {}
        # Acotar a número de sillas disponibles
        #for t in T:
        for t in range(1, 7):
            for m in range(1, BR+1):
                self.R5[m,t] =   self.model.addConstr(( quicksum(self.y[p,s,t,m] + 

                            quicksum(self.y[p,s,t, m - M_sp[p][s]] for m in range(1, BR+1) if  m - M_sp[p][s] >= 1)\

                            for p in P for s in S[p]) <= NS), name="Capacidad sillas")
       
        self.R6 = {}
        # Acotar a número de enfermeras
        #for t in T:
        for t in range(1, 7):
            for m in M:

                self.R6[m,t] = self.model.addConstr((quicksum(self.y[p,s,t,m] + self.u[p,s,t,m] for p in P for s in S[p]) <= NE), 
                                            name="Capacidad enfermeras")
        
        self.R7 = {}
        #"Definición w"
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t + 7 >= K_ps[p][s] +1:
                        if t+7 < len(T):

                            self.R7[p,s,t] = self.model.addConstr(self.w_prima[p,s,t] == 
                                self.w[p,s,t+7] + self.x[p,t-K_ps[p][s]+7],
                                        name="Definición w'")
                        else: 
                            self.w_prima[p,s,t] == 0
                    else: 
                        self.w_prima[p,s,t] == 0

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

                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t] == self.w[p,s,t] -γ * (self.w_prima[p,s,t]), name="Definicion omega")
                                
                        else: 
                            self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)
                    else: 

                        self.R19[p,s,t] = self.model.addConstr(self.omega[p,s,t]==0)       
        
        self.R20 = {}
        # Definición de rho
        for p in P:

            self.R20[p] = self.model.addConstr((self.rho[p] == self.r[p] - (γ *self.r_prima[p])), name="Definicion rho")

        self.Rx = {}
        self.Rx = self.model.addConstr(self.k_as == quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR + l] * l  for p in P for s in S[p] for t in range(1, 7) for l in range(1, BE + 1))*(CE-CR))
        
    def generateObjective(self):
        # Funcion costos para k pricing
        #self.k_as = quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR + l] * l  for p in P for s in S[p] for t in T for l in range(1, BE + 1))*(CE-CR)
        self.f_obj_pr = (1 - γ) * self.Beta + quicksum(self.omega[p,s,t] * self.W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(self.rho[p] * self.R[p] for p in P)
        self.model.setObjective(self.f_obj_pr, GRB.MAXIMIZE)


    def solveModel(self):
        self.model.optimize()
       
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
        info_k_as = {}
        info_k_as= self.k_as.x

        columna_actual = {'Rho': info_rho, 'Omega': info_omega, 'w': info_w, 'w_prima': info_w_prima, 'r': info_r, 'r_prima': info_r_prima, 'z': info_z, 'u': info_u, 'k_as': info_k_as}
        informacion[contador_de_columnas] = columna_actual 


print("------------------------------------")
print("COMIENZA LA FASE I")
print("------------------------------------\n")

contador_de_columnas = 1
C = [k for k in range(1, contador_de_columnas + 1)]

# PRIMERA COLUMNA INGRESADA
# CASO POSIBLE: DERIVAR A TODOS

r_inicial = {}

for p in P:

    r_inicial[p] = q[p]

w_inicial = {}

for p in P:
    for s in S[p]:
        for t in T:
            w_inicial[p,s,t] = 0



x_inicial = {}

for p in P:
    for t in T:
        x_inicial[p,t] = 0

z_inicial = {}
for p in P:

    z_inicial[p] = q[p]

r_prima_inicial = {}

for p in P:

    r_prima_inicial[p] = q[p]

w_prima_inicial = {}
for p in P:
    for s in S[p]:
        for t in T:
            # Condicion para evitar exponente igual a 0
                if t + 7 >= K_ps[p][s] +1 :
                    if t+7 < len(T):

                            w_prima_inicial[p,s,t] = w_inicial[p,s,t+7] + x_inicial[p,t-K_ps[p][s]+7]
                    else:
                        w_prima_inicial[p,s,t] = 0
                else:
                    w_prima_inicial[p,s,t] = 0

omega_inicial  = {}
for p in P:
    for s in S[p]:
        for t in T:
            omega_inicial[p,s,t] = 0

rho_inicial = {}
for p in P:
    rho_inicial[p] = r_inicial[p] - (γ *r_prima_inicial[p])

k_as_inicial = quicksum(CD[p] * z_inicial[p] for p in P) 

informacion = {1: {'Omega': omega_inicial, 'Rho': rho_inicial, 'w': w_inicial, 'w_prima': w_prima_inicial, 'r': r_inicial, 'r_prima': r_prima_inicial, 'z': z_inicial,  'k_as': k_as_inicial}} 

objetivo_maestro_fase1 = 99999999

while objetivo_maestro_fase1 != 0:
    print("------------------------------------")
    print("MAESTRO FASE 1 -- ITERACIÓN: " + str(contador_de_columnas - 1))
    print("------------------------------------")
    #se entrega la informacion de la columan respectiva
    Fase1Maestro = FaseUnoMasterProblem(informacion)
    Fase1Maestro.buildModel()
    Fase1Maestro.solveModel()
    Fase1Maestro.model.printAttr("X")
    #se solicita la informacion
    duales = Fase1Maestro.entregarDuales()
    
    objetivo_maestro_fase1 = Fase1Maestro.model.objVal

    #se ingresa el "espacio" para una nueva columna que será llenada con el resutado del pricing
    contador_de_columnas += 1
    C = [k for k in range(1, contador_de_columnas + 1)]
    print("------------------------------------")
    print("PRICING FASE 1 -- ITERACIÓN: " + str(contador_de_columnas - 1))
    print("------------------------------------")
    Fase1Pricing = FaseUnoPricing(duales)
    Fase1Pricing.buildModel()
    Fase1Pricing.solveModel()
    #se actualiza la informacion
    Fase1Pricing.entregarInformacion()
    objetivo_pricing_fase1 = Fase1Pricing.model.objVal

print("------------------------------------")
print("FIN DE LA FASE I")
print("------------------------------------\n")

print("------------------------------------")
print("INICIO DE LA FASE II")
print("------------------------------------\n")

valor_objetivo_maestro = 0 
valor_objetivo_pricing = 0

modelImprovable = True
while modelImprovable == True:
    print("------------------------------------")
    print("MAESTRO -- ITERACIÓN: " + str(contador_de_columnas - 1))
    print("------------------------------------")
    master_solution = MasterProblem(informacion)
    master_solution.buildModel()
    master_solution.model.optimize()

    #Actualizamos resultado
    valor_objetivo_maestro = master_solution.model.objVal
    
    #requerimos los beta, W y R (duales del maestro):
    duales = master_solution.entregarDuales()

    # Una vez resuelto el Master, usamos estos datos como input para el pricing
    print("------------------------------------")
    print("PRICING -- ITERACIÓN: " + str(contador_de_columnas - 1))
    print("------------------------------------")
    pricing_solution = SubProblem(duales)

    pricing_solution.buildModel()
    pricing_solution.model.optimize()
    pricing_solution.model.printAttr("X")

    #revisamos el valor del pricing
    valor_objetivo_pricing = pricing_solution.model.objVal
    
    #si el valor es positivo, aun se puede mejorar
    # se añade nueva columna
    contador_de_columnas += 1
    C = [k for k in range(1, contador_de_columnas + 1)]

    if valor_objetivo_pricing>0:
        modelImprovable = True
        #conseguimos la columna a ser ingresada
        pricing_solution.entregarInformacion()
        
    else:
        modelImprovable = False

print("------------------------------------")
print("FIN DE LA FASE II")
print("------------------------------------\n")

print("------------------------------------")
print("ESTADÍSTICAS")
print("------------------------------------\n")

print("1. Derivación por protocolo")
pacientes_llegados = 0
pacientes_derivados = 0
for p in P:
    print("Porcentaje de derivación protocolo", str(p), ":", (pricing_solution.z[p].x / pricing_solution.r[p].x) * 100,"%")
    pacientes_derivados += pricing_solution.z[p].x 
    pacientes_llegados += pricing_solution.r[p].x 
print("Derivación total:", (pacientes_derivados / pacientes_llegados) * 100, "%")

# Agregar más métricas de satisfacción
# Días de espera antes de comenzar el tratamiento
# Tiempo de ejecución
# Costo total versus simulación de agendamiento manual
# print("2. ")
<<<<<<< HEAD
=======
    
>>>>>>> 118b65e2644b3c7e0c1e815127b53b98d68a863f
