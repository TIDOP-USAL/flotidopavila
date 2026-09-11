import time
import os
import pandas as pd
import csv
import math
import json
import numpy as np
import geopandas as gpd
from flask import jsonify
from scipy.spatial import cKDTree
#import rasterio
#from rasterio.transform import from_origin
#from PIL import Image
#import matplotlib.pyplot as plt

from plugins.COPRAS import copras
from plugins.WASPAS import waspas
from plugins.EDAS import edas
from plugins.MABAC import mabac
from plugins.CRITIC import critic
from plugins.AHP import ahp, WeightedNormalizedDecisionMatrix,FinalRankingAlternatives,NormalizedDecisionMatrix
from plugins.plugins.Generacion_solar import callPVGIS
from plugins.produccion import cal_Produccion_multicriterio
from plugins.produccion import cargar_tarifa_entsoe
from extensions import db,app
from admin.modelAnalisis import Analisis
def matrizX(criterios, omegaC, Signo, cuenca, paneles, datos_entsoe, ruta, sufijoNombre):
    '''
    Genera una matriz X a partir de los datos que se leen de csv obtenidos del SIG
    :param criterios: array que indica si se debe on incluir dicho criterio en la matriz x
    :return: matriz X con los valores de los criterios que se han includio
    '''


    PathBase =os.path.dirname(os.path.abspath(__file__))
    Path = os.path.join(PathBase, 'BaseDeDatos', 'datosUnidos.csv')

    matrizX = []
    datos = pd.read_csv(Path, delimiter=';', index_col=False, encoding='latin-1')
    valueSign=[]
    omega = []
    borrados = []
    if cuenca != 'Todas':
        datos = datos.loc[datos['Cuenca'] == cuenca]
    #print("***********datos***********", datos)
    if criterios[0] == 'Si' or criterios[1] == 'Si' or criterios[2] == 'Si':
        LCOE,Emisiones,CF, Energia = calcularLCOEyEmisionesyCF(paneles, datos.index, datos_entsoe)
        datos["Energia"] = Energia
    if criterios[0] == 'Si':
        datos['CF'] = CF
        matrizX.append(datos['CF'])
        valueSign.append(Signo[0])
        omega.append(omegaC[0])

    if criterios[1] == 'Si':
        matrizX.append(datos['Variacion'].abs())
        valueSign.append(Signo[1])
        omega.append(omegaC[1])
        borrados.append(0)

    if criterios[2] == 'Si':
        matrizX.append(datos['Rosa'])
        valueSign.append(Signo[2])
        omega.append(omegaC[2])
        borrados.append(0)

    if criterios[3] == 'Si':
        datos['LCOE'] = LCOE
        matrizX.append(datos['LCOE'])
        valueSign.append(Signo[3])
        omega.append(omegaC[3])

    if criterios[4] == 'Si':
        matrizX.append(datos['Distancia'])
        valueSign.append(Signo[4])
        omega.append(omegaC[4])
        borrados.append(0)

    if criterios[5] == 'Si':
        datos['Emisiones']  =Emisiones
        matrizX.append(datos['Emisiones'])
        valueSign.append(Signo[5])
        omega.append(omegaC[5])

    if criterios[6] == 'Si':
        matrizX.append(datos['EC'])
        valueSign.append(Signo[6])
        omega.append(omegaC[6])
        borrados.append(0)

    if criterios[7] == 'Si':
        matrizX.append(datos['Regadios'])
        valueSign.append(Signo[7])
        omega.append(omegaC[7])
        borrados.append(0)

    Path = os.path.join(ruta, sufijoNombre+'datosUnidos.csv')
    datos.to_csv(Path, index=False)

    matrizX = pd.concat(matrizX, axis=1).to_numpy()

    return datos['Pos'].to_numpy(), datos['Longitud'].to_numpy(), datos['Latitud'].to_numpy(), matrizX, valueSign, omega

def calcularLCOEyEmisionesyCF(paneles, posiciones, datos_entsoe):
    #TafEnergy = cargar_tarifa_entsoe(datos_entsoe["fecha_inicio"], datos_entsoe["fecha_fin"], datos_entsoe["country_code"])
    PathBase = os.path.dirname(os.path.abspath(__file__))
    Path = os.path.join(PathBase, '..','static','datos','union.geojson')
    embalses = gpd.read_file(Path)
    LCOE = []
    Emisiones = []
    CF = []
    Energia = []
    embalse = embalses.iloc[posiciones[0]]
    geometry = embalse['geometry'].centroid
    Latitud = geometry.y
    Longitud = geometry.x
    datoSolar = callPVGIS(Latitud, Longitud)
    for posicion in posiciones:
    #for index, embalse in embalses.iterrows():
        embalse = embalses.iloc[posicion]
        geometry = embalse['geometry'].centroid
        paneles['area'] = embalse['area']  # *area embalse
        paneles['longitud'] = geometry.x
        paneles['latitud'] = geometry.y
        resultado = cal_Produccion_multicriterio(paneles,datoSolar)
        LCOE.append(float(resultado["LCOERef[€/MWh]"]))
        Emisiones.append(float(resultado["emisionesEvitadasAnual[MtCO2]"]))
        CF.append(float(resultado["CFRef[%]"]))
        Energia.append(sum(resultado["energiaAnualRef"]))
    return pd.Series(LCOE, index=posiciones),  pd.Series(Emisiones, index=posiciones),  pd.Series(CF, index=posiciones),  pd.Series(Energia, index=posiciones)



def mainMCDM(X, omega, signo, Metodo):
    ###############################################################################
    # CARGAR PARAMETROS QUE VIENEN DEL SIG
    ###############################################################################

    print("************************")
    print(Metodo)

    if Metodo == "copras":
        Ranking, Value = copras(X, omega, signo)
    elif Metodo == "waspas":
        Ranking, Value = waspas(X, omega, signo)
    elif Metodo == "edas":
        Ranking, Value = edas(X, omega, signo)
    elif Metodo == "mabac":
        Ranking, Value = mabac(X, omega, signo)
    elif Metodo == "WSP":
        r_asterisco = NormalizedDecisionMatrix(X, signo)
        R=WeightedNormalizedDecisionMatrix(r_asterisco,omega)
        Ranking,Value=FinalRankingAlternatives(R)

    return  Ranking, Value

'''Funcion para generar un geojson con los resultados del metodo multicriterio, se recibe el id, longitud, latitud, ranking, valores, cuenca, 
metodo y ponderacion para generar el geojson con las propiedades necesarias para mostrar los resultados en la vista'''

def generateGeoJsonyCSV(id, longitude, latitude, ranking, values, ruta, sufijoNombre):
    features = []
    '''print("longitud values**************",len(values))
    print(ranking)
    print("longitud longitude*******",len(longitude))
    print(longitude)
    print(latitude)'''

    PathGeojson = os.path.join(ruta, sufijoNombre+'Resultados.geojson')
    nameFileResult = os.path.join(ruta, sufijoNombre+'Resultados.csv')
    fileReuslt = open(nameFileResult, "w")
    fileReuslt.write('Id;Ranking;Value\n')
    for i in range(len(ranking)):
        parte = (len(ranking)) / 4
        if i == 0:
            orden = 0
        elif i < parte + 1:
            orden = 1
        elif i < (parte * 2) + 1:
            orden = 2
        elif i < (parte * 3) + 1:
            orden = 3
        else:
            orden = 4

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude[ranking[i]], latitude[ranking[i]]]
            },
            "properties": {
                "id": str(id[ranking[i]]),
                "orden": orden,
                "value": values[i],
                "ranking": ranking[i]
            }
        }
        features.append(feature)
        fileReuslt.write(str(id[ranking[i]]) + ';')
        fileReuslt.write(str(ranking[i]) + ';')
        fileReuslt.write(str(values[i]) + '\n')
    fileReuslt.close()

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(PathGeojson, 'w') as f:
        json.dump(geojson, f, indent=4)
    return geojson, nameFileResult



def mainAHP(MatrizCopareada):

    M=MatrizM(MatrizCopareada)

    PesosMatrices=[]
    RC=[]
    PesosCalculados=[]


    for i in range (0,len(M)):
        PesosInter,RCInter=ahp(M[i])

        PesosMatrices.append(PesosInter)
        RC.append(RCInter)
    PesosCalculados.append(PesosMatrices[0])
    Omega=[]
    for i in range(0,len(PesosCalculados)):
        for j in range(0,len(PesosCalculados[i])):
            Omega.append(PesosCalculados[i][j])


    #Xnorm=NormalizedDecisionMatrix(X,signo)

    #R=WeightedNormalizedDecisionMatrix(Xnorm,Omega)

#    print(len(R))

    #Ranking,Value=FinalRankingAlternatives(R)

    #return longitude, latitude, Ranking,Value,RC
    return Omega

def MatrizM(MatrizCopareada):

    M1=[] #
    M2=[] #
    M3=[] #
    M4=[] #
    M5=[] #
    M6 = []
    M7 = []


    MIntermedia=[M1,M2, M3, M4, M5, M6, M7]

    M=[]
###############################################################################
# CRITERIOS

    for i in range (0,len(MatrizCopareada['Criterios'])):
        M_fila=[]
        for j in range(0,len(MatrizCopareada['Criterios'][i])):

            if MatrizCopareada['Criterios'][i][j]==-1:
                pass
            else:

                M_fila.append(MatrizCopareada['Criterios'][i][j])

        if M_fila==[]:
            pass
        else:
            M1.append(M_fila)

###############################################################################•

    for i in range(0, len(MIntermedia)):
        if MIntermedia[i]==[]:
            pass
        else:
            M.append(MIntermedia[i])


    #print("Matriz M",M)

    return M


def calsEmbalses(datos, analisis_id, fecha_creacion, ruta):

    db.session.remove()
    db.session.configure(bind=db.engine)
    AnalisisGuardado = db.session.query(Analisis).get(analisis_id)
    AnalisisGuardado.estado = "Procesando"
    AnalisisGuardado.metodo = datos["metodo"]
    db.session.commit()

    t0 = time.time()
    critery = datos["criterios"]["Criterios"]
    omegaC = datos["criterios"]["OmegaC"]
    cuenca = datos ["cuenca"]
    Metodo = datos["metodo"]
    ponderacion =datos["ponderacion"]
    paneles = datos["paneles"]
    sufijoNombre = cuenca + '_' + ponderacion + '_' + Metodo + '_' + fecha_creacion+ '_'

    print(f'critery {critery}')
    print(f'omegaC {omegaC}')
    print ("**************datos****************")
    print(datos)
    datos_entsoe = {
        "fecha_inicio": datos["paneles"]["fechaInicio"],
        "fecha_fin": datos["paneles"]["fechaFin"],
        "country_code": "ES"
    }



    Signo = ['+', '-', '-', '-','-', '+', '+', '+']

    pos, longitude, latitude, X, signo, omega = matrizX(critery, omegaC, Signo, cuenca, paneles, datos_entsoe, ruta, sufijoNombre)

    if ponderacion == "Arbitrario":
        pesos = omega
    elif ponderacion == "AHP":
        MatrizCopareada = datos["AHP"]
        pesos = mainAHP(MatrizCopareada)
    elif ponderacion == "Critic":
        pesos = critic(X, omega, signo)
    else:
        pesos = omega

    #Guardo los pesos del multicriterio en un csv

    Path = os.path.join(ruta, sufijoNombre+'Pesos.csv')
    hof_df = pd.DataFrame(pesos)
    hof_df.to_csv(Path)
    AnalisisGuardado.ficheroPesos = Path

    ranking, value = mainMCDM(X, pesos, signo, Metodo)
    geoJson, nombreFicheroResultados = generateGeoJsonyCSV(pos, longitude, latitude, ranking, value, ruta, sufijoNombre)
    AnalisisGuardado.ficheroResultados = nombreFicheroResultados
    tf = time.time()
    print(f'Tiempo total: {tf-t0} segundos')
    AnalisisGuardado.tiempo = round(tf-t0, 2)
    AnalisisGuardado.estado = "Finalizado"
    db.session.commit()
    return {"mensaje":geoJson}



