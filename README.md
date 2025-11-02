# Purity — Data Quality Dashboard

A stunning, minimalist data quality assessment tool for analyzing CSV datasets. Built with a Jony Ive-inspired flat design aesthetic featuring clean lines, surgical precision, and electric accents.

## Features

- **Instant CSV Analysis** - Upload and analyze CSV files up to 50MB
- **Comprehensive Quality Assessment**
  - Missing value detection
  - Data type inference and validation
  - Statistical outlier detection
  - Logical consistency checking
  - Duplicate record identification
- **Quality Scoring** - Automated quality score (0-100) for datasets
- **Beautiful Visualization** - Clean, flat UI with intuitive dashboards
- **Analysis History** - Track all previous analyses
- **User Authentication** - Secure login and session management
- **Export Functionality** - Download analysis reports as JSON

## Tech Stack

### Frontend
- **HTML/CSS/JavaScript** - Vanilla JS with modern ES6+
- **Design** - Flat design with monochromatic foundation + electric accent colors
- **Typography** - Inter font family
- **Icons** - Custom SVG icons

### Backend
- **Flask** - Lightweight Python web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **Flask-Login** - User authentication and session management
- **pandas** - CSV processing and data analysis
- **numpy** - Statistical calculations
- **SQLite** - Local database for users and analysis history

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── models/                  # Database models
│   │   │   ├── user.py             # User model
│   │   │   └── analysis.py         # Analysis results model
│   │   ├── routes/                  # API endpoints
│   │   │   ├── auth.py             # Authentication routes
│   │   │   ├── api.py              # Data analysis API
│   │   │   └── main.py             # Main routes
│   │   └── services/                # Business logic
│   │       ├── file_service.py     # File handling
│   │       └── analysis_service.py # CSV analysis engine
│   ├── app.py                      # Application entry point
│   ├── config.py                   # Configuration management
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables
│
├── frontend/
│   ├── index.html                  # Main dashboard
│   ├── login.html                  # Login/signup page
│   ├── styles.css                  # Main styles
│   ├── login-styles.css            # Login page styles
│   ├── app-backend.js             # Main application logic
│   └── login.js                    # Login page logic
│
├── customers.csv                   # Sample dataset
├── transactions.csv                # Sample dataset
└── inventory.csv                   # Sample dataset
```

## Installation & Setup

### Prerequisites
- Python 3.8+ installed
- Git (optional, for cloning)

### Step 1: Clone or Download
```bash
cd C:\Users\kito_\OneDrive\Desktop\project
```

### Step 2: Set Up Python Virtual Environment
```bash
cd backend
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Usage

### 1. Create an Account
- Navigate to `http://127.0.0.1:5000`
- Click "Create Account"
- Enter username, email, and password
- Click "Create Account"

### 2. Upload CSV File
- After logging in, you'll see the main dashboard
- Drag and drop a CSV file into the upload zone, or click to browse
- The system will automatically upload and analyze your file
- Maximum file size: 50MB

### 3. View Analysis Results
- Quality Score: Overall data quality rating (0-100)
- Issues Detected: Detailed breakdown of data quality problems
- Column Analysis: Per-column statistics and status
- Quality Indicators: Completeness, Validity, Consistency metrics

### 4. Review History
- Click "History" in the sidebar
- View all previous analyses
- Click "View" on any item to reload that analysis

### 5. Export Reports
- From the Analysis view, click "Export Report"
- Downloads a JSON file with complete analysis results

## Data Quality Checks

### Missing Values
- Detects empty, null, or missing values in each column
- Calculates percentage of missing data
- Severity: Error if >10%, Warning if >5%

### Invalid Formats
- **Email Validation**: Checks for valid email format (contains @ and domain)
- **Date Validation**: Identifies future dates in historical data
- **Numeric Validation**: Detects non-numeric values in numeric columns

### Statistical Outliers
- Uses 3-sigma rule (3 standard deviations from mean)
- Identifies extreme values in numeric columns
- Helps detect data entry errors

### Logical Consistency
- **Negative Values**: Flags negative values in columns that should be positive (age, price, quantity, stock)
- **Business Rules**: Checks selling price vs cost price
- **Stock Levels**: Identifies stock below reorder threshold

### Duplicate Detection
- Identifies exact duplicate records
- Helps clean redundant data

## Configuration

### Environment Variables (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///purity.db
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=csv
SESSION_TIMEOUT=3600    # 1 hour
```

### Security Notes
- Change `SECRET_KEY` in production
- Use HTTPS in production deployment
- Passwords are hashed using Werkzeug's security utilities
- Sessions use HTTP-only cookies

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile

### Data Analysis
- `POST /api/upload` - Upload CSV file
- `POST /api/analyze` - Analyze uploaded file
- `GET /api/history` - Get analysis history
- `GET /api/results/<id>` - Get specific analysis
- `GET /api/export/<id>` - Export analysis as JSON
- `DELETE /api/delete/<id>` - Delete analysis

## Design Philosophy

### Visual Design
- **Flat Design**: No gradients, shadows, or 3D effects
- **Monochromatic Foundation**: Pure blacks, surgical grays, ultra-light whites
- **Electric Accents**: Cyan (#00F0FF), Pink (#FF006E), Purple (#8000FF), Green (#00FF94)
- **Zero Border Radius**: Pure rectangles throughout
- **Surgical Typography**: Inter font with precise spacing

### User Experience
- **Intuitive Navigation**: Clear sidebar with active states
- **Immediate Feedback**: Real-time progress indicators
- **Responsive Design**: Works on desktop and tablet
- **Accessibility**: High contrast, clear labels, keyboard navigation

## Testing

### Test with Provided Datasets

The project includes three test CSV files with intentional data quality issues:

**customers.csv** (505 records)
- Missing emails (4%)
- Invalid email formats (2%)
- Missing phone numbers (7%)
- Future registration dates (3%)
- Invalid ages (1%)
- Duplicate records (5)

**transactions.csv** (2,000 records)
- Pricing errors (1%)
- Negative amounts (0.7%)
- Missing payment methods (1.25%)
- Invalid transaction statuses (1.7%)

**inventory.csv** (15 records)
- Missing suppliers (12.5%)
- Selling price < cost price (20%)
- Stock below reorder (25%)
- Future restock dates (10%)

### Running Tests
1. Navigate to the Upload page
2. Upload each CSV file
3. Verify that all intentional issues are detected
4. Check that quality scores are calculated correctly

## Deployment

### Local Deployment
Follow the Installation & Setup instructions above.

### Production Deployment
1. Set `FLASK_ENV=production` in .env
2. Use a production WSGI server (gunicorn, uWSGI)
3. Configure a reverse proxy (Nginx, Apache)
4. Enable HTTPS
5. Use a production database (PostgreSQL, MySQL)
6. Set secure SECRET_KEY
7. Configure proper logging and monitoring

## Troubleshooting

### Server Won't Start
- Check Python version: `python --version` (must be 3.8+)
- Verify virtual environment is activated
- Ensure all dependencies are installed: `pip list`
- Check for port conflicts (default: 5000)

### Database Errors
- Delete `purity.db` and restart to reset database
- Check file permissions in backend directory

### File Upload Fails
- Verify file is CSV format
- Check file size (<50MB)
- Ensure `uploads/` directory exists

### Analysis Errors
- Check CSV file is properly formatted
- Verify first row contains headers
- Ensure file is not corrupted

## Contributing

This is a project assessment submission. For feedback or questions, please contact the development team.

## License

Proprietary - Assessment Project for Junior Full-Stack Developer Position

## Acknowledgments

- Design inspiration: Jony Ive's minimalist aesthetic
- Color palette: Electric accent colors with monochromatic foundation
- Typography: Inter font family
- Icons: Custom SVG icons

---

**Built with Flask, pandas, and a lot of attention to design detail.**

*"Purity is the ultimate sophistication." — Adapted from Leonardo da Vinci*
