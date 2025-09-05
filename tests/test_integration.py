
# tests/test_integration.py 
import pytest
from app import Student, db
import io
import uuid

def test_complete_application_workflow(auth_client):
    """Test complete application workflow from submission to approval"""
    with auth_client.application.app_context():
        unique_id = str(uuid.uuid4())[:8]
        # Step 1: Submit application
        data = {
            'first_name': 'Integration',
            'last_name': 'Test',
            'email': f'integration.test.{unique_id}@example.com',
            'phone': '9999999999',
            'address': '999 Integration Way',
            'date_of_birth': '1990-01-01',
            'course_applied': 'business_administration',
            'previous_qualification': 'Bachelor of Commerce',
            'cgpa': '8.0',
            'degree_certificate': (io.BytesIO(b'test degree'), 'degree.pdf'),
            'id_proof': (io.BytesIO(b'test id'), 'id.pdf')
        }
        
        response = auth_client.post('/apply', data=data, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 2: Find the created student
        student = Student.query.filter_by(email=f'integration.test.{unique_id}@example.com').first()
        assert student is not None
        assert student.status == 'pending'
        
        # Step 3: Admin reviews and approves
        response = auth_client.post(f'/admin/review/{student.id}', data={
            'status': 'approved',
            'comments': 'Integration test approval'
        })
        
        # Step 4: Check final status
        updated_student = Student.query.get(student.id)
        assert updated_student.status == 'approved'
        assert updated_student.admission_letter_path is not None
        
        # Step 5: Test status check
        response = auth_client.post('/check_status', data={
            'application_id': student.application_id
        })
        assert response.status_code == 200
        assert b'Integration Test' in response.data
        assert b'Approved' in response.data

def test_rejection_workflow(auth_client):
    """Test application rejection workflow"""
    with auth_client.application.app_context():
        unique_id = str(uuid.uuid4())[:8]
        # Create test student
        student = Student(
            application_id=f'REJECT{unique_id}',
            first_name='Reject',
            last_name='Test',
            email=f'reject.test.{unique_id}@example.com',
            phone='8888888888',
            address='888 Reject St',
            date_of_birth='1991-01-01',
            course_applied='civil_engineering',
            previous_qualification='Bachelor of Engineering',
            cgpa='6.0'
        )
        db.session.add(student)
        db.session.commit()
        
        # Reject the application
        response = auth_client.post(f'/admin/review/{student.id}', data={
            'status': 'rejected',
            'comments': 'Does not meet minimum requirements'
        })
        
        # Check status was updated
        updated_student = Student.query.get(student.id)
        assert updated_student.status == 'rejected'
        assert updated_student.admin_comments == 'Does not meet minimum requirements'
        
        # Test status check shows rejection
        response = auth_client.post('/check_status', data={
            'application_id': student.application_id
        })
        assert response.status_code == 200
        assert b'Rejected' in response.data