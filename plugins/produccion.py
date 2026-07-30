import os
import time
from typing import Any

from plugins.plugins.Tarifa_entsoe import callentsoe
from plugins.plugins.Generacion_solar import callPVGIS, NumMaxPaneles, calcProduccionAnual, Inclinationcorrection, \
    calcProduccionAnualSimplified

from plugins.plugins.Curvas import PerformancePanel
from plugins.plugins.AnalisisEconomico import Ingreso, Beneficio
from plugins.plugins.Rentabilidad import NPV, PeriodoRetornoSimple,TIR
import plugins.plugins.VariablesGlobales as vg
import json

import pandas as pd
import plugins.plugins.SistemaRefrigeracion as rf
import numpy as np
import plugins.plugins.KeyPerformanceIndicators as kpi

#from plugins.MCDM.COPRAS import copras

#from plugins.MCDM.WASPAS import waspas
#from plugins import ExportarMCDM as ex
#import plugins.OptimizadorGA as ga


def makeCalcs(data,ModeloSolar,BotonCalculo, tafEnergy):
    
    country_code='ES' #Variable global por defecto
   
###############################################################################
#  PASO 1: Extraer todos los datos que vienen del gis en un diccioanrio
###############################################################################  
       
    Latitud = data['latitud']   #[º]
    Longitud = data['longitud'] #[º] 
    SupFVMax = float(data['area'] )    #[m2]
    
    LongitudPanel =float( data['panel']['Long Side'])  # [m]
    AnchoPanel = float(data['panel']['Short Side'])   # [m]
#    EspesorPanel = float(panel["Espesor"])     # [m]
    PotPico = float(data['panel']['Pmax'])/1000              # [kW]
    
    #print(PotPico)
  
    SupPaneles = LongitudPanel * AnchoPanel
    
    Inclinacion=float(data['inclinacion'])
    Orientacion=float(data['orientacion'])
    
    FechaInicio=data['fechaInicio']
    Fechafinal=data['fechaFin']
    
    TONC=float(data['panel']['NOCT'])

    
    NumPaneles=float(data['numPaneles'])
    
    HoraDelAnio = int(data['horaDelAnio'])
#######################################################################################
    # PASO 2. OBTENEMOS EL NUMERO DE PANELES
#####################################################################################
#   Si  quiere que se le calcule numPaneles debería ser -1
    if NumPaneles==-1:
         NumPaneles = NumMaxPaneles(Latitud, Inclinacion, LongitudPanel, AnchoPanel, SupFVMax)


        
    else:
        NumPanelesMax = NumMaxPaneles(Latitud, Inclinacion, LongitudPanel, AnchoPanel, SupFVMax)
        if NumPaneles<=NumPanelesMax:
            NumPaneles=NumPaneles
        else:
            NumPaneles =NumPanelesMax
            print('El numero de paneles introducido supera al máximo permitido')

    #print('Numero Paneles ', NumPaneles)

####################################################################################
    # PASO 3. LLAMAMOS A PVGIS 
#######################################################################################
    datosolar = callPVGIS(Latitud, Longitud)

####################################################################################
    # PASO 4. CORREGIMOS IRRADIANCIA
#######################################################################################  

    BIPV= (data['panel']['BIPV'])
    Irradiancia=Inclinationcorrection(datosolar, Inclinacion, Orientacion, Latitud, Longitud, FechaInicio, Fechafinal,BIPV)





####################################################################################
    # PASO 5. CALCULO DE PRODUCCION
###################################################################################

    # Calculo de la temperatura con sistema de refrigeracion

    TemperaturaRef=rf.Refrigeracion(Irradiancia) 
    Temperatura=rf.SinRefrigeracion(Irradiancia,TONC)
    
#    print(TemperaturaRef)
    if ModeloSolar=='Modelo_Diodo_Simple':
        # Dentro de la funcion calcProduccionAnual hay que llamar a los datos de los paneles del SIG
        EnergiaAnual = calcProduccionAnual(Temperatura, Irradiancia, NumPaneles,data)
        EnergiaAnualRef = calcProduccionAnual(TemperaturaRef, Irradiancia, NumPaneles,data)
    elif ModeloSolar=='Modelo_energetico':
        EnergiaAnual = calcProduccionAnualSimplified(Temperatura, Irradiancia, NumPaneles, data)
        EnergiaAnualRef = calcProduccionAnualSimplified(TemperaturaRef, Irradiancia, NumPaneles, data)
   
    #print ("EnergiaAnualRef",EnergiaAnualRef.shape[0])
    
    results={}
    results['energiaAnual'] = EnergiaAnual
    results['energiaAnualRef'] = EnergiaAnualRef

    #print('Energia Tierra: ', EnergiaAnual)
    #print('\nEnergia Flotante: ', EnergiaAnualRef)



###################################################################################
    # PASO 6. CURVAS I-V e P-V PANEL Esto es para pintarlo en el GIS !!!!!!!!! MEJOR SACARLO??????????
#####################################################################################

    #El GIS de alguna manera debe de fijar la hora que determina una irradicancia y temepratura concreta

    Irradiancia=Irradiancia.reset_index()
    Fecha = Irradiancia['index'] [HoraDelAnio]
    #print ('Fecha Seleccionada: ', Fecha)
    IrradianciaPantalla = Irradiancia['poa_global'][HoraDelAnio]
    TemperaturaPantalla = Temperatura[HoraDelAnio]
    TemperaturaRefPantalla = TemperaturaRef[HoraDelAnio]

    #dos Graficos con los resultados  VP y VI
    V, I, P = PerformancePanel(Irradiancia['poa_global'][HoraDelAnio], Temperatura[HoraDelAnio],data)
    results['v'] = V
    results['i'] = I
    results['p'] = P

    V_Ref, I_Ref, P_Ref = PerformancePanel(Irradiancia['poa_global'][HoraDelAnio], TemperaturaRef[HoraDelAnio],data)
    results['vRef'] = V_Ref
    results['iRef'] = I_Ref
    results['pRef'] = P_Ref

    '''plt.figure()
    plt.plot(V, I, label=f'I-V T={TemperaturaPantalla:.2f}°C')
    plt.plot(V_Ref, I_Ref, label=f'I-V Tref={TemperaturaRefPantalla :.2f}°C', linestyle='--')
    plt.xlabel("Voltaje (V)")
    plt.ylabel("Corriente (A)")
    plt.title(f"Curvas I-V\n{Fecha} | G={IrradianciaPantalla:.1f} W/m²")
    
    plt.ylim(min(I.min(), I_Ref.min())*1.1, max(I.max(), I_Ref.max())*1.1)
    plt.xlim(0, max(V)*1.05)
    
    plt.grid(True)
    plt.legend()
    plt.tight_layout()'''
    # plt.show()

#######################################################################################
    # PASO 7: CARGAMOS  LA TARIFA DEL POOL DESDE ENTSOE
#######################################################################################
    if tafEnergy is None:
        TafEnergy = cargar_tarifa_entsoe(FechaInicio, Fechafinal, country_code)
    else:
        TafEnergy = tafEnergy

    ######################################################################################
    # PASO 8. RENTABILIDAD ENTRE SISTEMA FLOTANTE SIN Y CON SISTEMA DE REFRIGERACION
#####################################################################################
    Ingreso0 = Ingreso(EnergiaAnual, TafEnergy)
    IngresoFlotante = Ingreso(EnergiaAnualRef, TafEnergy)

    #print('Ingreso en Tierra: ', Ingreso0)
    #print('Ingreso en Flotante: ', IngresoFlotante)

    AumentoT, AumentoIngreso = Beneficio(Ingreso0, IngresoFlotante)

    results['ingreso0'] = Ingreso0
    results['ingresoFlotante'] = IngresoFlotante
 
    results['aumentoT'] = AumentoT*10**-6
  

    results['ingresoAnual[M€/año]'] = str(round(sum(Ingreso0) * 10 ** -6, 2))  # Escalar
    results['ingresoAnualRefrigerado[M€/año]'] = str(round(sum(IngresoFlotante) * 10 ** -6, 2)) # Escalar


    results['aumentoIngresoAnualRefrigerar[M€/año]'] = str(round(AumentoT * 10 ** -6, 2))  # Escalar
    results['aumentoIngresoAnualRefrigerar[%]'] = str(round(AumentoT / sum(Ingreso0) * 100, 2))  # Escalar
   


    #Grafico VAN
    VAN, NPVAhorro, NPVInversion, NPVOM, INVTotal = NPV(AumentoT, PotPico, SupPaneles, NumPaneles)
    results['VAN'] = VAN
    PR = PeriodoRetornoSimple(VAN)
    TIR_ = TIR(VAN)

    results['PR'] = PR
    results['TIR'] = TIR_
    #results['variacion'] = varitaion(Longitud, Latitud)
    #results['variacion'] = varitaion(data['denominacion'])

    results['inversionTotal[M€]']= str(round(INVTotal, 2))



    '''Mostrar todo, son valores'''

    # CAPACITY FACTOR [Escalar]
    CF = kpi.CapacityFactor(NumPaneles, sum(EnergiaAnual) * 10 ** -3, PotPico)
    CFRef = kpi.CapacityFactor(NumPaneles, sum(EnergiaAnualRef) * 10 ** -3, PotPico)

    #print('EnergiaAnual: ', sum(EnergiaAnual))
    #print('EnergiaAnual: ', sum(EnergiaAnualRef))

    results['CF[%]'] = str(round(CF, 2))
    results['CFRef[%]'] = str(round(CFRef, 2))

    #print('CF[%]. En Tierra', str(round(CF, 2)))
    #print('CFRef[%]. Flotante', str(round(CFRef, 2)))

    # EMISIONES EmisionesEvitadasAnual [8760 valores] y EmisionesEvitadasVidaUtil [Escalar]
    EmisionesEvitadasAnual, EmisionesEvitadasVidaUtil = kpi.Emisiones(sum(EnergiaAnual))
    EmisionesEvitadasAnualRef, EmisionesEvitadasVidaUtilRef = kpi.Emisiones(sum(EnergiaAnualRef))


    results['emisionesEvitadasVidaUtil[MtCO2]'] = str(round(EmisionesEvitadasVidaUtil, 2))
    results['emisionesEvitadasVidaUtilRef[MtCO2]'] = str(round(EmisionesEvitadasVidaUtilRef, 2))

    results['vidaUtil[años]'] = str(vg.VidaUtil)
    results['emisionesEvitadasAnual[MtCO2]'] = str(round(EmisionesEvitadasAnual, 2))
    results['emisionesEvitadasAnualRef[MtCO2]'] = str(round(EmisionesEvitadasAnualRef, 2))

    #print('emisiones: ', results['emisionesEvitadasAnualRef[MtCO2]'])

    # LCOE [Escalar]
    lcoe = kpi.LCOE(sum(EnergiaAnual) * 10 ** -3, NumPaneles, PotPico,vg.PrecioWp_Tierra,vg.CosteOM_Tierra)
    lcoeRef = kpi.LCOE(sum(EnergiaAnualRef) * 10 ** -3, NumPaneles, PotPico,vg.PrecioWp_Flotante,vg.CosteOM_Flotante)

    #print('LCOE[€/MWh]. En Tierra', round(lcoe, 2))
    #print('LCOE[€/MWh]. Flotante', round(lcoeRef, 2))

    results['LCOE[€/MWh]'] = str(round(lcoe, 2))
    results['LCOERef[€/MWh]'] = str(round(lcoeRef, 2))


    return results

###Saco la funcion cargar_tarifa_entsoe de la funcion makeCals para que se pueda llamar desde el metodo multicriterio una sola vez
def cargar_tarifa_entsoe(FechaInicio, Fechafinal, country_code):

    tz = "Europe/Brussels"

    # --- Rangos en hora local (para recortar por día civil) ---
    start_local = pd.to_datetime(FechaInicio, format="%d/%m/%Y").tz_localize(tz)
    end_local_exclusive = pd.to_datetime(Fechafinal, format="%d/%m/%Y").tz_localize(tz) + pd.Timedelta(days=1)
    end_local_inclusive = end_local_exclusive - pd.Timedelta(hours=1)

    # --- Convertir a UTC solo para la consulta a ENTSO-E ---
    start_utc = start_local.tz_convert("UTC")
    end_utc_exclusive = end_local_exclusive.tz_convert("UTC")

    # --- Llamada ENTSO-E ---
    TafEnergy = callentsoe(country_code, start_utc, end_utc_exclusive)  # €/MWh

    # Asegurar tz-aware en UTC si viniera naive
    if TafEnergy.index.tz is None:
        TafEnergy.index = TafEnergy.index.tz_localize("UTC")
    else:
        TafEnergy = TafEnergy.tz_convert("UTC")

    # --- Consolidar duplicados en UTC (por si acaso) ---
    TafEnergy = TafEnergy.groupby(TafEnergy.index).mean()

    # --- AQUÍ ESTÁ LA CLAVE: reindexar en UTC (sin DST) y rellenar huecos con el valor anterior ---
    full_utc = pd.date_range(
        start=start_utc,
        end=end_utc_exclusive - pd.Timedelta(hours=1),
        freq="h",
        tz="UTC"
    )
    TafEnergy = TafEnergy.reindex(full_utc).ffill()

    # --- Volver a hora local y recortar por rango local real ---
    TafEnergy = TafEnergy.tz_convert(tz)
    TafEnergy = TafEnergy.loc[start_local:end_local_inclusive]

    # --- Si en otoño aparece hora repetida al volver a local, consolidar ---
    TafEnergy = TafEnergy.groupby(TafEnergy.index).mean()

    # --- Convertir de €/MWh a €/kWh ---
    TafEnergy = TafEnergy / 1000.0
    TafEnergy.to_csv("Tafprueba.csv", header=True)
    # print('La tarifa de mercado es: ', TafEnergy)
    return TafEnergy


###############################################################################
# KEY PERFORMANCE INDICATOR
###############################################################################
# EMISIONES

# LCOE
# CAPACITY FACTOR
################################################################################
# EXPORTAR RESULTADOS
##############################################################################



def varitaionCoord(coordX, coordY):

        with open('static/datos/provincias.geojson', 'r') as archivo_json:
            # Carga el contenido del archivo JSON en una estructura de datos de Python
            data = json.load(archivo_json)

        features = data['features']

        # Punto de ejemplo (longitud, latitud)
        punto_embalse = Point(coordX, coordY)

        # Verificar la pertenencia del punto a las provincias
        for feature in features:
            geometry = shape(feature["geometry"])
            if geometry.contains(punto_embalse):
                if geometry.contains(punto_embalse):
                    return feature["properties"]["Variacion"]
        return -10

def varitaion(denominacion):

        nameFileDistances = "static/datos/distanciasVariaciones.csv"
        fileDistance = pd.read_csv(nameFileDistances, delimiter=';', index_col=False)
        nombre = fileDistance['nombre']
        variacion = fileDistance['variacion']

        for i in range(0, nombre.size):
            if nombre[i] == denominacion:
                return variacion[i]
        return 0


def cal_Produccion(dataGIS, tafEnergy=None):
        t0=time.time()

        '''dataGIS={'fechaInicio': '01/01/2025', 'fechaFin': '31/12/2025',
                 'numPaneles': '200', 'orientacion': '0', 'inclinacion': '25',
                 'panel': {'A_c': '0.662', 'BIPV': 'Y', 'ISC_Rear': '1.53', 'Ipmax': '10.5', 'Isc': '10.88', 
                           'Long Side': '2.172', 'Manufacturer': 'LG Electronics Inc.', 'Model Number': 'Bi_LG425N2T-E6', 
                           'NOCT': '42', 'N_p': '1', 'N_s': '144', 'PTC': '425',
                           'Pmax': '425', 'Prear_max': '60', 'Short Side': '1.12', 
                           'Tc_isc': '0.04', 'Tc_pmax': '-0.33', 'Tc_voc': '-0.26', 
                           'Technology': 'Mono-c-Si', 'Voc': '48.8', 'Vpmax': '48'}, 
                'longitud': -15.669878005190753, 'latitud': 28.048463391498103, 
                'area': 1246.98}'''

        #ModeloSolar='Modelo_Diodo_Simple' # 'Modelo_energetico' #Tiene que venir del GIS Podemos comparar a ver si aporta algo el Diodo simple con MPPT
        ModeloSolar = dataGIS['modeloSeleccionado']#'Modelo_energetico'

        #BotonCalculo='UserDefined' #'Dimensionado' Si es Dimensionado calcula el maximo numero de paneles, sino calculo la energia con los paneles que se metan
        if dataGIS['numPaneles'] == -1:
            BotonCalculo = 'Dimensionado'
        else:
            BotonCalculo = 'UserDefined'

        '''if BotonCalculo=='Dimensionado': #OJO cuando se llame a la función de multicriterio o de dimensionado NumPaneles debe ser -1
            dataGIS['numPaneles']=-1
        else:
            dataGIS['numPaneles'] = dataGIS['numPaneles']'''

        resultsEmbalse= makeCalcs(dataGIS,ModeloSolar,BotonCalculo, tafEnergy)
        t1=time.time()
        resultsEmbalse["fechaInicio"]=dataGIS['fechaInicio']
        resultsEmbalse["fechaFin"]=dataGIS['fechaFin']
        #print("resultados Embalse: ", resultsEmbalse)
        print('El tiempo que tarda en correr es [min]: ', round((t1-t0)/60,2))
        return resultsEmbalse
        
        