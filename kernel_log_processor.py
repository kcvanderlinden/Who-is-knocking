#!/usr/bin/env python3
import sys
import sqlite3
import datetime
import re

DB_PATH = '/var/log/kernel_logs.db'
TABLE = 'kernel_logs'

# Very tolerant regex: Mon DD HH:MM:SS host facility: message
PATTERN = r'''(?P<date>\d{4}-\d{2}-\d{2})[^0-9]*.*?
    (?P<time>\d{2}:\d{2}:\d{2})\s+2025.*?banIP/(?P<type>[^:]+):.*?
    SRC=(?P<src>\d{1,3}(?:\.\d{1,3}){3}).*?
    DST=(?P<dst>\d{1,3}(?:\.\d{1,3}){3})'''

def parse_line(line: str):
    try:
        m = re.search(PATTERN, line, re.VERBOSE)
    except:
        return None
    print(m.groupdict())

    date_str, t_str, type, src, dst = m.groupdict().values()
    ts_str = date_str + " " + t_str
    # Convert to ISO‑8601 UTC. dmesg uses local time by default,
    # but OpenWRT's logd logs UTC. Adjust if needed.
    ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    # Assume current year
    ts = ts.replace(year=datetime.datetime.utcnow().year)
    ts_iso = ts.replace(tzinfo=datetime.timezone.utc).isoformat()

    severity = 'info'  # default – can be expanded
    return (ts_iso, type, src, dst)

def insert_log(entry):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        f'INSERT INTO {TABLE} (ts, facility, severity, message) VALUES (?, ?, ?, ?)',
        entry
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        entry = parse_line(line)
        if entry:
            insert_log(entry)