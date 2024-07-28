# scraper.py
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False, unique=True)
    author = Column(String(100), nullable=False)
    tags = Column(String(255))

Base.metadata.create_all(engine)

def scrape_quotes():
    base_url = 'https://quotes.toscrape.com/page/{}/'
    
    for page_num in range(1, 11):
        url = base_url.format(page_num)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        quotes = soup.find_all('div', class_='quote')

        for quote in quotes:
            text = quote.find('span', class_='text').get_text()
            author = quote.find('small', class_='author').get_text()
            tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
            
            # Verificar si la cita ya existe en la base de datos
            existing_quote = session.query(Quote).filter_by(text=text).first()
            if not existing_quote:
                quote_data = Quote(text=text, author=author, tags=', '.join(tags))
                session.add(quote_data)
            else:
                logger.info(f'Skipping duplicate quote: {text} by {author}')

    session.commit()
    logger.info("Scraping completo y datos guardados en la base de datos.")

if __name__ == '__main__':
    scrape_quotes()


