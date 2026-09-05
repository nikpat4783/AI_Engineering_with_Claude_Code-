# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Quick Skills Reference

**Custom project skills** are available in `.claude/skills/`:

1. **Start Development Servers** - Run full application locally
2. **Clean Up Project** - Remove artifacts and logs
3. **API Development & Integration** - Work with async/await API handlers
4. **Frontend Component Development** - Create React components
5. **Backend Development & Deployment** - FastAPI endpoint development

See `.claude/skills/README.md` for complete skills documentation.

## Project Overview

ALOCA+ is a full-stack Quality Assurance tracking system for Eli Lilly. It allows QA teams to manage test cases, track defects, and monitor quality metrics in real-time.

**Tech Stack:**
- **Frontend**: React 18 with custom CSS (no framework dependencies like Material-UI)
- **Backend**: FastAPI with SQLAlchemy ORM and SQLite
- **Database**: SQLite (local development) with automatic schema creation
- **Deployment**: Docker and Docker Compose supported

---

## Development Workflow

### Starting the Application

**Option 1: Automated (Recommended)**
```bash
cd aloca-qa-system
./start.sh              # macOS/Linux
start.bat              # Windows
```

**Option 2: Manual Start**

Backend (Terminal 1):
```bash
cd backend
python -m venv venv
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate.bat         # Windows
pip install -r requirements.txt
python main.py
```

Frontend (Terminal 2):
```bash
cd frontend
npm install
BROWSER=none npm start
```

**Ports:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Architecture

### Frontend Architecture

**File Structure:**
```
frontend/src/
├── App.jsx              # Main router and sidebar navigation
├── index.css            # All styling (500+ lines, professional design)
├── index.js             # React entry point
└── pages/
    ├── Dashboard.jsx    # Real-time metrics, charts
    ├── TestCases.jsx    # Test case CRUD and results
    ├── Defects.jsx      # Defect tracking and management
    └── Reports.jsx      # Analytics and reporting
```

**Key Pattern:**
- Single-page app with client-side routing via sidebar navigation
- Each page component fetches data from backend API using axios
- Modal forms for data entry
- Real-time dashboard auto-refreshes every 30 seconds
- Charts use Recharts library

### Backend Architecture

**File Structure:**
```
backend/
├── main.py              # FastAPI app, all endpoints (25+)
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic validation schemas
└── requirements.txt
```

**Data Model:**
- **TestCase**: Test case definitions with module organization
- **TestResult**: Individual test execution records with pass/fail status
- **Defect**: Bug tracking with severity levels
- **QualityMetric**: Aggregated metrics snapshots (auto-generated)

**API Endpoints:**
```
GET    /health                       Health check
GET    /dashboard/stats              Dashboard statistics
POST   /test-cases                   Create test case
GET    /test-cases                   List test cases
POST   /test-results                 Record test result
GET    /test-results                 List test results
POST   /defects                      Create defect
GET    /defects                      List defects (filters: status, severity)
PATCH  /defects/{id}                 Update defect status
GET    /metrics                      Historical metrics
POST   /metrics/generate             Generate new metric snapshot
```

**Database:**
- SQLite file: `backend/aloca_qa.db` (auto-created on first run)
- Foreign key relationships between TestCase → TestResult and TestCase → Defect
- All tables use UUID strings as primary keys

---

## Common Development Tasks

### Running Servers

**Backend only (for API development):**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Frontend only (requires backend running):**
```bash
cd frontend
BROWSER=none npm start
```

### Database

**Reset database:**
```bash
cd backend
rm aloca_qa.db
python main.py  # Recreates schema on startup
```

**Inspect database:**
```bash
cd backend
sqlite3 aloca_qa.db
.tables
SELECT * FROM test_cases;
```

### API Testing

**Interactive API docs:**
```
http://localhost:8000/docs    # Swagger UI
http://localhost:8000/redoc   # ReDoc
```

**Quick curl tests:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/dashboard/stats
```

### Frontend Development

**API Integration (async/await):**

All API calls now use centralized async/await handlers in `src/api/`:
```typescript
import { dashboardApi, testCasesApi, defectsApi } from './api';

// Directly call async methods
const stats = await dashboardApi.getStats();
const testCases = await testCasesApi.listTestCases();
const defects = await defectsApi.getOpenDefects();

// Or use React hooks (recommended in components)
import { useDashboardStats, useDefects } from './api/hooks';
const { value: stats, status, error } = useDashboardStats();
```

Available API handlers:
- `dashboard.ts` - Dashboard stats, metrics
- `testCases.ts` - Test case CRUD, results
- `defects.ts` - Defect management, filtering
- `hooks.ts` - React hooks for all APIs (with loading/error states)

See `frontend/src/api/README.md` for complete API documentation.

**Add a new page:**
1. Create `src/pages/NewPage.jsx`
2. Use hooks from `src/api/hooks.ts` for data fetching
3. Import in `App.jsx`
4. Add menu item to `menuItems` array
5. Add case in `getPageContent()` switch statement

**Styling:**
- All styles in `src/index.css`
- CSS variables for colors (--primary, --success, --error, etc.)
- BEM-style class naming (e.g., `stat-card`, `btn-primary`)
- No CSS framework - custom implementation for control

### Backend Development

**Add a new endpoint:**
1. Create Pydantic schema in `schemas.py`
2. Create SQLAlchemy model in `models.py`
3. Add endpoint function in `main.py`
4. Use `get_db()` dependency for database access
5. Return schema response model

**Example:**
```python
@app.post("/my-endpoint", response_model=MySchema)
def create_item(item: MyCreateSchema, db: Session = Depends(get_db)):
    db_item = MyModel(id=str(uuid.uuid4()), **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
```

### Cleanup and Maintenance

**Clean build artifacts, logs, and cache:**

```bash
# macOS/Linux
./cleanup.sh

# Windows
cleanup.bat
```

**What gets cleaned:**
- `dist/`, `frontend/build/`, `frontend/.cache/` - Build directories
- `*.log` files - Application logs
- `__pycache__/`, `.pytest_cache/` - Python cache
- `.DS_Store` - OS artifacts

**Individual cleanup commands:**
```bash
rm -rf ./dist ./frontend/build ./frontend/.cache     # Build dirs
rm -rf ./backend/*.log ./frontend/*.log               # Logs
rm -rf ./backend/__pycache__ ./backend/.pytest_cache  # Python cache
rm -f ./backend/aloca_qa.db                           # Database (reset)
```

---

## Important Notes

### Current State
- ✅ Full-stack application is deployed and running locally
- ✅ All core features implemented (test cases, defects, metrics, reports)
- ✅ Professional UI with Eli Lilly branding
- ✅ Docker support ready
- ✅ Comprehensive documentation

### Key Design Decisions

1. **No CSS Framework**: Custom CSS provides full control over design and reduces bundle size
2. **SQLite for Development**: Easy setup, auto-initialization; upgrade to PostgreSQL in production by changing `DATABASE_URL`
3. **All Endpoints in main.py**: Small codebase, all endpoints in one file for visibility
4. **CORS Enabled for All Origins**: Development only; restrict in production
5. **Real-time Dashboard**: Auto-refresh every 30 seconds provides live metrics without WebSockets complexity
6. **Modal Forms**: Lightweight, no need for page navigation

### Automated Cleanup Hooks

Claude Code hooks are configured in `.claude/settings.json`:
- **cleanup-dist**: Removes `dist/`, `frontend/build/`, `.cache/`
- **cleanup-logs**: Removes `*.log` files and OS artifacts
- **cleanup-deps**: Removes `__pycache__/` and dependency caches
- **cleanup-db**: Removes SQLite database (for reset)
- **cleanup-all**: Full cleanup (dist, logs, cache, Python artifacts)

Hooks run automatically:
- **Before**: `build`, `deploy` commands
- **After**: `test` command

Manual cleanup:
```bash
./cleanup.sh    # macOS/Linux
cleanup.bat     # Windows
```

### CORS Configuration

Currently allows all origins:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

**For production**, update in `main.py`:
```python
allow_origins=["https://yourdomain.com"],
```

### Database Initialization

Database schema is created automatically on app startup via:
```python
Base.metadata.create_all(bind=engine)
```

No migrations needed for development changes; for production use Alembic.

---

## Documentation

- **README.md**: Full project documentation and setup
- **QUICKSTART.md**: 5-minute setup guide with examples
- **DEVELOPMENT.md**: How to extend the system (auth, WebSockets, etc.)
- **PROJECT_SUMMARY.md**: Complete feature list and architecture

---

## Deployment

### Docker
```bash
docker-compose up
```

Creates two containers:
- `aloca_backend` (port 8000)
- `aloca_frontend` (port 3000)

### Production Checklist
- [ ] Add authentication (JWT or OAuth)
- [ ] Restrict CORS origins
- [ ] Switch database to PostgreSQL
- [ ] Set up HTTPS
- [ ] Configure environment variables (.env)
- [ ] Add logging and monitoring
- [ ] Run security review
- [ ] Set up CI/CD pipeline

---

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.8+)
- Reinstall venv: `rm -rf venv && python -m venv venv`
- Verify pip packages: `pip list | grep fastapi`

**Frontend won't start:**
- Clear npm cache: `npm cache clean --force`
- Reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (need 14+)

**CORS errors:**
- Backend CORS is open for development; check browser console for actual error
- Ensure backend is running on port 8000
- Check API URL in frontend components

**Database errors:**
- Delete `backend/aloca_qa.db` and restart backend
- Check file permissions in backend directory
- Verify SQLite is available: `python -c "import sqlite3; print(sqlite3.version)"`

---

## API Response Format

All endpoints return either:

**Success Response:**
```json
{
  "id": "uuid-string",
  "field1": "value1",
  "created_at": "2026-09-05T04:00:00",
  ...
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

HTTP status codes:
- 200: Success
- 400: Bad request (validation error)
- 404: Not found
- 500: Server error

---

## Code Style Notes

**Python (Backend):**
- Use type hints for function parameters and returns
- Use Pydantic for data validation
- Use UUID strings for all IDs
- Import commonly used items from models and schemas at top

**JavaScript (Frontend):**
- Functional components with hooks
- Use axios for HTTP calls
- Modal-based forms (no page navigation for data entry)
- CSS class naming follows pattern: `component-name`, `component-name--variant`

---

## Performance Considerations

- Dashboard metrics auto-refresh: 30 seconds (balance between responsiveness and server load)
- Database queries are indexed on common filter columns (module, status, severity)
- Frontend lazy-loads pages (React suspense ready for future optimization)
- Charts use Recharts with reasonable data limits (7-30 days)

For high-traffic production, consider:
- Adding caching layer (Redis)
- Database connection pooling
- API rate limiting
- Frontend code splitting and lazy loading

---

## Frontend Utilities

### Query String Helper Functions

Location: `frontend/src/utils/format.ts`

```typescript
import { buildQueryString, parseQueryString, formatAPIUrl } from './utils/format';

// Build query string
const params = { status: 'open', severity: 'critical' };
const qs = buildQueryString(params); // "?status=open&severity=critical"

// Format API URL
const url = formatAPIUrl('http://localhost:8000', '/defects', params);
// "http://localhost:8000/defects?status=open&severity=critical"

// Parse query string
const parsed = parseQueryString(location.search);

// Get single parameter
const status = getQueryParam(location.search, 'status');

// Update single parameter
const newSearch = updateQueryParam(location.search, 'page', '2');

// Remove parameter
const cleanSearch = removeQueryParam(location.search, 'filter');
```

Available functions:
- `buildQueryString(params)` - Convert object to query string
- `parseQueryString(search)` - Parse query string to object
- `getQueryParam(search, key)` - Get single parameter
- `updateQueryParam(search, key, value)` - Update single parameter
- `removeQueryParam(search, key)` - Remove parameter
- `formatAPIUrl(baseURL, endpoint, filters)` - Build complete API URL
- `encodePath(path)` - URL encode path
- `decodePath(path)` - URL decode path

---

## Backend Route Rules & Security

**IMPORTANT**: All backend modifications must follow mandatory security and architecture rules.

See `BACKEND_RULES.md` for:
- ✅ Input validation requirements (Pydantic schemas)
- ✅ SQL injection prevention (ORM only)
- ✅ Authentication & authorization patterns
- ✅ CORS configuration
- ✅ Error handling best practices
- ✅ Database transaction management
- ✅ HTTP status code conventions
- ✅ Foreign key validation
- ✅ Endpoint design patterns

**Critical Rules Summary:**
1. All inputs validated with Pydantic schemas
2. SQLAlchemy ORM for all database access (no raw SQL)
3. Database transactions with rollback handling
4. Generic error messages to clients (detailed logs)
5. Correct HTTP status codes
6. Foreign key validation before creating related records
7. UUID strings for all IDs
8. CORS restricted to allowed origins
9. All endpoints with docstrings
10. Dependency injection for database sessions

---

## Environment Configuration

### Local Development
```bash
./cleanup.sh && source setup-local  # Auto-configure for localhost
```

### Production
```bash
# Manual configuration required
cp .env.production .env
# Update DATABASE_URL, REACT_APP_API_URL, SECRET_KEY
```

See `.env.production` for all configurable options.

---

## Version Info

- Python: 3.8+
- Node.js: 14+
- FastAPI: 0.109.0
- React: 18.2.0
- SQLAlchemy: 2.0.25
