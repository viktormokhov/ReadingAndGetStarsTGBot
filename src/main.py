# Если используется Uvicorn или Gunicorn, main.py нужен только чтобы указать:
# uvicorn main:app
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)