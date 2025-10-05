# AI Copilot Frontend (Vite + React + TypeScript)

React frontend for the AI Copilot app, colocated with the FastAPI backend in the same workspace.

## Environment Variables

Create a `.env` file in this folder (see `.env.example`):

```
VITE_API_BASE_URL=http://localhost:3001
```

If `VITE_API_BASE_URL` is not set, the app will automatically fall back to `http(s)://<current-host>:3001`.

## Development

- Dev server runs on port 3000 by default.
- Backend should be available on the same host on port 3001.

Scripts:
- `npm run dev` – start dev server
- `npm run build` – build for production
- `npm run preview` – preview build

## API Base URL Resolution

The axios client resolves the base URL with the following priority:
1. `import.meta.env.VITE_API_BASE_URL` if provided
2. Fallback to `window.location.protocol//window.location.hostname:3001`

All API calls are sent to `${BASE_URL}/api/*`.
