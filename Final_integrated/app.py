from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from dotenv import load_dotenv
from service_client import IntegratedServices

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key")

# Create the integrated services client
services = IntegratedServices()

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class FeedbackForm(FlaskForm):
    message = TextAreaField('Feedback', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        result = services.register_user(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if result:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Email may already be in use.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        success = services.login_user(
            email=form.email.data,
            password=form.password.data
        )
        print(success)
        if success:
            # Store user info in session
            session['user_id'] = services.current_user.get('_id')
            session['email'] = services.current_user.get('email')
            session['name'] = services.current_user.get('name')
            session['role'] = services.current_user.get('role')
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    # Get user's activity logs
    activity_logs = services.get_user_activity(limit=5)
    
    return render_template('dashboard.html', activity_logs=activity_logs)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        flash('Please log in to submit feedback.', 'warning')
        return redirect(url_for('login'))
    
    form = FeedbackForm()
    if form.validate_on_submit():
        success = services.submit_user_feedback(form.message.data)
        
        if success:
            flash('Feedback submitted successfully!', 'success')
            form.message.data = ''
        else:
            flash('Failed to submit feedback.', 'danger')
    
    return render_template('feedback.html', form=form)

@app.route('/activity')
def activity():
    if 'user_id' not in session:
        flash('Please log in to view your activity.', 'warning')
        return redirect(url_for('login'))
    
    # Get user's activity logs
    activity_logs = services.get_user_activity(limit=20)
    
    return render_template('activity.html', activity_logs=activity_logs)

@app.route('/admin/feedback')
def admin_feedback():
    if 'user_id' not in session:
        flash('Please log in to access admin features.', 'warning')
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all feedback
    all_feedback = services.get_all_feedback()
    
    return render_template('admin_feedback.html', feedbacks=all_feedback)

@app.route('/refresh-token')
def refresh_token():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success = services.refresh_session()
    
    if success:
        return 'Token refreshed successfully'
    else:
        # If token refresh fails, log the user out
        return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    if 'user_id' in session:
        services.logout()
        
    # Clear session data
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)