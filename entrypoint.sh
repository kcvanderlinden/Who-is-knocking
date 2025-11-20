#!/bin/sh
# 1. Start rsyslog in background
rsyslogd -n &
RSYS_PID=$!

# 2. Wait until the remote log file is present.
#    (rsyslog might not create it instantly, but it will be there soon.)
until [ -f /var/log/remote.log ]; do
    sleep 1
done

# 3. Tail the file and pipe it to our Python worker.
#    tail -F keeps the worker alive if the file is rotated.
tail -F /var/log/remote.log | python3 /usr/local/bin/kernel_log_processor.py

# 4. Wait for rsyslog to exit (if it ever does)
wait $RSYS_PID