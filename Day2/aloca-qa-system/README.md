# ALOCA+ QA System

A professional Quality Assurance tracking system for Eli Lilly with comprehensive test case management, defect tracking, and quality metrics reporting.

## Features

- **Dashboard**: Real-time quality metrics and statistics
- **Test Case Management**: Create, organize, and track test cases by module
- **Test Results Tracking**: Record test execution results with detailed metrics
- **Defect Management**: Track defects by severity and status
- **Quality Metrics**: Automated metrics generation and trend analysis
- **Comprehensive Reports**: Generate reports with charts and analytics
- **Professional UI**: Clean, modern interface with responsive design

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **ORM**: SQLAlchemy
- **Language**: Python 3.8+

### Frontend
- **Framework**: React 18
- **Charting**: Recharts
- **Styling**: Custom CSS with professional color scheme
- **HTTP Client**: Axios

## Project Structure

```
aloca-qa-system/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html    # HTML entry point
│   ├── src/
│   │   ├── App.jsx       # Main app component
│   │   ├── index.css     # Styles
│   │   ├── index.js      # React entry point
│   │   └── pages/
│   │       ├── Dashboard.jsx    # Dashboard page
│   │       ├── TestCases.jsx    # Test cases management
│   │       ├── Defects.jsx      # Defects management
│   │       └── Reports.jsx      # Reports and analytics
│   └── package.json      # npm dependencies
└── README.md
```

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd aloca-qa-system/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd aloca-qa-system/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## API Endpoints

### Dashboard
- `GET /dashboard/stats` - Get dashboard statistics
- `GET /health` - Health check

### Test Cases
- `POST /test-cases` - Create a new test case
- `GET /test-cases` - List all test cases
- `GET /test-cases/{id}` - Get test case details

### Test Results
- `POST /test-results` - Record test result
- `GET /test-results` - List test results

### Defects
- `POST /defects` - Create a new defect
- `GET /defects` - List defects (with filters)
- `GET /defects/{id}` - Get defect details
- `PATCH /defects/{id}` - Update defect

### Metrics
- `GET /metrics` - Get quality metrics
- `POST /metrics/generate` - Generate new metrics snapshot

## Features In Detail

### Dashboard
- Real-time quality statistics
- Today's test execution summary
- Pass rate trends (7-day view)
- Critical defects count
- Historical metrics visualization

### Test Cases
- Create test cases organized by module
- Search and filter functionality
- View test execution history
- Record test results with execution time
- Track test status (passed, failed, blocked, pending)

### Defect Management
- Track defects with severity levels (critical, high, medium, low)
- Assign defects to team members
- Update defect status (open, in progress, resolved, closed)
- Filter by severity and status
- Track defect creation and resolution dates

### Reports
- 30-day historical metrics
- Pass rate trends
- Defect trends over time
- Test distribution by module
- Defect distribution by severity and status
- Export to PDF/Excel functionality

## Color Scheme & Design

The application uses Eli Lilly's professional color palette:
- **Primary**: #0066cc (Blue)
- **Secondary**: #00a3e0 (Light Blue)
- **Success**: #16a34a (Green)
- **Warning**: #ea8c00 (Orange)
- **Error**: #dc2626 (Red)
- **Critical**: #9c0a1b (Dark Red)

## Database Schema

### Tables
- `test_cases` - Test case definitions
- `test_results` - Test execution results
- `defects` - Defect tracking
- `quality_metrics` - Quality metrics snapshots

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:
```
DATABASE_URL=sqlite:///./aloca_qa.db
API_PORT=8000
```

## Development

### Backend Development
- FastAPI auto-reloads on code changes
- Swagger UI available at `http://localhost:8000/docs`
- ReDoc available at `http://localhost:8000/redoc`

### Frontend Development
- React Hot Reload enabled
- ESLint configuration included
- CSS Modules support

## Building for Production

### Backend
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Frontend
```bash
npm run build
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Security Considerations

- CORS enabled for development
- Input validation on all endpoints
- Database query protection via SQLAlchemy ORM
- Rate limiting recommended for production

## Future Enhancements

- Authentication and authorization
- User role management
- Email notifications
- Advanced filtering and search
- API rate limiting
- Database migration support
- Automated testing integration
- CI/CD pipeline integration

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify port 8000 is not in use

### Frontend won't start
- Ensure Node.js 14+ is installed
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear npm cache: `npm cache clean --force`

### CORS errors
- Backend CORS is configured for all origins in development
- For production, update `CORSMiddleware` in `main.py`

## License

Eli Lilly QA System - Internal Use Only

## Support

For issues or feature requests, please contact the QA team.
