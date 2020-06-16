#!/bin/bash
echo '[*] Down Docker Container'
docker-compose -f docker-compose.test.yml down --remove-orphans
echo '[*] Build Images'
docker-compose -f docker-compose.test.yml build
echo '[*] Install Alembic'
docker-compose -f docker-compose.prod.yml run --entrypoint "pip install alembic" api
echo '[*] Database Migrate - Create Revision'
docker-compose -f docker-compose.dev.yml run -e PYTHONPATH='..' --entrypoint "bash -c \"cd app;alembic revision --autogenerate -m \"$(date +%Y_%m_%d_%H_%M_%S)\"\"" api
echo '[*] Database Migrate - Make Migrate'
docker-compose -f docker-compose.dev.yml run -e PYTHONPATH='..' --entrypoint "bash -c 'cd app;alembic upgrade head'" api
echo '[*] Build Frontend'
docker-compose -f docker-compose.test.yml run --entrypoint "bash -c 'yarn install --production=false && yarn build'" frontend
echo '[*] Run Database'
docker-compose -f docker-compose.test.yml up -d mongo postgres
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

echo '[*] Test Start'
# ADD TEST SCRIPT HERE
# docker-compose -f docker-compose.test.yml run --entrypoint 'pytest -v --cov=app --cov-report xml --cov-report term-missing' api
docker-compose -f docker-compose.test.yml run --entrypoint 'pytest -v --cov=app --cov-report xml --cov-report term-missing' api

echo '[*] Test Completed!'

exit 0