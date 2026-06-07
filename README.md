# FastAPI Portfolio

![tests](https://github.com/eniolatalabi/fastapi-portfolio/actions/workflows/ci.yml/badge.svg)

A backend monorepo containing two FastAPI services: a JWT-authenticated
Social Media API with object-level authorization, and a small Calculator
utility service. Every push runs a 30-test suite in CI.

## Social Media API

A CRUD API for users, posts, and votes, built with FastAPI, SQLAlchemy
2.0, PostgreSQL, and Alembic migrations.

### Endpoints

| Method | Path          | Auth | Description                              |
| ------ | ------------- | ---- | ---------------------------------------- |
| POST   | /login        | No   | Exchange credentials for an access and refresh token pair (rate limited) |
| POST   | /refresh      | No   | Rotate a refresh token for a new pair     |
| POST   | /logout       | No   | Revoke a refresh token, ending the session |
| POST   | /users        | No   | Register (email, password, optional phone)|
| GET    | /users/me     | Yes  | Own profile                               |
| PUT    | /users/me     | Yes  | Update own email, password, or phone      |
| DELETE | /users/me     | Yes  | Delete own account (posts/votes cascade)  |
| GET    | /users/{id}   | No   | Public profile by id                      |
| GET    | /posts        | No   | List posts with vote counts, search, pagination |
| GET    | /posts/{id}   | No   | Single post with vote count               |
| POST   | /posts        | Yes  | Create a post                             |
| PUT    | /posts/{id}   | Yes  | Update an owned post                      |
| DELETE | /posts/{id}   | Yes  | Delete an owned post                      |
| POST   | /vote/        | Yes  | Like (dir=1) or unlike (dir=0) a post     |
| GET    | /health       | No   | Liveness probe for the platform           |

Interactive documentation lives at `/docs` once the server is running.

### Security design

- **Authentication vs authorization are enforced separately.** A valid
  JWT identifies you; ownership checks decide what you may touch.
- **Object-level authorization returns 404, not 403.** A caller who
  does not own a post learns nothing about whether it exists. The test
  suite includes cross-user attack simulations proving this.
- **Failed login is 401** with a WWW-Authenticate header and a single
  generic message, so responses never reveal which credential was wrong.
- **Tokens for deleted accounts are rejected.** A cryptographically
  valid JWT whose user no longer exists raises 401 instead of leaking a
  None user into request handlers.
- **CORS is an explicit allowlist** from configuration. Wildcard
  origins with credentials are rejected by browsers and are never the
  right trust boundary; the allowlist is set via CORS_ORIGINS.
- **The /users/me design removes a whole attack surface.** Account
  mutations take no id parameter, so there is no way to address another
  user's account at all.
- **Passwords are bcrypt-hashed** via passlib; plaintext never touches
  the database, and password updates rotate credentials immediately.
- **Refresh tokens are database-backed, rotated, and reuse-aware.**
  Access tokens live 30 minutes; refresh tokens live 7 days and are
  recorded server-side, which is what makes three things possible that
  stateless JWTs cannot do: rotation on every use, a real logout, and
  reuse detection. Presenting an already-rotated token is treated as a
  breach signal and revokes every session for that user.
- **Token types are enforced both ways.** A refresh token never passes
  as an access token at protected routes, and an access token is never
  accepted at /refresh.
- **Login is rate limited** (default 5/minute per client, configurable
  via LOGIN_RATE_LIMIT) so credential stuffing meets a 429, not an
  open door.

### Observability

Every request emits one structured log line: method, path, status, and
duration in milliseconds. Unhandled exceptions are logged with a full
stack trace before becoming a 500, so production failures are never
silent. Error tracking is Sentry-ready: initialise the SDK with a DSN
in main.py and the existing exception path feeds it.

**Out of scope, by design:** password-reset emails and admin roles.
Each would add real infrastructure; their absence here is a deliberate
boundary, not an oversight.

### Tests

Forty-two tests cover every endpoint against an isolated in-memory
database on every push: registration and duplicate conflicts, the full
login matrix including the 429 rate limit, refresh rotation with the
reuse-detection family revocation, logout, profile self-service with
credential rotation, post CRUD, vote cycles, structured log emission,
and the cross-user BOLA attacks. Line coverage is 95%, and CI fails
any push that drops below 92%.

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests -q
```

### Database and migrations

```bash
alembic upgrade head
```

The second migration makes `users.phone_number` nullable: the column
was NOT NULL with no API input path, which made registration violate
its own schema. It is now an optional profile field exposed through
the user schemas and the /users/me endpoints.

### Configuration

Copy `.env.example` to `.env`. Either `DATABASE_URL` (typical on
Render) or all five discrete `DATABASE_*` variables (typical locally)
must be set; the settings object fails fast with a clear message if
neither source is complete.

### Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn social_media.main:app --reload
```

### Deployment (Render)

The Procfile runs gunicorn with uvicorn workers. Configure a Web
Service with build command `pip install -r requirements.txt`, health
check path `/health`, and environment variables `DATABASE_URL`,
`SECRET_KEY`, and `CORS_ORIGINS` set to the production frontend
origin. Run `alembic upgrade head` against the production database
after the first deploy and after any migration.

Live API: https://fastapi-portfolio-leme.onrender.com/docs

## Calculator API

A deliberately small service demonstrating typed query parameters and
defensive error handling: division and modulo by zero return a clean
400 instead of a stack trace.

```bash
uvicorn calculator.main:app --reload --port 8001
```

## Project structure

```
fastapi-portfolio/
├── social_media/
│   ├── main.py            # app, CORS allowlist, health endpoint
│   ├── config.py          # validated settings, fail-fast database config
│   ├── database.py        # engine, session dependency
│   ├── models.py          # SQLAlchemy models, portable server defaults
│   ├── schemas.py         # Pydantic request/response models
│   ├── oauth2.py          # token creation, rotation, reuse detection
│   ├── limiter.py         # shared rate limiter instance
│   ├── utils.py           # password hashing
│   └── routers/           # auth, users, posts, votes
├── calculator/
├── alembic/               # migrations
├── tests/                 # 42-test suite with sqlite fixtures
├── .github/workflows/     # CI: tests on every push
├── .env.example
├── requirements.txt       # pinned runtime dependencies
└── requirements-dev.txt   # pinned test dependencies
```
