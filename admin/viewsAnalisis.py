import os
from flask_admin import  expose
from flask_admin.contrib.sqla import ModelView
from wtforms import SelectField
from flask_security import current_user
from markupsafe import Markup
from flask import url_for, redirect, send_from_directory
from flask import flash

from extensions import db, app
from admin.modelAnalisis import Analisis

'''Vista para los roles de los Analisis, poder ver o descargar los analisis o borrarlos'''
class AnalisisView(ModelView):
    column_list = ('nombre', 'descripcion','estado','tiempo','fichero Pesos', 'fichero Resultados')

    form_excluded_columns = ('user')
    column_labels = {
        'tiempo': 'Tiempo (seg)',
        'valoracion': 'Valoración de 1 a 5 (1 mala, 5 buena)'
    }
    form_columns = ['nombre', 'descripcion', 'ficheroPesos', 'ficheroResultados', 'ficheroPng', 'valoracion']
    form_extra_fields = {
        'valoracion': SelectField(
            'Valoración de 1 a 5 (1 mala, 5 buena)',
            choices=[('0', '---'), (1, '1 - Mala'), (2, '2'), (3, '3'), (4, '4'), (5, '5 - Buena')],
            coerce=int
        )
    }
    #column_exclude_list = ['ficheroPesos', 'ficheroResultados']
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        #if current_user.has_role('user') or current_user.has_role('superuser'):
        return True

    def get_query(self):
        return self.session.query(self.model).filter_by(user_id=current_user.id)

    # Si también quieres que la búsqueda solo sea sobre los estudios del usuario logueado:
    def get_count_query(self):
        return self.session.query(db.func.count(Analisis.id)).filter_by(user_id=current_user.id)

    can_create = False
    can_delete = True
    edit_modal = True
    create_modal = True
    # Columna de acciones personalizadas
    column_formatters = {
        'fichero Pesos': lambda v, c, m, p: Markup(
            f'<a href="descargarResultados/{m.id}/0"><i class="fa fa-download"></i></a>') if m.ficheroPesos else Markup('<i class="fa fa-ban"></i>'),
        'fichero Resultados': lambda v, c, m, p: Markup(
            f'<a href="ver_enlace/{m.id}"><i class="fa fa-eye"></i></a> <a href="descargarResultados/{m.id}/1"><i class="fa fa-download"></i></a>') if m.ficheroResultados else Markup('<i class="fa fa-ban"></i>'),

    }

    @expose('/descargarResultados/<int:id>/<int:tipo>', methods=['GET'])
    def descargar(self, id, tipo):
        analisis = Analisis.query.get(id)
        print("*****************************")
        print(analisis)
        print(analisis.ficheroResultados)
        if analisis and analisis.ficheroResultados:
            if tipo==0:
                ruta = os.path.join('/', analisis.ficheroPesos)
            else:
                ruta = os.path.join('/', analisis.ficheroResultados)
            ruta = ruta.replace("\\", "/")
            print("*******RUTA*******", ruta)
            return redirect(ruta)
        return self.render('404.html')

    @expose('/ver_enlace/<int:id>', methods=['GET'])
    def ver_enlace(self, id):
        analisis = Analisis.query.get(id)
        if analisis and analisis.ficheroResultados:
            # Lógica para abrir un enlace
            ruta = os.path.join('/', analisis.ficheroResultados)
            ruta = ruta.replace("\\", "/")
            #ruta_dividida = ruta.split("/")
            #print(ruta_dividida)

            if "copeland" in analisis.metodo:
                return redirect('/herramienta?url=' + ruta + '&metodo=' + str(analisis.metodo) + '&cuenca=' + str(
                    analisis.cuenca) + '&imagen=' + analisis.ficheroPng)
            else:
                return redirect('/herramienta?url=' + ruta + '&metodo=' + str(analisis.metodo) + '&cuenca=' + str(
                    analisis.cuenca))

        return self.render('404.html')

    #@action('eliminar', 'Eliminar selección')
    # def eliminar_analisis(self, ids):
    def delete_model(self, model):

        try:

            # Lógica para eliminar un análisis
            #for id in ids:
            if model:
                id = model.id
                analisis = Analisis.query.get(id)
                if analisis:

                    if analisis.ficheroResultados:
                        rutaResultados = os.path.join('', analisis.ficheroResultados)
                        #rutaResultados = rutaResultados.replace("\\", "/")
                        if os.path.exists(rutaResultados):
                            os.remove(rutaResultados)
                        #en tuberias creamos dos ficheros el xlsx y el json
                        rutaResultadosTuberias = rutaResultados.replace(".xlsx", ".json")
                        if os.path.exists(rutaResultadosTuberias):
                            os.remove(rutaResultadosTuberias)
                        #en vehiculos se crean varios archivos para generar los graficos, hay que borrar los 4 archivos

                        rutaResultadosCsv = rutaResultados.replace("json","csv")
                        rutaResultados = rutaResultadosCsv.replace("resumen_hidrogenera_web_paper", "scheduling_horario_vehiculo")
                        if os.path.exists(rutaResultados):
                            os.remove(rutaResultados)
                        rutaResultados = rutaResultadosCsv.replace("resumen_hidrogenera_web_paper", "hrs_balance_horario")
                        if os.path.exists(rutaResultados):
                            os.remove(rutaResultados)
                        rutaResultados = rutaResultadosCsv.replace("resumen_hidrogenera_web_paper", "hrs_produccion_horaria")
                        if os.path.exists(rutaResultados):
                            os.remove(rutaResultados)
                        rutaResultados = rutaResultadosCsv.replace("resumen_hidrogenera_web_paper", "hrs_consumo_horario")
                        if os.path.exists(rutaResultados):
                            os.remove(rutaResultados)

                    if analisis.ficheroPesos:
                        rutaPesos = os.path.join('', analisis.ficheroPesos)
                        #rutaPesos = rutaPesos.replace("\\", "/")
                        if os.path.exists(rutaPesos):
                            os.remove(rutaPesos)

                    if analisis.ficheroPng:
                        rutaPng = os.path.join('', analisis.ficheroPng)
                        if os.path.exists(rutaPng):
                            os.remove(rutaPng)

                    db.session.delete(analisis)
            db.session.commit()
            return redirect(url_for('.index_view'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar analisis: {str(e)}", "error")

#ruta para descargar los ficheros
@app.route('/plugins/Results/<path:filename>', methods=['GET'])
def download_file(filename):
    print("filename",filename)
    results_dir = os.path.join(app.root_path, 'plugins', 'Results')
    file_path = os.path.join(results_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(results_dir, filename)
    else:
        return "File not found", 404

def vistasAnalisis(admin):
    admin.add_view(AnalisisView(Analisis, db.session, menu_icon_type='fa', menu_icon_value='fa-chart-pie', name="Analisis"))