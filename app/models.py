from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    name = db.Column(db.String(64))
    category = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    registrations = db.relationship('Registration', 
                                  backref='user',
                                  lazy='dynamic',
                                  foreign_keys='Registration.user_id')
    notifications = db.relationship('Notification',
                                  backref='user',
                                  lazy='dynamic',
                                  foreign_keys='Notification.user_id')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """检查是否为管理员"""
        return self.role == 'admin'

    @property
    def is_active(self):
        """用于Flask-Login"""
        return True

    def __repr__(self):
        return f'<User {self.username}>'

class Competition(db.Model):
    """比赛模型"""
    __tablename__ = 'competitions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(32), nullable=False)
    max_participants = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')
    description = db.Column(db.Text)
    registration_deadline = db.Column(db.DateTime)
    allow_same_category = db.Column(db.Boolean, default=True)
    require_approval = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    registrations = db.relationship('Registration',
                                  backref='competition',
                                  lazy='dynamic',
                                  foreign_keys='Registration.competition_id')

    def __repr__(self):
        return f'<Competition {self.name}>'

    def is_registration_open(self):
        """检查是否开放报名"""
        now = datetime.utcnow()
        return (
            self.status == 'pending' and
            self.registration_deadline and
            now <= self.registration_deadline
        )

    def get_participant_count(self):
        """获取报名人数"""
        return self.registrations.filter_by(status='registered').count()

    def has_available_slots(self):
        """检查是否还有名额"""
        if not self.max_participants:
            return True
        return self.get_participant_count() < self.max_participants

class Registration(db.Model):
    """报名模型"""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    category = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, registered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    scores = db.relationship('Score',
                           backref='registration',
                           lazy='dynamic',
                           foreign_keys='Score.registration_id')

    def __repr__(self):
        return f'<Registration {self.user_id} - {self.competition_id}>'

    def get_total_score(self):
        """计算总分"""
        scores = [score.score for score in self.scores.all()]
        return sum(scores) if scores else 0

    def get_ranking(self):
        """获取排名"""
        all_registrations = Registration.query.filter_by(
            competition_id=self.competition_id,
            category=self.category,
            status='registered'
        ).all()
        scores = [(r.id, r.get_total_score()) for r in all_registrations]
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        for i, (rid, _) in enumerate(sorted_scores, 1):
            if rid == self.id:
                return i
        return None

class Score(db.Model):
    """成绩模型"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Score {self.registration_id} - Round {self.round_number}>'

class Notification(db.Model):
    """通知模型"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.title}>'