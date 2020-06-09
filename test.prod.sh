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
sleep 15
echo '[*] Run Services'
docker-compose -f docker-compose.test.yml up -d api proxy
set -e
trap catch ERR
trap finally EXIT
function catch {
    echo '[!] Test Failed'
}
function finally {
    echo '[*] Remove Files'
    docker-compose -f docker-compose.test.yml down
}

echo '[*] Test Start'
# ADD TEST SCRIPT HERE
docker-compose -f docker-compose.test.yml exec api bash -c 'pytest'
echo '[*] Test Completed!'

exit 0