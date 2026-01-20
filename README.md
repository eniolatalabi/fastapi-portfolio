# FastAPI Portfolio

Welcome to my backend development portfolio. This repository serves as a monorepo containing multiple isolated applications built with **FastAPI**.

Each project demonstrates different backend concepts, from RESTful architecture and Pydantic validation to algorithmic logic.

## 📂 Projects Overview

| Project                                | Description                                    | Key Concepts                                  |
| :------------------------------------- | :--------------------------------------------- | :-------------------------------------------- |
| **[Social Media API](./social-media)** | A CRUD API mimicking a social network feed.    | REST Methods, Pydantic Models, Error Handling |
| **[Calculator API](./calculator)**     | A utility service for mathematical operations. | Query Parameters, Logic Implementation        |

##  Tech Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Package Manager:** uv (or pip)

##  Setup & Installation

To run any of the projects in this portfolio, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/eniolatalabi/fastapi-portfolio.git](https://github.com/eniolatalabi/fastapi-portfolio.git)
   cd fastapi-portfolio
   ```

2. Install Dependencies: Using uv (Recommended):

Bash
uv sync
Or using standard pip:

Bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn

3. Run a Project: Navigate to the specific project folder or check the project READMEs linked above for specific run commands.
