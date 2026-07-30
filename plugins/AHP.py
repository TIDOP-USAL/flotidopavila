##############################################################################
# Nombre del archivo: AHP.py
# Fecha última modificación: 17/04/2024
# Autor/es:
#   Néstor Velaz
# https://victoryepes.blogs.upv.es/2018/11/27/proceso-analitico-jerarquico-ahp/
###############################################################################

import numpy as np


def ahp(M):
   
    inc_rat  = np.array([0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.48, 1.56, 1.57, 1.59, 1.59,1.59,1.59,1.59,1.59,1.59,1.59,])

    M_array = np.array(M)


    Pesos = np.zeros(M_array.shape[1])
   
    ValoresPropios, VectoresPropios = np.linalg.eig(M_array)
    
    ValoresPropios_real          = np.real(ValoresPropios)
    
    lamb_max_index            = np.argmax(ValoresPropios_real)
    
    lamb_max                  = ValoresPropios_real[lamb_max_index]
    
    principal_VectoresPropios     = np.real(VectoresPropios[:, lamb_max_index])
    
    Pesos= principal_VectoresPropios / principal_VectoresPropios.sum()
    
    cons_ind = (lamb_max - M_array.shape[1])/(M_array.shape[1] - 1)
    
    Rc = cons_ind/inc_rat[M_array.shape[1]]
    
    return Pesos, Rc

def NormalizedDecisionMatrix(X,signo):
    
       
    NumAlternativas=X.shape[0]
    NumCriterios=X.shape[1]
    
    r_asterisco=np.zeros((NumAlternativas,NumCriterios)) 
    
    SumaColumna=np.sum(X, axis=0) # 0 suma columnas; 1 suma filas
#    SumaColumna8=np.sum(X[:,8]) # 0 suma columnas; 1 suma filas
#    print(SumaColumna8) # 0 suma columnas; 1 suma filas)
#    print('X')
#    print(X[:,8])
    
    for i in range (0,NumAlternativas):
        
        for j in range (0,NumCriterios):
                
            r_asterisco[i][j]=X[i][j]/SumaColumna[j]
#    print(SumaColumna[8])
#    print('R')
#    print(r_asterisco[:][8])
    return r_asterisco


#Metodo que se llama WSP metodo suma ponderada
def WeightedNormalizedDecisionMatrix(X,omega):
    
#    NumAlternativas=X.shape[0]
#    NumCriterios=X.shape[1]
    
#    R=np.zeros((NumAlternativas,NumCriterios)) 
    
#    for i in range (0,NumAlternativas):  

    R=np.dot(X,omega) 
#    print(R.shape)  
    return R

def FinalRankingAlternatives(AS):
    
    ASlist=AS.tolist()
    
#    print(type(ASlist))
    
    AS_tupla = list(enumerate(ASlist))
    AS_orden = sorted(AS_tupla, key=lambda x: x[1], reverse=True)

    valoresOrdenadosAS = []
    IndiceAS = []

    for index, value in AS_orden:
        IndiceAS.append(index)
        valoresOrdenadosAS.append(value)

    return IndiceAS, valoresOrdenadosAS
