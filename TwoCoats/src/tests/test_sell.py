from flask import Flask, jsonify, request
from services.database import db_session
from models import Transaction

app = Flask(__name__)

@app.route('/sell', methods=['POST'])
def sell_item():
    data = request.json
    item_name = data.get('item_name')
    quantity = data.get('quantity')
    price = data.get('price')

    if not item_name or not quantity or not price:
        return jsonify({'error': 'Missing data'}), 400

    transaction = Transaction(item_name=item_name, quantity=quantity, price=price, transaction_type='sell')
    db_session.add(transaction)
    db_session.commit()

    return jsonify({'message': 'Item sold successfully', 'transaction_id': transaction.id}), 201

@app.route('/sell/<int:transaction_id>', methods=['GET'])
def get_sell_transaction(transaction_id):
    transaction = db_session.query(Transaction).filter_by(id=transaction_id, transaction_type='sell').first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    return jsonify({
        'transaction_id': transaction.id,
        'item_name': transaction.item_name,
        'quantity': transaction.quantity,
        'price': transaction.price,
        'transaction_type': transaction.transaction_type
    }), 200

if __name__ == '__main__':
    app.run(debug=True)