import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import logging
import os
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
logger.info(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")  # Log the database URL without credentials

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Tabla de asociación many-to-many
quote_tag = Table('quote_tag', Base.metadata,
    Column('quote_id', Integer, ForeignKey('quotes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False, unique=True)
    author = Column(String(100), nullable=False)
    tags = relationship('Tag', secondary=quote_tag, lazy='subquery',
                        backref='quotes')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

def scrape_quotes():
    base_url = 'https://quotes.toscrape.com/page/{}/'
    
    for page_num in range(1, 11):
        url = base_url.format(page_num)
        logger.info(f"Scraping page: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        quotes = soup.find_all('div', class_='quote')
        logger.info(f"Found {len(quotes)} quotes on page {page_num}")

        for quote in quotes:
            text = quote.find('span', class_='text').get_text()
            author = quote.find('small', class_='author').get_text()
            tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]

            logger.info(f"Processing quote: {text[:30]}... by {author}")
            logger.info(f"Tags: {tags}")

            # Verificar si la cita ya existe en la base de datos
            existing_quote = session.query(Quote).filter_by(text=text).first()
            if not existing_quote:
                quote_data = Quote(text=text, author=author)
                session.add(quote_data)
                logger.info(f'Added new quote: {text[:30]}...')
            else:
                quote_data = existing_quote
                logger.info(f'Updating existing quote: {text[:30]}...')

            # Actualizar tags
            for tag_name in tags:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    logger.info(f'Added new tag: {tag_name}')
                if tag not in quote_data.tags:
                    quote_data.tags.append(tag)
                    logger.info(f'Added tag {tag_name} to quote: {text[:30]}...')

        try:
            session.commit()
            logger.info(f"Committed changes for page {page_num}")
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            session.rollback()

    logger.info("Scraping completo y datos guardados en la base de datos.")

if __name__ == '__main__':
    # Verificar la conexión a la base de datos
    try:
        connection = engine.connect()
        logger.info("Successfully connected to the database")
        connection.close()
    except Exception as e:
        logger.error(f"Error connecting to the database: {str(e)}")
        exit(1)

    # Crear tablas si no existen
    Base.metadata.create_all(engine)
    logger.info("Database tables created (if they didn't exist)")

    # Ejecutar el scraping
    scrape_quotes()

    # Verificar los datos insertados
    quote_count = session.query(Quote).count()
    tag_count = session.query(Tag).count()
    logger.info(f"Total quotes in database: {quote_count}")
    logger.info(f"Total tags in database: {tag_count}")

def print_database_contents():
    quotes = session.query(Quote).all()
    for quote in quotes:
        print(f"Quote: {quote.text[:30]}...")
        print(f"Author: {quote.author}")
        print(f"Tags: {[tag.name for tag in quote.tags]}")
        print("---")



