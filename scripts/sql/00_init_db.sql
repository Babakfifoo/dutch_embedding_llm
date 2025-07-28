PRAGMA journal_mode=WAL;

-- Now, create the table with the specified column types.
CREATE TABLE IF NOT EXISTS landuse (
    imro VARCHAR PRIMARY KEY,
    selected_sample BOOLEAN,
    feasability_text TEXT,
    feasability_en TEXT,
    indicators TEXT
);