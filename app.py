
import os

from flask import redirect, request
from masas_Agua import masas_agua_bp
from extensions import create_app

app = create_app()

from admin.routes import routes
from admin.build_sample_db import crearBaseDatos
import logging
from flask_login import login_required, current_user
@app.route('/ping-test')
def ping_test():
    return "ping ok"
@app.route('/debug-roles')
@login_required
def debug_roles():
    logging.warning(f"USER: {current_user.email}")
    logging.warning(f"ROLES: {[r.name for r in current_user.roles]}")
    logging.warning(f"HAS ADMIN: {current_user.has_role('admin')}")
    return f"roles: {[r.name for r in current_user.roles]} | has_role admin: {current_user.has_role('admin')}"

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
routes()
crearBaseDatos()
app.register_blueprint(masas_agua_bp)

if __name__ == '__main__':


    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
