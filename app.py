import os
import uuid
import boto3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from boto3.dynamodb.conditions import Key, Attr

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'medtrack_secret_key_123')

# Initialize AWS DynamoDB
region = os.getenv('AWS_REGION', 'eu-north-1')
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

if aws_access_key and aws_secret_key:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
    sns = boto3.client(
        'sns',
        region_name=region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
else:
    dynamodb = boto3.resource('dynamodb', region_name=region)
    sns = boto3.client('sns', region_name=region)

users_table = dynamodb.Table('UsersTable')
appointments_table = dynamodb.Table('AppointmentsTable')

TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

def send_notification(message, subject="MedTrack Notification"):
    if not TOPIC_ARN or "replace_with" in TOPIC_ARN:
        print(f"SNS notification skipped: {message}")
        return
    try:
        sns.publish(TopicArn=TOPIC_ARN, Message=message, Subject=subject)
    except Exception as e:
        print(f"Failed to send SNS: {e}")

def subscribe_user(email):
    """Automatically signs up a user to the SNS topic for alerts"""
    if not TOPIC_ARN or "replace_with" in TOPIC_ARN:
        return
    try:
        sns.subscribe(TopicArn=TOPIC_ARN, Protocol='email', Endpoint=email)
        print(f"Subscription invitation sent to {email}")
    except Exception as e:
        print(f"Subscription failed for {email}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role_selected = request.form.get('role')
        
        try:
            response = users_table.get_item(Key={'email': email})
            user = response.get('Item')
            
            if user and check_password_hash(user['PasswordHash'], password):
                if user.get('Role') == role_selected:
                    session['user_id'] = user['email']
                    session['role'] = user.get('Role')
                    session['name'] = user['Name']
                    flash(f"Welcome back, {session['name']}!")
                    return redirect(url_for('dashboard'))
                else:
                    flash(f"Unauthorized: You are registered as a {user.get('Role')}.")
            else:
                flash("Invalid email or password.")
        except Exception as e:
            flash(f"Database Error: {e}")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role', 'patient')
        specialization = request.form.get('specialization', 'General')
        
        try:
            if users_table.get_item(Key={'email': email}).get('Item'):
                flash("Email already registered.")
                return redirect(url_for('register'))

            password_hash = generate_password_hash(password)
            users_table.put_item(
                Item={
                    'email': email,
                    'Name': name,
                    'PasswordHash': password_hash,
                    'Phone': phone,
                    'Role': role,
                    'Specialization': specialization
                }
            )
            # NEW: Automatically invite them to get email alerts!
            subscribe_user(email)
            
            # Send the "Thank you for registering" mail content to the topic
            welcome_msg = (f"MedTrack Welcome!\n\n"
                          f"Hello {name},\n"
                          f"Thank you for registering with MedTrack Healthcare Cloud.\n"
                          f"Your account as a {role} is now active.")
            send_notification(welcome_msg, "MedTrack: Welcome!")
            
            flash(f"Thank you for registering, {name}! Please check your email and click 'Confirm' to receive your details.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}")
            
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    email = session['user_id']
    role = session['role']
    search_query = request.args.get('search', '').lower()
    
    try:
        if role == 'patient':
            response = appointments_table.query(
                IndexName='PatientIndex',
                KeyConditionExpression=Key('patient_email').eq(email)
            )
        else:
            response = appointments_table.scan(
                FilterExpression=Attr('doctor_email').eq(email)
            )
            
        appointments = response.get('Items', [])
        
        # Filter by search query if present
        if search_query:
            appointments = [a for a in appointments if search_query in a.get('PatientName', '').lower()]
            
        appointments.sort(key=lambda x: (x['Date'], x['Time']))
    except Exception as e:
        print(f"Dashboard error: {e}")
        appointments = []

    return render_template('dashboard.html', appointments=appointments)

@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        doctor_email = request.form.get('doctor_id')
        date = request.form.get('date')
        time = request.form.get('time')
        reason = request.form.get('reason')
        
        try:
            appointment_id = str(uuid.uuid4())
            appointments_table.put_item(
                Item={
                    'appointment_id': appointment_id,
                    'patient_email': session['user_id'],
                    'PatientName': session['name'],
                    'doctor_email': doctor_email,
                    'Date': date,
                    'Time': time,
                    'Reason': reason,
                    'Status': 'Scheduled'
                }
            )
            
            msg = (f"MedTrack: Appointment Confirmed!\n\n"
                   f"Hello {session['name']},\n"
                   f"Thank you for booking with us. Here are your details:\n\n"
                   f"Date: {date}\n"
                   f"Time: {time}\n"
                   f"Doctor Email: {doctor_email}\n"
                   f"Reason: {reason}\n\n"
                   f"See you soon!")
            
            send_notification(msg, "MedTrack: Appointment Details")
            flash(f"Success! Your appointment is confirmed for {date} at {time}. We look forward to seeing you!")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Booking Error: {str(e)}")
            
    doctors = users_table.scan(FilterExpression=Attr('Role').eq('doctor')).get('Items', [])
    return render_template('book.html', doctors=doctors)

@app.route('/diagnose/<appointment_id>', methods=['GET', 'POST'])
def submit_diagnosis(appointment_id):
    if 'user_id' not in session or session.get('role') != 'doctor':
        return redirect(url_for('login'))
    
    try:
        appointment = appointments_table.get_item(Key={'appointment_id': appointment_id}).get('Item')
        if not appointment or appointment['doctor_email'] != session['user_id']:
            flash("Access denied.")
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            title = request.form.get('title')
            observations = request.form.get('observations')
            treatment = request.form.get('treatment')
            
            appointments_table.update_item(
                Key={'appointment_id': appointment_id},
                UpdateExpression="SET #s = :s, Title = :t, Observations = :o, Treatment = :tr",
                ExpressionAttributeNames={'#s': 'Status'},
                ExpressionAttributeValues={':s': 'Completed', ':t': title, ':o': observations, ':tr': treatment}
            )
            flash("Diagnosis submitted!")
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error: {e}")

    return render_template('diagnose.html', appointment=appointment)

@app.route('/history')
@app.route('/history/<patient_email>')
def medical_history(patient_email=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    target_email = patient_email if patient_email else session['user_id']
    response = appointments_table.query(
        IndexName='PatientIndex',
        KeyConditionExpression=Key('patient_email').eq(target_email)
    )
    history = [i for i in response.get('Items', []) if i.get('Status') == 'Completed']
    return render_template('history.html', history=history, patient_email=patient_email)

@app.route('/cancel/<appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    try:
        # Fetch to get details for SNS
        appt = appointments_table.get_item(Key={'appointment_id': appointment_id}).get('Item')
        if not appt:
            flash("Appointment not found.")
            return redirect(url_for('dashboard'))
            
        # Permission check
        if appt['patient_email'] != session['user_id'] and appt['doctor_email'] != session['user_id']:
            flash("Access denied.")
            return redirect(url_for('dashboard'))

        appointments_table.update_item(
            Key={'appointment_id': appointment_id},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeNames={'#s': 'Status'},
            ExpressionAttributeValues={':s': 'Cancelled'}
        )
        
        send_notification(f"Appointment Cancelled!\nDate: {appt['Date']}\nPatient: {appt['PatientName']}", "MedTrack Cancelled")
        flash("Appointment cancelled successfully.")
    except Exception as e:
        flash(f"Error: {e}")
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
