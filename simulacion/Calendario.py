#!/usr/bin/env python
# coding: utf-8

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




