# tests/test_models.py
import pytest
from app import Student, Admin, db, generate_application_id
from werkzeug.security import check_password_hash
import uuid

def test_student_creation(client):
    """Test student model creation"""
    with client.application.app_context():
        unique_id = str(uuid.uuid4())[:8]
        student = Student(
            application_id=f'TEST{unique_id}',
            first_name='John',
            last_name='Doe',
            email=f'john.doe.{unique_id}@example.com',
            phone='1234567890',
            address='123 Test St',
            date_of_birth='1995-01-01',
            course_applied='computer_science',
            previous_qualification='Bachelor of Science',
            cgpa='8.5'
        )
        db.session.add(student)
        db.session.commit()
        
        assert student.id is not None
        assert student.status == 'pending'
        assert student.first_name == 'John'

def test_admin_password_hashing(client):
    """Test admin password hashing"""
    with client.application.app_context():
        admin = Admin.query.first()
        assert admin is not None
        assert check_password_hash(admin.password_hash, 'testpass')

def test_application_id_generation():
    """Test application ID generation"""
    app_id = generate_application_id()
    assert app_id.startswith('APP')
    assert len(app_id) == 19  # APP + 8 digit date + 8 char UUID

# tests/test_routes.py - FIXED VERSION  
import pytest
from app import Student, db
import io
import uuid

def test_index_route(client):
    """Test home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Student Admission System' in response.data

def test_apply_page_get(client):
    """Test application form display"""
    response = client.get('/apply')
    assert response.status_code == 200
    assert b'Student Application Form' in response.data

def test_apply_form_submission(client):
    """Test application form submission"""
    with client.application.app_context():
        unique_id = str(uuid.uuid4())[:8]
        # Create test files
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': f'jane.smith.{unique_id}@example.com',
            'phone': '9876543210',
            'address': '456 Test Ave',
            'date_of_birth': '1996-05-15',
            'course_applied': 'data_science',
            'previous_qualification': 'Bachelor of Engineering',
            'cgpa': '9.0',
            'degree_certificate': (io.BytesIO(b'test degree content'), 'degree.pdf'),
            'id_proof': (io.BytesIO(b'test id content'), 'id.pdf')
        }
        
        response = client.post('/apply', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Application submitted successfully' in response.data
        
        # Check if student was created in database
        student = Student.query.filter_by(email=f'jane.smith.{unique_id}@example.com').first()
        assert student is not None
        assert student.first_name == 'Jane'

def test_status_check_valid_id(client):
    """Test status check with valid application ID"""
    with client.application.app_context():
        unique_id = str(uuid.uuid4())[:8]
        # Create test student
        student = Student(
            application_id=f'TEST{unique_id}',
            first_name='Bob',
            last_name='Johnson',
            email=f'bob.johnson.{unique_id}@example.com',
            phone='5555555555',
            address='789 Test Blvd',
            date_of_birth='1994-08-20',
            course_applied='mechanical_engineering',
            previous_qualification='Bachelor of Technology',
            cgpa='7.8'
        )
        db.session.add(student)
        db.session.commit()
        
        response = client.post('/check_status', data={'application_id': f'TEST{unique_id}'})
        assert response.status_code == 200
        assert b'Bob Johnson' in response.data

def test_status_check_invalid_id(client):
    """Test status check with invalid application ID"""
    response = client.post('/check_status', data={'application_id': 'INVALID123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Application ID not found' in response.data

def test_admin_login_valid(client):
    """Test admin login with valid credentials"""
    with client.application.app_context():
        admin = Admin.query.first()
        response = client.post('/admin/login', data={
            'username': admin.username,
            'password': 'testpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data

def test_admin_login_invalid(client):
    """Test admin login with invalid credentials"""
    response = client.post('/admin/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_admin_dashboard_access(auth_client):
    """Test admin dashboard access"""
    response = auth_client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_admin_dashboard_unauthorized(client):
    """Test admin dashboard without login"""
    response = client.get('/admin/dashboard')
    assert response.status_code == 302  # Redirect to login

def test_review_application(auth_client):
    """Test application review functionality"""
    with auth_client.application.app_context():
        unique_id = str(uuid.uuid4())[:8]
        # Create test student
        student = Student(
            application_id=f'REVIEW{unique_id}',
            first_name='Alice',
            last_name='Wilson',
            email=f'alice.wilson.{unique_id}@example.com',
            phone='1111111111',
            address='321 Review St',
            date_of_birth='1993-12-10',
            course_applied='computer_science',
            previous_qualification='Bachelor of Computer Applications',
            cgpa='8.9'
        )
        db.session.add(student)
        db.session.commit()
        
        student_id = student.id
        
        # Test approval
        response = auth_client.post(f'/admin/review/{student_id}', data={
            'status': 'approved',
            'comments': 'Excellent application'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Application approved successfully' in response.data
        
        # Check if student status was updated
        updated_student = Student.query.get(student_id)
        assert updated_student.status == 'approved'
        assert updated_student.admin_comments == 'Excellent application'

def test_api_applications(auth_client):
    """Test API endpoint for applications"""
    response = auth_client.get('/api/applications')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
