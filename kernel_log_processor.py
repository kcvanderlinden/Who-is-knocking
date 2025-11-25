#!/usr/bin/env python3
import sys
import sqlite3
import datetime
import re
import urllib.request
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

DB_PATH = '/var/log/kernel_logs.db'
TABLE = 'kernel_logs'

# Very tolerant regex: Mon DD HH:MM:SS host facility: message
PATTERN = r'''(?P<date>\d{4}-\d{2}-\d{2})[^0-9]*.*?
    (?P<time>\d{2}:\d{2}:\d{2})\s+2025.*?banIP/(?P<type>[^:]+):.*?
    SRC=(?P<src>\d{1,3}(?:\.\d{1,3}){3}).*?
    DST=(?P<dst>\d{1,3}(?:\.\d{1,3}){3})'''

# ----------------------------------------------------------------------
# Helper: IP → Country --------------------------------------------------
# ----------------------------------------------------------------------
def get_country(ip: str) -> str | None:
    """
    Return the country name for the given IPv4 address.

    The function queries the free ipapi.co JSON endpoint:
        https://ipapi.co/<ip>/json/

    Parameters
    ----------
    ip : str
        The IPv4 address to look up.

    Returns
    -------
    str | None
        The country name (e.g., "United States") if the lookup succeeds,
        otherwise None.
    """
    # Reject obviously private or malformed IPs early
    if not ip or ip.startswith('127.') or ip.startswith('10.') or \
       ip.startswith('192.168.') or ip.startswith('172.'):
        return None

    url = f'https://ip.rootnet.in/lookup/{ip}'
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
            print(data)
            # ipapi.co returns both the 2‑letter code and the full name
            return data.get('as')['country'] 
    except Exception:
        # Any network error, parsing error, or HTTP error simply yields None
        return None

def parse_line(line: str):
    try:
        m = re.search(PATTERN, line, re.VERBOSE)
    except:
        return None
    # print(m.groupdict())

    date_str, t_str, ban_type, src, dst = m.groupdict().values()
    ts_str = date_str + " " + t_str
    # Convert to ISO‑8601 UTC. dmesg uses local time by default,
    # but OpenWRT's logd logs UTC. Adjust if needed.
    ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    # Assume current year
    ts = ts.replace(year=datetime.datetime.utcnow().year)
    ts_iso = ts.replace(tzinfo=datetime.timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Look up countries
    # ------------------------------------------------------------------
    country_src = get_country(src)
    country_dst = get_country(dst)

    return (ts_iso, ban_type, src, dst, country_src, country_dst)

def insert_log(entry):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        f'INSERT INTO {TABLE} (ts, ban_type, src, dst, country_src, country_dst) VALUES (?, ?, ?, ?, ?, ?)',
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