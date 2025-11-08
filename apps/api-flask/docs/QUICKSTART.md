# Quick Start Guide - Flask Todo API

## 1. Prerequisites

- Python 3.12+
- PostgreSQL running locally (or use the same DB as NestJS app)
- `uv` package manager installed

## 2. Installation (30 seconds)

```bash
cd apps/api-flask

# Copy environment configuration
cp .env.example .env

# Install dependencies
uv sync
```

## 3. Configure Environment

Edit `.env` and configure:

**Database:**

```bash
# Option 1: Use the same PostgreSQL database as NestJS
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db

# Option 2: Use a separate database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db_flask
```

**JWT Secrets (Important!):**

The Flask API uses the same JWT secret names as NestJS:

```bash
# Generate strong secrets (or use the same values as NestJS for token compatibility)
JWT_ACCESS_SECRET=your-256-bit-secret-here
JWT_REFRESH_SECRET=your-256-bit-secret-here

# To share tokens between Flask and NestJS, use the SAME secrets in both .env files!
# See JWT_CONFIGURATION.md for details
```

## 4. Start the Server

```bash
# Using the run script
./run.sh

# Or directly
uv run python main.py
```

The API will start on **http://localhost:5000**

## 5. Verify It's Working

Open your browser to:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **Health Check**: http://localhost:5000/health

## 6. Test with cURL

### Register a User (with auto-verify for testing)

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "fullName": "Test User",
    "autoverify": true
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

**Save the `accessToken` from the response!**

### Create a Todo

```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "description": "My first todo",
    "priority": "high"
  }'
```

### Get All Todos

```bash
curl http://localhost:5000/todos \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Current User Profile

```bash
curl http://localhost:5000/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 7. Using with Frontend Apps

The Flask API is compatible with all the frontend apps in the monorepo:

```bash
# In the frontend .env file, update:
VITE_API_URL=http://localhost:5000
# or
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 8. Using Swagger UI

1. Go to http://localhost:5000/docs
2. Click "Authorize" button
3. Register and login to get an access token
4. Paste the token in the authorization dialog
5. Try out the endpoints interactively!

## 9. Default Port

The Flask app runs on **port 5000** by default (different from NestJS which uses 3000).

To change the port:

```bash
# In .env
FLASK_PORT=8000

# Or via environment variable
FLASK_PORT=8000 uv run python main.py
```

## 10. Troubleshooting

### Database Connection Error

Make sure PostgreSQL is running:
```bash
# Check if postgres is running
pg_isready

# Create database if needed
createdb todo_db
```

### Port Already in Use

Change the port in `.env`:
```bash
FLASK_PORT=5001
```

### Import Errors

Make sure dependencies are installed:
```bash
uv sync
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [IMPLEMENTATION.md](IMPLEMENTATION.md) for architecture details
- Explore the API with Swagger UI at http://localhost:5000/docs
- Test integration with frontend applications

## Comparison with NestJS API

Both APIs are **100% compatible**:

| Feature | NestJS (port 3000) | Flask (port 5000) |
|---------|-------------------|-------------------|
| All endpoints | ✅ | ✅ |
| Database schema | ✅ | ✅ |
| Authentication | ✅ | ✅ |
| Can run simultaneously | ✅ | ✅ |

You can run both APIs at the same time and switch between them by changing the frontend's `API_URL` configuration!
