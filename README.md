# Github-Project-Analytics
  
  运行环境：参见requirements.txt文件
    
    进入shell交互式模式：
    python3 manage.py shell
    
    创建数据库
    from app import sqlite
    db = sqlite.SQLiteDB()
    db.init_db()
    
    加载txt数据到数据库：
    from app import loadData
    loadData.updateDB_from_json()
    
    
  运行：python3 manage.py runserver
    
