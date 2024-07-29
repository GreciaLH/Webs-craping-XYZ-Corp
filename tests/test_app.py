import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db, Quote, Tag
import logging

@pytest.fixture
def client():
	app.config['TESTING'] = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
	with app.test_client() as client:
		with app.app_context():
			db.create_all()
		yield client
		with app.app_context():
			db.drop_all()

def test_pagination_on_index_page(client):
	# Crear múltiples citas
	for i in range(15):
		quote = Quote(text=f'Test quote {i}', author='Author', tags=[])
		db.session.add(quote)
	db.session.commit()

	# Test de la primera página
	response = client.get('/?page=1')
	assert response.status_code == 200
	assert b'Test quote 0' in response.data
	assert b'Test quote 9' in response.data
	assert b'Test quote 10' not in response.data

	# Test de la segunda página
	response = client.get('/?page=2')
	assert response.status_code == 200
	assert b'Test quote 10' in response.data
	assert b'Test quote 14' in response.data
	assert b'Test quote 0' not in response.data

def test_tag_filtering(client):
	# Crear etiquetas y citas
	tag1 = Tag(name='tag1')
	tag2 = Tag(name='tag2')
	db.session.add(tag1)
	db.session.add(tag2)
	db.session.commit()

	quote1 = Quote(text='Quote with tag1', author='Author1', tags=[tag1])
	quote2 = Quote(text='Quote with tag2', author='Author2', tags=[tag2])
	db.session.add(quote1)
	db.session.add(quote2)
	db.session.commit()

	# Test de filtrado por tag1
	response = client.get('/tag/tag1')
	assert response.status_code == 200
	assert b'Quote with tag1' in response.data
	assert b'Quote with tag2' not in response.data

	# Test de filtrado por tag2
	response = client.get('/tag/tag2')
	assert response.status_code == 200
	assert b'Quote with tag2' in response.data
	assert b'Quote with tag1' not in response.data

def test_logging(client, caplog):
	# Crear una cita y etiqueta
	tag = Tag(name='log_tag')
	quote = Quote(text='Log test quote', author='Log Author', tags=[tag])
	db.session.add(tag)
	db.session.add(quote)
	db.session.commit()

	# Test de logging en la página de inicio
	with caplog.at_level(logging.DEBUG):
		client.get('/')
		assert any('Quote: Log test quote' in message for message in caplog.messages)

	# Test de logging en la página de etiqueta
	with caplog.at_level(logging.DEBUG):
		client.get('/tag/log_tag')
		assert any('Quote: Log test quote' in message for message in caplog.messages)