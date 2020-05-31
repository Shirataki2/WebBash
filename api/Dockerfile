FROM python:3.8 as DEV
RUN apt update -y && \
    apt upgrade -y && \
    apt install -y nginx
COPY etc/nginx/sites-enabled/* /etc/nginx/sites-enabled
RUN apt install curl && \
    curl -fsSL get.docker.com -o get-docker.sh && \
    sh get-docker.sh
COPY src/ /app
WORKDIR /app
RUN pip install -r requirements.txt

FROM python:3.8 as PROD
RUN apt update -y && \
    apt upgrade -y && \
    apt install -y nginx
COPY etc/nginx/sites-enabled/* /etc/nginx/sites-enabled
RUN apt install curl && \
    curl -fsSL get.docker.com -o get-docker.sh && \
    sh get-docker.sh
COPY src/ /app
WORKDIR /app
RUN pip install -r requirements.txt