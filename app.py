import os
import re
import random
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from sqlalchemy import text

from database import db
from models import User

app = Flask(__name__, template_folder='templates', static_folder='templates')
app.secret_key = 'calseva_super_secret_session_encryption_key'

# Configure PostgreSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:parthpostgress89##@localhost:5432/calsevav2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Helper function to send email via SMTP
def send_otp_email(to_email, otp_code):
    sender = "supportcalsevatec@gmail.com"
    app_password = "wvib cbaq dsza sexe"
    
    subject = "Your One-Time Password (OTP) - CalSEVA"
    
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center; color: #333333; padding: 20px; background-color: #f4f6f4;">
        <div style="max-width: 500px; margin: auto; border: 1px solid #dddddd; border-radius: 12px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); background-color: #ffffff;">
          <div style="text-align: center; margin: 0 auto 20px auto;">
            <img src="cid:logo" alt="CalSEVA Logo" style="width: 80px; height: 80px; object-fit: contain;">
          </div>
          <h2 style="color: #3A606E; margin-bottom: 5px; font-size: 20px; font-weight: bold;">Calseva Tec Solutions PVT.LTD</h2>
          <hr style="border: 0; border-top: 1.5px solid #eeeeee; margin: 20px 0;">
          <p style="font-size: 15px; line-height: 1.5; color: #555555; text-align: left;">Dear Customer,</p>
          <p style="font-size: 15px; line-height: 1.5; color: #555555; text-align: left;">You requested a One-Time Password (OTP) to login your account.</p>
          <p style="font-size: 15px; line-height: 1.5; color: #555555; text-align: left;">Your OTP is:</p>
          <div style="background-color: #f7f9f7; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h1 style="font-size: 38px; color: #3A606E; letter-spacing: 6px; margin: 0; font-weight: bold;">{otp_code}</h1>
          </div>
          <p style="font-size: 13px; color: #E35E5E; text-align: left;"><strong>Important:</strong> This code is valid for the next 5 minutes and can only be used once.</p>
          <hr style="border: 0; border-top: 1.5px solid #eeeeee; margin: 20px 0;">
          <p style="font-size: 11px; color: #888888; line-height: 1.5; text-align: left;">
            If you did not request this code, please ignore this email or secure your account immediately. Never share your OTP with anyone.
          </p>
          <p style="font-size: 13px; color: #666666; margin-top: 25px; text-align: left; line-height: 1.4;">
            Best regards,<br>
            <strong>Calseva Support Team</strong>
          </p>
        </div>
      </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = f"Calseva Support <{sender}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    # Attach Logo as inline CID image
    logo_path = "templates/caliprofile-pages/Calsevalogo.png"
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as f:
                img_data = f.read()
            msg_image = MIMEImage(img_data)
            msg_image.add_header('Content-ID', '<logo>')
            msg_image.add_header('Content-Disposition', 'inline', filename="Calsevalogo.png")
            msg.attach(msg_image)
        except Exception as attach_err:
            print(f"Error attaching logo: {attach_err}")
    else:
        print(f"Logo file not found at: {logo_path}")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, app_password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Validation helper for password complexity (8+ chars, alphanumeric + special character)
def is_valid_password(password):
    if len(password) < 8:
        return False
    # Must contain letter, number, and special character
    has_letter = re.search(r"[A-Za-z]", password)
    has_digit = re.search(r"\d", password)
    has_special = re.search(r"[@$!%*#?&_#@!%^&*()-+=]", password)
    return bool(has_letter and has_digit and has_special)

# Root route - Redirect to Login
@app.route('/')
def index():
    return redirect(url_for('serve_page_or_static', filepath='cal-login/cal-login.html'))

# Google Auth Fallback Handler
@app.route('/google-auth-fallback', methods=['POST'])
def google_auth_fallback():
    flash("Temporary unable to Proceed")
    # Redirect back to the referrer or login
    referrer = request.referrer or url_for('serve_page_or_static', filepath='cal-login/cal-login.html')
    return redirect(referrer)

# Login Page handler (intercepts GET and POST)
@app.route('/cal-login/cal-login.html', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId', '').strip()
        password = request.form.get('password', '').strip()

        # 1. Invalid Credentials check (empty fields)
        if not employee_id or not password:
            flash("Invalid Credentials")
            return redirect(url_for('login_route'))

        # 2. Employee ID format check (must be exactly 5 digits)
        if not re.match(r"^\d{5}$", employee_id):
            flash("Invalid Username Please Signup")
            return redirect(url_for('login_route'))

        # 3. Password Complexity validation
        if not is_valid_password(password):
            flash("Invalid Password Please Signup")
            return redirect(url_for('login_route'))

        # 4. User lookup in database
        try:
            user = User.query.filter_by(employee_id=employee_id).first()
            if not user:
                flash("Invalid Username Please Signup")
                return redirect(url_for('login_route'))
            
            # Check password hash match
            if not user.check_password(password):
                flash("Invalid Password Please Signup")
                return redirect(url_for('login_route'))

            # Successful Authentication -> Send OTP via email
            otp_code = str(random.randint(100000, 999999))
            session['otp_code'] = otp_code
            session['temp_employee_id'] = employee_id

            email_sent = send_otp_email(user.email, otp_code)
            if not email_sent:
                # Network or SMTP delivery issue fallback
                flash("Please try again later")
                return redirect(url_for('login_route'))

            # Redirect to verification code entries page
            return redirect(url_for('serve_page_or_static', filepath='caliverify/caliverify.html'))

        except Exception as db_err:
            print(f"Database error during login: {db_err}")
            # Server error fallback
            flash("Please try again later")
            return redirect(url_for('login_route'))

    return render_template('cal-login/cal-login.html')

# Signup Page handler (intercepts GET and POST)
@app.route('/cal-signup/cal-signup.html', methods=['GET', 'POST'])
def signup_route():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()

        # 1. Invalid Credentials check (empty fields)
        if not employee_id or not email or not phone or not password:
            flash("Invalid Credentials")
            return redirect(url_for('signup_route'))

        # 2. Employee ID check (exactly 5 digits)
        if not re.match(r"^\d{5}$", employee_id):
            flash("Employee ID must be exactly 5 digits")
            return redirect(url_for('signup_route'))

        # 3. Phone number check (exactly 10 digits)
        if not re.match(r"^\d{10}$", phone):
            flash("Phone no must be written in 10 digits")
            return redirect(url_for('signup_route'))

        # 4. Email check (must be a valid gmail format ending with @gmail.com)
        if not email.lower().endswith('@gmail.com'):
            flash("Email must be email format mostly as @gmail.com")
            return redirect(url_for('signup_route'))

        # 5. Password Complexity check
        if not is_valid_password(password):
            flash("Password must contain at least 8 alphanumeric characters and special symbols")
            return redirect(url_for('signup_route'))

        try:
            # Check if user already exists
            existing_user = User.query.filter_by(employee_id=employee_id).first()
            if existing_user:
                flash("Employee ID already registered please Login")
                return redirect(url_for('signup_route'))

            # Register user
            new_user = User(
                employee_id=employee_id,
                email=email,
                phone=phone
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Redirect directly to login on success
            return redirect(url_for('login_route'))

        except Exception as db_err:
            print(f"Database error during signup: {db_err}")
            flash("Please try again later")
            return redirect(url_for('signup_route'))

    return render_template('cal-signup/cal-signup.html')

# Verification code route handler
@app.route('/caliverify/caliverify.html', methods=['GET', 'POST'])
def verify_route():
    if request.method == 'POST':
        # Retrieve digits
        digit1 = request.form.get('digit1', '').strip()
        digit2 = request.form.get('digit2', '').strip()
        digit3 = request.form.get('digit3', '').strip()
        digit4 = request.form.get('digit4', '').strip()
        digit5 = request.form.get('digit5', '').strip()
        digit6 = request.form.get('digit6', '').strip()

        submitted_otp = f"{digit1}{digit2}{digit3}{digit4}{digit5}{digit6}"

        session_otp = session.get('otp_code')
        temp_emp_id = session.get('temp_employee_id')

        if not session_otp or not temp_emp_id:
            flash("Invalid Credentials")
            return redirect(url_for('login_route'))

        if submitted_otp == session_otp:
            # Successful validation -> Authenticate user session
            session['user_id'] = temp_emp_id
            session.pop('otp_code', None)
            session.pop('temp_employee_id', None)
            
            # Redirect to Home dashboard
            return redirect(url_for('home_route'))
        else:
            flash("Invalid OTP Code")
            return redirect(url_for('verify_route'))

    return render_template('caliverify/caliverify.html')

# Log out route
@app.route('/cal-login/cal-logout')
def logout_route():
    session.clear()
    return redirect(url_for('login_route'))

# Home Page dynamic dashboard route
@app.route('/home/home.html', methods=['GET'])
def home_route():
    if 'user_id' not in session:
        flash("Invalid Credentials")
        return redirect(url_for('login_route'))
        
    user_id = session['user_id']
    
    # Check and initialize tables if they don't exist
    try:
        # Check if table exists and has old schema
        reports_need_recreate = False
        try:
            db.session.execute(text(f"SELECT cert FROM reports_{user_id} LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(text(f"SELECT id FROM reports_{user_id} LIMIT 1"))
                reports_need_recreate = True
            except Exception:
                db.session.rollback()

        if reports_need_recreate:
            db.session.execute(text(f"DROP TABLE IF EXISTS reports_{user_id}"))
            db.session.commit()

        db.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS schedules_{user_id} (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                due_time TIMESTAMP NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE
            )
        """))
        db.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS reports_{user_id} (
                id BIGINT PRIMARY KEY,
                cert VARCHAR(200) NOT NULL,
                desc_text VARCHAR(200) NOT NULL,
                date_cal VARCHAR(100) NOT NULL,
                payload TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'completed'
            )
        """))
        db.session.commit()
    except Exception as init_err:
        print(f"Error initializing user tables: {init_err}")
        db.session.rollback()

    # Pre-seed test user 12345 tables if they are empty
    if user_id == '12345':
        try:
            s_count = db.session.execute(text(f"SELECT COUNT(*) FROM schedules_{user_id}")).scalar() or 0
            if s_count == 0:
                # Seed test schedules
                now = datetime.datetime.now()
                db.session.execute(text(f"""
                    INSERT INTO schedules_{user_id} (title, due_time) VALUES
                    ('Calibration of Pressure gauge', :overdue_time),
                    ('Temperature chamber test run', :approaching_time),
                    ('Multimeter verification check', :future_time)
                """), {
                    'overdue_time': now - datetime.timedelta(hours=1, minutes=30),
                    'approaching_time': now + datetime.timedelta(minutes=30),
                    'future_time': now + datetime.timedelta(days=2)
                })
                
                # Seed mock reports matching the new columns
                db.session.execute(text(f"""
                    INSERT INTO reports_{user_id} (id, cert, desc_text, date_cal, payload, status) VALUES
                    (1, 'CALS/2026/001', 'Pressure Gauge', '2026-06-29', :payload1, 'pending'),
                    (2, 'CALS/2026/002', 'Pressure Gauge', '2026-06-29', :payload2, 'completed')
                """), {
                    'payload1': '{"inwardNumber":"INW/2026/102","descriptionSelect":"Pressure Gauge"}',
                    'payload2': '{"inwardNumber":"INW/2026/103","descriptionSelect":"Pressure Gauge"}'
                })
                db.session.commit()
        except Exception as seed_err:
            print(f"Error seeding user 12345: {seed_err}")
            db.session.rollback()

    # Fetch stats and schedules from unique tables
    try:
        schedules_count = db.session.execute(text(f"SELECT COUNT(*) FROM schedules_{user_id}")).scalar() or 0
        reports_count = db.session.execute(text(f"SELECT COUNT(*) FROM reports_{user_id}")).scalar() or 0
        
        # Get all active schedules ordered by due_time
        schedules_rows = db.session.execute(text(f"SELECT id, title, due_time FROM schedules_{user_id} ORDER BY due_time ASC")).fetchall()
        
        # Check if there are any reports with a status of 'pending'
        pending_count = db.session.execute(text(f"SELECT COUNT(*) FROM reports_{user_id} WHERE status = 'pending'")).scalar() or 0
        has_pending_reports = pending_count > 0
    except Exception as query_err:
        print(f"Error querying statistics: {query_err}")
        schedules_count = 0
        reports_count = 0
        schedules_rows = []
        has_pending_reports = False

    schedules = []
    now = datetime.datetime.now()
    for row in schedules_rows:
        due_time = row[2]
        time_diff = due_time - now
        
        # Color coding:
        # - Overdue (due_time has passed) -> overdue-red
        # - Approaching (due_time in <= 1 hour) -> approaching-yellow
        # - Normal -> normal-green
        if time_diff.total_seconds() < 0:
            color_class = "overdue-red"
        elif time_diff.total_seconds() <= 3600:
            color_class = "approaching-yellow"
        else:
            color_class = "normal-green"
            
        schedules.append({
            'id': row[0],
            'title': row[1],
            'due_time': due_time.strftime('%Y-%m-%d %H:%M:%S'),
            'color_class': color_class
        })

    return render_template('home/home.html', 
                           username=user_id, 
                           schedules_count=schedules_count, 
                           reports_count=reports_count,
                           schedules=schedules,
                           has_pending_reports=has_pending_reports)

# Delete schedule route (POST only)
@app.route('/delete-schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    try:
        db.session.execute(text(f"DELETE FROM schedules_{user_id} WHERE id = :id"), {'id': schedule_id})
        db.session.commit()
        
        # Fetch new schedules count
        new_count = db.session.execute(text(f"SELECT COUNT(*) FROM schedules_{user_id}")).scalar() or 0
        return jsonify({'success': True, 'new_count': new_count})
    except Exception as delete_err:
        print(f"Error deleting schedule: {delete_err}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(delete_err)}), 500

# Get all schedules route (GET only)
@app.route('/get-schedules', methods=['GET'])
def get_schedules():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    try:
        # Check and initialize tables if they don't exist
        db.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS schedules_{user_id} (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                due_time TIMESTAMP NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE
            )
        """))
        db.session.commit()
        
        rows = db.session.execute(text(f"SELECT id, title, due_time FROM schedules_{user_id} ORDER BY due_time ASC")).fetchall()
        
        schedules = []
        now = datetime.datetime.now()
        for r in rows:
            due_time = r[2]
            time_diff = due_time - now
            if time_diff.total_seconds() < 0:
                color_class = "overdue-red"
            elif time_diff.total_seconds() <= 3600:
                color_class = "approaching-yellow"
            else:
                color_class = "normal-green"
                
            schedules.append({
                'id': r[0],
                'title': r[1],
                'date': due_time.strftime('%Y-%m-%d'),
                'color_class': color_class
            })
        return jsonify({'success': True, 'schedules': schedules})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Create schedule route (POST only)
@app.route('/create-schedule', methods=['POST'])
def create_schedule():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    data = request.get_json()
    if not data or 'title' not in data or 'date' not in data or 'time' not in data:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
    title = data['title'].strip()
    date_str = data['date'].strip()
    time_str = data['time'].strip() # e.g. "08:30 PM" or "10:00 AM"
    
    if not title or not date_str or not time_str:
        return jsonify({'success': False, 'error': 'Empty fields'}), 400
        
    try:
        # Parse date and 12-hour AM/PM time
        due_time_str = f"{date_str} {time_str}"
        due_time = datetime.datetime.strptime(due_time_str, '%Y-%m-%d %I:%M %p')
        
        # Ensure table exists
        db.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS schedules_{user_id} (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                due_time TIMESTAMP NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE
            )
        """))
        
        db.session.execute(text(f"""
            INSERT INTO schedules_{user_id} (title, due_time) 
            VALUES (:title, :due_time)
        """), {'title': title, 'due_time': due_time})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
# Get reports route (GET)
@app.route('/get-reports', methods=['GET'])
def get_reports():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    try:
        # Check if table exists and has old schema
        reports_need_recreate = False
        try:
            db.session.execute(text(f"SELECT cert FROM reports_{user_id} LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(text(f"SELECT id FROM reports_{user_id} LIMIT 1"))
                reports_need_recreate = True
            except Exception:
                db.session.rollback()

        if reports_need_recreate:
            db.session.execute(text(f"DROP TABLE IF EXISTS reports_{user_id}"))
            db.session.commit()

        # Ensure table exists
        db.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS reports_{user_id} (
                id BIGINT PRIMARY KEY,
                cert VARCHAR(200) NOT NULL,
                desc_text VARCHAR(200) NOT NULL,
                date_cal VARCHAR(100) NOT NULL,
                payload TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'completed'
            )
        """))
        db.session.commit()
        
        rows = db.session.execute(text(f"SELECT id, cert, desc_text, date_cal, payload, status FROM reports_{user_id} ORDER BY id DESC")).fetchall()
        reports = []
        for r in rows:
            reports.append({
                'id': int(r[0]),
                'cert': r[1],
                'desc': r[2],
                'date': r[3],
                'payload': r[4],
                'status': r[5]
            })
        return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Create report route (POST)
@app.route('/create-report', methods=['POST'])
def create_report():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    data = request.get_json()
    if not data or 'id' not in data or 'cert' not in data or 'desc' not in data or 'date' not in data or 'payload' not in data:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
    report_id = data['id']
    cert = data['cert'].strip()
    desc = data['desc'].strip()
    date = data['date'].strip()
    payload = data['payload']
    status = data.get('status', 'completed').strip()
    
    try:
        # Check if table exists and has old schema
        reports_need_recreate = False
        try:
            db.session.execute(text(f"SELECT cert FROM reports_{user_id} LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(text(f"SELECT id FROM reports_{user_id} LIMIT 1"))
                reports_need_recreate = True
            except Exception:
                db.session.rollback()

        if reports_need_recreate:
            db.session.execute(text(f"DROP TABLE IF EXISTS reports_{user_id}"))
            db.session.commit()

        # Ensure table exists
        db.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS reports_{user_id} (
                id BIGINT PRIMARY KEY,
                cert VARCHAR(200) NOT NULL,
                desc_text VARCHAR(200) NOT NULL,
                date_cal VARCHAR(100) NOT NULL,
                payload TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'completed'
            )
        """))
        
        # Insert or update
        db.session.execute(text(f"""
            INSERT INTO reports_{user_id} (id, cert, desc_text, date_cal, payload, status)
            VALUES (:id, :cert, :desc_text, :date, :payload, :status)
            ON CONFLICT (id) DO UPDATE SET
                cert = EXCLUDED.cert,
                desc_text = EXCLUDED.desc_text,
                date_cal = EXCLUDED.date_cal,
                payload = EXCLUDED.payload,
                status = EXCLUDED.status
        """), {
            'id': report_id,
            'cert': cert,
            'desc_text': desc,
            'date': date,
            'payload': payload,
            'status': status
        })
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Delete report route (POST)
@app.route('/delete-report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    try:
        db.session.execute(text(f"DELETE FROM reports_{user_id} WHERE id = :id"), {'id': report_id})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
# Profile Page dynamic route
@app.route('/caliprofile/caliprofile.html', methods=['GET'])
def profile_route():
    if 'user_id' not in session:
        flash("Invalid Credentials")
        return redirect(url_for('login_route'))
        
    user_id = session['user_id']
    user = User.query.filter_by(employee_id=user_id).first()
    if not user:
        flash("Invalid Credentials")
        return redirect(url_for('login_route'))
        
    return render_template('caliprofile/caliprofile.html', user=user)

# Serve user avatar binary from database
@app.route('/user/avatar/<employee_id>')
def serve_avatar(employee_id):
    user = User.query.filter_by(employee_id=employee_id).first()
    if not user or not user.profile_image:
        return "", 404
        
    from flask import Response
    return Response(user.profile_image, mimetype='image/jpeg')

# Upload avatar POST handler
@app.route('/user/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    user = User.query.filter_by(employee_id=user_id).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
        
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
        
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
        
    # Check extension
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
    try:
        # Read the file binary and save directly to database
        img_binary = file.read()
        user.profile_image = img_binary
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Notifications route
@app.route('/notifications/notifications.html', methods=['GET'])
def notifications_route():
    if 'user_id' not in session:
        flash("Invalid Credentials")
        return redirect(url_for('login_route'))
    return render_template('notifications/notifications.html')

# Route to serve the Material Symbols Outlined font file with correct MIME type
@app.route('/material-symbols-outlined.woff2')
@app.route('/templates/material-symbols-outlined.woff2')
@app.route('/<folder>/material-symbols-outlined.woff2')
def serve_font(folder=None):
    return send_from_directory('templates', 'material-symbols-outlined.woff2', mimetype='font/woff2')

# Dynamic template and static file catch-all router
@app.route('/<path:filepath>', methods=['GET'])
def serve_page_or_static(filepath):
    # Render HTML pages dynamically
    if filepath.endswith('.html'):
        # Check authentication for protected sub-pages
        protected_folders = ['home/', 'caliprofile/', 'cali-report/', 'cali-reports-data/', 'schedule-work/', 'caliprofile-pages/', 'tutorial/', 'cali-unit-convert/']
        is_protected = any(filepath.startswith(folder) for folder in protected_folders)
        
        if is_protected and 'user_id' not in session:
            flash("Invalid Credentials")
            return redirect(url_for('login_route'))
            
        return render_template(filepath)
    
    # Otherwise serve assets directly from templates subfolders
    return send_from_directory('templates', filepath)

if __name__ == '__main__':
    # Run the server on port 5000, listening on all interfaces (enables mobile connection)
    app.run(host='0.0.0.0', port=5000, debug=True)
