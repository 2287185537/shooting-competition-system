from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
from .models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    """加载用户，用于Flask-Login"""
    return User.query.get(int(user_id))

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from .competition import competition as competition_blueprint
    app.register_blueprint(competition_blueprint)
    
    from .notifications import notifications as notifications_blueprint
    app.register_blueprint(notifications_blueprint)
    
    # 错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                             error_code=404,
                             error_message='页面未找到'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('error.html',
                             error_code=500,
                             error_message='服务器内部错误'), 500
    
    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template('error.html',
                             error_code=403,
                             error_message='没有权限访问'), 403
                             
    @app.errorhandler(401)
    def unauthorized_error(e):
        return render_template('error.html',
                             error_code=401,
                             error_message='请先登录'), 401
    
    # 全局上下文处理器
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(current_user=current_user)
    
    # 初始化数据库
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            
            # 检查数据库连接
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            app.logger.info('数据库初始化成功')
        except Exception as e:
            app.logger.error(f'数据库初始化失败: {str(e)}')
            raise
    
    return app