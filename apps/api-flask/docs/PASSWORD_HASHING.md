# Password Hashing - Argon2id Compatibility

## Overview

Both Flask and NestJS backends now use **Argon2id** for password hashing with **identical parameters**, ensuring full compatibility. Users created in one backend can authenticate in the other.

## Why Argon2id?

- **Winner of Password Hashing Competition (2015)**
- **Resistant to side-channel attacks**
- **Memory-hard algorithm** (resistant to GPU/ASIC attacks)
- **Recommended by OWASP** for password storage
- **Better than bcrypt, scrypt, or PBKDF2**

## Configuration

### NestJS Configuration
```typescript
// @node-rs/argon2
{
  memoryCost: 19456,  // 19 MiB
  timeCost: 2,        // 2 iterations
  parallelism: 1,     // Single thread
}
```

### Flask Configuration
```python
# argon2-cffi
PasswordHasher(
    time_cost=2,        # timeCost (iterations)
    memory_cost=19456,  # memoryCost (in KiB)
    parallelism=1,      # parallelism (threads)
    hash_len=32,        # Hash output length
    salt_len=16,        # Salt length
    type=2              # Argon2id (type 2)
)
```

## Hash Format

Both backends produce compatible Argon2id hashes:

```
$argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>
```

Example:
```
$argon2id$v=19$m=19456,t=2,p=1$randomsalthere$hashedpasswordhere
```

## Parameters Explained

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `time_cost` | 2 | Number of iterations (passes over memory) |
| `memory_cost` | 19456 | Memory usage in KiB (≈19 MiB) |
| `parallelism` | 1 | Number of parallel threads |
| `hash_len` | 32 | Length of output hash in bytes |
| `salt_len` | 16 | Length of random salt in bytes |
| `type` | 2 | Argon2id variant (hybrid of Argon2i and Argon2d) |

## Cross-Backend Compatibility

### Scenario 1: User Created in NestJS, Login via Flask

1. User registers via NestJS:
   ```
   POST /auth/register
   { "email": "user@example.com", "password": "MyPass123!" }
   ```

2. NestJS hashes password with Argon2id:
   ```
   $argon2id$v=19$m=19456,t=2,p=1$...
   ```

3. User logs in via Flask:
   ```
   POST /auth/login
   { "email": "user@example.com", "password": "MyPass123!" }
   ```

4. Flask verifies password successfully ✅

### Scenario 2: User Created in Flask, Login via NestJS

Works identically in reverse!

## Implementation Files

### Flask
- **Password Service**: `src/services/password_service.py`
- **DB Reinit Script**: `scripts/manage.py` (db:reinit command)
- **Registration**: `src/api/auth.py`

### NestJS
- **Password Service**: `src/common/services/password.service.ts`
- **DB Reinit Script**: `scripts/utils.ts` (db:reinit command)

## Testing Compatibility

### Test 1: Create User in NestJS, Login via Flask

```bash
# Create user via NestJS
cd apps/api-nestjs
pnpm run db:reinit

# Login via Flask
cd apps/api-flask
python scripts/manage.py login admin1@zatvia.com "Todo####"
# Should succeed! ✅
```

### Test 2: Create User in Flask, Login via NestJS

```bash
# Create user via Flask
cd apps/api-flask
make db-reinit

# Login via NestJS
cd apps/api-nestjs
npx tsx scripts/utils.ts login admin1@zatvia.com "Todo####"
# Should succeed! ✅
```

## Migration from bcrypt

If you had users with bcrypt hashes (old Flask implementation), they will need to reset their passwords. Argon2 cannot verify bcrypt hashes and vice versa.

### Migration Strategy

**Option 1: Password Reset (Recommended)**
- Send password reset emails to all users
- Users set new passwords
- New passwords hashed with Argon2id

**Option 2: Hybrid Verification (Transition Period)**
```python
def verify_password(password_hash: str, password: str) -> bool:
    # Try Argon2id first
    try:
        PasswordHasher().verify(password_hash, password)
        return True
    except:
        pass

    # Fallback to bcrypt for legacy users
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except:
        return False
```

After verification, rehash with Argon2id:
```python
if verify_password(old_hash, password):
    if old_hash.startswith('$2b$'):  # bcrypt hash
        new_hash = PasswordHasher().hash(password)
        user.password_hash_primary = new_hash
        db.session.commit()
```

## Security Considerations

### Why These Parameters?

- **Memory Cost (19 MiB)**: Prevents parallel cracking attempts
- **Time Cost (2 iterations)**: Balances security vs performance
- **Parallelism (1 thread)**: Resists GPU attacks
- **Argon2id variant**: Protects against both side-channel and GPU attacks

### Performance Impact

Hashing time: ~50-100ms per password (acceptable for authentication)

### Tuning Parameters

For higher security (at performance cost):
```python
PasswordHasher(
    time_cost=3,        # More iterations
    memory_cost=32768,  # 32 MiB
    parallelism=2,      # 2 threads
)
```

**Note**: Changing parameters breaks compatibility with existing hashes!

## Common Issues

### Issue: "Invalid hash format"

**Cause**: Password hash in database is not Argon2id format

**Solution**:
1. Check hash format in database
2. Ensure both backends use Argon2id
3. Reinitialize database with matching hashes

### Issue: "Verification failed"

**Cause**: Parameters don't match between backends

**Solution**:
1. Verify parameters match exactly
2. Check hash format in database
3. Test hash generation in both backends

### Issue: ImportError for argon2

**Cause**: argon2-cffi not installed

**Solution**:
```bash
cd apps/api-flask
uv sync  # Installs argon2-cffi
```

## Verification

### Verify Flask Uses Argon2id

```python
from src.services.password_service import PasswordService

hash = PasswordService.hash_password("test123")
print(hash)
# Should output: $argon2id$v=19$m=19456,t=2,p=1$...

is_valid = PasswordService.verify_password(hash, "test123")
print(is_valid)  # Should be True
```

### Verify NestJS Uses Argon2id

```typescript
import { hash, verify } from '@node-rs/argon2';

const hashed = await hash('test123', {
  memoryCost: 19456,
  timeCost: 2,
  parallelism: 1,
});
console.log(hashed);
// Should output: $argon2id$v=19$m=19456,t=2,p=1$...

const isValid = await verify(hashed, 'test123');
console.log(isValid);  // Should be true
```

## Summary

✅ **Flask now uses Argon2id** (was bcrypt)
✅ **Same parameters as NestJS**
✅ **Full cross-backend compatibility**
✅ **Users can authenticate on either backend**
✅ **Industry-standard security**

Password hashing is now **fully compatible** between Flask and NestJS!
