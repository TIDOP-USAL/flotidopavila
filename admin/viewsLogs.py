
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask_login import user_logged_out
from flask import url_for, redirect, request

from extensions import db, app
from admin.modelAnalisis import Analisis
from admin.modelLogs import Logs

class LogsView(ModelView):
    # column_exclude_list = ['ficheroPesos', 'ficheroResultados']
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            return True
        # if current_user.has_role('user') or current_user.has_role('superuser'):
        return False

    can_edit = True
    can_create = True
    can_delete = True
    edit_modal = True
    create_modal = True

#guardar el log de desconexion
@user_logged_out.connect_via(app)
def log_logout(sender, user):
    if current_user.is_authenticated:
        log_entry = Logs(
            user_id=current_user.id,
            action='logout',
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        try:
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error al guardar log de logout: {e}')

    return redirect(url_for('security.login'))

def vistasLogs(admin):
    admin.add_view(
        LogsView(Logs, db.session, menu_icon_type='fa', menu_icon_value='fa-font-awesome', name="Logs de conexión",
                 endpoint='Logs', category="Gestión de Usuarios"))