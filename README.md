# CocktailBot

> A Telegram bot that helps you discover cocktails by name or by the ingredients you have at hand.

---

## Demo

| /start | /name | /ingredients |
|--------|-------------|--------------------------|
| ![start](docs/screenshots/start.jpg) | ![by_name](docs/screenshots/by_name.jpg) | ![by_ingredients](docs/screenshots/by_ingredients.jpg) |

---

## Product Context

### End Users
Home bartenders, cocktail enthusiasts, and anyone who wants to know what they can mix from what's in their fridge.

### Problem Solved
Users don't know which cocktails they can make from available ingredients, or they want a quick recipe without leaving Telegram.

### Solution
CocktailBot is a Telegram bot backed by a FastAPI service and PostgreSQL database. It searches [TheCocktailDB](https://www.thecocktaildb.com/) public API and caches results locally. Users can ask for cocktail recipes by name or send a list of ingredients to find matching cocktails.

---

## Architecture

```
┌──────────────────┐       HTTP        ┌──────────────────────┐
│  Telegram User   │ ◄───────────────► │  Telegram Bot        │
└──────────────────┘                   │  (aiogram 3.x)       │
                                        └──────────┬───────────┘
                                                   │
┌──────────────────┐       HTTP        ┌──────────▼───────────┐
│  Browser User    │ ◄───────────────► │  React Frontend      │
│  localhost:3000  │                   │  (Vite + shadcn/ui)  │
└──────────────────┘                   └──────────┬───────────┘
                                                   │ HTTP REST
                                        ┌──────────▼───────────┐
                                        │  FastAPI Backend      │
                                        │  /cocktails/by-name   │
                                        │  /cocktails/by-ingr.  │
                                        │  /cocktails/random    │
                                        │  /history             │
                                        │  /favorites           │
                                        └──────────┬────────────┘
                                        ┌──────────┼────────────┐
                                        │          │            │
                               ┌────────▼───┐  ┌──▼────────────┐
                               │ PostgreSQL  │  │ TheCocktailDB │
                               │ (cache +   │  │  Public API   │
                               │  history)  │  └───────────────┘
                               └────────────┘
```

**Services:**
| Service | Technology | Port |
|---------|-----------|------|
| Frontend | React + Vite + Nginx | 3000 |
| Bot | Python + aiogram 3.x | — |
| Backend | Python + FastAPI | 8000 |
| Database | PostgreSQL 16 | 5432 |
| pgAdmin | pgAdmin 4 | 5050 |

---

## Features

### Version 1 ✅ (Implemented)
- `/start` — Welcome message
- `/help` — Full command reference
- `/name <cocktail>` — Search cocktail by name, returns full recipe
- `/ingredients <list>` — Search cocktails by comma-separated ingredients
- `/history` — View recent searches (stored in PostgreSQL)
- `/favorites` — View saved favorites
- `/favorite <name>` — Save a cocktail to favorites
- Plain-text message handling (deterministic intent detection)
- Graceful error handling and user-friendly messages
- Full Dockerization (backend + db + bot)
- PostgreSQL caching of API results and search history

### Version 2 ✅ (Implemented)
- Optional LLM-based intent detection (via OpenRouter or any OpenAI-compatible API)
- Favorites management (add, view)
- Nice HTML-formatted messages with emojis
- CLI test mode for handler logic verification without a real Telegram connection
- Automatic result caching in PostgreSQL (avoids redundant API calls)

### Planned / Not Yet Implemented
- Inline keyboard shortcuts for multi-result selection
- Remove from favorites command
- User-specific cocktail ratings
- Pagination for large result sets
- Image thumbnails via Telegram photo messages

---

## Usage

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome screen |
| `/help` | Show all commands |
| `/name Mojito` | Get the Mojito recipe |
| `/name Old Fashioned` | Get the Old Fashioned recipe |
| `/ingredients vodka, lime, mint` | Find cocktails using those ingredients |
| `/history` | Show your recent searches |
| `/favorites` | Show your saved cocktails |
| `/favorite Margarita` | Save Margarita to favorites |

### Plain-Text Messages

You can also just send free text — the bot will detect your intent:

| You send | Bot interprets |
|----------|---------------|
| `Margarita` | Search by name |
| `vodka, lime, mint` | Search by ingredients |
| `what can I make with gin and tonic?` | Search by ingredients |
| `how to make a Cosmopolitan` | Search by name |

---

## Local Deployment

### Requirements
- **OS:** Ubuntu 22.04 / 24.04 (or macOS / any Linux with Docker)
- **Docker:** 24.0+ with Docker Compose v2 (`docker compose`)
- **Git**
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and set your bot token:

```dotenv
BOT_TOKEN=...
```

All other defaults work as-is for local Docker Compose.

### 3. Start all services

```bash
docker compose up --build
```

This starts PostgreSQL, the FastAPI backend, and the Telegram bot in the correct order (DB → backend → bot).

### 4. Verify startup

```bash
# Backend health check
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"cocktailbot-api"}

# Check backend API docs
open http://localhost:8000/docs

# Web frontend
open http://localhost:3000

# Check Docker logs
docker compose logs -f backend
docker compose logs -f bot
docker compose logs -f frontend
```

### 5. Use the bot or web UI

- **Telegram bot:** Open Telegram, find your bot (by the username you set with BotFather), and send `/start`.
- **Web UI:** Open [http://localhost:3000](http://localhost:3000) in your browser. Same features as the bot: search by name, by ingredients, random cocktail, favorites, history.

### 6. Stop

```bash
docker compose down
# To also remove the database volume:
docker compose down -v
```

---

## Running Without Docker (Local Development)

### Backend

```bash
cd backend
pip install -e ".[dev]"  # or: uv pip install -e ".[dev]"
# Start a local PostgreSQL instance first, then:
DATABASE_URL=postgresql+asyncpg://cocktail:cocktail@localhost:5432/cocktaildb \
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bot

```bash
cd bot
pip install -e ".[dev,llm]"
BOT_TOKEN=<your_token> BACKEND_URL=http://localhost:8000 python -m bot.bot
```

### CLI Test Mode (no Telegram required)

```bash
cd bot
python -m bot.bot cli-test
```

This lets you type messages and see how the intent detector classifies them — useful for quick verification without a running bot token.

---

## Running Tests

### Backend tests

```bash
cd backend
pip install -e ".[dev]"
pytest -v
```

### Bot tests

```bash
cd bot
pip install -e ".[dev]"
pytest -v
```

---

## Optional LLM Integration

To enable natural language understanding via an LLM:

1. Get an API key from [OpenRouter](https://openrouter.ai/) or any OpenAI-compatible provider.
2. In `.env`:
   ```dotenv
   LLM_ENABLED=true
   LLM_API_KEY=sk-or-...
   LLM_API_BASE_URL=https://openrouter.ai/api/v1
   LLM_API_MODEL=openai/gpt-4o-mini
   ```
3. Restart the bot service: `docker compose restart bot`

If `LLM_ENABLED=false` or `LLM_API_KEY` is empty, the bot uses deterministic intent detection and works fully without any LLM credentials.

---

## API Reference

The backend exposes these REST endpoints (interactive docs at `http://localhost:8000/docs`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/cocktails/by-name?name=<name>` | Search by cocktail name |
| GET | `/cocktails/by-ingredients?ingredients=<a,b,c>` | Search by ingredients |
| GET | `/history` | Recent search history |
| GET | `/favorites?user_id=<id>` | User's favorites |
| POST | `/favorites` | Add a favorite |
| DELETE | `/favorites/{cocktail_id}?user_id=<id>` | Remove a favorite |

---

## Repository Structure

```
se-toolkit-hackathon/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routers/          # FastAPI route handlers
│   │   ├── services/         # Business logic (API client, DB service)
│   │   ├── database.py       # Async SQLAlchemy engine + session
│   │   ├── main.py           # FastAPI app factory
│   │   └── settings.py       # Pydantic settings
│   ├── tests/                # Backend unit + integration tests
│   ├── Dockerfile
│   └── pyproject.toml
├── bot/                      # Telegram bot
│   ├── handlers/             # aiogram message + command handlers
│   ├── services/             # Backend client, LLM client, intent, formatter
│   ├── tests/                # Bot unit tests
│   ├── bot.py                # Entry point
│   ├── config.py             # Bot settings
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                 # React web frontend
│   ├── client/
│   │   └── src/
│   │       ├── components/   # CocktailCard, CocktailDetail, Sidebar
│   │       ├── pages/        # Home (search), Favorites, History
│   │       ├── lib/api.ts    # API client for FastAPI backend
│   │       └── App.tsx       # Routing + layout
│   ├── nginx.conf            # Nginx config for serving static build
│   ├── Dockerfile            # Multi-stage: Node build → Nginx serve
│   └── package.json
├── docs/screenshots/         # Bot and UI screenshots
├── docker-compose.yml        # Orchestrates all four services
├── .env.example              # Environment variable template
├── .gitignore
├── LICENSE
└── README.md
```

---

## Example Demo Queries

Use these in the Telegram bot during your demo:

1. `/name Mojito` — Shows a full Mojito recipe
2. `vodka, lime, mint` — Lists cocktails with all three ingredients
3. `/ingredients gin, tonic` — Gin & Tonic variations
4. `Margarita` — Deterministic name detection → full recipe
5. `/history` — Shows your search history from the database

---

## User Registration & Authentication

### Frontend User Interface

The web application now includes a complete user registration and authentication system:

**Registration Page** (`/#/register`):
- Create a new account with username, email, and password
- Password must be at least 6 characters
- Passwords are securely hashed with bcrypt before storage
- Automatic login after successful registration

**Login Page** (`/#/login`):
- Sign in with username and password
- Session persists across page reloads (stored in localStorage)
- Secure logout functionality

**Protected Features**:
- **Favorites**: Only registered users can save and view favorite cocktails
- **History**: Only registered users can view their search history
- Unauthenticated users are prompted to login/register when accessing protected pages

### User Registration API

The backend provides user authentication endpoints:

**Register:** `POST /users/register`

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```


**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

**Error Responses:**
- `400 Bad Request` — Username or email already exists
- `422 Validation Error` — Invalid input format

Passwords are securely hashed using bcrypt before storage.

### pgAdmin — Database Management Interface

pgAdmin is a web-based management tool for the PostgreSQL database, accessible at [http://localhost:5050](http://localhost:5050).

**Default Credentials:**
- **Email:** `admin@local.dev` (customizable via `PGADMIN_EMAIL` in `.env`)
- **Password:** `admin` (customizable via `PGADMIN_PASSWORD` in `.env`)

**Connecting to the Database in pgAdmin:**

1. Open [http://localhost:5050](http://localhost:5050) in your browser
2. Log in with the credentials above
3. Click "Add New Server"
4. In the **Connection** tab:
   - **Host name/address:** `db` (Docker service name)
   - **Port:** `5432`
   - **Maintenance database:** `cocktaildb`
   - **Username:** `cocktail`
   - **Password:** `cocktail`
5. Click **Save**

You can now:
- Browse all tables (`users`, `cached_cocktails`, `search_history`, `favorites`)
- Execute SQL queries
- View and edit user records
- Monitor database performance

**Environment Variables:**

Add these to your `.env` file to customize pgAdmin:

```dotenv
PGADMIN_EMAIL=your-email@example.com
PGADMIN_PASSWORD=your-secure-password
```

---

## License

MIT — see [LICENSE](LICENSE).
