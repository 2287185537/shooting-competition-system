import os
from flask import render_template
from app import create_app, db
from app.models import User, Competition, Registration, Score, Notification
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_ENV', 'default'))
migrate = Migrate(app, db)

# 添加Shell上下文
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Competition': Competition,
        'Registration': Registration,
        'Score': Score,
        'Notification': Notification
    }

# 注册错误处理器
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message='页面未找到'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message='服务器内部错误'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, error_message='没有权限访问此页面'), 403

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html', error_code=401, error_message='请先登录'), 401

# CLI命令
@app.cli.command('init-db')
def init_db_command():
    """初始化数据库命令"""
    try:
        db.create_all()
        # 创建管理员账户（如果不存在）
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                name='系统管理员'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员账户创建成功：')
            print('用户名：admin')
            print('密码：admin123')
        print('数据库初始化成功！')
    except Exception as e:
        print(f'错误：{str(e)}')
        print('数据库初始化失败')

@app.cli.command('create-admin')
def create_admin_command():
    """创建新的管理员账户"""
    import click
    username = click.prompt('请输入用户名')
    email = click.prompt('请输入邮箱')
    password = click.prompt('请输入密码', hide_input=True)
    password_repeat = click.prompt('请再次输入密码', hide_input=True)
    
    if password != password_repeat:
        click.echo('两次输入的密码不一致')
        return
        
    try:
        if User.query.filter_by(username=username).first():
            click.echo('用户名已存在')
            return
            
        if User.query.filter_by(email=email).first():
            click.echo('邮箱已被使用')
            return
            
        user = User(
            username=username,
            email=email,
            role='admin',
            name='管理员'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo('管理员账户创建成功')
        
    except Exception as e:
        click.echo(f'错误：{str(e)}')
        click.echo('管理员账户创建失败')

@app.cli.command('reset-password')
def reset_password_command():
    """重置用户密码"""
    import click
    username = click.prompt('请输入用户名')
    new_password = click.prompt('请输入新密码', hide_input=True)
    
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo('用户不存在')
            return
            
        user.set_password(new_password)
        db.session.commit()
        click.echo('密码重置成功')
        
    except Exception as e:
        click.echo(f'错误：{str(e)}')
        click.echo('密码重置失败')

@app.cli.command('list-users')
def list_users_command():
    """列出所有用户"""
    try:
        users = User.query.all()
        if not users:
            print('没有找到用户')
            return
            
        print('用户列表:')
        for user in users:
            print(f'ID: {user.id}')
            print(f'用户名: {user.username}')
            print(f'邮箱: {user.email}')
            print(f'角色: {user.role}')
            print(f'创建时间: {user.created_at}')
            print('-' * 30)
            
    except Exception as e:
        print(f'错误：{str(e)}')
        print('获取用户列表失败')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)