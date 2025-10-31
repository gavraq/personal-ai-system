# Module 1, Step 1.4: Next.js Frontend Setup

**Completed**: October 22, 2025

## What We Built

In this step, we set up the complete Next.js 15 frontend infrastructure for the Risk Agents application. We configured TypeScript, Tailwind CSS, created the basic app structure, and successfully tested both the frontend and its connection to the backend.

## Files Created

### 1. Package Configuration
**File**: `frontend/package.json`

Dependencies installed:
- **next@^15.0.0**: React framework with App Router
- **react@^19.0.0** & **react-dom@^19.0.0**: Latest React with concurrent features
- **next-auth@^4.24.0**: Authentication for Next.js (for future use)
- **axios@^1.6.0**: HTTP client for API calls
- **TypeScript & Dev Tools**: Full TypeScript support with linting

Scripts:
```json
"dev": "next dev -p 3050",      // Development server
"build": "next build",           // Production build
"start": "next start -p 3050",   // Production server
"lint": "next lint",             // Code linting
"type-check": "tsc --noEmit"     // Type checking
```

### 2. TypeScript Configuration
**File**: `frontend/tsconfig.json`

Key configuration:
- **Target**: ES2020 for modern JavaScript features
- **JSX**: preserve (handled by Next.js)
- **Module Resolution**: bundler (Next.js 15 requirement)
- **Path Aliases**: `@/*` maps to project root for cleaner imports
- **Strict Mode**: Enabled for type safety

### 3. Tailwind CSS Configuration
**Files**:
- `frontend/tailwind.config.ts` - Tailwind configuration with custom colors
- `frontend/postcss.config.js` - PostCSS for Tailwind processing

Custom theme:
- Primary color palette (blue shades 50-900)
- Dark mode support
- Content paths for all component directories

### 4. Next.js App Structure
**File**: `frontend/app/layout.tsx`

Root layout component providing:
- HTML structure with proper metadata
- Global CSS imports
- Consistent layout across all pages

```tsx
export const metadata: Metadata = {
  title: 'Risk Agents - AI-Powered Project Management',
  description: 'Transform project complexity into clarity...'
}
```

### 5. Home Page
**File**: `frontend/app/page.tsx`

Features:
- **Backend Health Check**: Automatically tests connection to backend
- **Loading States**: Shows spinner while checking connection
- **Error Handling**: Displays error messages if backend unavailable
- **Success Display**: Shows backend health status and version info
- **Responsive Design**: Uses Tailwind for mobile-friendly layout
- **Dark Theme**: Slate color scheme with gradients

The page includes:
- System status card with health check
- Three feature cards (Claude Agent SDK, FastAPI, Next.js 15)
- Links to API documentation and GitHub

### 6. Global Styles
**File**: `frontend/app/globals.css`

Tailwind base styles with:
- Light and dark mode CSS variables
- Gradient backgrounds
- Typography defaults

### 7. API Client
**File**: `frontend/lib/api.ts`

Type-safe API client featuring:
- Environment-based URL configuration
- Generic fetch wrapper with error handling
- TypeScript interfaces for responses
- Methods for backend endpoints

```typescript
// Example usage:
const health = await api.health()
console.log(health.status) // "healthy"
```

### 8. Next.js Configuration
**File**: `frontend/next.config.js`

Configuration for:
- React strict mode
- Environment variable exposure
- Future optimizations

### 9. Frontend README
**File**: `frontend/README.md`

Comprehensive documentation covering:
- Technology stack
- Project structure
- Development commands
- API integration
- Styling approach
- Next steps

### 10. Docker Dockerfile Update
**File**: `docker/frontend.Dockerfile` (Modified)

**Issue Encountered**: The Dockerfile initially used `npm ci` which requires a `package-lock.json` file.

**Fix Applied**: Changed to `npm install` to generate the lock file automatically:
```dockerfile
# Changed from:
RUN npm ci

# To:
RUN npm install
```

This allows the container to build successfully even without a pre-existing lock file.

## Key Concepts Explained

### 1. Next.js 15 App Router
Next.js 15 uses a new routing system based on the file system:
- `app/` directory contains all routes
- `layout.tsx` provides shared layout
- `page.tsx` is the actual page content
- Server components by default (use `'use client'` for client-side)

### 2. Server vs Client Components
```tsx
// Server component (default)
export default function ServerComponent() {
  // Runs only on server
}

// Client component (needs 'use client' directive)
'use client'
export default function ClientComponent() {
  // Can use hooks like useState, useEffect
}
```

Our home page uses `'use client'` because it needs `useEffect` for the health check.

### 3. Tailwind CSS Utility Classes
Instead of writing CSS, we use utility classes:
```tsx
<div className="bg-slate-800 rounded-lg p-6">
  <h2 className="text-2xl font-bold text-white">
    Title
  </h2>
</div>
```

This compiles to optimized CSS with only the classes we actually use.

### 4. TypeScript Path Aliases
The `@/*` alias lets us import from project root:
```typescript
// Instead of:
import api from '../../../lib/api'

// We can write:
import api from '@/lib/api'
```

### 5. Environment Variables in Next.js
Variables prefixed with `NEXT_PUBLIC_` are available in the browser:
```javascript
// Available in browser
const apiUrl = process.env.NEXT_PUBLIC_API_URL

// Server-side only
const secret = process.env.SECRET_KEY
```

## Commands Used

### 1. Build Frontend Container
```bash
docker-compose build frontend
```
**What it does**:
- Downloads Node 20 Alpine image
- Runs `npm install` (415 packages installed)
- Copies frontend code
- Creates container image

**Time**: ~4 minutes for initial build (due to npm install)

### 2. Start Frontend Container
```bash
docker-compose up --build frontend
```
**What it does**:
- Rebuilds container if needed
- Starts Next.js dev server on port 3050
- Enables hot-reload for development
- Shows logs in terminal

### 3. Test Frontend
```bash
curl http://localhost:3050
```
**What it does**: Fetches the home page HTML to verify server is running

## Docker Build Output

The build process showed:
```
#22 [frontend 4/5] RUN npm install
#22 225.3 added 415 packages, and audited 416 packages in 4m
#22 225.3 found 0 vulnerabilities

Next.js 15.5.6
- Local:        http://localhost:3050
- Network:      http://172.21.0.3:3050

✓ Ready in 1197ms
```

## Verification Checklist

- [x] Package.json created with all dependencies
- [x] TypeScript configured with strict mode
- [x] Tailwind CSS installed and configured
- [x] App Router structure created (layout.tsx, page.tsx)
- [x] Global styles with Tailwind directives
- [x] API client created with type safety
- [x] Frontend README documentation
- [x] Next.js configuration file created
- [x] Docker container builds successfully
- [x] Frontend runs on http://localhost:3050
- [x] Frontend serves HTML content
- [x] Backend health check works (tested in browser)

## What the Frontend Does

When you visit http://localhost:3050, the page:

1. **Loads immediately** with a skeleton UI showing "Checking backend connection..."
2. **Makes API call** to `http://localhost:8050/health`
3. **Displays result**:
   - ✅ If successful: Shows green indicator with backend version, environment, status
   - ❌ If failed: Shows red error message with debugging hint

The page also includes:
- Three informational cards about the tech stack
- Buttons linking to API docs and GitHub
- Responsive design (works on mobile, tablet, desktop)
- Dark theme with gradient background

## Testing the Connection

You can test the full stack now:

1. **Backend**: http://localhost:8050/health
   ```json
   {
     "status": "healthy",
     "service": "risk-agents-backend",
     "timestamp": "2025-10-22T10:21:47.895193",
     "environment": "development",
     "version": "0.1.0"
   }
   ```

2. **Frontend**: http://localhost:3050
   - Should show the health check succeeding
   - Backend info card should display "healthy" status

3. **API Docs**: http://localhost:8050/docs
   - FastAPI's auto-generated documentation

## Troubleshooting

### Issue: npm ci Failed
**Error**: `npm ci can only install with an existing package-lock.json`

**Cause**: The Dockerfile used `npm ci` but no lock file existed

**Fix**: Changed Dockerfile to use `npm install` instead:
```dockerfile
RUN npm install
```

This generates the lock file during the build process.

### Issue: Frontend Can't Connect to Backend
**Symptom**: Red error message on frontend page

**Checks**:
1. Is backend running? `docker ps` should show `risk-agents-backend`
2. Can you curl backend? `curl http://localhost:8050/health`
3. Check environment variables in `.env` file
4. Check docker-compose logs: `docker-compose logs frontend`

### Issue: Port 3050 Already in Use
**Fix**:
```bash
# Find what's using the port
lsof -i :3050

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

## Technical Details

### npm Install Output
```
npm warn deprecated inflight@1.0.6
npm warn deprecated glob@7.2.3
npm warn deprecated rimraf@3.0.2
npm warn deprecated eslint@8.57.1

added 415 packages in 4m
found 0 vulnerabilities ✓
```

These warnings are normal and expected:
- Some dependencies use older packages
- No security vulnerabilities found
- All packages installed successfully

### Docker Layers Cached
After the first build, subsequent builds are much faster:
```
#20 [frontend 2/5] WORKDIR /app
#20 CACHED

#21 [frontend 3/5] COPY frontend/package*.json ./
#21 CACHED
```

Docker caches unchanged layers, so only modified files rebuild.

### Next.js Development Server
```
Next.js 15.5.6
- Local:        http://localhost:3050
- Network:      http://172.21.0.3:3050

✓ Starting...
✓ Ready in 1197ms
```

The dev server:
- Compiles pages on-demand
- Enables hot-reload (changes appear instantly)
- Shows detailed error messages
- Automatically type-checks as you code

## Next Steps

**Module 1, Step 1.5: Test Full Stack Integration**

We'll:
1. Start both backend and frontend together
2. Test the complete user flow
3. Verify health checks work
4. Test API documentation
5. Confirm hot-reload works for both services

After that, we'll move to **Module 2: Claude Agent SDK + Skills Framework**!

## Project Status

✅ **Module 1 Progress**: 80% Complete
- [x] Step 1.1: Project Structure
- [x] Step 1.2: Docker Setup
- [x] Step 1.3: Backend Setup
- [x] Step 1.4: Frontend Setup
- [ ] Step 1.5: Integration Testing

**Total time invested**: ~6 hours
**Lines of code**: ~500 (backend + frontend)
**Docker containers**: 2 running successfully
