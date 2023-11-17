FROM python:3.11.4-alpine3.18

ARG MONGO_URI

ENV MONGO_URI=${MONGO_URI}

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code

EXPOSE 6420

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6420", "--proxy-headers"]