
# tests/test_forms.py 
import pytest
from app import ApplicationForm, LoginForm, ReviewForm, app

def test_application_form_validation():
    """Test application form validation"""
    with app.app_context():
        form = ApplicationForm(
            first_name='',
            email='invalid-email',
            phone='123'
        )
        assert not form.validate()

def test_application_form_valid_data():
    """Test application form with valid data"""
    with app.app_context():
        form = ApplicationForm(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            address='123 Test Street, Test City',
            date_of_birth='1995-01-01',
            course_applied='computer_science',
            previous_qualification='Bachelor of Science in Computer Science',
            cgpa='8.5'
        )
        # Note: File fields will fail validation without actual files
        # This tests the text field validation
        form.degree_certificate.data = None
        form.id_proof.data = None
        
        # Check individual field validation (excluding file fields)
        assert form.first_name.validate(form)
        assert form.last_name.validate(form)
        assert form.email.validate(form)
        assert form.phone.validate(form)

def test_login_form_validation():
    """Test login form validation"""
    with app.app_context():
        form = LoginForm(username='', password='')
        assert not form.validate()

def test_login_form_valid_data():
    """Test login form with valid data"""
    with app.app_context():
        form = LoginForm(username='admin', password='password123')
        assert form.validate()

def test_review_form_validation():
    """Test review form validation"""
    with app.app_context():
        form = ReviewForm(status='', comments='x' * 501)  # Exceeds max length
        assert not form.validate()

def test_review_form_valid_data():
    """Test review form with valid data"""
    with app.app_context():
        form = ReviewForm(status='approved', comments='Good application')
        assert form.validate()
