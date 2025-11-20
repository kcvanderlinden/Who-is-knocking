# Base image already has rsyslog
FROM rsyslog/rsyslog:latest

# Install Python3 (apk is lightweight)
RUN apk add --no-cache python3 py3-pip

# Copy our application files
COPY kernel_log_processor.py /usr/local/bin/kernel_log_processor.py
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint executable
RUN chmod +x /entrypoint.sh

# We want rsyslog to run in the foreground
CMD ["/entrypoint.sh"]