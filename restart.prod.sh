docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.dev.yml up -d frontend
docker-compose -f docker-compose.dev.yml exec frontend yarn install
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d es01 es02 mongo
docker-compose -f docker-compose.prod.yml up frontend
docker-compose -f docker-compose.prod.yml up -d --scale api=8 kibana api proxy