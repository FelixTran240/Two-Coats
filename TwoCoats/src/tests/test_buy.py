import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_buy(client):
    response = client.post('/buy', json={
        'item_id': 1,
        'quantity': 2,
        'price': 100.0
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['item_id'] == 1
    assert data['quantity'] == 2
    assert data['price'] == 100.0

def test_get_buy(client):
    response = client.get('/buy/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['item_id'] == 1
    assert data['quantity'] == 2
    assert data['price'] == 100.0

def test_get_nonexistent_buy(client):
    response = client.get('/buy/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Buy transaction not found'