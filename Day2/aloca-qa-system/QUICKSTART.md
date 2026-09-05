# ALOCA+ QA System - Quick Start Guide

Get up and running with ALOCA+ in 5 minutes!

## Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 14+** - [Download](https://nodejs.org/)
- **Git** (optional) - [Download](https://git-scm.com/)

## Automated Setup (Recommended)

### On macOS/Linux:
```bash
cd aloca-qa-system
chmod +x start.sh
./start.sh
```

### On Windows:
```bash
cd aloca-qa-system
start.bat
```

The system will automatically:
- Create a Python virtual environment
- Install all Python dependencies
- Install all npm dependencies
- Start both backend and frontend servers

Then open your browser to: **http://localhost:3000**

---

## Manual Setup

If you prefer to set things up manually:

### Step 1: Start the Backend

```bash
cd aloca-qa-system/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # macOS/Linux
# OR
venv\Scripts\activate.bat       # Windows

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python main.py
```

The backend will start at `http://localhost:8000`

### Step 2: Start the Frontend (in a new terminal)

```bash
cd aloca-qa-system/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will automatically open at `http://localhost:3000`

---

## Verify Installation

### Backend is Working
Visit: http://localhost:8000/health

You should see:
```json
{"status": "healthy"}
```

### API Documentation
Visit: http://localhost:8000/docs

You'll see the interactive Swagger UI with all API endpoints.

---

## First Steps in the App

### 1. Create a Test Case
1. Click **"Test Cases"** in the sidebar
2. Click **"+ New Test Case"** button
3. Fill in:
   - **Test Case Name**: e.g., "Login Form Validation"
   - **Module**: e.g., "Authentication"
   - **Description**: Describe what the test does
4. Click **"Create Test Case"**

### 2. Record a Test Result
1. From the Test Cases page, click **"+ Add Result"** on a test case
2. Select the **Status**: Passed, Failed, Blocked, or Pending
3. Enter **Execution Time** in milliseconds
4. Add optional notes
5. Click **"Record Result"**

### 3. Create a Defect
1. Click **"Defects"** in the sidebar
2. Click **"+ New Defect"** button
3. Fill in:
   - **Title**: Brief defect summary
   - **Description**: Detailed issue description
   - **Severity**: Critical, High, Medium, or Low
   - **Assign To**: Team member name (optional)
4. Click **"Create Defect"**

### 4. View Dashboard
1. Click **"Dashboard"** in the sidebar
2. View real-time quality metrics:
   - Total test cases
   - Pass rate
   - Critical defects
   - Today's test results

### 5. Generate Reports
1. Click **"Reports"** in the sidebar
2. View charts and metrics for:
   - 30-day pass rate trends
   - Defect trends
   - Test distribution by module
3. Click **"Export PDF"** or **"Export Excel"** to export reports

---

## Common Issues

### Backend won't start
```bash
# Make sure Python 3.8+ is installed
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check if port 8000 is available
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend won't start
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules
npm install

# Check if port 3000 is available
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows
```

### CORS Errors
The backend is configured to accept requests from all origins in development. This is fine for development but should be restricted in production.

### Database Issues
The database file (`aloca_qa.db`) is created automatically in the backend directory. If you want to reset:
```bash
cd backend
rm aloca_qa.db  # Delete the database file
python main.py  # It will recreate it on startup
```

---

## Project Structure

```
aloca-qa-system/
├── backend/                # FastAPI backend
│   ├── main.py            # Main application
│   ├── models.py          # Database models
│   ├── schemas.py         # Data validation
│   ├── requirements.txt    # Python dependencies
│   └── venv/              # Virtual environment (auto-created)
│
├── frontend/              # React frontend
│   ├── public/            # Static files
│   ├── src/               # React components
│   ├── package.json       # npm dependencies
│   └── node_modules/      # Installed packages (auto-created)
│
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
├── start.sh               # Linux/macOS startup script
├── start.bat              # Windows startup script
└── .gitignore             # Git ignore rules
```

---

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Custom CSS** - Professional styling

---

## Next Steps

1. **Configure for Your Team**
   - Create test modules that match your project
   - Invite team members to assign defects
   - Set up automated metrics generation

2. **Integrate with Your Workflow**
   - Import existing test cases
   - Link to your issue tracker
   - Set up automated reports

3. **Deployment**
   - See README.md for production deployment
   - Configure database for your environment
   - Set up proper CORS and security

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **Project README**: See `README.md`
- **Report Issues**: Contact your QA team lead

---

## Tips

✅ **Regular Use**
- Record test results after each test run
- Update defect status promptly
- Check the dashboard daily for metrics

✅ **Best Practices**
- Use consistent module names
- Provide detailed descriptions for defects
- Include notes for failed tests
- Keep severity levels accurate

✅ **Performance**
- The dashboard auto-refreshes every 30 seconds
- Clear old test results periodically (database management)
- Export reports for archiving

---

Enjoy using ALOCA+! 🎉
