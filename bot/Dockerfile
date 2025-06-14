FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir -p ml/models

CMD ["python", "main.py"]


