import math
import numpy as np


def PerformancePanel(G,Tc,data):
    
    #ESTOS DATOS SE CARGAN CON GIS
    To=Tc+273.15
     #Constantes  globales no dependen del panel
    Trc = 25  # Temperatura [ºC] stc
    Tr = Trc + 273.15  # Temperatura referencia (K)
    k = 1.3805 * (10 ** (-23))  # Constante de Bolzmann
    A = 1.3  # Factor ideal del diodo 
    Gref = 1000  # Radiación solar 1000[w/m^2]  
    q = 1.602 * (10 ** (-19))  # Carga del electrón (C)
    Eg = 1.1  # Brecha energetica (band gap), para el silicio (1.1 eV-->Silicio)
   
    #Datos que vienen del panel seleccionado por GIS
    
    Ns =float(data['panel']['N_s'])  # Número de celdas conectadas en serie 
    Ki =float(data['panel']['Tc_isc'])  # Coeficiente de corriente de cortocircuito de la celula (%/ºC)
    
    Isc = float(data['panel']['Isc'])  # Isc: Corriente  de cortocircuito (A) at STC
    Voc = float(data['panel']['Voc'])  # Voc: Tensión de de circuito abierpto (V) JAM78S10 435-455/MR
    
    Np = float(data['panel']['N_p']) # Número de celulas en paralelo, para modelo JAM78S10 435-455/MR
    NskATo=Ns*k*A*To

       
    Iph = (Isc + Ki * (To-Tr)) * (G/Gref) #Iph: Corriente fotoelectrica de la celula solar con la radiacion recibida
   
   
    Irs = Isc / (math.exp((q*Voc)/NskATo)-1)  # Irs: Corriente de saturación inversa de diodo en Trtc (A)
  
   
    Is = Irs * (To/Tr)**3 * math.exp((q*Eg)/(A*k)*(1/Tr-1/To))
         
    
    V = np.linspace(0,Voc,100)
    
    I = lambda V : Np*Iph - Np*Is*(np.exp(q*((V/NskATo)))-1)
    P = lambda V : (Np*Iph - Np*Is*(np.exp(q*((V/NskATo)))-1))*V
    
    aa = I(V)
    bb = P(V)
    aa= np.maximum(aa, 0) 

#    print(V)
#    print(aa)
#    print(bb)
    return V,aa,bb
