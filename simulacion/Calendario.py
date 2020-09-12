#!/usr/bin/env python
# coding: utf-8
<<<<<<< HEAD
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

=======
>>>>>>> b252586bd8b711dce57c3d029714da95d637d719

# In[20]:


calendario = {}
modulo={}
for i in range (1,41):
    ocupado=False
    if ocupado==False:
         modulo[i]={"ocupado":None,"cantidad":0,"hora_extra":None}
    else:
         modulo[i]={"ocupado":True,"cantidad":0,"hora_extra":None}
            
semana={"lunes":modulo,"martes":modulo,"miercoles":modulo,"jueves":modulo,"viernes":modulo,"sabado":modulo,"domingo":modulo}
for i in range (1,3):
    calendario[i]=semana
print (calendario)


# In[ ]:




