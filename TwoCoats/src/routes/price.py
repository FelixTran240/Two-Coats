from flask import Blueprint, request, jsonify
from services.database import SessionLocal
from models import Stock  # Adjust import if your Stock model is elsewhere

bp = Blueprint('price', __name__)

@bp.route('/price', methods=['GET'])
def check_price():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400

    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    db.close()

    if not stock:
        return jsonify({'error': 'Stock not found'}), 404

    return jsonify({'symbol': stock.symbol, 'price': stock.price}), 200