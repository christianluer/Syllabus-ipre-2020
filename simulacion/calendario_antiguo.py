#!/usr/bin/env python
# coding: utf-8
from collections import defaultdict
# In[14]:

semanas_de_simulacion = 6

dias = ["lunes", "martes", "miercoles", "jueves","viernes", "sabado"]
calendario = defaultdict(defaultdict)


class Modulo:
    def __init__(self, identificador):
        self.paciente = None
        self.ocupado = False
        self.necesita_enfermera = False
        self.identificador = None

cuenta = 0
for i in range(semanas_de_simulacion):
    semana = defaultdict(defaultdict)
    for j in dias:
        asiento = defaultdict(defaultdict)
        for k in range(1, 15):
            modulo = defaultdict(classmethod)
            for u in range(1, 41):  # numero modulos
                cuenta += 1
                modulo[u] = Modulo(cuenta)
            asiento[k] = modulo
        semana[j] = asiento
    calendario[i] = semana



