service nginx start
uvicorn main:api --log-level debug --port 6000 --reload