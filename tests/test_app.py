import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db, Quote, Tag

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        db.session.remove()
        db.drop_all()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Quotes' in response.data

def test_tag_page(client):
    # Crear datos de prueba
    tag = Tag(name='test_tag')
    db.session.add(tag)
    quote = Quote(text='This is a test quote.', author='Test Author', tags=[tag])
    db.session.add(quote)
    db.session.commit()

    response = client.get('/tag/test_tag')
    assert response.status_code == 200
    assert b'This is a test quote.' in response.data
    assert b'Test Author' in response.data
    assert b'test_tag' in response.data

def test_404_page(client):
    response = client.get('/non_existent_page')
    assert response.status_code == 404

