#!/bin/sh
set -e

# 1️⃣ Create the database (if needed)
DB="/var/log/kernel_logs.db"
if [ ! -f "$DB" ]; then
    echo "Creating new SQLite DB at $DB"
    sqlite3 "$DB" < /init.sql
fi

# 2️⃣ Start rsyslog in the background
rsyslogd -n &
RSYS_PID=$!

# 3️⃣ Wait for the log file that rsyslog writes
until [ -f /var/log/remote.log ]; do
    sleep 1
done

# 4️⃣ Tail it and feed the Python processor
tail -F /var/log/remote.log | python3 /usr/local/bin/kernel_log_processor.py

# 5️⃣ Keep the container alive (rsyslog)
wait $RSYS_PID