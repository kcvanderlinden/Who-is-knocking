import sys
import sqlite3
import datetime
import re
import os

DB_PATH = '/var/log/kernel_logs.db'
TABLE   = 'kernel_logs'

# Very tolerant regex: Mon DD HH:MM:SS host facility: message
LOG_RE = re.compile(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+[^ ]+\s+([^:]+):\s*(.*)$')

def init_db():
    """Create the table if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE} (
            ts TEXT,
            facility TEXT,
            severity TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

def parse_line(line: str):
    """Return a tuple (ts_iso, facility, severity, message) or None."""
    m = LOG_RE.match(line)
    if not m:
        return None
    ts_str, facility, msg = m.group(1, 2, 3)

    # dmesg → local time; OpenWRT logs → UTC
    ts = datetime.datetime.strptime(ts_str, "%b %d %H:%M:%S")
    # Assume current year (makes sense for the container)
    ts = ts.replace(year=datetime.datetime.utcnow().year)
    ts_iso = ts.replace(tzinfo=datetime.timezone.utc).isoformat()

    # The regex does not expose severity – keep it “info” for now.
    severity = 'info'
    return (ts_iso, facility, severity, msg)

def insert_log(entry):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        f'INSERT INTO {TABLE} (ts, facility, severity, message) VALUES (?, ?, ?, ?)',
        entry
    )
    conn.commit()
    conn.close()

def main():
    init_db()
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        entry = parse_line(line)
        if entry:
            insert_log(entry)

if __name__ == "__main__":
    main()