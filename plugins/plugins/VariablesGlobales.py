VidaUtil=20 #Vida Util instalación [años]. Paper A. Manso-Burgos https://doi.org/10.1016/j.egyr.2022.08.181

d=0.07  #Tasa de descuento Paper A. Manso-Burgos https://doi.org/10.1016/j.egyr.2022.08.181
ielec=0 #tasa de inflacción electricidad Paper A. Manso-Burgos https://doi.org/10.1016/j.egyr.2022.08.181

#PrecioWp= 1.2 # Precio instalación completa por Wp instalado.€/Wp Dato inventado, pero por ahi debe andar 
PrecioWp= 620 # [€/kW]Paper de FLotante MLopz
CosteOM1=9.35 # [€/kW]Paper de FLotante MLopz

PrecioWp_Flotante=750 #[€/kWp] 20% ma que en tierra
PrecioWp_Tierra= 620   #[€/kWp]
#CosteOM= 0.02*PrecioWp #Precio operación y mantenimeinto €/Wp/año, se presupone que todos los años habra un coste en mantenimeinto

CosteOM_Tierra=0.015
CosteOM_Flotante=0.03




FactorRed=0.190 # tCO2/MWh Paper de FLotante MLopz
FactorPV=0.020  # tCO2/MWh # Manso Burgos Revisar este dato
    
PerdidaAnual=0.6 #[%/año] Perdida rendimiento anual panel. Fabricante