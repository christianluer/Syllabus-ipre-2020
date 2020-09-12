#!/usr/bin/env python
# coding: utf-8
from collections import defaultdict
# In[14]:

semanas_de_simulacion = 4

dias = ["lunes", "martes", "miercoles", "jueves","viernes", "sabado", "domingo"]
calendario = defaultdict(defaultdict)
semana = defaultdict(defaultdict)
modulo = defaultdict(bool)
for i in range(1, 41):
    modulo[i] = True
for i in dias:
    semana[i] = modulo


for i in range(semanas_de_simulacion):
    calendario[i] = semana




# In[ ]:




