# ALOCA+ QA System - Development Guide

This guide is for developers looking to extend and customize the ALOCA+ QA System.

---

## 🏗️ Architecture Overview

### System Design
```
┌─────────────────────────────────────────────────────────┐
│                  ALOCA+ QA System                        │
├──────────────────┬────────────────────────────────────┤
│                  │                                      │
│   React Frontend │           FastAPI Backend            │
│   (Port 3000)    │           (Port 8000)                │
│                  │                                      │
│  ┌────────────┐  │  ┌──────────────────────────┐      │
│  │ Dashboard  │  │  │   API Endpoints          │      │
│  ├────────────┤  │  ├──────────────────────────┤      │
│  │ Test Cases │  │  │ - Test Cases CRUD        │      │
│  ├────────────┤  │  │ - Test Results           │      │
│  │ Defects    │  │  │ - Defects Management     │      │
│  ├────────────┤  │  │ - Metrics                │      │
│  │ Reports    │  │  │ - Dashboard Stats       │      │
│  └────────────┘  │  └──────────────────────────┘      │
│                  │                                      │
│                  │  ┌──────────────────────────┐      │
│                  │  │   SQLite Database        │      │
│                  │  ├──────────────────────────┤      │
│                  │  │ - test_cases             │      │
│                  │  │ - test_results           │      │
│                  │  │ - defects                │      │
│                  │  │ - quality_metrics        │      │
│                  │  └──────────────────────────┘      │
│                  │                                      │
└──────────────────┴────────────────────────────────────┘
```

---

## 🔌 Backend API Structure

### FastAPI Application
```python
app = FastAPI()
├── Models (SQLAlchemy ORM)
│   ├── TestCase
│   ├── TestResult
│   ├── Defect
│   └── QualityMetric
├── Schemas (Pydantic)
│   ├── TestCaseCreate/Response
│   ├── TestResultCreate/Response
│   ├── DefectCreate/Response/Update
│   └── QualityMetricResponse
└── Endpoints
    ├── GET /health
    ├── GET /dashboard/stats
    ├── TestCase endpoints (POST, GET)
    ├── TestResult endpoints (POST, GET)
    ├── Defect endpoints (POST, GET, PATCH)
    └── Metrics endpoints (GET, POST)
```

### Adding a New Endpoint

1. **Create Pydantic Schema** (schemas.py):
```python
class MyFeatureCreate(BaseModel):
    field1: str
    field2: int
    
class MyFeatureResponse(BaseModel):
    id: str
    field1: str
    field2: int
    created_at: datetime
```

2. **Create Database Model** (models.py):
```python
class MyFeature(Base):
    __tablename__ = "my_features"
    id = Column(String, primary_key=True)
    field1 = Column(String)
    field2 = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

3. **Add Endpoint** (main.py):
```python
@app.post("/my-feature", response_model=MyFeatureResponse)
def create_feature(feature: MyFeatureCreate, db: Session = Depends(get_db)):
    db_feature = MyFeature(
        id=str(uuid.uuid4()),
        field1=feature.field1,
        field2=feature.field2
    )
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature
```

---

## 🎨 Frontend Component Structure

### React Components
```
App (Main Router)
├── Sidebar (Navigation)
├── Header
└── Main Content
    ├── Dashboard
    │   ├── StatCard
    │   ├── Chart Components
    │   └── MetricsTable
    ├── TestCases
    │   ├── TestCaseForm (Modal)
    │   ├── TestResultForm (Modal)
    │   └── TestCaseTable
    ├── Defects
    │   ├── DefectForm (Modal)
    │   ├── DefectFilters
    │   └── DefectTable
    └── Reports
        ├── Charts
        ├── Metrics Summary
        └── Export Functions
```

### Adding a New Page Component

1. **Create Page Component** (src/pages/MyPage.jsx):
```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function MyPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/my-endpoint');
      setData(response.data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="spinner"></div>;

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">My Feature</div>
      </div>
      <div className="card-body">
        {/* Your content here */}
      </div>
    </div>
  );
}
```

2. **Add to Router** (App.jsx):
```jsx
import MyPage from './pages/MyPage';

// In menu items:
{ id: 'my-page', label: 'My Feature', icon: '✨' }

// In getPageContent():
case 'my-page':
  return <MyPage />;
```

---

## 🗄️ Database Management

### Adding a New Table

1. **Create Model** (models.py):
```python
class NewTable(Base):
    __tablename__ = "new_tables"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Create Database**:
```python
# Tables are auto-created on startup via:
Base.metadata.create_all(bind=engine)
```

### Upgrading to PostgreSQL

1. **Update connection string**:
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/aloca_qa"
```

2. **Install PostgreSQL driver**:
```bash
pip install psycopg2-binary
```

3. **Update requirements.txt** and restart

---

## 📦 Extending Features

### Adding Authentication

1. **Install dependencies**:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

2. **Create auth module** (backend/auth.py):
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

3. **Add auth endpoints**:
```python
@app.post("/auth/login")
def login(username: str, password: str):
    # Verify credentials
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}
```

### Adding Email Notifications

1. **Install dependencies**:
```bash
pip install python-dotenv aiosmtplib email-validator
```

2. **Create notification module** (backend/notifications.py):
```python
import aiosmtplib
from email.mime.text import MIMEText

async def send_defect_notification(email: str, defect: Defect):
    message = MIMEText(f"New defect: {defect.title}")
    message["Subject"] = f"ALOCA+ Alert: {defect.title}"
    message["From"] = "alerts@eli-lilly.com"
    message["To"] = email
    
    async with aiosmtplib.SMTP() as smtp:
        await smtp.send_message(message)
```

### Adding Real-time Updates (WebSocket)

1. **Install dependencies**:
```bash
pip install websockets python-socketio
```

2. **Create WebSocket handler**:
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast updates
            await websocket.send_text(f"Message: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
```

---

## 🧪 Testing

### Backend Testing

Create `backend/test_main.py`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_test_case():
    response = client.post("/test-cases", json={
        "name": "Test Case 1",
        "description": "Description",
        "module": "Auth"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Case 1"
```

Run tests:
```bash
pytest backend/test_main.py -v
```

### Frontend Testing

Create `frontend/src/App.test.js`:
```javascript
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard link', () => {
  render(<App />);
  const dashboardLink = screen.getByText(/Dashboard/i);
  expect(dashboardLink).toBeInTheDocument();
});
```

Run tests:
```bash
npm test
```

---

## 🚀 Deployment

### Docker Deployment

1. **Build images**:
```bash
docker-compose build
```

2. **Run containers**:
```bash
docker-compose up -d
```

3. **View logs**:
```bash
docker-compose logs -f
```

### Kubernetes Deployment

Create `k8s/backend-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aloca-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aloca-backend
  template:
    metadata:
      labels:
        app: aloca-backend
    spec:
      containers:
      - name: backend
        image: aloca-backend:latest
        ports:
        - containerPort: 8000
```

---

## 📊 Performance Optimization

### Backend Optimization

1. **Add caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_dashboard_stats():
    # Expensive operation
    pass
```

2. **Database indexing** (already implemented):
```python
class TestCase(Base):
    __tablename__ = "test_cases"
    name = Column(String, unique=True, index=True)  # Indexed
    module = Column(String, index=True)  # Indexed
```

### Frontend Optimization

1. **Code splitting**:
```javascript
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
```

2. **Memoization**:
```javascript
const StatCard = React.memo(({ data }) => {
  return <div>{data}</div>;
});
```

---

## 🔒 Security Best Practices

### Input Validation
- ✅ Using Pydantic for all inputs
- ✅ Database ORM prevents SQL injection
- ✅ React prevents XSS by default

### Security Improvements for Production

1. **Add HTTPS**:
```python
@app.middleware("http")
async def https_redirect(request, call_next):
    if request.url.scheme == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=url)
    return await call_next(request)
```

2. **Add rate limiting**:
```bash
pip install slowapi
```

3. **Add CORS restrictions**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Resources

### FastAPI Documentation
- https://fastapi.tiangolo.com/
- https://docs.sqlalchemy.org/

### React Documentation
- https://react.dev/
- https://recharts.org/

### Docker Documentation
- https://docs.docker.com/
- https://docs.docker.com/compose/

### Testing
- https://pytest.org/
- https://testing-library.com/

---

## 🆘 Common Development Tasks

### Add a new severity level for defects
1. Update enum in `models.py`
2. Update enum in `schemas.py`
3. Add badge styling in `index.css`
4. Update frontend dropdowns

### Change database to PostgreSQL
1. Install: `pip install psycopg2-binary`
2. Update DATABASE_URL
3. Restart application

### Add new metrics field
1. Add column to QualityMetric model
2. Update schema
3. Update generation logic in `/metrics/generate`
4. Update dashboard display

---

## 🐛 Debugging Tips

### Backend Debugging
```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)

@app.get("/test-cases")
def list_test_cases(db: Session = Depends(get_db)):
    logger.debug(f"Fetching test cases...")
    return db.query(TestCase).all()
```

### Frontend Debugging
```javascript
// Use React DevTools browser extension
// Console logging
console.log('State:', data);
console.error('Error:', error);

// Network debugging - use browser DevTools
```

### Database Debugging
```bash
# Access SQLite shell
sqlite3 backend/aloca_qa.db

# Useful commands
.tables
.schema test_cases
SELECT * FROM test_cases;
```

---

## 🎯 Common Customizations

### Change color scheme
Edit `index.css` CSS variables section:
```css
:root {
  --primary: #your-color;
  --primary-dark: #your-darker-color;
  /* etc */
}
```

### Add new menu item
Edit `App.jsx` menuItems array:
```jsx
const menuItems = [
  { id: 'your-page', label: 'Your Feature', icon: '🎯' },
];
```

### Change API endpoint
Update `API_BASE` in page components:
```javascript
const API_BASE = 'https://your-production-api.com';
```

---

## 📞 Getting Help

- Check existing code for examples
- Review FastAPI/React documentation
- Check browser console for errors
- Check backend console for errors
- Use Docker logs: `docker-compose logs -f`

---

Happy coding! 🚀
