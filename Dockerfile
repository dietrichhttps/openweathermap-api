FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Use entrypoint to ensure errors.log is a file
ENTRYPOINT ["./entrypoint.sh"]
