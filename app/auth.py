from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('competition.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('请检查用户名和密码')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('competition.index')
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('competition.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return redirect(url_for('auth.register'))
            
        user = User(
            username=username,
            email=email,
            role='user'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('competition.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('邮箱已被使用')
            return redirect(url_for('auth.profile'))
            
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('当前密码错误')
                return redirect(url_for('auth.profile'))
            current_user.set_password(new_password)
            
        current_user.name = name
        current_user.email = email
        
        db.session.commit()
        flash('个人信息已更新')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html')

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('competition.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # 在实际应用中，这里应该发送重置密码的邮件
            # 为了演示，我们直接重置为默认密码
            user.set_password('123456')
            db.session.commit()
            flash('密码已重置为: 123456')
            return redirect(url_for('auth.login'))
        flash('未找到该邮箱对应的用户')
        
    return render_template('auth/reset_password_request.html')