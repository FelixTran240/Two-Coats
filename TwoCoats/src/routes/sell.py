from flask import Blueprint, request, jsonify
from services.database import create_sell_transaction, get_sell_transactions

sell_bp = Blueprint('sell', __name__)

@sell_bp.route('/sell', methods=['POST'])
def sell_item():
    data = request.get_json()
    item_name = data.get('item_name')
    price = data.get('price')
    
    if not item_name or not price:
        return jsonify({'error': 'Item name and price are required'}), 400
    
    transaction = create_sell_transaction(item_name, price)
    return jsonify(transaction), 201

@sell_bp.route('/sell', methods=['GET'])
def list_sells():
    transactions = get_sell_transactions()
    return jsonify(transactions), 200