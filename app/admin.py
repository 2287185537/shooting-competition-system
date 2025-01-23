from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import User, Competition, Registration, Score, Notification
from datetime import datetime
import os
import json
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('需要管理员权限')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def create_notification(user_id, title, message):
    """创建系统通知"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.session.add(notification)
    try:
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f'创建通知失败: {str(e)}')
        db.session.rollback()
        return False

# 仪表板
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    competitions_count = Competition.query.count()
    registrations_count = Registration.query.count()
    pending_count = Registration.query.filter_by(status='pending').count()
    
    recent_competitions = Competition.query.order_by(Competition.date.desc()).limit(5).all()
    recent_registrations = Registration.query.order_by(Registration.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         users_count=users_count,
                         competitions_count=competitions_count,
                         registrations_count=registrations_count,
                         pending_count=pending_count,
                         recent_competitions=recent_competitions,
                         recent_registrations=recent_registrations)

# 用户管理
@admin.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(
        page=page, 
        per_page=20,
        error_out=False
    )
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('new_password')
        
        if username != user.username and User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('admin.user_edit', id=id))
            
        if email != user.email and User.query.filter_by(email=email).first():
            flash('邮箱已被使用')
            return redirect(url_for('admin.user_edit', id=id))
            
        user.username = username
        user.email = email
        if role and user.id != current_user.id:
            user.role = role
            
        if password:
            user.set_password(password)
            
        db.session.commit()
        flash('用户信息已更新')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/user_edit.html', user=user)

@admin.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('不能删除自己的账户')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除')
    return redirect(url_for('admin.users'))

# 比赛管理
@admin.route('/competitions')
@login_required
@admin_required
def competitions():
    page = request.args.get('page', 1, type=int)
    competitions = Competition.query.order_by(Competition.date.desc()).paginate(
        page=page, 
        per_page=20,
        error_out=False
    )
    return render_template('admin/competitions.html', competitions=competitions)

@admin.route('/competition/create', methods=['GET', 'POST'])
@login_required
@admin_required
def competition_create():
    if request.method == 'POST':
        name = request.form.get('name')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        category = request.form.get('category')
        max_participants = request.form.get('max_participants', type=int)
        registration_deadline = datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%d')
        description = request.form.get('description')
        allow_same_category = bool(request.form.get('allow_same_category'))
        require_approval = bool(request.form.get('require_approval'))
        
        competition = Competition(
            name=name,
            date=date,
            category=category,
            max_participants=max_participants,
            registration_deadline=registration_deadline,
            description=description,
            allow_same_category=allow_same_category,
            require_approval=require_approval
        )
        
        db.session.add(competition)
        db.session.commit()
        
        flash('比赛创建成功')
        return redirect(url_for('admin.competitions'))
        
    return render_template('admin/competition_create.html')

@admin.route('/competition/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def competition_edit(id):
    competition = Competition.query.get_or_404(id)
    
    if request.method == 'POST':
        competition.name = request.form.get('name')
        competition.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        competition.category = request.form.get('category')
        competition.max_participants = request.form.get('max_participants', type=int)
        competition.registration_deadline = datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%d')
        competition.description = request.form.get('description')
        competition.status = request.form.get('status')
        competition.allow_same_category = bool(request.form.get('allow_same_category'))
        competition.require_approval = bool(request.form.get('require_approval'))
        
        db.session.commit()
        flash('比赛信息已更新')
        return redirect(url_for('admin.competitions'))
        
    return render_template('admin/competition_edit.html', competition=competition)

@admin.route('/competition/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def competition_delete(id):
    competition = Competition.query.get_or_404(id)
    
    db.session.delete(competition)
    db.session.commit()
    flash('比赛已删除')
    return redirect(url_for('admin.competitions'))

@admin.route('/competition/<int:id>/registrations')
@login_required
@admin_required
def competition_registrations(id):
    competition = Competition.query.get_or_404(id)
    registrations = Registration.query.filter_by(competition_id=id).all()
    return render_template('admin/competition_registrations.html',
                         competition=competition,
                         registrations=registrations)

# 报名管理
@admin.route('/registrations/pending')
@login_required
@admin_required
def pending_registrations():
    registrations = Registration.query.filter_by(
        status='pending'
    ).order_by(
        Registration.created_at.desc()
    ).all()
    return render_template('admin/pending_registrations.html', registrations=registrations)

@admin.route('/registration/<int:registration_id>/review', methods=['POST'])
@login_required
@admin_required
def review_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    
    if registration.status != 'pending':
        return jsonify({
            'success': False,
            'message': '此报名已经被处理'
        }), 400
    
    action = request.json.get('action')
    if action not in ['approve', 'reject']:
        return jsonify({
            'success': False,
            'message': '无效的操作'
        }), 400
    
    registration.status = 'registered' if action == 'approve' else 'cancelled'
    
    # 创建通知
    title = '报名审核结果'
    message = f'您报名的比赛 "{registration.competition.name}" {"已通过审核" if action == "approve" else "未通过审核"}。'
    create_notification(registration.user_id, title, message)
    
    db.session.commit()
    
    return jsonify({'success': True})

# 成绩管理
@admin.route('/score/entry/<int:registration_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def score_entry(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    
    if request.method == 'POST':
        score_value = request.form.get('score', type=float)
        round_number = request.form.get('round_number', type=int)
        notes = request.form.get('notes')
        
        if not score_value or not round_number:
            return jsonify({
                'success': False,
                'message': '请输入有效的分数和轮次'
            }), 400
            
        # 检查轮次是否已有成绩
        existing_score = Score.query.filter_by(
            registration_id=registration_id,
            round_number=round_number
        ).first()
        
        if existing_score:
            existing_score.score = score_value
            existing_score.notes = notes
        else:
            score = Score(
                registration_id=registration_id,
                score=score_value,
                round_number=round_number,
                notes=notes
            )
            db.session.add(score)
            
        db.session.commit()
        
        # 创建通知
        create_notification(
            registration.user_id,
            '成绩已更新',
            f'您在比赛 "{registration.competition.name}" 第{round_number}轮的成绩已录入: {score_value}分'
        )
        
        return jsonify({'success': True})
        
    return render_template('admin/score_entry.html', registration=registration)

# 系统管理
@admin.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings_file = os.path.join(current_app.root_path, 'static', 'settings.json')
    
    if request.method == 'POST':
        settings = {
            'competition_categories': request.form.getlist('categories[]'),
            'max_rounds': int(request.form.get('max_rounds', 3)),
            'registration_close_hours': int(request.form.get('registration_close_hours', 24)),
            'enable_notifications': bool(request.form.get('enable_notifications')),
            'site_name': request.form.get('site_name', '射击比赛管理系统'),
            'admin_email': request.form.get('admin_email', '')
        }
        
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
            
        flash('设置已保存')
        return redirect(url_for('admin.settings'))
    
    # 读取当前设置
    settings = {
        'competition_categories': ['手枪', '步枪', '气步枪'],
        'max_rounds': 3,
        'registration_close_hours': 24,
        'enable_notifications': True,
        'site_name': '射击比赛管理系统',
        'admin_email': ''
    }
    
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings.update(json.load(f))
    
    return render_template('admin/settings.html', settings=settings)

@admin.route('/logs')
@login_required
@admin_required
def view_logs():
    log_file = os.path.join(current_app.root_path, '..', 'logs', 'shooting_competition.log')
    log_entries = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-1000:]  # 最后1000行
            for line in lines:
                try:
                    parts = line.split(' ', 3)
                    if len(parts) >= 4:
                        log_entries.append({
                            'timestamp': ' '.join(parts[:2]),
                            'level': parts[2],
                            'message': parts[3].strip()
                        })
                except Exception as e:
                    current_app.logger.error(f'解析日志出错: {str(e)}')
    
    return render_template('admin/logs.html', log_entries=log_entries)