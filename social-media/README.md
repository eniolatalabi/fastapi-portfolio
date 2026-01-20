The SOCIAL MEDIA README
**File Location:** `fastapi-portfolio/social-media/README.md`
**Purpose:** Documentation for the posts application.

````markdown
# 📱 Social Media API

A lightweight RESTful API designed to handle social media posts. This application demonstrates standard **CRUD** (Create, Read, Update, Delete) operations using an in-memory database structure.

##  Features

- **Create Posts:** Users can submit new posts with title and content validation.
- **Read Feed:** Retrieve all posts or fetch a specific post by ID.
- **Delete Posts:** Remove posts from the feed with error handling for non-existent IDs.
- **Validation:** strictly typed data using Pydantic models.

##  How to Run

From the **root** of the repository (`fastapi-portfolio`), run:

```bash
# Using uv
uv run uvicorn social-media.main:app --reload

# Using standard python
uvicorn social-media.main:app --reload
```
````

🔗 API Endpoints
Method Endpoint Function Payload / Notes
GET /posts Get all posts -
GET /posts/latest Get the newest post -
GET /posts/{id} Get post by ID Path Param: id (int)
POST /posts Create a post JSON: {"title": "...", "content": "..."}
DELETE /posts/{id} Delete a post Path Param: id (int)

Interactive Docs: Once running, visit http://127.0.0.1:8000/docs to test the endpoints.
