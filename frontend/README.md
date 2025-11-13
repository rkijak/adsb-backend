```markdown
# ADS-B Frontend (React + Vite)

Prereqs:
- Node 18+ (or Node 16+)
- npm or yarn

Install and run (from frontend/):

# install dependencies
npm install

# start dev server
npm run dev

# build for production
npm run build

Configuration:
Set VITE_BACKEND_URL in frontend/.env (or export VITE_BACKEND_URL in your environment) to point to your backend, e.g.:
VITE_BACKEND_URL=http://localhost:5001

This simple UI calls the backend /api/collect_adsb_data endpoint and shows a table of aircraft returned by the backend.
```
