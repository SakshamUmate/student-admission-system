import pytest
import tempfile
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# tests/conftest.py 
from app import app, db, Admin
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Create a test client with isolated database"""
    # Create a temporary file to serve as the database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    app.config['PDF_FOLDER'] = 'test_pdfs'
    
    # Create test directories
    os.makedirs('test_uploads', exist_ok=True)
    os.makedirs('test_pdfs', exist_ok=True)
    
    with app.test_client() as client:
        with app.app_context():
            # Drop all tables first to avoid conflicts
            db.drop_all()
            # Create fresh tables
            db.create_all()
            # Create test admin with unique username
            admin = Admin(
                username='testadmin_' + str(os.getpid()),  # Make username unique
                password_hash=generate_password_hash('testpass')
            )
            db.session.add(admin)
            db.session.commit()
        yield client
    
    # Cleanup
    try:
        os.close(db_fd)
        os.unlink(app.config['DATABASE'])
    except:
        pass

@pytest.fixture
def auth_client(client):
    """Client with admin logged in"""
    with client.application.app_context():
        admin = Admin.query.first()
        client.post('/admin/login', data={
            'username': admin.username,
            'password': 'testpass'
        })
    return client

