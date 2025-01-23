from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import Competition, Registration, Notification, User
from datetime import datetime
import json
import os

competition = Blueprint('competition', __name__)

def create_notification(user_id, title, message):
    """创建系统通知"""
    try:
        # 检查是否启用了通知
        settings_file = os.path.join(current_app.root_path, 'static', 'settings.json')
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if not settings.get('enable_notifications', True):
                    return True

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f'创建通知失败: {str(e)}')
        db.session.rollback()
        return False

@competition.route('/')
def index():
    upcoming_competitions = Competition.query.filter(
        Competition.date >= datetime.utcnow()
    ).order_by(Competition.date.asc()).limit(5).all()
    
    return render_template('competition/index.html',
                         upcoming_competitions=upcoming_competitions)

@competition.route('/list')
def list():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Competition.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
        
    competitions = query.order_by(
        Competition.date.desc()
    ).paginate(
        page=page, 
        per_page=10,
        error_out=False
    )
    
    # 获取系统设置中的比赛类别列表
    categories = ['手枪', '步枪', '气步枪']  # 默认类别
    settings_file = os.path.join(current_app.root_path, 'static', 'settings.json')
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                categories = settings.get('competition_categories', categories)
        except Exception as e:
            current_app.logger.error(f'读取系统设置失败: {str(e)}')
    
    return render_template('competition/list.html',
                         competitions=competitions,
                         category=category,
                         status=status,
                         categories=categories)

@competition.route('/<int:id>')
def detail(id):
    competition = Competition.query.get_or_404(id)
    registration = None
    if current_user.is_authenticated:
        registration = Registration.query.filter_by(
            user_id=current_user.id,
            competition_id=id
        ).first()
        
    return render_template('competition/detail.html',
                         competition=competition,
                         registration=registration)

@competition.route('/<int:id>/register', methods=['POST'])
@login_required
def register(id):
    competition = Competition.query.get_or_404(id)
    
    if not competition.is_registration_open():
        flash('报名已截止')
        return redirect(url_for('competition.detail', id=id))
        
    if not competition.has_available_slots():
        flash('报名人数已满')
        return redirect(url_for('competition.detail', id=id))
        
    # 检查是否已经报名
    existing_registration = Registration.query.filter_by(
        user_id=current_user.id,
        competition_id=id
    ).first()
    
    if existing_registration:
        flash('您已经报名过此比赛')
        return redirect(url_for('competition.detail', id=id))
    
    # 检查是否已报名同类别的比赛
    if not competition.allow_same_category:
        category = request.form.get('category')
        same_category_registration = Registration.query.join(
            Competition
        ).filter(
            Registration.user_id == current_user.id,
            Competition.category == category,
            Competition.status != 'completed'
        ).first()
        
        if same_category_registration:
            flash('您已报名参加同类别的其他比赛')
            return redirect(url_for('competition.detail', id=id))
        
    category = request.form.get('category')
    if not category:
        flash('请选择参赛组别')
        return redirect(url_for('competition.detail', id=id))
        
    registration = Registration(
        user_id=current_user.id,
        competition_id=id,
        category=category,
        status='pending' if competition.require_approval else 'registered'
    )
    
    db.session.add(registration)
    
    # 创建通知
    if competition.require_approval:
        title = '报名等待审核'
        message = f'您已成功提交 "{competition.name}" 的报名申请，请等待管理员审核。'
        flash('报名已提交，等待管理员审核')
    else:
        title = '报名成功'
        message = f'您已成功报名参加 "{competition.name}"。'
        flash('报名成功')
    
    create_notification(current_user.id, title, message)
    
    # 如果需要审核，通知管理员
    if competition.require_approval:
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            create_notification(
                admin.id,
                '新的报名申请',
                f'用户 {current_user.username} 提交了 "{competition.name}" 的报名申请，请及时审核。'
            )
    
    db.session.commit()
    
    return redirect(url_for('competition.detail', id=id))

@competition.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_registration(id):
    registration = Registration.query.filter_by(
        user_id=current_user.id,
        competition_id=id
    ).first_or_404()
    
    competition = Competition.query.get_or_404(id)
    
    if not competition.is_registration_open():
        flash('报名已截止，无法取消')
        return redirect(url_for('competition.detail', id=id))
        
    # 检查是否已经有成绩记录
    if registration.scores.count() > 0:
        flash('已有成绩记录，无法取消报名')
        return redirect(url_for('competition.detail', id=id))
        
    db.session.delete(registration)
    
    # 创建取消通知
    create_notification(
        current_user.id,
        '取消报名',
        f'您已成功取消 "{competition.name}" 的报名。'
    )
    
    db.session.commit()
    
    flash('报名已取消')
    return redirect(url_for('competition.detail', id=id))

@competition.route('/my_competitions')
@login_required
def my_competitions():
    registrations = Registration.query.filter_by(
        user_id=current_user.id
    ).join(
        Competition
    ).order_by(
        Competition.date.desc()
    ).all()
    
    return render_template('competition/my_competitions.html',
                         registrations=registrations)