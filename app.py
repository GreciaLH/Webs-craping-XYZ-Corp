# app.py
from flask import Flask, render_template, request
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
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False, unique=True)
    author = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(255))

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    # Obtener el número de página actual desde los parámetros de la URL
    page = request.args.get('page', 1, type=int)
    per_page = 10
    quotes = Quote.query.order_by(Quote.id).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('index.html', quotes=quotes)

if __name__ == "__main__":
    app.run(debug=True)

