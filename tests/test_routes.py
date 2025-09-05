import pytest
from app import Student, db
import io

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
        # Create test files
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
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
        student = Student.query.filter_by(email='jane.smith@example.com').first()
        assert student is not None
        assert student.first_name == 'Jane'

def test_status_check_valid_id(client):
    """Test status check with valid application ID"""
    with client.application.app_context():
        # Create test student
        student = Student(
            application_id='TEST456',
            first_name='Bob',
            last_name='Johnson',
            email='bob.johnson@example.com',
            phone='5555555555',
            address='789 Test Blvd',
            date_of_birth='1994-08-20',
            course_applied='mechanical_engineering',
            previous_qualification='Bachelor of Technology',
            cgpa='7.8'
        )
        db.session.add(student)
        db.session.commit()
        
        response = client.post('/check_status', data={'application_id': 'TEST456'})
        assert response.status_code == 200
        assert b'Bob Johnson' in response.data

def test_admin_login_valid(client):
    """Test admin login with valid credentials"""
    response = client.post('/admin/login', data={
        'username': 'testadmin',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_admin_dashboard_access(auth_client):
    """Test admin dashboard access"""
    response = auth_client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data