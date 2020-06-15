#!/bin/bash
echo '[*] Down Docker Container'
docker-compose -f docker-compose.prod.yml down --remove-orphans
echo '[*] Build Images'
docker-compose -f docker-compose.prod.yml build
echo '[*] Build Frontend'
docker-compose -f docker-compose.prod.yml run --entrypoint "bash -c 'yarn install --production=false && yarn build'" frontend
echo '[*] Run Database'
docker-compose -f docker-compose.prod.yml up -d mongo postgres
echo '[*] Wait for Start Database'
sleep 20
echo '[*] Run Services'
docker-compose -f docker-compose.prod.yml up -d --scale api=8 api proxy