from fastapi import FastAPI, HTTPException, status

app = FastAPI(
    title="Calculator API",
    description="Minimal utility service demonstrating query parameter "
                "validation and defensive error handling.",
)


@app.get("/")
def root():
    return {"service": "Calculator API", "status": "online", "docs": "/docs"}


@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}


@app.get("/subtract")
def subtract(a: int, b: int):
    return {"result": a - b}


@app.get("/multiply")
def multiply(a: int, b: int):
    return {"result": a * b}


@app.get("/divide")
def divide(a: int, b: int):
    if b == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Division by zero is not allowed")
    return {"result": a / b}


@app.get("/modulo")
def modulo(a: int, b: int):
    if b == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Modulo by zero is not allowed")
    return {"result": a % b}
