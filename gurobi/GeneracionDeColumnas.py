import pandas as pd
import numpy as np
import gurobipy as gu


########################
# DEFINICIÓN DE CLASES #
########################

class MasterProblem:
    def __init__(self, patternDF, inputDF):
        self.patternCost = patternDF['PatternCost'].values
        self.pattern = patternDF['PatternFill'].values
        self.amount = inputDF['Amount'].values
        self.model = gu.model('MasterProblem')
        self.patternsIndex = patternDF.index.values

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

        self.r= {}
        # Cantidad de pacientes en la semana del protocolo p
        for p in P:
            self.r[p] = self.model.addVar(lb=0,  vtype=GRB.INTEGER, name="r[%s]"%(p))

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

    def generateConstraints(self):
        # Restricción 1
        self.model.addConstr((1 - γ) * sum(pi[c] for c in C) == 1)

        # Restricción 2
        for p in P: 
            for s in S[p]:
                for t in T:     
                    self.model.addConstr(sum((omega_cpst[c,p,s,t] * pi[c]) for c in C) >= E_alpha_w[p,s,t])

        # Restricción 3
        for p in P: 
            self.model.addConstr(sum((rho_cp[c,p] * pi[c]) for c in C) >= E_alpha_r[p])

        # Restricción 4
        for c in C: 
            self.model.addConstr(pi[c] >= 0)

    def generateObjective(self):
        self.model.setObjective(sum((k_c[c] * pi[c]) for c in C), GRB.MINIMIZE)

    def addColumn(self, objective, newPattern): 
        ctName = ('PatternUseVar[%s]' %len(self.model.getVars()))
        newColumn = gu.Column(newPattern, self.model.getConstrs())
        self.model.addVar(vtype = gu.GRB.INTEGER, lb=0, obj=objective, column=newColumn, name=ctName)
        self.model.update()

    def solveModel(self, timeLimit=None, GAP='EPSILON'):
        self.model.setParam('TimeLimit', timeLimit)
        self.model.setParam('MIPGap', 'EPSILON')
        self.model.optimize()


class SubProblem:
    def __init__(self, inputDF, rollWidth, duals):
        self.patternCost = patternDF['PatternCost'].values
        self.pattern = patternDF['PatternFill'].values
        self.amount = inputDF['Amount'].values
        self.pieceSize = inputDF['Size'].values
        self.rollWidth = rollWidth
        self.duals = duals
        self.model = gu.model('SubProblem')
        self.piecesIndex = inputDF.index.values

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
        self.ω = {}
        for p in P:
            for s in S[p]:
                for t in T:
                    self.ω[p,s,t] = self.model.addVar(lb=0,  vtype=GRB.CONTINUOUS, name="ω[%s,%s,%s]"%(p,s,t))

        self.ρ = {}
        for p in P:
            self.ρ[p] = self.model.addVar(lb=0,   vtype=GRB.CONTINUOUS, name="ρ[%s]"%(p))
        

    def generateConstraints(self):
        # Funcion costos para k pricing
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
    
    def getNewPattern(self):
        return self.model.gettAtr('X', self.model.getVars())


##########################
# GENERACIÓN DE COLUMNAS #
##########################

#last_obj_master = 1
actual_obj_master = 0
actual_pricing_value = -1000

columnas = [0]
column_to_enter = len(columnas)
# *POR AHORA SE DEJAN EN VALOR CERO, PERO HAY QUE CAMBIARLOS DPS a ser matrices [l,g]
chi_pr = chi_primera_col # que sea una lista, donde cada posicion es una columna, y en c/ columna tengo un dict con chi_pr[l,g]
delta_pr = delta_primera_col
rho_pr = [18]
k = [0]
####

#actual_pricing_value > 0.00001
while (actual_pricing_value < -0.00001 and len(columnas) < 1000):
  
    last_obj_master = actual_obj_master
    
    aux_chi_pr = {}
    aux_delta_pr = {}
    aux_rho_pr = 0
    aux_k = 0

    #Optimizamos el master
      
    master_solution = MasterProblem({"columnas": columnas, "chi_pr": chi_pr, "delta_pr": delta_pr, "rho_pr": rho_pr, "k": k})
    master_solution.buildModel()
    master_solution.model.optimize()

    #Actualizamos resultado
    actual_obj_master = master_solution.model.objVal
    #print("RESULTADO MASTER:", actual_obj_master)
    
    master_solution.model.printAttr('X')
    print("RESULTADOS PI")
    print(master_solution.model.getVars())
    rest = master_solution.model.getConstrs()
    X_dados, D_dados = {}, {}
    for r in rest:
        if r.constrName == "beta":
            beta_dado = r.Pi
        elif r.constrName[0] == "X":
           X_dados[r.constrName] = r.Pi
        elif r.constrName[0] == "D":
            D_dados[r.constrName] = r.Pi  
        else:
            rho_dado = r.Pi
    # print("Llega hasta iteración: ", column_to_enter)
    # print("beta_dado: ", beta_dado)
    # print("X_dados: ", X_dados)
    # print("D_dados: ", D_dados)
    # print("rho_dado: ", rho_dado)

    # una vez resuelto el Master, usamos estos datos como input para el pricing, para resolver este
    #pricing_solution = PricingProblem({"beta_dado": beta_dado, "X_dados": X_dados, "D_dados": D_dados, "rho_dado": rho_dado})

    #ESTAMOS FORZANDO RHO DADO = 1 PARA QUE FUNCIONE EL PRICING (NO SIRVE CON 0 -> tira valores sin sentido para b)
    pricing_solution = PricingProblem({"beta_dado": beta_dado, "X_dados": X_dados, "D_dados": D_dados, "rho_dado": 1})

    pricing_solution.buildModel()
    pricing_solution.model.optimize()
    lista_variables_pricing = pricing_solution.model.getVars()

    actual_pricing_value = pricing_solution.model.objVal
    pricing_solution.model.printAttr('X')

    for v in lista_variables_pricing: 
        name = v.varName
        if name[0] == "c": # para chi_pr
            aux_chi_pr[name] = v.x # Key del dict será "chi_pr[indicex,indicey]"
        elif name[0] == "d": # para delta_pr
            aux_delta_pr[name] = v.x
        elif name[0] == "r": # para rho_pr
            aux_rho_pr = v.x
        elif name[0] == "k": # para k
            aux_k = v.x
    
    
    #if actual_pricing_value > 0:
    print("Veamos pricing_valur:" + str(actual_pricing_value))
    if actual_pricing_value < 0:
        columnas.append(column_to_enter)
        #print(columnas)
        chi_pr.append(aux_chi_pr)
        delta_pr.append(aux_delta_pr)
        rho_pr.append(aux_rho_pr)
        k.append(aux_k)
    column_to_enter += 1
    #print("Número de iteraciones" + str(column_to_enter))
    if column_to_enter == 30:
        break



# imprimo valores resultantes del master
#print("Llega hasta iteración: ", column_to_enter - 1)


