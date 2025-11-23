FROM rsyslog/rsyslog:latest

# Install python3 (sqlite3 CLI is already in the base image)
RUN apk add --no-cache python3

# Copy everything we need into the image
COPY kernel_log_processor.py /usr/local/bin/kernel_log_processor.py
COPY entrypoint.sh /entrypoint.sh
COPY init.sql /init.sql
COPY rsyslog.conf /etc/rsyslog.conf

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Start the container with our script
CMD ["/entrypoint.sh"]