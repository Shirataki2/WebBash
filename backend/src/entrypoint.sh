sleep 30

service nginx start
uvicorn main:api --log-level debug --port 6000