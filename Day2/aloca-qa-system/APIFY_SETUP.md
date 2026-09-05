# Apify MCP Search Integration Setup

This guide walks you through configuring the new web search feature powered by Apify's MCP server.

## Overview

A new **Search** page has been added to ALOCA+ that lets you search the web using Apify's `rag-web-browser` actor via the Model Context Protocol (MCP). Results are fetched from a hosted MCP endpoint and displayed in the UI with clickable links.

## Quick Start

### 1. Get an Apify API Token

1. Visit [https://apify.com](https://apify.com) and sign up or log in
2. Go to **Settings → API tokens** (or [https://console.apify.com/account/integrations/api](https://console.apify.com/account/integrations/api))
3. Copy your API token (or create a new one if needed)

### 2. Configure Environment Variables

**Backend configuration** (`backend/.env`):
```bash
cd backend
# Open .env and fill in your token:
APIFY_API_TOKEN=<your-api-token-here>
MCP_SERVER_URL=https://mcp.apify.com
```

**Frontend** (optional, already configured):
- `REACT_APP_API_URL` — defaults to `http://localhost:8000` for development

### 3. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (if this is your first run)
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 — Backend:**
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
BROWSER=none npm start
# App runs on http://localhost:3000
```

### 5. Test the Search Feature

1. Open http://localhost:3000 in your browser
2. Click the **"🔎 Search"** menu item in the sidebar
3. Enter a search query (e.g., "Python async await") and click **Search**
4. Results should appear with title, URL, and snippet

## Architecture

### Backend

- **New endpoint**: `POST /search`
  - Input: `{ "query": string, "max_results": int (default 10) }`
  - Output: `{ "query": string, "results": [{ "title", "url", "snippet" }, ...] }`
  - Rate limit: 20 requests/minute (since each request calls a paid API)

- **MCP client** (`backend/mcp_client.py`):
  - Connects to `https://mcp.apify.com` using a Bearer token
  - Calls the MCP tool `call-actor` with actor `apify/rag-web-browser`
  - Parses structured JSON results from the actor
  - Returns clean, filtered results to the route handler

- **Error handling**:
  - Missing token → 502 error with generic message ("Search service unavailable")
  - Network/timeout → 502 error
  - Invalid response → Returns empty results gracefully

### Frontend

- **New page**: `pages/Search.jsx`
  - Controlled form with search input + button
  - Loading spinner while request is pending
  - Results rendered as clickable cards (links open in new tab)
  - Error and empty states with friendly messages

- **API integration** (`api/search.ts`, `api/hooks.ts`):
  - Follows the documented pattern: API handler class + React hook
  - Uses centralized `apiClient` so base URL respects `REACT_APP_API_URL` env var
  - Type-safe (`SearchRequest`, `SearchResponse`, `SearchResultItem`)

- **Styling** (`index.css`):
  - Added `.search-container`, `.search-input-group`, `.result-card`, etc.
  - Consistent with existing design (Eli Lilly branding, neutral palette)

## Testing

### API Testing (without frontend)

```bash
# Start backend with token set in .env
cd backend
python main.py

# In another terminal:
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test search"}'

# Expected response:
# {
#   "query": "test search",
#   "results": [
#     {
#       "title": "Test Results | ...",
#       "url": "https://...",
#       "snippet": "..."
#     },
#     ...
#   ]
# }
```

### Interactive API Docs

Open http://localhost:8000/docs (Swagger UI) to test the `/search` endpoint interactively.

### Frontend Testing

1. Start both backend and frontend (see "Run the Application" section above)
2. Navigate to the Search page in the sidebar
3. **Test cases**:
   - Valid query → Results display ✓
   - No token set → Friendly error message ✓
   - Network down → Friendly error message ✓
   - Empty query → Search button disabled ✓
   - Results with long URLs → Text wraps cleanly ✓
   - Click result link → Opens in new tab ✓

## Troubleshooting

### "Search service unavailable" Error

**Cause**: `APIFY_API_TOKEN` is not set or is invalid.

**Solution**:
```bash
# Check backend/.env
cat backend/.env | grep APIFY_API_TOKEN

# If empty or missing, add your token:
# APIFY_API_TOKEN=your-actual-token-here

# Restart backend:
python main.py
```

### TypeError: `json.loads()` on token

**Cause**: Token not loaded from `.env` file.

**Solution**:
1. Ensure `backend/.env` exists and has `APIFY_API_TOKEN=...` (no quotes)
2. Restart the backend
3. Check that `backend/mcp_client.py` calls `os.getenv("APIFY_API_TOKEN")`

### CORS Error in Browser Console

**Cause**: Backend not running or not on `http://localhost:8000`.

**Solution**:
1. Start backend: `cd backend && python main.py`
2. Check terminal for "Uvicorn running on http://0.0.0.0:8000"
3. Frontend should auto-retry when backend comes back online

### Timeout on Search

**Cause**: Apify MCP server slow or no internet connection.

**Solution**:
- Default timeout is 30 seconds
- Try a simpler query (e.g., "python")
- Check internet connection
- Check that `MCP_SERVER_URL=https://mcp.apify.com` is set

## Files Changed

**Backend:**
- `backend/requirements.txt` — Added `mcp`, `python-dotenv`, `httpx`
- `backend/.env` — New file (gitignored), stores your token
- `backend/.env.example` — Updated with `APIFY_API_TOKEN`, `MCP_SERVER_URL`
- `backend/mcp_client.py` — New file, MCP client logic
- `backend/schemas.py` — Added `SearchRequest`, `SearchResponse`, `SearchResultItem`
- `backend/main.py` — Added `/search` endpoint, `load_dotenv()` call

**Frontend:**
- `frontend/src/api/search.ts` — New file, API handler
- `frontend/src/api/index.ts` — Added search exports
- `frontend/src/api/hooks.ts` — Added `useSearch()` hook
- `frontend/src/pages/Search.jsx` — New file, page component
- `frontend/src/App.jsx` — Added search menu item
- `frontend/src/index.css` — Added search-related styles

## Environment Variables

### Backend

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `APIFY_API_TOKEN` | (empty) | **Yes** | Get from https://console.apify.com/account/integrations/api |
| `MCP_SERVER_URL` | `https://mcp.apify.com` | No | Change only if using a different MCP endpoint |
| `DATABASE_URL` | `sqlite:///./aloca_qa.db` | No | SQLite for dev, PostgreSQL for prod |

### Frontend

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `REACT_APP_API_URL` | `http://localhost:8000` | No | Respects `process.env.REACT_APP_API_URL` in dev |

## Production Deployment

Before deploying to production:

1. **Environment variables**: Set `APIFY_API_TOKEN` in your production environment (never commit to git)
2. **Rate limiting**: Current limit is 20 requests/minute per IP (adjust in `main.py` if needed)
3. **CORS**: Update `CORS_ORIGINS` in `backend/main.py` to restrict to your domain
4. **Logging**: Real errors are logged server-side; clients see generic messages only
5. **Monitoring**: Watch backend logs for MCP connection failures

## Support & Resources

- **Apify Documentation**: https://docs.apify.com/
- **MCP Documentation**: https://modelcontextprotocol.io/
- **MCP Servers Registry**: https://mcpservers.org/
- **rag-web-browser Actor**: https://apify.com/actors/rag-web-browser

## Notes

- Search results are **not persisted** to the database — they're fetched fresh on each request
- The `apify/rag-web-browser` actor is designed for AI-friendly web search; results may differ from traditional search engines
- MCP calls may be slow on first request (cold start); subsequent requests are faster
- This integration is read-only; you cannot create or modify Apify Actors through this UI
