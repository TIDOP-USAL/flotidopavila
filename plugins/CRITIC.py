##############################################################################
# Nombre del archivo: CRITIC.py
# Fecha última modificación: 16/14/2024
# Autor/es:
#   Néstor Velaz
# Pag 199 libro
###############################################################################

import numpy as np
import math
import pandas as pd
import os


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

def CorrelationCoefficient(r_asterisco):
    
    #Se ha tenido que ir haciendo los bucles por separado generando matrices intermedias 
    # que contengan los terminos que necesita la ecuacion 26.4 de la pagina 200 del libro
    
    NumAlternativas=r_asterisco.shape[0]
    NumCriterios=r_asterisco.shape[1]
    
    #MEDIA
    
    x_j=np.zeros(NumCriterios)
    x_k=np.zeros(NumCriterios)
    
    for j in range(0,NumCriterios):
        k=j
        x_j[j]=(1/NumCriterios)*np.sum(r_asterisco[:,j])
        x_k[k]=(1/NumCriterios)*np.sum(r_asterisco[:,k])
  
    #RADICANDOS
    Radicando1=np.zeros(NumCriterios)
    Radicando2=np.zeros(NumCriterios)
    
    for j in range (0,NumCriterios):
        Aux=0
        for i in range(0,NumAlternativas):
           Aux=Aux+(r_asterisco[i][j]-x_j[j])**2 
        
        Radicando1[j]=Aux
        
    for k in range (0,NumCriterios):
        Aux=0
        for i in range(0,NumAlternativas):
           Aux=Aux+(r_asterisco[i][k]-x_j[k])**2 
        
        Radicando2[k]=Aux
    
    #PRODUCTOS NUMERADOR
    Producto1=np.zeros((NumAlternativas,NumCriterios))
    Producto2=np.zeros((NumAlternativas,NumCriterios))
    
    
    for j in range(0,NumCriterios):
        
        for i in range(0,NumAlternativas):
            
            Producto1[i][j]=r_asterisco[i][j]-x_j[j]
            
    for k in range(0,NumCriterios):
        
        for i in range(0,NumAlternativas):
            
            Producto2[i][k]=r_asterisco[i][k]-x_j[k]
       
    #NUMERADOR    
    Numerador=np.zeros((NumAlternativas,NumCriterios))
    
    for j in range (0,NumCriterios):
        
        for k in range(0,NumCriterios):
            Aux=0
            for i in range(0,NumAlternativas):
                Aux=Aux+Producto1[i][j]*Producto2[i][k]   
                
            Numerador[j][k]=Aux    
    
    #CALCULO CORRELACION FINAL
    
    rho_jk=np.zeros((NumAlternativas,NumCriterios)) 
    for j in range (0,NumCriterios):
        Aux=0
        for k in range(0,NumCriterios):
            
            Aux=Numerador[j][k]/math.sqrt(Radicando1[j]*Radicando2[k])
            
            rho_jk[j][k]=Aux
   
    return rho_jk 

def StandardDeviation(r_asterisco):
    
    NumAlternativas=r_asterisco.shape[0]
    NumCriterios=r_asterisco.shape[1]
    
    x_j=np.zeros(NumCriterios)
    sigma=np.zeros(NumCriterios)
    
    for j in range(0,NumCriterios):
      
        x_j[j]=(1/NumCriterios)*np.sum(r_asterisco[:,j]) #media

    for j in range(0,NumCriterios):
        Aux=0
        for i in range(0,NumAlternativas):
            Aux=Aux+(r_asterisco[i][j]-x_j[j])**2
            
        sigma[j]=math.sqrt(1/(NumCriterios-1)*Aux)
    
    return sigma

        
def IndexC(sigma,rho):
    
    NumCriterios=sigma.size
    
    C=np.zeros(NumCriterios)
    
    for j in range(0,NumCriterios):
        Aux=0
        for k in range(0,NumCriterios):
            Aux=Aux+(1-rho[j][k])    
        
        C[j]=sigma[j]*Aux

    return C    

def WeightAttributes(C):
    
    NumCriterios=C.size
    Pesos=np.zeros(NumCriterios)
    
    for j in range (0,NumCriterios):
        Pesos[j]=C[j]/np.sum(C)
        
    
    return Pesos

def WeightedNormalizedDecisionMatrix(X,omega):
    

                                             
    R=np.dot(X,omega) 
 
    return R

def FinalRankingAlternatives(S):
    S_tupla = list(enumerate(S))
    S_orden = sorted(S_tupla, key=lambda x: x[1], reverse=True)

    valoresOrdenadosS = []
    IndiceS = []

    for index, value in S_orden:
        IndiceS.append(index)
        valoresOrdenadosS.append(value)

    return IndiceS, valoresOrdenadosS


def critic(X,omega,signo):
    
#    OJO Este metodo lo que calcula son los pesos y ordena las variables  
#    si tienen más o menos peso, por lo que realmente omega no es necesario
#    se mantinene como variable de entrada para mantener la uniformidad con
#    el resto de metodos, pero luego no se usará

################################################################################ 
#
#    ##    Ejemplo libro pag 201
#    
#    X=np.array([[30, 0.100, 1, 20],
#                [100, 0.700, 1, 40],
#                [50, 1, 2, 10],
#                [300,2, 3, 35]])
#    
#    omega=np.array([0.25, 0.25, 0.25,0.25])
#    signo=['-','-','+','-']
###############################################################################      
  
    r_asterisco=NormalizedDecisionMatrix(X,signo)
    
    rho=CorrelationCoefficient(r_asterisco)

    sigma=StandardDeviation(r_asterisco)
    
    C=IndexC(sigma,rho)
    
    Pesos=WeightAttributes(C)
    
     #exportar hof!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print (Pesos)

    return Pesos
    #R=WeightedNormalizedDecisionMatrix(r_asterisco,Pesos)
            
    #Ranking,Value=FinalRankingAlternatives(R)
    
         
    #return Ranking,Value
