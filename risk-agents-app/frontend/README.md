# Risk Agents Frontend

Next.js 15 frontend for the Risk Agents AI-powered project management application.

## Technology Stack

- **Next.js 15**: React framework with App Router
- **React 19**: Latest React with concurrent features
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Next-Auth**: Authentication for Next.js

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles with Tailwind
├── components/            # React components
├── lib/                   # Utility libraries
│   └── api.ts            # API client for backend
├── public/               # Static assets
├── package.json          # Node dependencies
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.ts    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
└── next.config.js        # Next.js configuration
```

## Key Features

### 1. App Router (Next.js 15)
Uses the new App Router with:
- Server components by default
- Client components with 'use client' directive
- File-based routing in `app/` directory

### 2. TypeScript Configuration
Strict TypeScript with:
- Path aliases (`@/*` for imports)
- React 19 types
- Next.js plugin integration

### 3. Tailwind CSS Styling
Modern utility-first CSS with:
- Custom color scheme (primary blues)
- Dark mode support
- Responsive design utilities

### 4. API Client
Type-safe API client in `lib/api.ts`:
- Environment-based URL configuration
- Error handling
- TypeScript interfaces for responses

## Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8050
NEXTAUTH_URL=http://localhost:3050
NEXTAUTH_SECRET=your_secret_here
```

## Development

### Running Locally (without Docker)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

### Running with Docker

```bash
# Build and start frontend container
docker-compose up frontend

# Or build and start everything
docker-compose up --build
```

The frontend will be available at http://localhost:3050

## API Integration

The frontend connects to the backend API using the client in `lib/api.ts`:

```typescript
import api from '@/lib/api'

// Example: Check backend health
const health = await api.health()
console.log(health)
```

## Components

### Home Page (app/page.tsx)
- Displays system status
- Checks backend connectivity
- Shows health check information
- Links to API documentation

## Styling with Tailwind

Tailwind utility classes are used throughout:

```tsx
<div className="bg-slate-800 rounded-lg p-6">
  <h2 className="text-2xl font-bold text-white">
    Title
  </h2>
</div>
```

Custom colors defined in `tailwind.config.ts`:
- `primary-500`, `primary-600`, etc. (blue theme)
- Dark mode colors (slate palette)

## Next Steps

1. Add authentication with NextAuth
2. Create project management UI components
3. Implement Claude Agent interaction interface
4. Add Skills Framework browser
5. Build risk taxonomy visualization

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs)
