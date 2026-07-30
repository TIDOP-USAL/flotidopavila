##############################################################################
# Nombre del archivo: KeyPerformanceIndicators.py
# Fecha última modificación: 05/10/2023
# Autor/es:
#   Néstor Velaz
###############################################################################
# Proyecto: CTC Solar Flotante
###############################################################################
# Descripción:
# XXXXXXXXXXXXXXXXXXXXXXXX
###############################################################################
# Archivos relacionados:
# XXXXXXXXXXXXXXXXXXXXXXXX
###############################################################################
# Parametros de entrada
#   XXXXXXXXXXXXXXXXXXXXXXXXXX
###############################################################################
# Parámetros de salida
#   XXXXXXXXXXXXXX
###############################################################################
# Importación de librerías/módulos
# PANDAS: Extensión de Numpy para la manipulación y análisis de datos
# NUMPY: Librería basada en la implementación de métodos matemáticos
###############################################################################

import pandas as pd

import numpy as np

import plugins.plugins.VariablesGlobales as vg



def CapacityFactor(NumPaneles,EnergiaAnual,PotPico):
    
      
    Eideal=PotPico*10**-3*NumPaneles*8760 #MWh
    
    
    CF=EnergiaAnual/Eideal*100
    
    return CF

def Emisiones(EnergiaAnual): 
    
    Ered=EnergiaAnual*vg.FactorRed #tCO2
    EFlotante=EnergiaAnual*vg.FactorPV#tCO2
    
    EmisionesEvitadasAnual= Ered-EFlotante#tCO2
    EmisionesEvitadasVidaUtil=EmisionesEvitadasAnual*vg.VidaUtil#tCO2
    
        
    return EmisionesEvitadasAnual*10**-6, EmisionesEvitadasVidaUtil*10**-6 #MtCO2

def LCOE(EAnual,NumPaneles,PotPico,PrecioWp,p_Opex): #Eanual[MWh] PotPico [kWh]

    r=vg.d
    CAPEX=PotPico*NumPaneles*PrecioWp
    CRF=(r*(1+r)**vg.VidaUtil)/((1+r)**vg.VidaUtil-1)
    OPEX=p_Opex*CAPEX

    lcoe=(CAPEX*CRF+OPEX)/EAnual

    return lcoe #[€/MWh]

