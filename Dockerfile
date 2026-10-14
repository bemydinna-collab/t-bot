FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium AND all required system dependencies automatically
RUN playwright install chromium --with-deps

COPY . .

CMD ["python", "discord_bot.py"]