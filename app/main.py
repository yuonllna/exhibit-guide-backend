from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_rood():
    return {"Hello": "World"}