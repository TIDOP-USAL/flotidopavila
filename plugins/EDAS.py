##############################################################################
# Nombre del archivo: EDAS.py
# Fecha última modificación: 08/11/2023
# Autor/es:
#   Néstor Velaz
# Pag 87 libro
###############################################################################

import numpy as np


def AverageSolution(X):
           
    NumAlternativas=X.shape[0]
    NumCriterios=X.shape[1]
    
    AV=np.zeros(NumCriterios) 
    
    SumaColumna=np.sum(X, axis=0) # 0 suma columnas; 1 suma filas    
        
    for j in range (0,NumCriterios):
            
        AV[j]=SumaColumna[j]/NumAlternativas

            
    return AV

def PositiveNegativeDistance(X,AV,signo):
    
    NumAlternativas=X.shape[0]
    NumCriterios=X.shape[1]
    
    PDA=np.zeros((NumAlternativas,NumCriterios))
    NDA=np.zeros((NumAlternativas,NumCriterios))
    
        
    for i in range(0,NumAlternativas):
        for j in range(0,NumCriterios):
            if signo[j]=='+':
                
                PDA[i][j]=max(0,X[i][j]-AV[j])/AV[j]
                NDA[i][j]=max(0,AV[j]-X[i][j])/AV[j]
            
            elif signo[j]=='-':
                 
                NDA[i][j]=max(0,X[i][j]-AV[j])/AV[j]
                PDA[i][j]=max(0,AV[j]-X[i][j])/AV[j]
    
    return PDA,NDA

def WeightedPDA_NDA(PDA,NDA,omega):
    
    NumAlternativas=PDA.shape[0]
    NumCriterios=PDA.shape[1]
    
    SP=np.zeros(NumAlternativas) 
    SN=np.zeros(NumAlternativas) 
    
    for i in range (0,NumAlternativas):  
        Aux_Positivo=0
        Aux_Negativo=0
        for j in range(0,NumCriterios):
            Aux_Positivo=Aux_Positivo+(PDA[i][j]*omega[j])
            Aux_Negativo=Aux_Negativo+(NDA[i][j]*omega[j])
                                             
        SP[i]=Aux_Positivo
        SN[i]=Aux_Negativo 
        
    return SP,SN

def WeightedNormalizedPDA_NDA(SP,SN):
    
    NumAlternativas=SP.size
    
    NSP=np.zeros(NumAlternativas)
    NSN=np.zeros(NumAlternativas)
    
    for i in range(0,NumAlternativas):
        NSP[i]=SP[i]/max(SP)
        NSN[i]=SN[i]/max(SN)
        
    return NSP,NSN
    

def AppraisalScore(NSP,NSN):

    NumAlternativas=NSP.size
    
    AS=np.zeros(NumAlternativas)
    
    for i in range(0,NumAlternativas):
        AS[i]=0.5*(NSP[i]+NSN[i])
    
    
        
    return AS

def FinalRankingAlternatives(AS):
    AS_tupla = list(enumerate(AS))
    AS_orden = sorted(AS_tupla, key=lambda x: x[1], reverse=True)

    valoresOrdenadosAS = []
    IndiceAS = []

    for index, value in AS_orden:
        IndiceAS.append(index)
        valoresOrdenadosAS.append(value)

    return IndiceAS, valoresOrdenadosAS


def edas(X,omega,signo):

################################################################################    
##    Ejemplo libro pag 151
    
#    X=np.array([[0.710, 4.100, 0.180, 0.720, 0.990, 0.250],
#                [1.330, 5.900, 0.740, 0.310, 0.420, 0.830],
#                [1.450, 4.900, 0.270, 0.650, 0.420, 0.440]])
#    
#    omega=np.array([0.171, 0.185, 0.177,0.225,0.157,0.085])
#    signo=['-','-','+','-','-','+']
###############################################################################      
  
    AV_j=AverageSolution(X)
    
    PDA,NDA=PositiveNegativeDistance(X,AV_j,signo)
        
    SP,SN=WeightedPDA_NDA(PDA,NDA,omega)
    
    NSP,NSN=WeightedNormalizedPDA_NDA(SP,SN)
        
    AS=AppraisalScore(NSP,NSN)
       
    Ranking,Value=FinalRankingAlternatives(AS)
            
    return Ranking,Value