-- init.sql
CREATE TABLE IF NOT EXISTS kernel_logs (
    ts          TEXT,
    ban_type    TEXT,
    src         TEXT,
    dst         TEXT, 
    country_src TEXT,
    country_dst TEXT
);