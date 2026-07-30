

import numpy as np   


###############################################################################
# Función que calcula el ingreso de venta de energía a red
###############################################################################
def Ingreso(EnergiaProducida,TafEnergy): #Energia[kWh] Tarifa[€/kWh]
    
    Periodo=EnergiaProducida.size
    Ing=np.zeros(Periodo)
    #print('pppppppppppp', Periodo)
    #print('llllllllllll', len(TafEnergy))
    ##print('kkkkkkkkkkkk', TafEnergy[110:120])
    #print('xxxxxxxxxxxx', EnergiaProducida[110:120])
    
    for i in range (0, Periodo):
        if (TafEnergy.iloc[i]>0):
            Ing[i]=EnergiaProducida[i]*TafEnergy.iloc[i]
        else:
            Ing[i]=0
    #print('ingresos', Ing[110:120])
    #print('ingresos', Ing)
    return Ing #[€]

###############################################################################
# Función que calcula el ingreso extra por el hehco de producir más energía
###############################################################################

def Beneficio(IngresoOriginal,IngresoRef):
    
    Periodo=IngresoOriginal.size
    
    AumentoIngreso=np.zeros(Periodo)
    
    for i in range (0, Periodo):
        AumentoIngreso[i]=IngresoRef[i]-IngresoOriginal[i]
   
    AumentoT=0
    for i in range (0, Periodo):
       AumentoT=AumentoT+AumentoIngreso[i] 
                  
    return AumentoT,AumentoIngreso