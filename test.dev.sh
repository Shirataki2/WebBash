#!/bin/bash
rm -f ./api/src/test.sqlite
docker-compose -f docker-compose.test.yml run --entrypoint 'pytest -v --cov=app --cov-report xml --cov-report html --cov-report term-missing' api