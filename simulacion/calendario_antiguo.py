#!/usr/bin/env python
# coding: utf-8
from collections import defaultdict
# In[14]:

semanas_de_simulacion = 4

dias = ["lunes", "martes", "miercoles", "jueves","viernes", "sabado"]
calendario = defaultdict(defaultdict)
semana = defaultdict(defaultdict)
modulo = defaultdict(list)
asiento = defaultdict(defaultdict)

class Modulo:
    def __init__(self):
        self.paciente = None
        self.ocupado = False
        self.necesita_enfermera = False

for i in range(1, 41):#numero modulos
    modulo[i] = Modulo()

for i in range(1, 15):
    asiento[i] = modulo

for i in dias:
    semana[i] = asiento


for i in range(semanas_de_simulacion):
    calendario[i] = semana

for j in range(len(calendario[0]["lunes"][1])):
    string = f""
    for i in calendario[0]["lunes"]:
        string += f"{calendario[0]['lunes'][i][1]}  "


# In[ ]:




