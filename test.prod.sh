docker-compose -f docker-compose.test.yml down
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml run --entrypoint "bash -c 'yarn install --production=false && yarn build'" frontend
docker-compose -f docker-compose.test.yml up -d es01 es02 mongo
sleep 20
docker-compose -f docker-compose.test.yml up -d --scale api=8 kibana api proxy

docker-compose -f docker-compose.test.yml exec api pytest

docker-compose -f docker-compose.test.yml down
