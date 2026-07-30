import numpy as np
import numpy_financial as npf
import plugins.plugins.VariablesGlobales as vg

      
def NPV(Ahorro, PotPico,SupPaneles,NumPaneles): #€, kW,m2,ud

    INV=np.zeros(vg.VidaUtil+1)
    
    INVInstalacion=PotPico* NumPaneles*vg.PrecioWp_Flotante

    INVTotal=INVInstalacion

    OMTotal=INVTotal*vg.CosteOM_Flotante
#    print(OM)
#    Saving=np.zeros(NumUsuarios)
    
    Saving=Ahorro 
#    print(Saving)
###############################################################################
# CALCULO VAN 
###############################################################################      
    
    NPVAhorro=np.zeros(vg.VidaUtil) #Por filas año
    NPVOM=np.zeros(vg.VidaUtil)
    NPVInversion=np.zeros(vg.VidaUtil+1)
    NPV=np.zeros(vg.VidaUtil)
    
   

 
    n=0 # n marca el año
    NPVInversion[0]=INVTotal # año 0 inversion=inversion inicial
    for j in range (1,vg.VidaUtil+1):

        n=j
        
        NPVAhorro[j-1]=(Saving/(vg.d-vg.ielec))*(1-(((1+vg.ielec)/(1+vg.d))**n))
        
        NPVOM[j-1]=(OMTotal/vg.d)*(1-(1/(1+vg.d))**n)
        
        NPVInversion[j]=NPVInversion[j-1]+INV[j]/(1+vg.d)**n
    
        NPV[j-1]=NPVAhorro[j-1]-NPVOM[j-1]-NPVInversion[j-1]

    return NPV,NPVAhorro,NPVInversion, NPVOM, INVTotal

def PeriodoRetornoSimple(VAN):
    
    VAN=VAN.tolist()
    
    Año=-1
    if VAN[-1]<0:
        PR=-1
        return PR
    else:
        for i in range(0,len(VAN)):
            if VAN[i]<0 and VAN[i+1]>0:
           
               Año=VAN.index(VAN[i])
    
    if Año==-1:
        PR=-1
    else:
        PR=Año-(((VAN[Año]-0)/(VAN[Año]-VAN[Año+1]))*(Año-(Año+1)))

    return PR+1 #el +1 es si consideramos que empezamos a contar en el Año 1

def TIR(VAN):
    if VAN[-1] < 0:
        return -1

    VAN=VAN.tolist()
    TIR=npf.irr(VAN) ## Esta función podría sustituirse por un for que vaya 
    # llamando a VAN y variando d hasta que abs(VAN-0)<Tolerancia
    
    return round(TIR*100,2)

