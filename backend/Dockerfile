FROM python:3.11.6-slim
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
ARG MONGO_DB_NAME
ARG MONGO_URI

ARG GOOGLE_CLIENT_ID
ARG GOOGLE_CLIENT_SECRET

ARG ENCRYPTION_KEY

ARG ALLOWED_DOMAINS
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
ENV MONGO_DB_NAME=${MONGO_DB_NAME}
ENV MONGO_URI=${MONGO_URI}

ENV GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
ENV GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}

ENV ENCRYPTION_KEY=${ENCRYPTION_KEY}

ENV ALLOWED_DOMAINS=${ALLOWED_DOMAINS}
ENV PROD=true
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

RUN apt update
RUN apt upgrade
RUN apt install g++ libffi-dev -y

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]