
from flask_admin import  expose, AdminIndexView, Admin
from flask_login import login_user, current_user
from flask import url_for, redirect, request, render_template, session, flash
from flask_security import verify_password
from datetime import datetime

from admin.modelLogs import Logs
from admin.modelUser import CustomLoginForm
from admin.views import vistas
from extensions import app, db , user_datastore


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated:
            role_names = [role.name for role in current_user.roles]  # Extrae los nombres de los roles
            '''if 'user' in role_names:
                #return redirect(url_for('Usuarios.index_view'))
                return self.render('admin/index.html')
            else:
                return redirect(url_for('role.index_view'))'''

            return self.render('admin/index.html') #es lo mismo return self.render('admin/base.html')
        else:
            #flash('Por favor, inicie sesión', 'error')
            #form = CustomLoginForm()
            #return render_template("security/login_user.html", form=form)
            return redirect('/login')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = CustomLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = user_datastore.find_user(email=email)
        if user and verify_password(password, user.password):
            session.clear()
            login_user(user, remember=form.remember_me.data)
            '''role_names = [role.name for role in current_user.roles]  # Extrae los nombres de los roles
            if 'user' in role_names:
                return redirect(url_for('Usuarios.index_view'))
            else:
                return redirect(url_for('role.index_view'))'''
            log_entry = Logs(
                user_id=user.id,
                action='login',
                timestamp=datetime.utcnow(),
                ip_address=request.remote_addr
            )
            try:
                db.session.add(log_entry)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error al guardar el log de login: {e}')
            next_page = request.args.get('next') or url_for('admin.index')
            return redirect(next_page)
            #return redirect(url_for('admin.index'))
        else:
            flash(f"Error nombre de usuario o contraseña invalidos", "error")
            form = CustomLoginForm()
            return render_template("security/login_user.html", form=form)
    else:
        flash('Por favor, inicie sesión', 'info')
        form = CustomLoginForm()
        return render_template("security/login_user.html", form=form)


admin = Admin(app, index_view=MyAdminIndexView(url='/'), name='FloTidopAvila')
def routes():
    admin.base_template = 'admin/base.html'
    vistas(admin)