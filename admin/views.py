from extensions import db
from extensions import app
from admin.viewsAnalisis import vistasAnalisis
from admin.viewsUser import vistasUsuario
from admin.viewsLogs import vistasLogs


def vistas(admin):
    vistasAnalisis(admin)
    vistasUsuario(admin)
    vistasLogs(admin)

