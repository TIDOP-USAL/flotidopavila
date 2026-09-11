
import os

from flask import redirect, request
from masas_Agua import masas_agua_bp
from extensions import create_app

app = create_app()

from admin.routes import routes
from admin.build_sample_db import crearBaseDatos
@app.errorhandler(403)
def forbidden_error(error):
    return redirect('/login')


@app.errorhandler(404)
def page_not_found(error):
    print("URL solicitada:", request.url)  # URL completa
    print("Ruta solicitada:", request.path)  # Solo el path
    print(error)
    return redirect('/login')


UPLOAD_FOLDER = os.path.join( 'plugins', 'Results')
if __name__ == '__main__':

    routes()
    crearBaseDatos()

    app.register_blueprint(masas_agua_bp)
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
