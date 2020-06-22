#!/bin/bash
echo '[*] Down Docker Container'
docker-compose -f docker-compose.prod.yml down --remove-orphans
echo '[*] Build Images'
docker-compose -f docker-compose.prod.yml build
echo '[*] Migrate Alembic'
docker-compose -f docker-compose.prod.yml run -e PYTHONPATH='..' --entrypoint "bash -c \"pip install alembic;cd app;alembic revision --autogenerate -m \"$(date +%Y_%m_%d_%H_%M_%S)\";alembic upgrade head\"" api
echo '[*] Build Frontend'
docker-compose -f docker-compose.prod.yml run --entrypoint "bash -c 'yarn install --production=false && yarn build'" frontend
echo '[*] Run Database'
docker-compose -f docker-compose.prod.yml up -d mongo postgres
echo '[*] Wait for Start Database'
sleep 20
echo '[*] Run Services'
docker-compose -f docker-compose.prod.yml up -d --scale api=8 api proxy
