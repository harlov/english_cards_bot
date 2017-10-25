FROM python:3.6.3-alpine
WORKDIR /usr/src/app/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONPATH $PYTHONPATH:/usr/src/app

VOLUME ["/var/lib/english_cards"]
CMD [ "python", "./english_cards/bot.py", "config.json"]