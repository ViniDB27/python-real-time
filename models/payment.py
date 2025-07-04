from repository.database import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False) 
    bank_payment_id = db.Column(db.String(200), nullable=True)
    qrcode = db.Column(db.String(100), nullable=True) 
    expiration_date = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'paid': self.paid,
            'bank_payment_id': self.bank_payment_id,
            'qrcode': self.qrcode,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None
        }
