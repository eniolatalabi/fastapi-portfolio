from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/add")
async def add(a: int, b: int):
    return { a + b}

@app.get("/subtract")
def subtract(a: int, b: int):
    return {"result": a - b}

@app.get("/multiply")
def multiply(a: int, b: int):
    return {"result": a * b}

@app.get("/divide")
def divide(a: int, b: int):
    return {"result": a / b}

@app.get("/modulo")
def modulo(a: int, b: int):
    return {"result": a % b}

@app.get("/square")
def square(a: int):
    return {"result": a**2}