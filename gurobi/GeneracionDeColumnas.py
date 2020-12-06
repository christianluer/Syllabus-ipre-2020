from gurobipy import *

import numpy as np


##FALTA:
# No estoy segura que parametros incorporar dentro de la clase y cuales dejar fuera
# Faltan β, W, R  y los parametros compartidos


# Creación de la clase pricing con el problema respectivo
class Pricing:
    def __init__(self, input):
        self.model = Model("Asignación")
        #Esperable un input como diccionario con todos los datos necesarios
        self.x = x #ejemplo, no estoy segura cuales son los que nosostros necesitamos
        

    def buildModel(self):
        #funciones de gurobi
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()
    

    def generateVariables(self): #variables
        self.ω = = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.ω[p,s,t] = self.model.addVar(lb=0,  vtype=GRB.CONTINUOUS, name="ω[%s,%s,%s]"%(p,s,t))
        

        self.ρ = {}
        for p in P:
            self.ρ[p] = self.model.addVar(lb=0,   vtype=GRB.CONTINUOUS, name="ρ[%s]"%(p))
        

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
    

    def generateConstraints(self):
        # funcion costos para k pricing
        self.model.addConstr(self.k_as == quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR+l]*l  for p in P for s in S[p] for t in T for l in range(1, BE+1))*(CE-CR))
        
        
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
        "Definición w"
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
        # Definición de ω
        for p in P:
            for s in S[p]:
                for t in T:
                    if t+7 <len(T): 
                        # Condición de avance de sesiones
                        if t + 1 >= K_ps[p][s]:

                            self.R19[p,s,t] = self.model.addConstr(self.ω[p,s,t] == self.w[p,s,t] - γ * (self.w[p,s,T[t+7]] 
                                + self.x[p,T[t+7]]), name="Definicion ω")
                        else: 
                            self.R19[p,s,t] = self.model.addConstr(self.ω[p,s,t]==0)
                    else: 

                        self.R19[p,s,t] = self.model.addConstr(self.ω[p,s,t]==0)       
        
        
        self.R20 = {}
        # Definición de ρ
        for p in P:

            self.R20[p] = self.model.addConstr((self.ρ[p] == self.r[p] - (γ *self.r_prima[p])), name="Definicion ρ")

    def generateObjective(self):
        self.f_obj_pr = (1 - γ) * β + quicksum(self.ω[p,s,t] * W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(self.ρ[p] * self.R[p] for p in P) - self.k_as
        self.model.setObjective(self.f_obj_pr, GRB.MAXIMIZE)




#faltan los inputs dados (creo que se hace con la otra parte  si como con la relacion)
#falta k_c, omega_cspt, rho_cp, E_alpha_w, E_alpha_r

#creación de la clase main con el problema respectivo
class MasterProblem:
    def __init__(self, input):
        self.model = Model("Main")


    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()
    
    def generateVariables(self):
        self.pi = self.model.addVars(C, lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name="Columna ingresada"))

    def generateConstraints(self):
        #restricción 1
        self.model.addConstr((1 - γ) * sum(self.pi[c] for c in C) == 1)
        
        #restriccion 2
        for p in P: 

            for s in S[p]:

                for t in T:
            
                    self.model.addConstr(sum((omega_cpst[c,p,s,t] * self.pi[c]) for c in C) >= E_alpha_w[p,s,t])
        
        #restriccion 3
        for p in P: 
            self.model.addConstr(sum((rho_cp[c,p] * self.pi[c]) for c in C) >= E_alpha_r[p])

        #restricción 4
        for c in C: 
            self.model.addConstr(pi[c] >= 0)


    def generateObjective(self):
        self.f_obj_master = quicksum((k_c[c] * self.pi[c]) for c in C)
        self.model.setObjective(self.f_obj_master, GRB.MINIMIZE)


