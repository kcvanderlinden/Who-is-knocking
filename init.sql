-- init.sql
CREATE TABLE IF NOT EXISTS kernel_logs (
    ts       TEXT,
    facility TEXT,
    severity TEXT,
    message  TEXT
);