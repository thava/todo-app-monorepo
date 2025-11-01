# Todo App - Next.js Frontend

This is the Next.js frontend for the Todo application, part of the monorepo.

## Getting Started

From the root of the monorepo:

```bash
# Install dependencies
pnpm install

# Run the development server
pnpm dev:frontend
```

Or from this directory:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Using Shared Types

This frontend uses types from the shared packages:

```typescript
import { PublicUser, Todo, UserRole, TodoPriority } from '@todo-app/database';
import { registerInputSchema, loginInputSchema } from '@todo-app/shared';
```

## Project Structure

- `src/app/` - Next.js App Router pages
- `src/components/` - Reusable React components
- `src/lib/` - Utility functions and API client

## API Integration

The frontend connects to the NestJS API at `http://localhost:3000` (configurable via environment variables).
