##############################################################################
# Nombre del archivo: MABAC.py
# Fecha última modificación: 16/14/2024
# Autor/es:
#   Néstor Velaz
# Pag 193 libro
###############################################################################

import numpy as np


def NormalizedDecisionMatrix(X,signo):
    
       
    NumAlternativas=X.shape[0]
    NumCriterios=X.shape[1]
    
    r_asterisco=np.zeros((NumAlternativas,NumCriterios)) 
    
    for i in range (0,NumAlternativas):
           
        for j in range (0,NumCriterios):
            
            Max_i=max(X[:,j])
            Min_i=min(X[:,j])
            
            if signo[j]=='+':
                
                r_asterisco[i][j]=(X[i][j]-Min_i)/(Max_i-Min_i)
           
            elif signo[j]=='-':
                 
                r_asterisco[i][j]=(X[i][j]-Max_i)/(Min_i-Max_i)
            
    return r_asterisco

def WeightedNormalizedDecisionMatrix(r_asterisco,omega):
    
    NumAlternativas=r_asterisco.shape[0]
    NumCriterios=r_asterisco.shape[1]
    
    r_virgulilla=np.zeros((NumAlternativas,NumCriterios)) 
    
    for i in range (0,NumAlternativas): 
        for j in range(0,NumCriterios):
                                             
            r_virgulilla[i][j]=omega[j]+r_asterisco[i][j]*omega[j] 
        
    return r_virgulilla

def BorderApproximationArea(r_virgulilla):
    
    NumAlternativas=r_virgulilla.shape[0]
    NumCriterios=r_virgulilla.shape[1]
    
    g=np.zeros(NumCriterios)
    
    for j in range(0,NumCriterios):
        productorio=1
        for i in range(0,NumAlternativas):
        
            productorio=productorio*r_virgulilla[i][j]
                 
        
        g[j]=productorio**(1/NumAlternativas)
    
    return g

def DistanceBorder(r_virgulilla,g):
   
    NumAlternativas=r_virgulilla.shape[0]
    NumCriterios=r_virgulilla.shape[1]
    
    q=np.zeros((NumAlternativas,NumCriterios))
    
    for i in range (0,NumAlternativas):
        for j in range(0,NumCriterios):
            
            q[i][j]=r_virgulilla[i][j]-g[j]
    
    return q

def TotalDistanceBorder(q):
       
    S=np.sum(q,axis=1)
       
    return S

def FinalRankingAlternatives(S):
    S_tupla = list(enumerate(S))
    S_orden = sorted(S_tupla, key=lambda x: x[1], reverse=True)

    valoresOrdenadosS = []
    IndiceS = []

    for index, value in S_orden:
        IndiceS.append(index)
        valoresOrdenadosS.append(value)

    return IndiceS, valoresOrdenadosS


def mabac(X,omega,signo):

################################################################################ 
#
#    ##    Ejemplo libro pag 195
#    
#    X=np.array([[5, 54, 600, 80],
#                [1, 97, 200, 65],
#                [7, 72, 400, 83],
#                [10,75, 1000, 40]])
#    
#    omega=np.array([0.25, 0.25, 0.25,0.25])
#    signo=['-','-','+','+']
###############################################################################      
  
    r_asterisco=NormalizedDecisionMatrix(X,signo)
      
    r_virgulilla=WeightedNormalizedDecisionMatrix(r_asterisco,omega)
    
    g=BorderApproximationArea(r_virgulilla)
    
    q=DistanceBorder(r_virgulilla,g)
      
    S=TotalDistanceBorder(q)
          
    Ranking,Value=FinalRankingAlternatives(S)
                
    return Ranking,Value
