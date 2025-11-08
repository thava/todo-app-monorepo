# JWT Secrets - Complete Explanation

## Your Question

> How are `JWT_ACCESS_SECRET` and `JWT_SECRET_KEY` related?
> How does `create_access_token()` know which secret to use?

## The Answer

**Flask-JWT-Extended automatically reads `app.config['JWT_SECRET_KEY']` from the Flask application config.**

You don't need to pass it explicitly because Flask extensions use the **application context** to access configuration.

## The Configuration Chain

### 1. Environment File (`.env`)

```bash
JWT_ACCESS_SECRET=your-256-bit-secret-here
JWT_REFRESH_SECRET=your-256-bit-secret-here
```

### 2. Config Class (`src/config.py`)

```python
class Config:
    # Read from environment
    JWT_ACCESS_SECRET_KEY = os.getenv('JWT_ACCESS_SECRET', 'default')
    JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET', 'default')

    # CRITICAL LINE: Flask-JWT-Extended looks for JWT_SECRET_KEY
    JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY

    # Other JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
```

### 3. Flask App Initialization (`src/app.py`)

```python
def create_app(config_name=None):
    app = Flask(__name__)

    # Load ALL config variables into app.config
    app.config.from_object(config[config_name])

    # Initialize JWT extension - it reads app.config['JWT_SECRET_KEY']
    jwt.init_app(app)

    return app
```

### 4. Token Generation (`src/services/token_service.py`)

```python
from flask_jwt_extended import create_access_token

@staticmethod
def generate_access_token(identity: str, additional_claims: dict = None) -> str:
    # Flask-JWT-Extended internally does:
    # secret = current_app.config['JWT_SECRET_KEY']
    # jwt.encode(payload, secret, algorithm='HS256')
    return create_access_token(
        identity=identity,
        additional_claims=additional_claims or {}
    )
```

## Variable Naming Explanation

| Variable | Location | Purpose |
|----------|----------|---------|
| `JWT_ACCESS_SECRET` | `.env` file | Environment variable name (matches NestJS) |
| `JWT_ACCESS_SECRET_KEY` | `config.py` | Our internal config variable (descriptive name) |
| `JWT_SECRET_KEY` | `config.py` | Flask-JWT-Extended's required config key |
| `JWT_REFRESH_SECRET` | `.env` file | Environment variable for refresh tokens |
| `JWT_REFRESH_SECRET_KEY` | `config.py` | Our internal config for refresh tokens |

**Key insight:** We set `JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY` to bridge our naming convention with Flask-JWT-Extended's requirements.

## Why This Approach?

### Consistency with NestJS ✅
```bash
# Both use the same environment variable names
NestJS .env:  JWT_ACCESS_SECRET=xxx
Flask .env:   JWT_ACCESS_SECRET=xxx
```

### Clear Internal Naming ✅
```python
# In our code, we have descriptive names
JWT_ACCESS_SECRET_KEY   # For access tokens
JWT_REFRESH_SECRET_KEY  # For refresh tokens
```

### Flask-JWT-Extended Compatibility ✅
```python
# Flask-JWT-Extended expects JWT_SECRET_KEY
JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY
```

## How Flask-JWT-Extended Works

Flask-JWT-Extended uses Flask's **application context** (`current_app`) to access configuration:

```python
# Inside Flask-JWT-Extended's source code (simplified)
from flask import current_app

def create_access_token(identity, additional_claims):
    # Reads from app.config automatically
    secret = current_app.config['JWT_SECRET_KEY']
    expires = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']

    payload = {
        'sub': identity,
        'exp': datetime.utcnow() + expires,
        **additional_claims
    }

    return jwt.encode(payload, secret, algorithm='HS256')
```

**This is why you don't need to pass the secret explicitly!**

## Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ 1. .env File                                                 │
│    JWT_ACCESS_SECRET=abc123                                  │
│    JWT_REFRESH_SECRET=xyz789                                 │
└────────────────────┬─────────────────────────────────────────┘
                     │ os.getenv()
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. src/config.py                                             │
│    JWT_ACCESS_SECRET_KEY = os.getenv('JWT_ACCESS_SECRET')   │
│    JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET') │
│    JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY  ← CRITICAL!       │
└────────────────────┬─────────────────────────────────────────┘
                     │ app.config.from_object()
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Flask app.config Dictionary                               │
│    {                                                          │
│      'JWT_SECRET_KEY': 'abc123',                             │
│      'JWT_ACCESS_SECRET_KEY': 'abc123',                      │
│      'JWT_REFRESH_SECRET_KEY': 'xyz789',                     │
│      'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),      │
│      ...                                                      │
│    }                                                          │
└────────────────────┬─────────────────────────────────────────┘
                     │ jwt.init_app(app)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Flask-JWT-Extended Reads Config                           │
│    - Stores reference to app                                 │
│    - Reads JWT_SECRET_KEY for access tokens                  │
│    - Reads JWT_ACCESS_TOKEN_EXPIRES, etc.                    │
└────────────────────┬─────────────────────────────────────────┘
                     │
     ┌───────────────┴───────────────┐
     │                               │
     ▼                               ▼
┌─────────────────────┐    ┌─────────────────────┐
│ Access Token        │    │ Refresh Token       │
│ (Automatic)         │    │ (Manual)            │
├─────────────────────┤    ├─────────────────────┤
│ create_access_token │    │ generate_refresh_   │
│ Uses:               │    │ Uses:               │
│ current_app.config  │    │ current_app.config  │
│ ['JWT_SECRET_KEY']  │    │ ['JWT_REFRESH_      │
│                     │    │  SECRET_KEY']       │
│ (Flask-JWT-Extended)│    │ (PyJWT directly)    │
└─────────────────────┘    └─────────────────────┘
```

## Verification

You can verify this configuration by running:

```bash
python verify_jwt_config.py
```

This script will show:
- ✅ Environment variables loaded correctly
- ✅ Config variables set correctly
- ✅ JWT_SECRET_KEY equals JWT_ACCESS_SECRET_KEY
- ✅ Token generation works
- ✅ Token verification works

## Common Questions

### Q: Why not just use `JWT_SECRET_KEY` everywhere?

**A:** For clarity and NestJS compatibility. Using descriptive names (`JWT_ACCESS_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`) makes the code self-documenting and matches the NestJS convention.

### Q: Where is the access token secret actually used?

**A:** Inside Flask-JWT-Extended's internal functions:
- `create_access_token()` - Uses `current_app.config['JWT_SECRET_KEY']`
- `verify_jwt_in_request()` - Uses `current_app.config['JWT_SECRET_KEY']`
- `decode_token()` - Uses `current_app.config['JWT_SECRET_KEY']`

### Q: Can I see proof that it's using the right secret?

**A:** Yes! You can test token compatibility:

```bash
# 1. Login with Flask API
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# 2. Use the access token with NestJS API (if secrets match)
# If the token works, the secrets are correctly configured!
curl http://localhost:3000/me \
  -H "Authorization: Bearer <token-from-flask>"
```

## Summary

**The secret is configured through the Flask application config system:**

1. Environment → Config Class → Flask app.config → Flask-JWT-Extended
2. `create_access_token()` doesn't need explicit secret parameter
3. It automatically uses `current_app.config['JWT_SECRET_KEY']`
4. We set `JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY` for clarity
5. This maintains NestJS compatibility while using Flask conventions

**Bottom line:** It's all working correctly! Flask-JWT-Extended reads from `app.config` automatically via the application context.
