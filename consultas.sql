SELECT * FROM quotes;
SELECT * FROM tags;
SELECT * FROM quote_tag;
SELECT * FROM quotes ORDER BY id ASC;

DELETE FROM quotes
WHERE id NOT IN (
    SELECT MIN(id)
    FROM quotes
    GROUP BY text
);

-- Obtener el nombre de la secuencia asociada a la columna id
SELECT pg_get_serial_sequence('quotes', 'id');

ALTER SEQUENCE public.quotes_id_seq RESTART WITH 1;

SELECT q.id, q.text, q.author, t.name as tag
FROM quotes q
JOIN quote_tag qt ON q.id = qt.quote_id
JOIN tags t ON t.id = qt.tag_id;


SELECT q.id, q.text, q.author, t.name as tag
FROM quotes q
JOIN quote_tag qt ON q.id = qt.quote_id
JOIN tags t ON t.id = qt.tag_id
WHERE q.author = 'Autor Específico'
ORDER BY t.name;




SELECT * FROM quotes WHERE text IN (
    "The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.",
    "It is our choices, Harry, that show what we truly are, far more than our abilities.",
    "There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.",
    "The person, be it gentleman or lady, who has not pleasure in a good novel, must be intolerably stupid.",
    "Imperfection is beauty, madness is genius and it's better to be absolutely ridiculous than absolutely boring."
);

SELECT * FROM tags WHERE name IN ('inspirational', 'life', 'humor', 'philosophy', 'love', 'success', 'wisdom');


