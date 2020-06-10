#!/bin/bash
echo '[*] Down Docker Container'
docker-compose -f docker-compose.dev.yml down --remove-orphans
echo '[*] Build Images'
docker-compose -f docker-compose.dev.yml build
echo '[*] Prepare Frontend'
docker-compose -f docker-compose.dev.yml up -d frontend
echo '[*] Run Database'
docker-compose -f docker-compose.dev.yml up -d mongo
echo '[*] Wait for Start Database'
sleep 20
echo '[*] Run Services'
docker-compose -f docker-compose.dev.yml up -d api proxy
echo '[I] Service Started!'
echo -e "[I] To Run Frontend, execute \033[0;34m'docker-compose -f docker-compose.dev.yml exec frontend yarn serve'\033[0;39m"
echo "    and access to http://<host_ip>:<frontend_port>"

