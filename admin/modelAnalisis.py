from extensions import db

class Analisis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cuenca = db.Column(db.String(10), nullable=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    ficheroPesos = db.Column(db.String(255), nullable=True)
    ficheroResultados = db.Column(db.String(255), nullable=True)
    ficheroPng = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.String(55), nullable=True)
    metodo = db.Column(db.String(55), nullable=True)
    tiempo = db.Column(db.Float , nullable=True)
    valoracion = db.Column(db.Integer , nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    usuario = db.relationship('User', backref=db.backref('Analisis', lazy=True))
    '''users = db.relationship('User', secondary=studies_users,
                            backref=db.backref('studies', lazy='dynamic'))'''
    def __str__(self):
        """Returns a string representative of Studies"""
        return f"Analisis: '{str(self.nombre)}', description: {self.descripcion}."