PRAGMA journal_mode=WAL;

-- Now, create the table with the specified column types.
CREATE TABLE IF NOT EXISTS landuse (
    imro VARCHAR PRIMARY KEY,
    md_file TEXT,
    feasability_text TEXT,
    llm_cost_brief TEXT,
    agreement BOOLEAN,
    agreement_type VARCHAR,
);