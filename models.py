import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    employee_id = db.Column(db.String(5), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.LargeBinary, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.employee_id}>"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(5), db.ForeignKey('users.employee_id', ondelete='CASCADE'), nullable=False)
    icon = db.Column(db.String(50), default='info')
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Notification {self.id} for {self.employee_id}>"

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(5), db.ForeignKey('users.employee_id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    due_time = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Schedule {self.id} title={self.title} for {self.employee_id}>"

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.BigInteger, primary_key=True)
    employee_id = db.Column(db.String(5), db.ForeignKey('users.employee_id', ondelete='CASCADE'), nullable=False, index=True)
    cert = db.Column(db.String(200), nullable=False)
    desc_text = db.Column(db.String(200), nullable=False)
    date_cal = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='completed')

    def __repr__(self):
        return f"<Report {self.id} cert={self.cert} for {self.employee_id}>"

class FCMToken(db.Model):
    __tablename__ = 'fcm_tokens'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(5), db.ForeignKey('users.employee_id', ondelete='CASCADE'), nullable=False, index=True)
    fcm_token = db.Column(db.String(500), unique=True, nullable=False)
    device_info = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<FCMToken {self.id} user={self.employee_id}>"

class NotificationHistory(db.Model):
    __tablename__ = 'notification_history'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    action_url = db.Column(db.String(500), nullable=True)
    target_type = db.Column(db.String(50), nullable=False)  # 'all', 'single', 'multiple'
    target_reference = db.Column(db.Text, nullable=True)     # Target employee IDs or description
    sender_admin_id = db.Column(db.String(5), db.ForeignKey('users.employee_id'), nullable=False)
    send_status = db.Column(db.String(50), default='sent')   # 'sent', 'partial_failure', 'failed'
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<NotificationHistory {self.id} title='{self.title}'>"
