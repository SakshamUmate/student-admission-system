from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
import uuid
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admission_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['PDF_FOLDER'] = 'static/admission_letters'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    course_applied = db.Column(db.String(100), nullable=False)
    previous_qualification = db.Column(db.String(200), nullable=False)
    cgpa = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    degree_certificate = db.Column(db.String(200))
    id_proof = db.Column(db.String(200))
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    review_date = db.Column(db.DateTime)
    admin_comments = db.Column(db.Text)
    admission_letter_path = db.Column(db.String(200))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

# Forms
class ApplicationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    date_of_birth = StringField('Date of Birth (YYYY-MM-DD)', validators=[DataRequired()])
    course_applied = SelectField('Course Applied', choices=[
        ('computer_science', 'Computer Science'),
        ('mechanical_engineering', 'Mechanical Engineering'),
        ('electrical_engineering', 'Electrical Engineering'),
        ('civil_engineering', 'Civil Engineering'),
        ('business_administration', 'Business Administration'),
        ('data_science', 'Data Science')
    ], validators=[DataRequired()])
    previous_qualification = StringField('Previous Qualification', validators=[DataRequired(), Length(min=5, max=200)])
    cgpa = StringField('CGPA/Percentage', validators=[DataRequired(), Length(min=1, max=10)])
    degree_certificate = FileField('Degree Certificate', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Only PDF, JPG, JPEG, PNG files allowed!')
    ])
    id_proof = FileField('ID Proof', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Only PDF, JPG, JPEG, PNG files allowed!')
    ])
    submit = SubmitField('Submit Application')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReviewForm(FlaskForm):
    status = SelectField('Status', choices=[('approved', 'Approve'), ('rejected', 'Reject')], validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Length(max=500)])
    submit = SubmitField('Update Status')

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_application_id():
    return f"APP{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

def save_file(file, folder):
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())[:8]}_{filename}"
        filepath = os.path.join(folder, unique_filename)
        file.save(filepath)
        return unique_filename
    return None

def generate_admission_letter(student):
    """Generate PDF admission letter for approved student"""
    filename = f"admission_letter_{student.application_id}.pdf"
    filepath = os.path.join(app.config['PDF_FOLDER'], filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title = Paragraph("UNIVERSITY ADMISSION LETTER", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Date
    date_text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Student details
    student_info = f"""
    <para>
    <b>Dear {student.first_name} {student.last_name},</b><br/><br/>
    
    Congratulations! We are pleased to inform you that your application for admission has been <b>APPROVED</b>.<br/><br/>
    
    <b>Application Details:</b><br/>
    Application ID: {student.application_id}<br/>
    Course: {student.course_applied.replace('_', ' ').title()}<br/>
    Email: {student.email}<br/>
    Phone: {student.phone}<br/>
    Previous Qualification: {student.previous_qualification}<br/>
    CGPA: {student.cgpa}<br/><br/>
    
    Please report to the admission office within 30 days of receiving this letter to complete your enrollment process.<br/><br/>
    
    Welcome to our university!<br/><br/>
    
    Best regards,<br/>
    Admissions Committee<br/>
    University Name
    </para>
    """
    
    story.append(Paragraph(student_info, styles['Normal']))
    doc.build(story)
    
    return filename

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    form = ApplicationForm()
    if form.validate_on_submit():
        # Save uploaded files
        degree_cert_filename = save_file(form.degree_certificate.data, app.config['UPLOAD_FOLDER'])
        id_proof_filename = save_file(form.id_proof.data, app.config['UPLOAD_FOLDER'])
        
        # Create new student application
        student = Student(
            application_id=generate_application_id(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            course_applied=form.course_applied.data,
            previous_qualification=form.previous_qualification.data,
            cgpa=form.cgpa.data,
            degree_certificate=degree_cert_filename,
            id_proof=id_proof_filename
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash(f'Application submitted successfully! Your Application ID is: {student.application_id}', 'success')
        return redirect(url_for('application_status'))
    
    return render_template('apply.html', form=form)

@app.route('/status')
def application_status():
    return render_template('status.html')

@app.route('/check_status', methods=['POST'])
def check_status():
    application_id = request.form.get('application_id')
    student = Student.query.filter_by(application_id=application_id).first()
    
    if student:
        return render_template('status_result.html', student=student)
    else:
        flash('Application ID not found!', 'error')
        return redirect(url_for('application_status'))

@app.route('/download_letter/<application_id>')
def download_letter(application_id):
    student = Student.query.filter_by(application_id=application_id).first()
    
    if not student or student.status != 'approved':
        flash('Admission letter not available!', 'error')
        return redirect(url_for('application_status'))
    
    if student.admission_letter_path:
        filepath = os.path.join(app.config['PDF_FOLDER'], student.admission_letter_path)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=f"admission_letter_{application_id}.pdf")
    
    flash('Admission letter not found!', 'error')
    return redirect(url_for('application_status'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password!', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    applications = Student.query.order_by(Student.application_date.desc()).all()
    return render_template('admin_dashboard.html', applications=applications)

@app.route('/admin/review/<int:student_id>', methods=['GET', 'POST'])
@login_required
def review_application(student_id):
    student = Student.query.get_or_404(student_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        student.status = form.status.data
        student.admin_comments = form.comments.data
        student.review_date = datetime.utcnow()
        
        # Generate admission letter if approved
        if form.status.data == 'approved':
            letter_filename = generate_admission_letter(student)
            student.admission_letter_path = letter_filename
        
        db.session.commit()
        flash(f'Application {form.status.data} successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('review_application.html', student=student, form=form)

# API Routes
@app.route('/api/applications')
@login_required
def api_applications():
    applications = Student.query.all()
    return jsonify([{
        'id': app.id,
        'application_id': app.application_id,
        'name': f"{app.first_name} {app.last_name}",
        'email': app.email,
        'course': app.course_applied,
        'status': app.status,
        'application_date': app.application_date.isoformat() if app.application_date else None
    } for app in applications])

@app.route('/api/application/<int:student_id>')
@login_required
def api_application_detail(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'id': student.id,
        'application_id': student.application_id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'phone': student.phone,
        'course_applied': student.course_applied,
        'status': student.status,
        'cgpa': student.cgpa,
        'application_date': student.application_date.isoformat() if student.application_date else None,
        'admin_comments': student.admin_comments
    })

def create_admin_user():
    """Create default admin user if not exists"""
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)