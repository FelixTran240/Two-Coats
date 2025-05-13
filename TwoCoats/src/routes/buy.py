from flask import Blueprint, request, jsonify
from services.database import create_buy_transaction, get_buy_transactions

buy_bp = Blueprint('buy', __name__)

@buy_bp.route('/buy', methods=['POST'])
def buy():
    data = request.json
    if not data or 'item' not in data or 'amount' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    
    transaction = create_buy_transaction(data['item'], data['amount'])
    return jsonify(transaction), 201

@buy_bp.route('/buy', methods=['GET'])
def get_buys():
    transactions = get_buy_transactions()
    return jsonify(transactions), 200