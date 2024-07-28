import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import responses
from scraper import scrape_quotes, engine, Session, Quote, Tag
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def session():
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@responses.activate
def test_scrape_quotes(session):
    responses.add(
        responses.GET,
        'https://quotes.toscrape.com/page/1/',
        body="""<div class="quote">
                    <span class="text">"Test quote"</span>
                    <small class="author">Test Author</small>
                    <div class="tags">
                        <a class="tag">test_tag</a>
                    </div>
                </div>""",
        status=200
    )

    scrape_quotes()

    quotes = session.query(Quote).all()
    assert len(quotes) == 1
    assert quotes[0].text == '"Test quote"'
    assert quotes[0].author == 'Test Author'
    assert len(quotes[0].tags) == 1
    assert quotes[0].tags[0].name == 'test_tag'