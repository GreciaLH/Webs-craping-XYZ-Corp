# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import logging

load_dotenv()  # Cargar las variables de entorno desde el archivo .env

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Quote(db.Model):
    __tablename__ = 'quotes'  # Asegúrate de que el nombre de la tabla es correcto
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(255))

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    quotes = Quote.query.all()
    for quote in quotes:
        logger.debug(f'Quote: {quote.text} by {quote.author}')
    return render_template('index.html', quotes=quotes)  # Renderizar la plantilla con los datos

if __name__ == "__main__":
    app.run(debug=True)
