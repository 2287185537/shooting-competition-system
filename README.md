# 射击比赛报名与成绩管理系统

一个基于Flask的Web应用，用于管理射击比赛的报名、成绩记录和排名。

## 功能特点

### 用户管理
- 支持管理员和普通用户角色
- 用户注册和登录
- 个人资料管理
- 密码重置功能

### 比赛管理
- 创建和编辑比赛信息
- 设置报名截止时间
- 限制参赛人数
- 支持多个比赛类别
- 报名审核功能

### 成绩管理
- 多轮次成绩录入
- 自动计算总分
- 实时排名显示
- 成绩导出功能

### 系统功能
- 实时通知系统
- 系统设置管理
- 日志查看和导出
- 数据备份功能

## 安装说明

### 系统要求

- Python 3.8+
- SQL Server 2017+
- ODBC Driver 17 for SQL Server
- Windows身份验证

### 安装步骤

1. 克隆项目并进入目录
```bash
git clone <repository-url>
cd shooting-competition-system
```

2. 创建并激活虚拟环境
```bash
# 使用conda
conda create -n agent_learn python=3.8
conda activate agent_learn
```

3. 安装依赖
```bash
# Windows
.\start.bat

# Linux/macOS
./start.sh
```

4. 配置环境变量
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑.env文件，设置必要的配置项
# - 数据库连接信息
# - 密钥
# - 邮件服务器配置
```

5. 初始化数据库
```bash
python init_db.py
```

6. 运行应用
```bash
flask run
```

### 默认管理员账户

```
用户名: admin
密码: admin123
```

## 使用说明

### 管理员功能

1. 比赛管理
   - 创建新比赛
   - 编辑比赛信息
   - 管理报名
   - 录入成绩

2. 用户管理
   - 查看所有用户
   - 编辑用户信息
   - 重置用户密码

3. 系统管理
   - 系统设置
   - 查看日志
   - 审核报名

### 用户功能

1. 比赛报名
   - 查看比赛列表
   - 报名参加比赛
   - 取消报名

2. 个人中心
   - 查看我的比赛
   - 查看成绩
   - 个人资料管理

3. 通知中心
   - 查看系统通知
   - 标记已读/未读

## 技术栈

- 后端框架：Flask
- 数据库：SQL Server
- 前端框架：Bootstrap 5
- 认证：Flask-Login
- ORM：SQLAlchemy
- 模板引擎：Jinja2

## 目录结构

```
shooting_competition/
├── app/                    # 应用主目录
│   ├── templates/         # HTML模板
│   ├── static/           # 静态文件
│   ├── models.py        # 数据模型
│   ├── auth.py         # 认证相关
│   ├── admin.py        # 管理功能
│   └── competition.py  # 比赛功能
├── config.py             # 配置文件
├── init_db.py           # 数据库初始化
└── run.py              # 应用入口
```

## 问题排查

1. 数据库连接问题
   - 确保SQL Server服务正在运行
   - 确认Windows身份验证已启用
   - 检查ODBC Driver 17是否正确安装

2. 权限问题
   - 确保当前Windows用户有数据库操作权限
   - 检查logs目录是否有写入权限

3. 日志查看
   - 检查logs目录下的日志文件
   - 查看系统管理页面的日志记录

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证