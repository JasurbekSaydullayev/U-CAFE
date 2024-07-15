FROM python:3.10.12-alpine

WORKDIR /app

COPY req.txt req.txt

RUN pip install --upgrade pip
RUN pip install -r req.txt

COPY . .

#CMD ["daphne", "-b", "0.0.0.0", "-p", "4000", "ucafe.asgi:application"]
