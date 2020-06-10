#!/bin/bash
echo '[*] Down Docker Container'
docker-compose -f docker-compose.test.yml down --remove-orphans
echo '[*] Build Images'
docker-compose -f docker-compose.test.yml build
echo '[*] Build Frontend'
docker-compose -f docker-compose.test.yml run --entrypoint "bash -c 'yarn install --production=false && yarn build'" frontend
echo '[*] Run Database'
docker-compose -f docker-compose.test.yml up -d es01 mongo
echo '[*] Wait for Start Database'
sleep 25
echo '[*] Run Services'
docker-compose -f docker-compose.test.yml up -d proxy
set -e
trap finally EXIT
function finally {
    echo '[*] Remove Files'
    docker-compose -f docker-compose.test.yml down
}

echo '[*] ES Log'
docker-compose -f docker-compose.test.yml logs es01
echo '[*] Test Start'
# ADD TEST SCRIPT HERE

docker-compose -f docker-compose.test.yml run --entrypoint 'pytest -v --cov=app --cov-report xml --cov-report term-missing' api

echo '[*] Test Completed!'

exit 0