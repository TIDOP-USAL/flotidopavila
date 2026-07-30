##############################################################################
# Nombre del archivo: WASPAS.py
# Fecha última modificación: 08/11/2023
# Autor/es:
#   Néstor Velaz

# PAg 93 método 13 libro
###############################################################################

import numpy as np


def NormalizedDecisionMatrix(X,signo): 
    
    NumAlternativas=X.shape[0]
    NumCriterios=X.shape[1]
    
    r_asterisco=np.zeros((NumAlternativas,NumCriterios))
      
    
    Max=[]
    Min=[]
    for j in range(0,NumCriterios):
        
        Max.append(max(X[:,j]))
        Min.append(min(X[:,j]))
        

    for i in range (0,NumAlternativas):
        for j in range (0,NumCriterios):
          
            if signo[j]=='+':
                r_asterisco[i][j]=X[i][j]/Max[j]
            else:
                if X[i][j]==0:
                    r_asterisco[i][j]=0
                else:
                    r_asterisco[i][j]=Min[j]/X[i][j]
            
#    print(r_asterisco)
    return r_asterisco

def AdditiveRelativeImportance(r_asterisco,omega): 
    
    NumAlternativas=r_asterisco.shape[0]
    
    
    Q1=np.zeros(NumAlternativas)
    
    for i in range(0,NumAlternativas):
  
        Q1[i]=sum(r_asterisco[i,:]*omega)
    
    return Q1

def MultiplicativeRelativeImportance(r_asterisco,omega):
    NumAlternativas=r_asterisco.shape[0]
    NumCriterios=r_asterisco.shape[1]
    
    Q2=np.zeros(NumAlternativas)
    
    for i in range(0,NumAlternativas):
        a=[]
        for j in range (0,NumCriterios):
             a.append(r_asterisco[i,j]**omega[j])  
             
        Q2[i]=np.prod(a)
    
    return Q2

def JointGeneralizedCriterion(Q1,Q2,Lambda):
    
    NumAlternativas=Q1.size

    
    Q=np.zeros(NumAlternativas)
    
    for i in range(0,NumAlternativas):
  
        Q[i]=Lambda*Q1[i]+(1-Lambda)*Q2[i]
    
    
    return Q

def FinalRankingAlternatives(Q):
    Q_tupla = list(enumerate(Q))
    Q_orden = sorted(Q_tupla, key=lambda x: x[1], reverse=True)

    valoresOrdenadosQ = []
    IndiceQ = []

    for index, value in Q_orden:
        IndiceQ.append(index)
        valoresOrdenadosQ.append(value)

    return IndiceQ, valoresOrdenadosQ

def waspas(X,omega,signo):

###############################################################################    
##    Ejemplo libro pag 95
#    
#    X=np.array([[0.035,847,0.335,1.760,0.590],
#                [0.027, 834, 0.335, 1.680,0.665],
#                [0.037,808,0.590,2.400,0.500],
#                [0.028,821,0.50,1.590,0.410]])
#    
#    omega=np.array([0.331, 0.181, 0.369,0.072,0.047])
#    signo=['-','-','+','-','+']
###############################################################################    
    
    r_asterisco=NormalizedDecisionMatrix(X,signo)
    
  
    Q1=AdditiveRelativeImportance(r_asterisco,omega)

    Q2=MultiplicativeRelativeImportance(r_asterisco,omega)
     #Lambda sirve para dar mas peso al sumatorio o al productorio, dejamos por defecto 0.5 para que este equilibrado
    Q=JointGeneralizedCriterion(Q1,Q2,Lambda=0.5)
    
#    print(Q)
    
    Ranking,Value=FinalRankingAlternatives(Q)
    
    return Ranking,Value