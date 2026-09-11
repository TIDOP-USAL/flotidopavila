
from flask_security import UserMixin, RoleMixin
from flask_security.forms import LoginForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from extensions import db

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)
class Role(db.Model, RoleMixin):
    """Role Model inherited"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    descripcion = db.Column(db.String(255))

    def __str__(self):
        """Returns a string representative of Role"""
        return f"Role: '{str(self.name)}', description: {self.descripcion}."

class User(db.Model, UserMixin):
    """User Model inherited"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellidos = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fichero = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    def __str__(self):
        """Returns a string representative of User"""
        return f"User: '{str(self.email)}', Name: {self.nombre} {self.apellidos}."

class CustomLoginForm(LoginForm):
    email = StringField("Email", render_kw={"placeholder": "Correo electrónico"})
    password = PasswordField("Contraseña", render_kw={"placeholder": "Contraseña"})
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField("Ingresar")