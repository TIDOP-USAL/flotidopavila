import os
from flask_security import hash_password

from extensions import db, app, user_datastore
from admin.modelUser import User, Role
from admin.modelAnalisis import Analisis


def build_sample_db():
    """Populate a small db with some example entries."""

    import string
    import random
    with app.app_context():
        # Delete tables
        db.drop_all()
        # Create tables
        db.create_all()

        with app.app_context():
            # Create 'user role'
            user_role = Role(name='user')
            # Create 'super user role'
            super_user_role = Role(name='admin')
            # Add object to database
            db.session.add(user_role)
            # Add object to database
            db.session.add(super_user_role)
            # Commit changes
            db.session.commit()
            # Create Admin user via Flask-Security
            test_user = user_datastore.create_user(
                nombre='Admin',
                email='admin@admin.es',
                password=hash_password('admin'),
                roles=[super_user_role],
                fichero=''
            )

            db.session.add(Analisis(nombre='Estudio de prueba', descripcion='Estudio de prueba', user_id=1))

            '''test_user = user_datastore.create_user(
                nombre='Admin',
                email='admin2@admin.es',
                password=hash_password('admin2'),
                roles=[user_role],
                fichero = ''
            )
            db.session.add(Analisis(nombre='Estudio de prueba', descripcion='Estudio de prueba', user_id=2))'''


            db.session.commit()
    return

def crearBaseDatos():
    app_dir =os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    database_path = os.path.join(app_dir, 'instance', app.config['DATABASE_FILE'])
    print ("database path",database_path)
    if not os.path.exists(database_path):
        print("Creating database")
        build_sample_db()
