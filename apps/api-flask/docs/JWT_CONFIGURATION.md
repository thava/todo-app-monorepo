# JWT Configuration - Flask vs NestJS

## Summary

The Flask API now uses **the same JWT configuration** as the NestJS API for consistency and compatibility.

## Environment Variables Mapping

### NestJS (apps/api-nestjs)

```bash
JWT_ACCESS_SECRET=your-256-bit-secret-here    # Signs access tokens (15 min expiry)
JWT_REFRESH_SECRET=your-256-bit-secret-here   # Signs refresh tokens (7 day expiry)
```

### Flask (apps/api-flask)

```bash
SECRET_KEY=your-secret-key-change-in-production  # Flask's general secret (sessions, CSRF)
JWT_ACCESS_SECRET=your-256-bit-secret-here       # Signs access tokens (15 min expiry)
JWT_REFRESH_SECRET=your-256-bit-secret-here      # Signs refresh tokens (7 day expiry)
```

## How They Work

### 1. **SECRET_KEY** (Flask only)

- **Purpose**: Flask's built-in secret for general cryptographic operations
- **Used for**: Session cookies, CSRF tokens, flash messages
- **Not used for**: JWT tokens in this application
- **Can be**: Any random string, doesn't need to match NestJS

### 2. **JWT_ACCESS_SECRET** (Both)

- **Purpose**: Signs and verifies access tokens
- **Token lifespan**: 15 minutes
- **Used for**: Short-lived authentication
- **Should be**: The same value in both Flask and NestJS if sharing users/tokens

### 3. **JWT_REFRESH_SECRET** (Both)

- **Purpose**: Signs and verifies refresh tokens
- **Token lifespan**: 7 days
- **Used for**: Obtaining new access tokens without re-login
- **Should be**: The same value in both Flask and NestJS if sharing users/tokens

## Why Separate Secrets?

Using different secrets for access and refresh tokens provides **defense in depth**:

1. **Token Isolation**: If one secret is compromised, the other token type remains secure
2. **Rotation**: You can rotate one secret without invalidating the other token type
3. **Scope Separation**: Different tokens have different privileges and lifespans
4. **Best Practice**: Follows OAuth2/OIDC security recommendations

## Token Flow

### Login Flow

```
1. User logs in with email/password
2. Server validates credentials
3. Server generates:
   - Access token (signed with JWT_ACCESS_SECRET, 15 min)
   - Refresh token (signed with JWT_REFRESH_SECRET, 7 days)
4. Both tokens returned to client
```

### Refresh Flow

```
1. Client's access token expires (after 15 min)
2. Client sends refresh token
3. Server verifies refresh token (using JWT_REFRESH_SECRET)
4. Server checks token hash in database
5. Server revokes old refresh token (rotation)
6. Server generates new token pair:
   - New access token (signed with JWT_ACCESS_SECRET)
   - New refresh token (signed with JWT_REFRESH_SECRET)
7. Both new tokens returned to client
```

## Implementation Details

### Flask Implementation

**Token Generation** (src/services/token_service.py):
```python
def generate_access_token(identity: str, additional_claims: dict = None) -> str:
    """Uses JWT_ACCESS_SECRET via Flask-JWT-Extended"""
    return create_access_token(identity=identity, additional_claims=additional_claims)

def generate_refresh_token(identity: str, additional_claims: dict = None) -> str:
    """Uses JWT_REFRESH_SECRET directly via PyJWT"""
    # Flask-JWT-Extended doesn't support separate refresh secret,
    # so we use PyJWT directly with the refresh secret
    expires = datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES
    payload = {'sub': identity, 'exp': expires, 'type': 'refresh', ...}
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm='HS256')
```

**Token Verification**:
```python
# Access token verification (automatic via @jwt_required_with_user decorator)
# Uses JWT_ACCESS_SECRET automatically

# Refresh token verification (manual in /auth/refresh endpoint)
def verify_refresh_token(token: str) -> dict:
    """Uses JWT_REFRESH_SECRET"""
    return jwt.decode(token, JWT_REFRESH_SECRET, algorithms=['HS256'])
```

### NestJS Implementation

**Token Generation** (src/common/services/jwt.service.ts):
```typescript
generateAccessToken(payload: JwtPayload): string {
  return this.jwtService.sign(payload, {
    secret: this.configService.get<string>('jwt.accessSecret'), // JWT_ACCESS_SECRET
    expiresIn: '15m',
  });
}

generateRefreshToken(payload: JwtPayload): string {
  return this.jwtService.sign(payload, {
    secret: this.configService.get<string>('jwt.refreshSecret'), // JWT_REFRESH_SECRET
    expiresIn: '7d',
  });
}
```

## Configuration Files

### Flask: src/config.py

```python
class Config:
    # Flask's general secret
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # JWT - Separate secrets for access and refresh tokens
    JWT_SECRET_KEY = os.getenv('JWT_ACCESS_SECRET', 'jwt-access-secret-dev')
    JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET', 'jwt-refresh-secret-dev')

    # Token expiration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
```

### NestJS: src/common/config/configuration.ts

```typescript
export default () => ({
  jwt: {
    accessSecret: process.env.JWT_ACCESS_SECRET,
    refreshSecret: process.env.JWT_REFRESH_SECRET,
    accessExpiresIn: '15m',
    refreshExpiresIn: '7d',
  },
});
```

## Using the Same Secrets Across Both APIs

If you want **interchangeable tokens** between Flask and NestJS:

### Option 1: Share Secrets (Recommended for Development)

Use the **same values** in both `.env` files:

**apps/api-nestjs/.env**:
```bash
JWT_ACCESS_SECRET=my-shared-access-secret-123
JWT_REFRESH_SECRET=my-shared-refresh-secret-456
```

**apps/api-flask/.env**:
```bash
JWT_ACCESS_SECRET=my-shared-access-secret-123
JWT_REFRESH_SECRET=my-shared-refresh-secret-456
```

**Result**: Tokens generated by Flask can be verified by NestJS and vice versa!

### Option 2: Separate Secrets (Recommended for Production)

Use **different values** for each backend:

**Result**: Each API has its own tokens, better security isolation.

## Testing

### Generate Secrets

```bash
# For JWT_ACCESS_SECRET
openssl rand -base64 32

# For JWT_REFRESH_SECRET
openssl rand -base64 32

# For SECRET_KEY (Flask only)
openssl rand -base64 32
```

### Verify Token Compatibility

```bash
# 1. Login with Flask API
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Save the accessToken

# 2. Use the token with NestJS API (if secrets match)
curl http://localhost:3000/me \
  -H "Authorization: Bearer <accessToken-from-flask>"

# Should work if JWT_ACCESS_SECRET is the same!
```

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use strong random secrets** (32+ bytes, base64 encoded)
3. **Rotate secrets periodically** in production
4. **Use different secrets** for different environments (dev/staging/prod)
5. **Keep access tokens short-lived** (15 min is good)
6. **Implement token rotation** for refresh tokens (both APIs do this)
7. **Use HTTPS** in production to prevent token interception

## Quick Reference

| Variable | Purpose | Used By | Shared? |
|----------|---------|---------|---------|
| `SECRET_KEY` | Flask general secret | Flask only | No |
| `JWT_ACCESS_SECRET` | Access token signing | Both APIs | Optional |
| `JWT_REFRESH_SECRET` | Refresh token signing | Both APIs | Optional |

**Bottom Line**: The Flask API now uses the **exact same JWT configuration** as NestJS, with separate secrets for access and refresh tokens!
