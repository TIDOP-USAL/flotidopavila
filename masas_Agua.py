import csv
import os
import uuid
import decimal

import numpy as np

from flask import request, jsonify, Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

from plugins.calculos import calsEmbalses
from plugins.produccion import cal_Produccion
from admin.modelAnalisis import Analisis
from extensions import db
masas_agua_bp = Blueprint('masas_agua', __name__)

@masas_agua_bp.route('/herramienta')
@login_required
def home():
    url = request.args.get('url')

    if url == None:
        return render_template('home.html', resultado={})
    else:
        cuenca = request.args.get('cuenca')
        metodo = request.args.get('metodo')
        return render_template('home.html', resultado={'url': url, 'cuenca': cuenca, 'metodo': metodo})
'''
Ruta para realizar el metodo multicriterio de los embalses, se recibe un json con los datos necesarios para realizar el calculo, 
se llama a la funcion calsEmbalses y se devuelve un geojson con los resultados
'''
@masas_agua_bp.route('/calcularEmbalsesAvila', methods=["POST"])
def calcularEmbalses():
    try:
        datos = request.get_json()
        usuario = current_user
        id, fecha_creacion = guardar_datos_bd(datos["nombre"], datos["ponderacion"], datos["metodo"], cuenca=datos["cuenca"], usuario=usuario.id)

        ruta = os.path.join('plugins', 'Results', str(usuario.id))
        datos = calsEmbalses(datos, id, fecha_creacion, ruta)
        response = {"geoJson": datos['mensaje']},200
        return response
    except FileNotFoundError:
        print("No se encuentra el archivo")
        return {"geoJson": "El archivo no fue encontrado"},400

    except PermissionError:
        print("No hay permisos")
        return {"geoJson": "No hay permisos para leer el archivo"},403

    except Exception as e:
        print("Ocurrió un error inesperado:", str(e))
        # Captura cualquier otro error inesperado (como errores de encoding o delimitadores)
        return {"geoJson": str(e)},500

def guardar_datos_bd(texto, ponderacion, metodo, directorio="", cuenca="", usuario = 1):
    # Añado un registro a la tabla analisis
    FechaCreacion = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    nuevo_analisis = Analisis(
        nombre=texto,
        descripcion=texto+", ponderación: " + ponderacion + ", método: " + metodo + ", Elaborado en la fecha: " + FechaCreacion,
        estado="En espera",
        tiempo=0,
        user_id=usuario,  # Debe coincidir con un usuario existente
        metodo = metodo,
        cuenca = cuenca
    )

    db.session.add(nuevo_analisis)
    db.session.commit()
    return nuevo_analisis.id, FechaCreacion

'''Ruta para obtener los datos de los paneles solares, se lee el archivo CSV y se devuelve un JSON con los datos'''
@masas_agua_bp.route('/csv-pv-modules')
def pv_modules():
    try:
        data = []
        path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join( path ,'static','datos','PV_Modules.csv')
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                data.append(row)

        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "El archivo no fue encontrado", "path": file_path}), 404

    except PermissionError:
        return jsonify({"error": "No hay permisos para leer el archivo"}), 403

    except Exception as e:
        # Captura cualquier otro error inesperado (como errores de encoding o delimitadores)
        return jsonify({"error": "Ocurrió un error inesperado", "mensaje": str(e)}), 500


'''Cache para almacenar los resultados de la produccion, 
se utiliza un diccionario para guardar los resultados con un id unico generado con uuid'''
produccion_cache = {}

'''Funcion para calcular la produccion de un embalse, se recibe un json con los datos necesarios para realizar el calculo,
se llama a la funcion cal_Produccion y se devuelve un id unico para luego obtener los resultados en la vista'''
@masas_agua_bp.route('/calcular_produccion', methods=["POST"])
def calcularProduccion():
    try:
        datos = request.json
        #print(datos)
        produccion = cal_Produccion(datos)
        # Generar un ID único
        resultado_id = str(uuid.uuid4())
        # Guardar en cache
        produccion_cache[resultado_id] = produccion
        # Devolver solo el ID
        return {
            "resultado_id": resultado_id
        },200
    except Exception as e:
        print("Ocurrió un error inesperado:", str(e))
        # Captura cualquier otro error inesperado (como errores de encoding o delimitadores)
        return {"info": str(e)},500

'''Ruta para mostrar la vista de calcular produccion, se renderiza la plantilla vista_produccion.html
Cuando se usan muchos datos es mejor hacerlo de esta forma, en lugar de renderizar y pasar los datos directamente a la plantilla, 
ya que se puede generar un error de memoria al intentar renderizar con muchos datos, 
ademas de que se puede mejorar el rendimiento al cargar la vista sin tener que esperar a que se renderice con los datos,'''
@masas_agua_bp.route('/calcular_produccion_vista', methods=["GET"])
def calcularProduccionVista():
    return render_template('vista_produccion.html')

'''Ruta para obtener los resultados de la produccion, se recibe el id unico generado en la funcion calcularProduccion,
se busca en la cache y se devuelve el resultado en formato JSON'''
@masas_agua_bp.route('/api/produccion/<resultado_id>')
def obtenerProduccion(resultado_id):
    datos = produccion_cache.get(resultado_id)
    if not datos:
        return jsonify({"error": "resultado no encontrado"}), 404
    del produccion_cache[resultado_id]
    return {"datos":to_serializable(datos)},200

'''Funcion para convertir objetos no serializables a formatos compatibles con JSON, como listas o diccionarios,
 para poder enviar los resultados a la vista de manera correcta'''
def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return obj.astype(float).tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj