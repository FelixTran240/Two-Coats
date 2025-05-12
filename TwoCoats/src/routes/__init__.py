from .buy import buy_routes
from .sell import sell_routes

def init_routes(app):
    app.register_blueprint(buy_routes)
    app.register_blueprint(sell_routes)