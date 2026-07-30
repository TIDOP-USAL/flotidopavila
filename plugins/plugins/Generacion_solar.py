import math 
import numpy as np

from sympy import *

import pvlib
import pandas as pd


def callPVGIS(latitude, longitude):
    
    tmy, meta  = pvlib.iotools.get_pvgis_tmy(
                                                        latitude=latitude,
                                                        longitude=longitude,
                                                        outputformat='json',
                                                        usehorizon=True,
                                                        map_variables=True,
                                                        timeout=30)
    
    return tmy

def Inclinationcorrection(tmy, tilt, azimuth, latitude, longitude, InitialDate, FinalDate,BIPV):
    
    #print('Fecha Inicio: ', InitialDate)
    #print('Fecha Final: ', FinalDate)
    
    initial_dt = pd.to_datetime(InitialDate, dayfirst=True)
    final_dt   = pd.to_datetime(FinalDate,   dayfirst=True)
    initial_dt = initial_dt.tz_localize("UTC")
    final_dt = final_dt.tz_localize("UTC")
    final_dt = final_dt + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
    
    # Comprobación
    if final_dt <= initial_dt:
        raise HTTPException(
            status_code=400,
            detail="La fecha final debe ser posterior a la fecha inicial."
        )
    

    
    Initialyear = initial_dt.year
    Finalyear = final_dt.year
    
    #print("Año inicio: ",Initialyear )
    #print("Año final: ",Finalyear )
    
    
    new_index = pd.date_range(
        start=initial_dt,
        end=final_dt,
        freq="h",
        tz="UTC"
    )

  
    tmy_key = tmy.index.strftime("%m-%d %H:%M")

   
    new_key = new_index.strftime("%m-%d %H:%M")

    
    tmy_dict = dict(zip(tmy_key, tmy.values))

    #new_values = [tmy_dict[k] for k in new_key]
    new_values = []
    for k in new_key:
        if k in tmy_dict:
            new_values.append(tmy_dict[k])
        else:
            # PVGIS TMY no tiene 02-29 -> usar 02-28 misma hora
            k2 = k.replace("02-29", "02-28")
            new_values.append(tmy_dict[k2])
    
    tmy_filtered = pd.DataFrame(new_values, index=new_index, columns=tmy.columns)
    
#    tmy_filtered=tmy_filtered[0:-1]
    
    
    ghi = tmy_filtered['ghi']
    dni = tmy_filtered['dni']
    dhi = tmy_filtered['dhi']


    solar_pos = pvlib.solarposition.get_solarposition(
        tmy_filtered.index, latitude, longitude )



#   valores  plano del panel
    dni_extra = pvlib.irradiance.get_extra_radiation(tmy_filtered.index, method='spencer')
    poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth+180,
    dni=dni,
    ghi=ghi,
    dhi=dhi,
    dni_extra=dni_extra,
    solar_zenith=solar_pos['zenith'],
    solar_azimuth=solar_pos['azimuth'],
    model='haydavies')

#  Irradiancia final en plano del panel se mete bifacial con modelo simple usando el bifaciality
    if BIPV=='Y':
        valor_albedo = 0.06
        Irradiancia_Trasera=ghi*valor_albedo
        bifaciality=0.7
        poa_global = poa['poa_global']+bifaciality*Irradiancia_Trasera
    else:
        poa_global = poa['poa_global']

    #print(poa_global)



    result=pd.DataFrame({
    'Fechas': tmy_filtered.index,
    'poa_global': poa_global.loc[tmy_filtered.index],
    'temp_air': tmy_filtered['temp_air'],
    'wind_speed':tmy_filtered['wind_speed'] })

    #print('Irradaincia_poa: ', sum(poa_global.loc[tmy_filtered.index]))
    #print(result)
    poa_global.to_csv("irradiancia.csv")
    return result

def AlturaSolarMinima(Latitud):

    n=365
    AnguloHorarioMS=0 # AnguloHorario medio Día Solar
    AnguloDeclinacion=[]
    AlturaSolar=[]
    
    
    for i in range (1,n+1):
        AnguloDeclinacion.append(23.45*math.sin(math.radians(360*((284+i)/365))))
    
    for i in range (0,len(AnguloDeclinacion)):   
        AlturaSolar.append(90-math.degrees(math.acos(math.sin(math.radians(AnguloDeclinacion[i]))*math.sin(math.radians(Latitud))+math.cos(math.radians(AnguloDeclinacion[i]))*math.cos(math.radians(Latitud))*math.cos(math.radians(AnguloHorarioMS)))))
    
    AlturaSolarMin=min(AlturaSolar)
    

    return AlturaSolarMin


def RadiacionSolarCorregida(modo, datosolar, n, HoraLocal, Latitud, Longitud, Inclinacion, Orientacion):

###############################################################################
# IRRADIANCIA Horizontal

    Irradiancia=datosolar['G(h)']
    Irradiancia.tolist()
    IrradianciaDiaria=Irradiancia[(n-1)*24:n*24]
    SHorizontal=IrradianciaDiaria.iloc[HoraLocal]
   
    

    AnguloDeclinacion=23.45*math.sin(math.radians(360*((284+n)/365)))
#    print(AnguloDeclinacion)


    AnguloHorarioMS=0 # AnguloHorario medio Día Solar
    

    
    B=360/364*(n-81)
    ET=9.87*math.sin(math.radians(2*B))-7.53*math.cos(math.radians(B))-1.5*math.sin(math.radians(B))
    GTM=1 ## En Verano varía a 2
    LSTM=15*GTM 
    
    TC=4*(Longitud-LSTM)+ET
    LT=HoraLocal*60
    LST=LT+TC/60
    HRA=15*(LST-12)

    OmegaSP=math.degrees(math.acos(math.tan(math.radians(AnguloDeclinacion))*math.tan(math.radians(Latitud))))
    AzimutSP=math.degrees(math.acos((-math.sin(math.radians(AnguloDeclinacion)))/math.cos(math.radians(Latitud))))
    

    sum1=math.sin(math.radians(AnguloDeclinacion))*math.sin(math.radians(Latitud))
    sum2=math.cos(math.radians(AnguloDeclinacion))*math.cos(math.radians(Latitud))*math.cos(math.radians(HRA))
    AnguloElevacion=math.degrees(math.asin(sum1+sum2))
    
    Num=math.sin(math.radians(AnguloDeclinacion)*math.cos(math.radians(Longitud)-math.cos(math.radians(AnguloDeclinacion))*math.sin(math.radians(Longitud))*math.cos(math.radians(HRA)))) 
    Den=math.cos(math.radians(AnguloElevacion))

    if round(Num/Den,4) > 1.0:
        Azimut = math.degrees(math.acos(1.0))
    elif round(Num/Den,4) < -1.0:
        Azimut = math.degrees(math.acos(-1.0))
    else:
        Azimut=math.degrees(math.acos(round(Num/Den,4)))

###############################################################################    
    
    SIncidente=SHorizontal/math.sin(math.radians(AnguloElevacion))
   
    if modo!=-1:
##  Correccion solo por inclinación
        Smodulo=SHorizontal*math.sin(math.radians(AnguloElevacion+Inclinacion))/math.sin(math.radians(AnguloElevacion))
       
##  Correccion por inclinación y orientación arbitrarias
    else:
        if Orientacion<0:
            
            Smodulo=SIncidente*(math.cos(math.radians(AnguloElevacion))*math.sin(math.radians(Inclinacion))*math.cos(math.radians(Orientacion+Azimut))+math.sin(math.radians(AnguloElevacion))*math.cos(math.radians(Inclinacion)))
        else:    
            Smodulo=SIncidente*(math.cos(math.radians(AnguloElevacion))*math.sin(math.radians(Inclinacion))*math.cos(math.radians(Orientacion-Azimut))+math.sin(math.radians(AnguloElevacion))*math.cos(math.radians(Inclinacion)))

    return Smodulo

def IrradianciaCorregida(modo, datosolar, Latitud,Longitud,Inclinacion,Orientacion):

    ###### OJO PRECISION SI SE QUIERE PRECISION MINUTOS
    HoraLocal=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    IrrCorreg=[]
    AngDeclinacion=[]
    AlturaSolar=[]
    n=365
    for j in range (1,n+1):
        for i in range(0,len(HoraLocal)):
           Smodule=RadiacionSolarCorregida(modo,datosolar, j, HoraLocal[i], Latitud,Longitud,Inclinacion,Orientacion)
           IrrCorreg.append(Smodule)

    return IrrCorreg

def RadiacionSolarCorregidaMCDM(modo, datosolar, n, HoraLocal, Latitud, Longitud, Inclinacion, Orientacion):

###############################################################################
# IRRADIANCIA Horizontal
  
    Irradiancia=datosolar
    Irradiancia.tolist()
    IrradianciaDiaria=Irradiancia[(n-1)*24:n*24]
    IrradianciaDiaria.tolist()
    SHorizontal=IrradianciaDiaria[HoraLocal]

    

    AnguloDeclinacion=23.45*math.sin(math.radians(360*((284+n)/365)))
#    print(AnguloDeclinacion)


    AnguloHorarioMS=0 # AnguloHorario medio Día Solar
    

    
    B=360/364*(n-81)
    ET=9.87*math.sin(math.radians(2*B))-7.53*math.cos(math.radians(B))-1.5*math.sin(math.radians(B))
    GTM=1 ## En Verano varía a 2
    LSTM=15*GTM 
    
    TC=4*(Longitud-LSTM)+ET
    LT=HoraLocal*60
    LST=LT+TC/60
    HRA=15*(LST-12)

    OmegaSP=math.degrees(math.acos(math.tan(math.radians(AnguloDeclinacion))*math.tan(math.radians(Latitud))))
    AzimutSP=math.degrees(math.acos((-math.sin(math.radians(AnguloDeclinacion)))/math.cos(math.radians(Latitud))))
    

    sum1=math.sin(math.radians(AnguloDeclinacion))*math.sin(math.radians(Latitud))
    sum2=math.cos(math.radians(AnguloDeclinacion))*math.cos(math.radians(Latitud))*math.cos(math.radians(HRA))
    AnguloElevacion=math.degrees(math.asin(sum1+sum2))
    
    Num=math.sin(math.radians(AnguloDeclinacion)*math.cos(math.radians(Longitud)-math.cos(math.radians(AnguloDeclinacion))*math.sin(math.radians(Longitud))*math.cos(math.radians(HRA)))) 
    Den=math.cos(math.radians(AnguloElevacion))

    if round(Num/Den,4) > 1.0:
        Azimut = math.degrees(math.acos(1.0))
    elif round(Num/Den,4) < -1.0:
        Azimut = math.degrees(math.acos(-1.0))
    else:
        Azimut=math.degrees(math.acos(round(Num/Den,4)))

###############################################################################    
    
    SIncidente=SHorizontal/math.sin(math.radians(AnguloElevacion))
   
    if modo!=-1:
##  Correccion solo por inclinación
        Smodulo=SHorizontal*math.sin(math.radians(AnguloElevacion+Inclinacion))/math.sin(math.radians(AnguloElevacion))
       
##  Correccion por inclinación y orientación arbitrarias
    else:
        if Orientacion<0:
            
            Smodulo=SIncidente*(math.cos(math.radians(AnguloElevacion))*math.sin(math.radians(Inclinacion))*math.cos(math.radians(Orientacion+Azimut))+math.sin(math.radians(AnguloElevacion))*math.cos(math.radians(Inclinacion)))
        else:    
            Smodulo=SIncidente*(math.cos(math.radians(AnguloElevacion))*math.sin(math.radians(Inclinacion))*math.cos(math.radians(Orientacion-Azimut))+math.sin(math.radians(AnguloElevacion))*math.cos(math.radians(Inclinacion)))

    return Smodulo

def IrradianciaCorregida(modo, datosolar, Latitud,Longitud,Inclinacion,Orientacion):

    ###### OJO PRECISION SI SE QUIERE PRECISION MINUTOS
    HoraLocal=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    IrrCorreg=[]
    AngDeclinacion=[]
    AlturaSolar=[]
    n=365
    for j in range (1,n+1):
        for i in range(0,len(HoraLocal)):
           Smodule=RadiacionSolarCorregida(modo,datosolar, j, HoraLocal[i], Latitud,Longitud,Inclinacion,Orientacion)
           IrrCorreg.append(Smodule)

    return IrrCorreg

def distanciaPaneles(Latitud, Inclinacion, LongitudPanel):
    
    AlturaSolar=AlturaSolarMinima(Latitud)
    
    a=LongitudPanel*math.cos(math.radians(Inclinacion))
    b=LongitudPanel*math.sin(math.radians(Inclinacion))
    
    d2=b/math.tan(math.radians(AlturaSolar))
    d1=a+d2
    return d1

def IrradianciaCorregidaMCDM(modo, datosolar, Latitud,Longitud,Inclinacion,Orientacion):

    ###### OJO PRECISION SI SE QUIERE PRECISION MINUTOS
    HoraLocal=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    IrrCorreg=[]
    AngDeclinacion=[]
    AlturaSolar=[]
    n=365
    for j in range (1,n+1):
        for i in range(0,len(HoraLocal)):
           Smodule=RadiacionSolarCorregidaMCDM(modo,datosolar, j, HoraLocal[i], Latitud,Longitud,Inclinacion,Orientacion)
           IrrCorreg.append(Smodule)

    return IrrCorreg

def distanciaPaneles(Latitud, Inclinacion, LongitudPanel):
    
    AlturaSolar=AlturaSolarMinima(Latitud)
    
    a=LongitudPanel*math.cos(math.radians(Inclinacion))
    b=LongitudPanel*math.sin(math.radians(Inclinacion))
    
    d2=b/math.tan(math.radians(AlturaSolar))
    d1=a+d2
    return d1

def SuperficiePanel(d1,AnchoPanel):
    
    Sup=d1*AnchoPanel
    
    return Sup

def NumMaxPaneles(Latitud,Inclinacion,LongitudPanel,AnchoPanel,SupAgua):
    
    d1=distanciaPaneles(Latitud,Inclinacion,LongitudPanel)
    
    SupPanel=SuperficiePanel(d1,AnchoPanel)
    
#    print(SupPanel)
#    print(SupAgua)
    
    NumPaneles=math.floor(SupAgua/SupPanel)
    
    return NumPaneles

def calcProduccionAnual(Temperatura, Irradiancia, Num_paneles,data):
    
    #print(data)
    
    #Constantes  globales no dependen del panel
    Trc = 25  # Temperatura [ºC] stc
    Tr = Trc + 273.15  # Temperatura referencia (K)
    k = 1.3805 * (10 ** (-23))  # Constante de Bolzmann
    A = 1.3  # Factor ideal del diodo 
    Gref = 1000  # Radiación solar 1000[w/m^2]  
    q = 1.602 * (10 ** (-19))  # Carga del electrón (C)
    Eg = 1.1  # Brecha energetica (band gap), para el silicio (1.1 eV-->Silicio)
   
    #Datos que vienen del panel seleccionado por GIS
    
    Ns =float(data['panel']['N_s'])  # Número de celdas conectadas en serie 
    Ki =float(data['panel']['Tc_isc'])  # Coeficiente de corriente de cortocircuito de la celula (%/ºC)
    
    Isc = float(data['panel']['Isc'])  # Isc: Corriente  de cortocircuito (A) at STC
    Voc = float(data['panel']['Voc'])  # Voc: Tensión de de circuito abierpto (V) JAM78S10 435-455/MR
    
    Np = float(data['panel']['N_p']) # Número de celulas en paralelo, para modelo JAM78S10 435-455/MR
    Pinv = 8  # Goodwe GW 8000-DT
    
    
    Irradiancia_list=Irradiancia['poa_global']
    
    
    # CALCULOS POTENCIA

    tiemp = []
    temp = []
    rad = []
    volt = []
    inten = []
    pot = []

    #    IrradianciaCorregida=RadiacionSolarCorregida(modo=0, n=162, HoraLocal=12, SHorizontal=100, Latitud=42.6,Longitud=-4,Inclinacion=45,Orientacion=20)

    for j4 in range(0, len(Irradiancia_list)):

        if Irradiancia_list.iloc[j4] != 0:
            To = Temperatura[j4] + 273.15  # Trtc =
            # Temperatuta en real-time (ºC) y To= Temperatura en real time (k)
            NskATo = Ns * k * A * To
            # print ('NskATo: ',NskATo)
            # Iph = [Isc +Ki(To - Tr)]*(G/Gref)
            Iph = (Isc + Ki * (To - Tr)) * (Irradiancia_list.iloc[j4]/ Gref) # Iph:
            # Corriente fotoelectrica de la celula solar
            #            print ("Iph: ", Iph)

            # Cuarto paso: Modo de corriente de saturación inversa PV
            # Irs = Isc / [e^((q*Voc)/(NskATo))-1]

            Irs = Isc / (math.exp((q * Voc) / NskATo) - 1)  # Irs:
            # Corriente de saturación inversa de diodo en Trtc (A)

            # Quinto paso: Modelo corriente saturación
            # Is = Irs*(To/Tr)^3*e^[(q*Eg)/(A*K)*(1/Tr-1/To)]
            Is = Irs * (To / Tr) ** 3 * math.exp((q * Eg) / (A * k) * (1 / Tr - 1 / To))
            #            print ("Is: ", Is)

            # Sexto paso: Modelo de corriente de salida fotovoltaica
            # I = Np ∗ Iph − Np ∗ Is[exp(q(V + IRs)/NsKATo)− 1]

            V = 46.22  # Voltaje de salida del modulo de PV (V)
            I = Np * Iph - Np * Is * (math.exp(q * ((V / NskATo))) - 1)
            # print ("I: " , I)

            # Calculo valor Voc para I=0.
            Voc2 = np.log(Iph/Is + 1)* (NskATo/q)
#            print ("Voc, para analizar el error: ", Voc2)

            #Calculos las potencias maxima, Vmp e Imp, MPPT.
            V = symbols('V')
            derivada = diff((Np*Iph - Np*Is*(exp(q*((V/NskATo)))-1))*V,V)
            #print ("Derivada: ", derivada)
            derivada_segunda = diff(derivada,V)
            #print ("2ºDerivada: ", derivada_segunda)

            #NEWTON-RAphson para MPPT
            x=50 #Ha de ser cercano a Voc
            for i in range (0,15):
                x = x - (derivada.subs(V,x)/derivada_segunda.subs(V,x))
#            print ("Valor de Vmp: " , float(x)*Paneles_serie)
            Imp = Np*Iph - Np*Is*(exp(q*((x/NskATo)))-1)
                        # print ("Valor de Imp: ", Imp*Paneles_paralelo)
            Pmax = (Np * Iph - Np * Is * (math.exp(q * ((x / NskATo))) - 1)) * x
#            print("Potencia maxima Pmp", Pmax*Num_paneles*10**-6, "(MW)" )

        else:
            Pmax = 0
            x = 0
            Imp = 0
            # print("Potencia max",Pmax)
        #
        #
        temp.append(Temperatura[j4])
        rad.append(Irradiancia_list.iloc[j4])
        #        volt.append(round(x*Paneles_serie,3))
        #        inten.append(round(Imp*Paneles_paralelo,3))
        
        pot.append(max(round((Pmax * Num_paneles), 3),0))
        potsolar = np.array(pot)  # np.array(pot[8:]+pot[0:8])


    #Num_Inversor = math.ceil((potsolar / 1000) / Pinv)
#    Num_Inversor = math.ceil(np.max((potsolar / 1000) / Pinv))

#    generateFilesProduccion(Num_paneles, Num_Inversor, numProductor, numUsuario, Irradiancia, potsolar, tipoUsu)
#    print('Produccion anual creada')
    return potsolar/1000


def calcProduccionAnualSimplified(Temperatura, Irradiancia, NumPaneles,data):

    # Constantes  globales no dependen del panel
    Tstc = 25  # Temperatura [ºC] stc
    Gstc = 1000  # Irradiancia en condiciones STC (1000 W/m2)
    rendSistema = 0.85

    # Datos que vienen del panel seleccionado por GIS
    Pstc = float(data['panel']['Pmax'])/1000  # W
    alpha = float(data['panel']['Tc_pmax']) / 100
    TONC = float(data['panel']['NOCT'])

    Irradiancia_list = Irradiancia['poa_global']

    EHoraria = []
    Tc=[]

    for i in range(0,len(Irradiancia_list)):
        Tc.append(Temperatura[i]+((TONC-20)*(Irradiancia_list.iloc[i]/800)))

    for i in range(0, len(Irradiancia_list)):
        EHoraria.append(rendSistema * Pstc * (Irradiancia_list.iloc[i] /Gstc) * (1 + alpha * (Tc[i] - Tstc))* NumPaneles)
    EHoraria = np.array(EHoraria)
    return EHoraria #kWh

