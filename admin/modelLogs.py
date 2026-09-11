from extensions import db

class Logs(db.Model):
    """Logs Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user = db.relationship('User', backref=db.backref('logs', lazy=True))

    def __str__(self):
        """Returns a string representative of Log"""
        return f"Log: '{self.action}' by User ID: {self.user_id} at {self.timestamp}."