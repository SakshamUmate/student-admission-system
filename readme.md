# Student Admission System

A comprehensive web-based application for managing student admissions, built with Flask and modern web technologies.

## Project Overview

The Student Admission System streamlines the entire admission process from application submission to final decision. Students can submit their applications online with required documents, while administrators can efficiently review, approve, or reject applications. The system automatically generates PDF admission letters for approved students.

### Key Features

- **Student Application Portal**: Online form with document upload capabilities
- **Admin Dashboard**: Comprehensive interface for reviewing applications
- **Document Management**: Secure file upload and storage system
- **PDF Generation**: Automatic admission letter creation
- **Status Tracking**: Real-time application status checking
- **RESTful API**: JSON endpoints for external integration
- **Responsive Design**: Mobile-friendly Bootstrap interface

## Technology Stack

- **Backend**: Python 3.7+, Flask 2.3.3
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL/MySQL (production)
- **Forms**: Flask-WTF with WTForms validation
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, Bootstrap 5.1.3, JavaScript
- **Testing**: Pytest with Flask testing utilities
- **Security**: Werkzeug password hashing, Flask-WTF CSRF protection

## Installation Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd student-admission-system
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Environment Variables (Optional)

```bash
# Create .env file for production settings
echo "SECRET_KEY=your-production-secret-key" > .env
echo "DATABASE_URL=your-database-url" >> .env
```

### Step 5: Initialize Database

```bash
python app.py
```

The application will automatically:

- Create the SQLite database
- Set up all required tables
- Create a default admin user (username: `admin`, password: `admin123`)

### Step 6: Create Required Directories

The application automatically creates these directories, but you can create them manually if needed:

```bash
mkdir -p static/uploads
mkdir -p static/admission_letters
mkdir -p templates
```

## Usage Instructions

### Running the Application

1. **Start the development server:**

   ```bash
   python app.py
   ```

2. **Access the application:**
   - Open your web browser
   - Navigate to `http://localhost:5000`

### For Students

1. **Submit Application:**

   - Go to the home page and click "Apply Now"
   - Fill out the application form with personal and academic information
   - Upload required documents (degree certificate and ID proof)
   - Submit the form to receive your unique Application ID

2. **Check Application Status:**
   - Click "Check Status" from the navigation menu
   - Enter your Application ID
   - View your application status and details
   - Download admission letter if approved

### For Administrators

1. **Login to Admin Panel:**

   - Click "Admin Login" from the navigation menu
   - Use credentials: username `admin`, password `admin123`
   - Change default password after first login

2. **Review Applications:**

   - Access the Admin Dashboard to see all applications
   - Click "Review" on any application to see detailed information
   - View uploaded documents
   - Approve or reject applications with optional comments
   - Approved applications automatically generate PDF admission letters

3. **Manage Applications:**
   - View application statistics on the dashboard
   - Filter applications by status
   - Access individual application details
   - Update application status and add comments

### API Usage

The system provides RESTful API endpoints for external integration:

1. **Get All Applications:**

   ```bash
   GET /api/applications
   # Requires admin authentication
   ```

2. **Get Specific Application:**
   ```bash
   GET /api/application/<student_id>
   # Requires admin authentication
   ```

## File Structure

```
student-admission-system/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── FRD.md                     # Functional Requirements Document
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Home page
│   ├── apply.html             # Application form
│   ├── status.html            # Status check page
│   ├── status_result.html     # Status display
│   ├── admin_login.html       # Admin login
│   ├── admin_dashboard.html   # Admin dashboard
│   └── review_application.html # Application review
├── static/
│   ├── uploads/               # Student uploaded documents
│   └── admission_letters/     # Generated PDF letters
├── tests/                     # Test files
│   ├── conftest.py           # Test configuration
│   ├── test_models.py        # Model tests
│   ├── test_routes.py        # Route tests
│   ├── test_forms.py         # Form tests
│   └── test_integration.py   # Integration tests
└── instance/
    └── admission_system.db    # SQLite database (auto-created)
```

## Testing

The project includes comprehensive test coverage using Test-Driven Development (TDD) principles.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run with coverage report
pytest --cov=app
```

### Test Categories

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test complete workflows
3. **Form Validation Tests**: Test form input validation
4. **Route Tests**: Test all application endpoints
5. **Authentication Tests**: Test security features

### Test Coverage

The test suite covers:

- Model creation and validation
- Form submission and validation
- User authentication and authorization
- File upload functionality
- PDF generation
- API endpoints
- Complete application workflow

## Configuration

### Environment Variables

| Variable        | Description                   | Default                               |
| --------------- | ----------------------------- | ------------------------------------- |
| `SECRET_KEY`    | Flask secret key for sessions | `dev-secret-key-change-in-production` |
| `DATABASE_URL`  | Database connection string    | `sqlite:///admission_system.db`       |
| `UPLOAD_FOLDER` | Directory for uploaded files  | `static/uploads`                      |
| `PDF_FOLDER`    | Directory for generated PDFs  | `static/admission_letters`            |

### Database Configuration

- **Development**: SQLite database (admission_system.db)
- **Production**: PostgreSQL or MySQL (set via DATABASE_URL)

### File Upload Settings

- **Maximum File Size**: 16MB
- **Allowed Extensions**: PDF, JPG, JPEG, PNG
- **Storage**: Local filesystem with unique filenames

## Security Features

1. **Password Hashing**: Werkzeug security for admin passwords
2. **CSRF Protection**: Flask-WTF CSRF tokens
3. **Input Validation**: Comprehensive form validation
4. **File Security**: Secure filename generation and validation
5. **Session Management**: Flask secure sessions
6. **SQL Injection Prevention**: SQLAlchemy ORM protection

## Deployment

### Development Deployment

```bash
python app.py
```

### Production Deployment

1. **Using Gunicorn:**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Using Docker:**

   ```dockerfile
   FROM python:3.9
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   EXPOSE 5000
   CMD ["python", "app.py"]
   ```

3. **Environment Setup:**
   - Set production SECRET_KEY
   - Configure production database
   - Set up proper file permissions
   - Configure reverse proxy (Nginx)

## Database Schema

### Student Table

- `id`: Primary key
- `application_id`: Unique application identifier
- `first_name`, `last_name`: Student name
- `email`, `phone`: Contact information
- `address`: Student address
- `date_of_birth`: Student DOB
- `course_applied`: Selected course
- `previous_qualification`: Academic background
- `cgpa`: Academic performance
- `status`: Application status (pending/approved/rejected)
- `degree_certificate`, `id_proof`: Uploaded file names
- `application_date`: Submission timestamp
- `review_date`: Review timestamp
- `admin_comments`: Admin feedback
- `admission_letter_path`: PDF file path

### Admin Table

- `id`: Primary key
- `username`: Admin username
- `password_hash`: Hashed password

## API Documentation

### Authentication

All API endpoints require admin authentication via session cookies.

### Endpoints

#### GET /api/applications

Returns list of all applications.

**Response:**

```json
[
  {
    "id": 1,
    "application_id": "APP20241201ABCD1234",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "course": "computer_science",
    "status": "pending",
    "application_date": "2024-12-01T10:30:00"
  }
]
```

#### GET /api/application/<id>

Returns detailed information for a specific application.

**Response:**

```json
{
  "id": 1,
  "application_id": "APP20241201ABCD1234",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "1234567890",
  "course_applied": "computer_science",
  "status": "approved",
  "cgpa": "8.5",
  "application_date": "2024-12-01T10:30:00",
  "admin_comments": "Excellent candidate"
}
```

## Assumptions and Design Decisions

### Assumptions Made During Development

1. **User Environment:**

   - Users have modern web browsers with JavaScript enabled
   - Stable internet connection for file uploads
   - Basic computer literacy for administrators

2. **Data Constraints:**

   - Application IDs are unique and sufficient for tracking
   - File uploads are reasonable in size (under 16MB)
   - Single admin role is sufficient for initial deployment

3. **Business Logic:**
   - Applications can only be in one of three states: pending, approved, rejected
   - Once approved, admission letters are immediately available
   - Student personal information is accurate and verified externally

### Design Decisions

1. **Database Choice:**

   - SQLite for development simplicity
   - Support for PostgreSQL/MySQL in production
   - SQLAlchemy ORM for database abstraction

2. **File Storage:**

   - Local filesystem storage for simplicity
   - Unique filename generation to prevent conflicts
   - Server-side storage for security

3. **PDF Generation:**

   - ReportLab for professional document creation
   - Server-side generation for security
   - Immediate generation upon approval

4. **Authentication:**

   - Session-based authentication for simplicity
   - Single admin role to start with
   - Password hashing for security

5. **Frontend Framework:**
   - Bootstrap for responsive design
   - Server-side rendering for simplicity
   - Progressive enhancement approach

## Troubleshooting

### Common Issues

1. **Database Connection Errors:**

   ```bash
   # Recreate database
   rm instance/admission_system.db
   python app.py
   ```

2. **File Upload Issues:**

   ```bash
   # Check directory permissions
   chmod 755 static/uploads
   chmod 755 static/admission_letters
   ```

3. **Template Not Found:**

   - Ensure all template files are in the `templates/` directory
   - Check file names match exactly

4. **Admin Login Issues:**
   - Default credentials: admin / admin123
   - Clear browser cookies if session issues persist

### Debug Mode

Enable debug mode for development:

```python
app.run(debug=True)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run test suite: `pytest`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the GitHub repository
- Check the documentation and FAQ
- Review test files for usage examples

## Changelog

### Version 1.0.0 (Initial Release)

- Student application submission
- Admin review interface
- PDF admission letter generation
- Status tracking system
- RESTful API endpoints
- Comprehensive test suite
- Responsive web interface

---

_For technical documentation and requirements, see the Functional Requirements Document (FRD.md)._
