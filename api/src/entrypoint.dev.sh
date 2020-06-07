service nginx start
uvicorn app.main_fastapi:api --log-level debug --port 6000 --reload