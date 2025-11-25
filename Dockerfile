FROM rsyslog/rsyslog:latest

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
apt-get install -y --no-install-recommends \
    ca-certificates python3 python3-pip python3.12-venv \
    && rm -rf /var/lib/apt/lists/*

# Install runtime dependencies
COPY requirements.txt .
RUN python3 -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy everything we need into the image
COPY kernel_log_processor.py /usr/local/bin/kernel_log_processor.py
COPY entrypoint.sh /entrypoint.sh
COPY init.sql /init.sql
COPY rsyslog.conf /etc/rsyslog.conf

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Start the container with our script
ENTRYPOINT ["/entrypoint.sh"]