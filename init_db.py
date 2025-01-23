import os
import sys
import pyodbc
from dotenv import load_dotenv
import time
from werkzeug.security import generate_password_hash

# 加载环境变量
load_dotenv()

def wait_for_sql_server():
    """等待SQL Server启动"""
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            # 使用Windows身份验证连接
            conn = pyodbc.connect(
                server=os.getenv('DB_HOST', 'DESKTOP-N0UKV4T'),
                database='master',
                trusted_connection='yes'
            )
            conn.close()
            print("SQL Server connection successful")
            return True
        except Exception as e:
            attempt += 1
            print(f"Waiting for SQL Server... Attempt {attempt}/{max_attempts}")
            print(f"Error: {str(e)}")
            time.sleep(5)
    return False

def create_database():
    """创建数据库"""
    try:
        print("Starting database initialization...")
        
        # 首先等待SQL Server可用
        if not wait_for_sql_server():
            print("Error: Cannot connect to SQL Server, please ensure:")
            print("1. SQL Server is running")
            print("2. Windows Authentication is enabled")
            print("3. Server name is correct (DESKTOP-N0UKV4T)")
            print("4. Port 1433 is open")
            sys.exit(1)

        # 连接到SQL Server
        print("Connecting to SQL Server...")
        conn = pyodbc.connect(
            server=os.getenv('DB_HOST', 'DESKTOP-N0UKV4T'),
            database='master',
            trusted_connection='yes'
        )
        cursor = conn.cursor()
        
        # 创建数据库
        db_name = os.getenv('DB_NAME', 'shooting_competition_v1')
        print(f"Creating database: {db_name}")
        cursor.execute(f"""
        IF NOT EXISTS (
            SELECT name 
            FROM sys.databases 
            WHERE name = N'{db_name}'
        )
        BEGIN
            CREATE DATABASE {db_name}
        END
        """)
        conn.commit()
        
        # 切换到新数据库
        conn.close()
        conn = pyodbc.connect(
            server=os.getenv('DB_HOST', 'DESKTOP-N0UKV4T'),
            database=db_name,
            trusted_connection='yes'
        )
        cursor = conn.cursor()
        
        # 创建users表
        print("Creating users table...")
        cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables WHERE name = 'users'
        )
        CREATE TABLE users (
            id INT PRIMARY KEY IDENTITY(1,1),
            username NVARCHAR(64) UNIQUE NOT NULL,
            email NVARCHAR(120) UNIQUE NOT NULL,
            password_hash NVARCHAR(128) NOT NULL,
            role NVARCHAR(20) NOT NULL DEFAULT 'user',
            name NVARCHAR(64),
            category NVARCHAR(32),
            created_at DATETIME DEFAULT GETDATE()
        )
        """)
        
        # 创建competitions表
        print("Creating competitions table...")
        cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables WHERE name = 'competitions'
        )
        CREATE TABLE competitions (
            id INT PRIMARY KEY IDENTITY(1,1),
            name NVARCHAR(128) NOT NULL,
            date DATETIME NOT NULL,
            category NVARCHAR(32) NOT NULL,
            max_participants INT,
            status NVARCHAR(20) DEFAULT 'pending',
            description NTEXT,
            registration_deadline DATETIME,
            allow_same_category BIT DEFAULT 1,
            require_approval BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE()
        )
        """)
        
        # 创建registrations表
        print("Creating registrations table...")
        cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables WHERE name = 'registrations'
        )
        CREATE TABLE registrations (
            id INT PRIMARY KEY IDENTITY(1,1),
            user_id INT NOT NULL,
            competition_id INT NOT NULL,
            category NVARCHAR(32) NOT NULL,
            status NVARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT GETDATE(),
            review_note NTEXT,
            reviewed_at DATETIME,
            reviewed_by INT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (competition_id) REFERENCES competitions(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
        """)
        
        # 创建scores表
        print("Creating scores table...")
        cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables WHERE name = 'scores'
        )
        CREATE TABLE scores (
            id INT PRIMARY KEY IDENTITY(1,1),
            registration_id INT NOT NULL,
            score FLOAT NOT NULL,
            round_number INT NOT NULL,
            notes NTEXT,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (registration_id) REFERENCES registrations(id)
        )
        """)
        
        # 创建notifications表
        print("Creating notifications table...")
        cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables WHERE name = 'notifications'
        )
        CREATE TABLE notifications (
            id INT PRIMARY KEY IDENTITY(1,1),
            user_id INT NOT NULL,
            title NVARCHAR(128) NOT NULL,
            message NTEXT NOT NULL,
            is_read BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        # 创建管理员账户
        print("Checking default admin account...")
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            admin_password_hash = generate_password_hash('admin123')
            cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, name)
            VALUES (?, ?, ?, 'admin', 'System Admin')
            """, ('admin', 'admin@example.com', admin_password_hash))
            print("Default admin account created:")
            print("Username: admin")
            print("Password: admin123")
            
        conn.commit()
        print("Database tables created successfully!")
        
        # 检查并添加索引
        print("Creating indexes...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_registrations_status')
        CREATE INDEX idx_registrations_status ON registrations(status);
        
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_competitions_date')
        CREATE INDEX idx_competitions_date ON competitions(date);
        
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_registrations_competition_user')
        CREATE INDEX idx_registrations_competition_user ON registrations(competition_id, user_id);
        """)
        conn.commit()
        print("Indexes created successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nInitialization failed! Please check:")
        print("1. SQL Server is installed and running")
        print("2. Windows Authentication is enabled")
        print("3. Server name is correct (DESKTOP-N0UKV4T)")
        print("4. You have sufficient permissions")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed")

if __name__ == '__main__':
    if create_database():
        print("\nYou can now run 'flask run' to start the application")
    else:
        print("\nPlease resolve the issues above and try again")