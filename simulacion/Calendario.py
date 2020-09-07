#!/usr/bin/env python
# coding: utf-8

# In[14]:


calendario = {}
semana={"lunes":"0","martes":"1","miercoles":"2","jueves":"3","viernes":"4","sabado":"5","domingo":"6"}
modulo={}
for i in range (1,41):
    modulo[i]=i
semana={"lunes":modulo,"martes":modulo,"miercoles":modulo,"jueves":modulo,"viernes":modulo,"sabado":modulo,"domingo":modulo}
for i in range (0,2):
    calendario[i]=semana
print (calendario)


# In[ ]:




