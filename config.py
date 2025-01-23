import os
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
import sys

# Ensure proper encoding for all platforms
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

class Config:
    # Basic Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    JSON_AS_ASCII = False  # Enable UTF-8 encoding for JSON responses
    
    # Database Configuration
    # 使用 pyodbc 连接字符串格式
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc:///?odbc_connect="
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={os.getenv('DB_HOST', 'DESKTOP-N0UKV4T')};"
        f"Database={os.getenv('DB_NAME', 'shooting_competition_v1')};"
        "Trusted_Connection=yes;"
        "charset=utf8;"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 启用连接检查
        'pool_size': 10,  # 连接池大小
        'max_overflow': 20,  # 最大溢出连接数
        'pool_timeout': 30,  # 连接超时时间
        'pool_recycle': 1800,  # 连接回收时间（30分钟）
    }
    
    # Application Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file upload limit
    
    # Competition Categories
    COMPETITION_CATEGORIES = ['手枪', '步枪', '气步枪']
    REGISTRATION_CLOSE_HOURS = 24  # Close registration 24 hours before competition
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Logging Configuration
    LOG_DIR = 'logs'
    LOG_FILE = 'shooting_competition.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    LOG_ENCODING = 'utf-8'  # Ensure UTF-8 encoding for logs
    
    @classmethod
    def init_app(cls, app):
        # 确保日志目录存在
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
        
        # 配置日志处理器
        file_handler = RotatingFileHandler(
            os.path.join(cls.LOG_DIR, cls.LOG_FILE),
            maxBytes=cls.LOG_MAX_SIZE,
            backupCount=cls.LOG_BACKUP_COUNT,
            encoding=cls.LOG_ENCODING
        )
        file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
        file_handler.setLevel(logging.INFO)
        
        # 添加处理器到应用日志
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('射击比赛管理系统启动')
        
        # 测试数据库连接
        if not cls.test_database_connection(app):
            app.logger.error('无法连接到数据库，请检查配置')
            app.logger.error('确保 SQL Server 正在运行且 Windows 认证已启用')
            app.logger.error(f'服务器名称: {os.getenv("DB_HOST", "DESKTOP-N0UKV4T")}')
            raise Exception('数据库连接失败')
    
    @staticmethod
    def test_database_connection(app):
        """测试数据库连接"""
        try:
            import pyodbc
            conn_str = (
                "Driver={ODBC Driver 17 for SQL Server};"
                f"Server={os.getenv('DB_HOST', 'DESKTOP-N0UKV4T')};"
                f"Database={os.getenv('DB_NAME', 'shooting_competition_v1')};"
                "Trusted_Connection=yes;"
            )
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            return True
        except Exception as e:
            app.logger.error(f'数据库连接测试失败: {str(e)}')
            return False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 开发环境添加控制台日志
        if app.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
            console_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(console_handler)

class TestingConfig(Config):
    TESTING = True
    # 使用测试数据库
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc:///?odbc_connect="
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={os.getenv('DB_HOST', 'DESKTOP-N0UKV4T')};"
        "Database=shooting_competition_test;"
        "Trusted_Connection=yes;"
        "charset=utf8;"
    )
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境特定配置
        app.logger.setLevel(logging.INFO)
        
        # 错误通知
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = () if app.config['MAIL_USE_TLS'] else None
            mail_handler = logging.handlers.SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_USERNAME'],
                toaddrs=['admin@example.com'],  # 替换为实际管理员邮箱
                subject='射击比赛系统 - 应用错误',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}