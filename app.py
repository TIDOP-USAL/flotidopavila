import csv
import json
import os

from flask import Flask, render_template, request, jsonify
from plugins.calculos import calsEmbalses
app = Flask(__name__)

@app.route('/')
def home():  # put application's code here
    return render_template('home.html')


@app.route('/aeropuerto/<datos>')
def aeropuerto(datos):
    '''data = json.loads(datos)
    result = json.dumps(data)
    return render_template('aeropuerto.html', resultado=result)'''



'''
Ruta para realizar el metodo multicriterio de los embalses, se recibe un json con los datos necesarios para realizar el calculo, 
se llama a la funcion calsEmbalses y se devuelve un geojson con los resultados
'''
@app.route('/calcularEmbalsesAvila', methods=["POST"])
def calcularEmbalses():
    try:
        datos = request.get_json()
        print(datos)
        datos = calsEmbalses(datos)

        #response = {"geoJson": 'mensaje'},200
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

'''Ruta para obtener los datos de los paneles solares, se lee el archivo CSV y se devuelve un JSON con los datos'''
@app.route('/csv-pv-modules')
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
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
