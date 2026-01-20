The CALCULATOR README
**File Location:** `fastapi-portfolio/calculator/README.md`
**Purpose:** Documentation for the math application.

````markdown
# Calculator API

A utility API that performs mathematical operations via HTTP requests. This project demonstrates how to handle **Query Parameters** in FastAPI.

## Features

- Supports basic arithmetic: Addition, Subtraction, Multiplication, Division.
- Advanced operations: Modulo (Remainder) and Squaring.
- Type validation to ensure inputs are integers.

## How to Run

From the **root** of the repository (`fastapi-portfolio`), run:

```bash
# Using uv
uv run uvicorn calculator.main:app --reload

# Using standard python
uvicorn calculator.main:app --reload

```
````

API Endpoints
All endpoints use query parameters (e.g., ?a=10&b=5).

Endpoint Description Example Usage
/add Sum of a and b /add?a=10&b=5
/subtract a minus b /subtract?a=10&b=5
/multiply a times b /multiply?a=10&b=5
/divide a divided by b /divide?a=10&b=5
/modulo Remainder of a / b /modulo?a=10&b=3
/square a squared /square?a=5
