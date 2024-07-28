SELECT * FROM quotes;
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

UPDATE quotes SET id = DEFAULT;