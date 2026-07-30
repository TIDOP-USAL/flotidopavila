##############################################################################
# Nombre del archivo: SistemaRefrigeracion.py
# Fecha última modificación: 06/11/2023
# Autor/es:
#   Néstor Velaz
###############################################################################"
import numpy as np
import os
import pandas as pd
from scipy.interpolate import interpn 
from scipy.interpolate import RegularGridInterpolator as rgi

def Refrigeracion(Irradiancia):
    
    Ta=Irradiancia['temp_air']
    Vw=Irradiancia['wind_speed']
    G=Irradiancia['poa_global']
    
    #print('Irradiancia:', G)
    
    TCRef=[]
    
    e0=2.0458
    e1=0.9458
    e2=0.0215
    e3=1.2376
    
    
    for i in range (0,Ta.size):
        TCRef.append(e0+e1*Ta.iloc[i]+e2*G.iloc[i]-e3*Vw.iloc[i])
        
    
    return TCRef

def SinRefrigeracion(Irradiancia,TONC):
    Ta=Irradiancia['temp_air']
    G=Irradiancia['poa_global']
    
    TC=[]
    
#    TONC=47 #DAto panel debería venir SIG
    
    for i in range (0,Ta.size):
        
        
        TC.append(Ta.iloc[i]+G.iloc[i]*(TONC-20)/800)
        
    
    return TC
    
def RefrigeracionMCDM(G,Ta,Vw):
    
    
    TCRef=[]
    
    e0=2.0458
    e1=0.9458
    e2=0.0215
    e3=1.2376
    
    
    for i in range (0,Ta.size):
        TCRef.append(e0+e1*Ta[i]+e2*G[i]-e3*Vw[i])
    
    return TCRef

def Interpolacioncsv(VReal,GReal,TReal):
    
    #print(VReal)
    #print(GReal)
    #print(TReal)
    
    
    PathBase=os.getcwd()
    PathCarpeta='\\Database\\SistemaRefrigeracionCTC'
    Archivo='\\vGTaTs2.csv'
    
    Path=PathBase+PathCarpeta+Archivo

    Termico=pd.read_csv(Path,delimiter=';',index_col=False)
    
    V=Termico['Vw']
    G=Termico['G']
    T=Termico['Tamb']
    Tc=Termico['Tpv']
    
    V=V.tolist()
    G=G.tolist()
    T=T.tolist()
    Tc=Tc.tolist()
    
#    print(len(V))
    
#    V=[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
#    G=[400,400,400,400,500,500,500,500,400,400,400,400,500,500,500,500]
#    
#    T=[10,12,14,16,10,12,14,16,10,12,14,16,10,12,14,16]
#    
#    Tc=[30,32,40,45,47,34,38,43,35,39,41,46,100,150,160,125]
#    
#    VReal=0.75
#    GReal=200
#    TReal=15.7
#    
#    TCInterpolada=0
#    IndiceT=[]
    
    indexT=[]
    
#######################################################################################################################
# Subdividir los vectores T,G,TC y V en sublistas organizadas
#####################################################################################################################    
    for i in range(0,len(T)):
        if T[i]==T[0]:
            indexT.append(i)
        else:
            pass
    
        
#    print(indexT)
    
    Tsub=[]
    Tcsub=[]
    Gsub=[]
    Vsub=[]
    
    for j in range(0,len(indexT)-1):
        
        Tsub.append(T[indexT[j]:indexT[j+1]])
        Tcsub.append(Tc[indexT[j]:indexT[j+1]])
        Gsub.append(G[indexT[j]:indexT[j+1]])
        Vsub.append(V[indexT[j]:indexT[j+1]])
    
    Tsub.append(T[indexT[-1]:])
    Tcsub.append(Tc[indexT[-1]:])
    Gsub.append(G[indexT[-1]:])
    Vsub.append(V[indexT[-1]:])
    
#    print(len(Tcsub))
#    print(Vsub)
#    print(Gsub)
#    print(Tsub)
#    print(Tcsub)
    
#    print(Gsub[0][0])
#    print(Gsub[1][0])
#############################################################################################################################
# INTERPOLACION en T
#############################################################################################################################    
    
    
    for p in range (0,len(Tsub)-1):
#        print("a")
#        print(Tsub[p][0])
#        print(len(Tcsub[p][:])+1)
        if TReal<Tsub[p][0]:
            for i in range(0,len(Tcsub[p][:])): #Si valor menor del menor valor del rango
#                print(i)
                Tcsub[p][i]=Tcsub[p][0]
                
                Tcsub[-1][i]=Tcsub[-1][0]
                
#                print("a")
        elif TReal>Tsub[p][-1]:
            for i in range (0,len(Tcsub[p][:])): #Si valor mayor del mayor valor del rango
                Tcsub[p][i]=Tcsub[p][-1]
              
                Tcsub[-1][i]=Tcsub[-1][-1]
                
#                print("b")
        else:                               #si el valor esta dentro de los rangos
            for i in range(0,len(Tsub[p][:])-1):
                                
        
                if TReal-Tsub[p][i]>0 and TReal-Tsub[p][i+1] < 0:  
                    TInter=Tcsub[p][i]- ((Tsub[p][i]-TReal)/(Tsub[p][i]-Tsub[p][i+1]))*(Tcsub[p][i]-Tcsub[p][i+1])
                    TInterult=Tcsub[-1][i]- ((Tsub[-1][i]-TReal)/(Tsub[-1][i]-Tsub[-1][i+1]))*(Tcsub[-1][i]-Tcsub[-1][i+1])
#                    print("c")
                    for j in range (0,len(Tcsub[p][:])):
                        Tcsub[p][j]=TInter
                        Tcsub[-1][j]=TInterult
               
    #print("Interpolacion en T:")
#############################################################################################################################
# INTERPOLACION en G
#############################################################################################################################    
    for p in range (0,len(Gsub)-1):
        
        
        
        if GReal-Gsub[p][0]<0 and GReal-Gsub[p+1][0]<0:
            
            for i in range(0,len(Tcsub[p][:])):
                Tcsub[p][i]=Tcsub[p][0]
#                Tcsub[p+1][i]=Tcsub[0][0]
#                Tcsub[-1][i]=Tcsub[-1][0]
#                print("a")
                
        elif GReal-Gsub[p][0]>0 and GReal-Gsub[p+1][0]>0:
            for i in range (0,len(Tcsub[p][:])):
                Tcsub[p][i]=Tcsub[p][-1]
#                Tcsub[p+1][i]=Tcsub[0][0]
#                Tcsub[-1][i]=Tcsub[-1][0]
#                print("b")
        else: 
           
            if GReal-Gsub[p][0]>0 and GReal-Gsub[p+1][0] < 0: 
                
                TInter=Tcsub[p][0]- ((Gsub[p][0]-GReal)/(Gsub[p][0]-Gsub[p+1][0]))*(Tcsub[p][0]-Tcsub[p+1][0])
#                TInter=Tcsub[p][0]- ((Gsub[p][0]-GReal)/(Gsub[p][0]-Gsub[p+1][0]))*(Tcsub[p][0]-Tcsub[p+1][0])
#                TInterult=Tcsub[-1][0]- ((Gsub[-1][0]-TReal)/(Gsub[-1][0]-Gsub[-1][i+1]))*(Tcsub[-1][0]-Tcsub[-1][i+1])
#                print("c")
                for j in range (0,len(Tcsub[p][:])):
                    
                    Tcsub[p][j]=TInter
                    Tcsub[p+1][j]=TInter
#                    Tcsub[-1][j]=TInter
   
    #print("Interpolacion en G:")
    
    
#############################################################################################################################
# INTERPOLACION en V
#############################################################################################################################    
    for p in range (0,len(Vsub)-1):
        
        
            
        if VReal-Vsub[p][0]<0 and GReal-Gsub[p+1][0]<0:
            
            for i in range(0,len(Tcsub[p][:])):
                TInter=Tcsub[p][0]
#                Tcsub[p+1][i]=Tcsub[0][0]
#                Tcsub[-1][i]=Tcsub[-1][0]
#                print("a")
                
        elif VReal-Vsub[p][0]>0 and VReal-Vsub[p+1][0]>0:
            for i in range (0,len(Tcsub[p][:])):
                TInter=Tcsub[p][-1]
#                Tcsub[p+1][i]=Tcsub[0][0]
#                Tcsub[-1][i]=Tcsub[-1][0]
#                print("b")
        else: 
           
            if VReal-Vsub[p][0]>0 and VReal-Vsub[p+1][0] < 0: 
                
                TInter=Tcsub[p][0]- ((Vsub[p][0]-VReal)/(Vsub[p][0]-Vsub[p+1][0]))*(Tcsub[p][0]-Tcsub[p+1][0])
#                TInter=Tcsub[p][0]- ((Gsub[p][0]-GReal)/(Gsub[p][0]-Gsub[p+1][0]))*(Tcsub[p][0]-Tcsub[p+1][0])
#                TInterult=Tcsub[-1][0]- ((Gsub[-1][0]-TReal)/(Gsub[-1][0]-Gsub[-1][i+1]))*(Tcsub[-1][0]-Tcsub[-1][i+1])
#                print("c")
#                for j in range (0,len(Tcsub)):
#                    Tcsub[p][j]=TInter
##                    Tcsub[p+1][j]=TInter
#                    Tcsub[-1][j]=TInter
   
#    print(Tcsub)
                
    #print("Interpolacion en V:")
    return TInter


