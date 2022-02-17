FROM python:3.11.0a5-alpine3.14

WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["flask","run"]