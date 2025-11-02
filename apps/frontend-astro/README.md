# TodoGizmo - Astro Frontend

An alternative frontend implementation for TodoGizmo built with Astro, React, and Tailwind CSS.

## Features

- **Pure SSG/SPA**: Static site generation with client-side routing
- **React Integration**: Interactive components using React
- **Tailwind CSS**: Utility-first styling with custom theme
- **Dark Mode**: Light/dark theme support
- **JWT Authentication**: localStorage/sessionStorage based auth with remember me option

## Technology Stack

- **Astro 5.x**: Static site generator
- **React 19**: UI components
- **Tailwind CSS 4**: Styling
- **Zustand**: State management
- **TypeScript**: Type safety

## Getting Started

### Prerequisites

- Node.js 18+ and pnpm
- Backend API running at `http://localhost:3000` (default)

### Installation

```bash
cd apps/frontend-astro
pnpm install
```

### Development

```bash
# Run on default port 4200
pnpm dev

# Run on custom port
ASTRO_PORT=5000 pnpm dev
```

### Build

```bash
# Build static files for production
pnpm build

# Preview production build
pnpm preview
```

The built files will be in the `dist/` directory and can be hosted on any static web server.

## Environment Variables

Astro reads `.env` files from the project directory (`apps/frontend-astro/.env`) by default.

**Important**: Client-side variables must be prefixed with `PUBLIC_`:

```env
# API Configuration (accessible in browser)
PUBLIC_API_URL=http://localhost:3000

# Server port (server-side only, used during dev)
ASTRO_PORT=4200
```

**Usage in code**:
```typescript
// Use import.meta.env (NOT process.env)
const apiUrl = import.meta.env.PUBLIC_API_URL;

// Or use the config helper
import { config } from '@/lib/config';
const apiUrl = config.apiUrl;
```

See `.env.example` for a template.

## Project Structure

```
apps/frontend-astro/
├── src/
│   ├── components/     # React components
│   ├── layouts/        # Astro layouts
│   ├── pages/          # Astro pages (routes)
│   ├── lib/            # Utilities and API client
│   └── styles/         # Global CSS
├── public/             # Static assets
└── dist/               # Build output (git-ignored)
```

## Deployment

The built static files can be deployed to any static hosting service:

- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront
- Any nginx/Apache server

Simply upload the contents of the `dist/` directory.
