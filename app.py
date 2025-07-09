from flask import Flask, jsonify, request, send_file, render_template
from repository.database import db
from models.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


db.init_app(app)
socketio = SocketIO(app)

@app.route('/payments/pix', methods=['POST'])
def create_payment_pix():
    data = request.get_json()
    if 'value' not in data:
        return jsonify({'error': 'Invalid value'}), 400
    expiration_date = datetime.now() + timedelta(minutes=30)
    new_payment = Payment(value=data['value'], expiration_date=expiration_date)
    pix = Pix()
    payment_pix = pix.create_payment()
    new_payment.bank_payment_id = payment_pix['bank_payment_id']
    new_payment.qrcode = payment_pix['qrcode_path']
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({
        'message': 'Payment created successfully', 
        'method': 'pix',
        'payment': new_payment.to_dict(),
    }), 201

@app.route('/payments/pix/qr_code/<file_name>', methods=['GET'])
def get_qr_code(file_name):
   return send_file(f'static/img/{file_name}.png', mimetype='image/png')

@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_confirmation():
    data = request.get_json()
    if 'bank_payment_id' not in data and 'value' not in data:
        return jsonify({'error': 'Invalid payment data'}), 400
    payment = Payment.query.filter_by(bank_payment_id=data.get('bank_payment_id')).first()
    if not payment or payment.paid:
        return jsonify({'error': 'Payment not found'}), 404
    if data.get('value') != payment.value:
        return jsonify({'error': 'Invalid payment data'}), 400
    payment.paid = True
    db.session.commit()
    socketio.emit(f'payment-confirmed-{payment.id}')
    return jsonify({'message': 'Payment confirmed successfully', 'method': 'pix'}), 201

@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)
    if payment.paid:
        return render_template('confirmed_payment.html',
            payment_id=payment.id,
            value=payment.value,
        )
    return render_template(
        'payment.html',
        payment_id=payment.id, 
        value=payment.value, 
        host="http://127.0.0.1:5000",
        qr_code=payment.qrcode,
    )

# websocket
@socketio.on('connect')
def handle_connect():
    print('Client connected to the server')

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)