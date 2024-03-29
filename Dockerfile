FROM python:3.11-slim

EXPOSE 5000

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [  "python3", "main.py" ]