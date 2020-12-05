from gurobipy import *

import numpy as np


##FALTA:
#No estoy segura que parametros incorporar dentro de la clase y cuales dejar fuera
#implementar variables


#creación de la clase pricing con el problema respectivo
class Pricing:
    def __init__(self, input):
        self.model = Model("Asignación")
        #Esperable un input como diccionario con todos los datos necesarios
        self.x = x #ejemplo, no estoy segura cuales son los que nosostros necistamos
        
    def buildModel(self):
        #funciones de gurobi
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()
    
    def generateVariables(self): #variables
        self.ω = self.model.addVars()
        self.ρ = self.model.addVars()
        self.w = self.model.addVar()
        self.w_prima= self.model.addVar()
        self.r= self.model.addVars()
        self.r_prima= self.model.addVars()
        self.x = self.model.addVars()
        self.y = self.model.addVar()
        self.z = self.model.addVar()
        self.u = self.model.addVar()

    
    def generateConstraints(self):
        # funcion costos para k pricing
        self.model.addConstr(self.k_as == quicksum(CD[p] * self.z[p] for p in P) + quicksum(self.u[p,s,t,BR+l]*l  for p in P for s in S[p] for t in T for l in range(1, BE+1))*(CE-CR))
        R1 = {}
        # Respetar cantidad de modulos de atencion
        for t in T:
                R1[t] = self.model.addConstr(quicksum(self.x[p,T[t-K_ps[p][s]-1]] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])\
                    + quicksum(self.w[p,s,t] * M_sp[p][s] for p in P for s in S[p] if t >= K_ps[p][s])  <= BR + BE, name="Capacidad bloques[%s]" %t)
        
        R2 = {}
        # Definifinición de y
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t >= K_ps[p][s]:

                        R2[p,s,t] = self.model.addConstr(quicksum(self.y[p,s,t,m] for m in range(1, BR+1)) == self.x[p,T[t - K_ps[p][s] - 1]] + self.w[p,s,t]\

                        , name="Definicion y [%s, %s, %s]"%(p,s,t))
                    else: 
                        R2[p,s,t] = self.model.addConstr( self.w[p,s,t]==0)

        R3 = {}
        # Conservacion de flujo de pacientes
        for p in P:
            R3[p] = self.model.addConstr( (self.r[p] == self.z[p] + quicksum(self.x[p, d]   for d in range(1, (Lp[p]+1))) ), 
        name="Conservacion de flujo")

        R4 = {}
        # Definicion de u, con y
        for p in P:
            for s in S[p]:
                for t in T:
                    for m in range(1, BR+1):
                        # Condición: termino en mismo día
                        if m + M_sp[p][s] - 2 <= BR + BE:

                            R4[p,s,t,m] = self.model.addConstr(self.y[p,s,t,m] == self.u[p,s,t,M[m + M_sp[p][s] - 2]],
                                name="Definicion u [%s, %s, %s, %s]"%(p,s,t,m))

        R5 = {}
        # Acotar a número de sillas disponibles
        for t in T:
            for m in range(1, BR+1):
                R5[m,t] =   self.model.addConstr(( quicksum(self.y[p,s,t,m] + 

                            quicksum(self.y[p,s,t, m - M_sp[p][s]] for m in M if  m - M_sp[p][s] >= 1)\

                            for p in P for s in S[p]) <= NS), name="Capacidad sillas")
       
        R6 = {}
        # Acotar a número de enfermeras
        for t in T:

            for m in M:

                R6[m,t] = self.model.addConstr((quicksum(self.y[p,s,t,m] + self.u[p,s,t,m] for p in P for s in S[p]) <= NE), 
                                            name="Capacidad enfermeras")
        R7 = {}
        "Definición w"
        for p in P:
            for s in S[p]:
                for t in T:
                    # Condicion para evitar exponente igual a 0
                    if t + 7 >= K_ps[p][s]:
                        if t+7 < len(T):

                            R7[p,s,t] = self.model.addConstr(self.w_prima[p,s,t] == 
                                self.w[p,s,T[t-K_ps[p][s]+7]] + self.x[p,T[t+7]],
                                        name="Definición w'")

        R8 = {}
        # Realización de llegadas - probabilidades de transición
        for p in P:
            R8[p] = self.model.addConstr((self.r_prima[p] == q[p]), name="Realizacion de las llegadas")
        
        
        R19 = {}
        # Definición de ω
        for p in P:
            for s in S[p]:
                for t in T:
                    if t+7 <len(T): 
                        # Condición de avance de sesiones
                        if t + 1 >= K_ps[p][s]:

                            R19[p,s,t] = self.model.addConstr(self.ω[p,s,t] == self.w[p,s,t] - γ * (self.w[p,s,T[t+7]] 
                                + self.x[p,T[t+7]]), name="Definicion ω")
                        else: 
                            R19[p,s,t] = self.model.addConstr(self.ω[p,s,t]==0)
                    else: 

                        R19[p,s,t] = self.model.addConstr(self.ω[p,s,t]==0)       
        
        
        R20 = {}
        # Definición de ρ
        for p in P:

            R20[p] = self.model.addConstr((self.ρ[p] == self.r[p] - (γ *self.r_prima[p])), name="Definicion ρ")

    def generateObjective(self):
        self.f_obj_pr = (1 - γ) * β + quicksum(self.ω[p,s,t] * W[p,s,t] for p in P for s in S[p] for t in T) + quicksum(self.ρ[p] * self.R[p] for p in P) - self.k_as
        self.model.setObjective(self.f_obj_pr, GRB.MAXIMIZE)







#creación de la clase main con el problema respectivo
class MasterProblem:
    def __init__(self, input):
        self.model = Model("Main")
        #Esperable un input estilo diccionario con todos los datos necesarios
        self.columnas = input["columnas"] #lista con los indices de todas las columnas que se estan considerando
        #faltan

    def buildModel(self):
        self.generateVariables()
        self.generateConstraints()
        self.generateObjective()
        self.model.update()
    
    def generateVariables(self):
        # le quitamos el lb=0, revisar dps
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


