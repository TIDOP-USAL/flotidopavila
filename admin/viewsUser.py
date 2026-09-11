import os

from flask_admin.contrib.sqla import ModelView
from flask_security import current_user, hash_password

from flask import url_for, redirect
from flask import flash, abort, request
from wtforms.fields.simple import PasswordField
import uuid

from extensions import db, app
from admin.modelAnalisis import Analisis
from admin.modelUser import User, Role


class MyRoleView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    can_edit = True
    edit_modal = True
    create_modal = False
    can_export = False
    can_view_details = True
    details_modal = True
    can_create = False
    can_delete = False

'''Vista para el usuario logueado'''
class ProfileView(ModelView):

    form_excluded_columns = ('fs_uniquifier', 'active', 'confirmed_at', 'Analisis', 'logs')
    #column_editable_list = ['email', 'first_name', 'last_name']
    column_exclude_list = ['password']
    column_list = ('email', 'nombre', 'apellidos','roles')
    column_details_exclude_list = column_exclude_list
    form_overrides = {
        'password': PasswordField
    }

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        #if not current_user.has_role('superuser'):
        #    return True
        return True

    def get_query(self):
        return self.session.query(self.model).filter_by(id=current_user.id)

    # Si también quieres que la búsqueda solo sea sobre los estudios del usuario logueado:
    def get_count_query(self):
        return self.session.query(db.func.count(User.id)).filter_by(id=current_user.id)

    def is_visible(self):
        return False
    can_create = True
    can_delete = True
    can_edit = True
    edit_modal = True
    create_modal = True

'''Vista para administrar usuarios'''
class UserView(MyRoleView):
    form_excluded_columns = ('fs_uniquifier','active','confirmed_at', 'Analisis', 'fichero', 'logs')
    column_list = ('email', 'nombre', 'apellidos', 'roles')
    #column_editable_list = ['email', 'nombre', 'apellidos']
    #column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    #column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }
    can_create = True
    can_delete = True
    can_edit = True
    edit_modal = True
    create_modal = True
    #Para genera un fs_uniquifier pues no se pide en el formulario
    def on_model_change(self, form, model, is_created):
        if is_created and not model.fs_uniquifier:
            model.fs_uniquifier = str(uuid.uuid4())
        if form.password.data:
            model.password = hash_password(form.password.data).encode('utf-8')
        model.active = 1
        model.fichero = 'pendiente_config.csv'
    '''@action('borrar', 'Eliminar selección')
    def eliminar_usuario(self, ids):'''

    def after_model_change(self, form, model, is_created):
        """Después de guardar el modelo"""
        if is_created:
            # Ruta base
            base_dir = os.path.join('plugins', 'Results')
            user_dir = os.path.join(base_dir, str(model.id))
            os.makedirs(user_dir, exist_ok=True)
            self.session.commit()
    def delete_model(self, model):
        try:
            # Lógica para eliminar un usuario
            '''for user_id in ids:
                usuario = User.query.get(user_id)
                if usuario:'''
            analisis_list = Analisis.query.filter_by(user_id=model.id).all()
            if analisis_list:
                for analisis in analisis_list:
                    if analisis.ficheroResultados:
                        rutaResultados = os.path.join('', analisis.ficheroResultados)
                        # rutaResultados = rutaResultados.replace("\\", "/")
                        if os.path.exists(rutaResultados):
                            os.remove(rutaResultados)
                        rutaPesos = os.path.join('', analisis.ficheroPesos)
                        # rutaPesos = rutaPesos.replace("\\", "/")
                        if os.path.exists(rutaPesos):
                            os.remove(rutaPesos)
                    db.session.delete(analisis)
            rutaFichero = os.path.join('', model.fichero) #Fichero configuracion
            #print(rutaFichero)
            if os.path.exists(rutaFichero):
                os.remove(rutaFichero)

            rutaDirectorio = os.path.join('plugins', 'Results', str(model.id))
            if os.path.exists(rutaDirectorio):
                os.rmdir(rutaDirectorio)
            db.session.delete(model)
            db.session.commit()

            return redirect(url_for('.index_view'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar usuario: {str(e)}", "error")
def vistasUsuario(admin):
    admin.add_view(MyRoleView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles",
                               category="Gestión de Usuarios"))
    admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Administrar Usuarios",
                 category="Gestión de Usuarios"))
    admin.add_view(ProfileView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-user', name="Perfil Usuario",
                               endpoint='Usuarios'))
