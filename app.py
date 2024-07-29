from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import logging

load_dotenv()  # Cargar las variables de entorno desde el archivo .env

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Configurar Flask-Migrate

# Tabla de asociación many-to-many
quote_tag = db.Table('quote_tag',
    db.Column('quote_id', db.Integer, db.ForeignKey('quotes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False, unique=True)
    author = db.Column(db.String(100), nullable=False)
    tags = db.relationship('Tag', secondary=quote_tag, lazy='joined',
                           backref=db.backref('quotes', lazy=True))

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    about = db.Column(db.Text, nullable=True)

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    quotes = Quote.query.options(db.joinedload(Quote.tags)).order_by(Quote.id).paginate(page=page, per_page=per_page, error_out=False)
    
    for quote in quotes.items:
        logger.debug(f"Quote: {quote.text[:30]}..., Tags: {[tag.name for tag in quote.tags]}")
    
    return render_template('index.html', quotes=quotes)

@app.route('/tag/<tag_name>')
def tag(tag_name):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    quotes = Quote.query.filter(Quote.tags.contains(tag)).order_by(Quote.id).paginate(page=page, per_page=per_page, error_out=False)
    
    for quote in quotes.items:
        logger.debug(f"Quote: {quote.text[:30]}..., Tags: {[tag.name for tag in quote.tags]}")
    
    return render_template('index.html', quotes=quotes, current_tag=tag)

@app.route('/author/<author_name>')
def author(author_name):
    author = Author.query.filter_by(name=author_name).first_or_404()
    return render_template('author.html', author=author)

if __name__ == "__main__":
    app.run(debug=True)

