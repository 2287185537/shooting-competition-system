import pyodbc
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_connection():
    """测试数据库连接和创建"""
    try:
        print("Testing SQL Server connection...")
        
        # 列出可用的驱动
        drivers = [x for x in pyodbc.drivers() if 'SQL Server' in x]
        print("Available drivers:", drivers)
        
        # 连接到master数据库
        conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            f"Server={os.getenv('DB_HOST', 'DESKTOP-N0UKV4T')};"
            "Database=master;"
            "Trusted_Connection=yes;"
        )
        
        # 测试连接
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # 检查数据库是否已存在
        db_name = "shooting_competition_v1"
        cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            create_db_sql = f"CREATE DATABASE {db_name}"
            cursor.execute(create_db_sql)
            print(f"数据库 {db_name} 创建成功")
        else:
            print(f"数据库 {db_name} 已存在，跳过创建步骤")
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        error_message = str(e)
        print("发生错误:", error_message)
        if "已存在" in error_message:
            print(f"数据库 {db_name} 已经存在，无需重新创建")
        else:
            print("\n故障排除步骤:")
            print("1. 确认SQL Server正在运行")
            print("2. 确认Windows身份验证已启用")
            print("3. 确认已安装ODBC Driver 17")
            print("4. 确认当前Windows用户具有足够权限")
            print("5. 确认服务器名称正确")
    finally:
        print("\n数据库连接已关闭")

def show_database_info():
    """显示数据库的详细信息"""
    try:
        # 连接到master数据库
        conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            f"Server={os.getenv('DB_HOST', 'DESKTOP-N0UKV4T')};"
            "Database=master;"
            "Trusted_Connection=yes;"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 查询数据库文件位置
        sql = """
        SELECT 
            db.name AS DatabaseName,
            mf.physical_name AS DatabasePath,
            mf.type_desc AS FileType
        FROM sys.master_files mf
        INNER JOIN sys.databases db ON db.database_id = mf.database_id
        WHERE db.name = 'shooting_competition_v1'
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        if results:
            print("\n数据库位置信息:")
            for row in results:
                print(f"数据库名称: {row.DatabaseName}")
                print(f"文件路径: {row.DatabasePath}")
                print(f"文件类型: {row.FileType}")
        else:
            print("未找到数据库信息")
            
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print("查询数据库信息时发生错误:", str(e))

if __name__ == "__main__":
    test_connection()
    print("\n正在查询数据库位置...")
    show_database_info()