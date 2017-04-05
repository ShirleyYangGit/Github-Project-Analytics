# -*- coding: utf-8 -*-
import sqlite3
import os
from flask import g
from contextlib import closing

from . import rackhd_config as rc

DATABASE = 'app/sqlite3.db'

class SQLiteDB(object):
    def __init__(self):
        self.conn = sqlite3.connect('app/sqlite3.db')
        self.cur = self.conn.cursor()
        self.conn.isolation_level = None  # None: 每次数据库操作，自动提交
        #sqlite3_limit(self.conn, 4, 50000)  #first parameter: database connection; second parameter: the id of SQLITE_LIMITE_COMPOUND_SELECT; third parameter: new limit for that construct
        
	
    def openDB(self):
        """open DataBase
        """
        self.conn = sqlite3.connect(DATABASE)
        self.conn.isolation_level = None
        self.cur = self.conn.cursor()
	
    def init_db(self):
        with open('app/schema.sql', mode='r') as f:
            self.cur.executescript(f.read())
        self.insertReposTB()
        self.insertUsersTB()
	
    def closeDB(self):
        self.cur.close()
        self.conn.close()

    def query_db(self, query, args, one=False):
        self.cur.execute(query, args)
        rv = self.cur.fetchall()
        #self.cur.close()
        return (rv[0] if rv else None) if one else rv

    def getResult(self, selectsql):        
        self.cur.execute(selectsql)
        self.res = self.cur.fetchall()
        return self.res

    def execute_sqls(self, sqls):
        for sql in sqls:
		    ####Test
            #print("Comments Table Insert SQL: \n %s" % sql)
            self.cur.execute(sql)
		
    def insertReposTB(self):
        """ REPLACE into REPOS Table. The data is from rackhd_config file.
        """
        repos = rc.repos
        if len(repos) == 0 :
            insert_sql = ""
        else:  
            items = []
            items.append("REPLACE INTO REPOS (name) VALUES")
            buffer_repo = None
            for repo in repos:
                if buffer_repo != None:
                    items.append("('%s')," % buffer_repo)  #add the previous repo              
                buffer_repo = repo
            items.append("('%s')" % buffer_repo)
            insert_sql = ' '.join(items)
        #####Test
        #print(insert_sql) 			
        self.cur.execute(insert_sql)
		
    def insertUsersTB(self):
        """ REPLACE into USERS Table. The data is from rackhd_config file.
        """
        teams = rc.Teams
        if len(teams) == 0 :
            insert_sql = ""
        else:        
            items = []
            items.append("REPLACE INTO USERS (userName, teamName) VALUES")
            for key, team in teams.items():
                for user in team:
                    items.append("( '%s', '%s' )," % (user, key))
            sql = ' '.join(items)
            insert_sql = sql[:-1]
        #####Test
        #print(insert_sql)        
        self.cur.execute(insert_sql)
		
    def ReplacedPullRequestTB(self, data):
        """REPLACE Into PullRequests Table
        args:
            data: list[[id:' ', user:' ', repo:' ', ...], ...]
        """
        if len(data) != 0:
            items = []
            items.append("REPLACE INTO PullRequests (id, user, number, repo, title, state, merged, comments_count, createDate, endDate ) VALUES ")
            for pr in data:
                items.append( "(%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )," % \
                        (int(pr['id']), pr['user'], pr['number'], pr['repo'], pr['title'].replace('\'', '\"'), pr['state'], pr['merged'], pr['comments_count'], pr['createDate'], pr['endDate']) )
            sql = ' '.join(items)
            insert_sql = sql[:-1]  # del the last comma
        else:
            insert_sql = ""
        ####Test
        #print("PullRequests Table Insert SQL: \n %s" % insert_sql)        
        self.cur.execute(insert_sql)
	
    def ReplacedCommentsTB(self, data):
        """REPLACE Into Comments Table
        args:
            data: list[[id:' ', from_user:' ', repo:' ', ...], ...]
        """
        if len(data) != 0:  
            items = []
            items.append("REPLACE INTO Comments (id, id_pr, repo, from_user, to_user, body, isApproved, submitDate) VALUES ")
            for cm in data:
                items.append(" (%d, %d, '%s', '%s', '%s', '%s', %d, '%s')," %\
                        (int(cm['id']), int(cm['id_pr']), cm['repo'], cm['from_user'], cm['to_user'], cm['body'].replace('\'', '\"'), cm['isApproved'], cm['submitDate']))                           
            sql = ' '.join(items)
            insert_sql = sql[:-1]  # del the last comma
        else:
            insert_sql = ""        
        ####Test
        #print("Comments Table Insert SQL: \n %s" % insert_sql)        
        self.cur.execute(insert_sql)        

    def insertPullRequestsTBfromJson(self, data):
        """REPLACE Into PullRequests Table and the data is from JSON file
        args:
            data: dict{id:{user:' ' ,repo:' ',...}, ...}
        """
        insert_sqls = []
        sql_head = "REPLACE INTO PullRequests (id, user, number, repo, title, state, merged, comments_count, createDate, endDate ) VALUES "
        if len(data) != 0:
            n = 1
            items = []
            for key, pr in data.items():
                if n == 1:
                    items.append(sql_head)
                if n % 500 == 0:
                    sql_body = ' '.join(items)[:-1]
                    insert_sqls.append(sql_body)
                    items.clear()
                    items.append(sql_head)
                n += 1   
                items.append( "(%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )," % \
                        (int(key), pr['user'], pr['number'], pr['repo'], pr['title'].replace('\'', '\"'), pr['state'], pr['merged'], pr['comments_count'], pr['createDate'], pr['endDate']) )
            insert_sqls.append(' '.join(items)[:-1])
        ####Test
        #print("PullRequests Table Insert SQL: \n %s \n %s" % (insert_sqls[0], insert_sqls[1]))        
        self.execute_sqls(insert_sqls)
    

    def insertCommentsTBfromJson(self, data):
        """REPLACE Into Comments Table and the data is from JSON file
        args:
            data: dict{id:{from_user:' ' ,repo:' ',...}, ...}
        """
        insert_sqls = []
        sql_head = "REPLACE INTO Comments (id, id_pr, repo, from_user, to_user, body, isApproved, submitDate) VALUES "
        if len(data) != 0:
            n = 1
            items = []
            for key, cm in data.items():
                if n == 1:
                    items.append(sql_head)
                if n % 500 == 0:
                    sql_body = ' '.join(items)[:-1]
                    insert_sqls.append(sql_body)
                    items.clear()
                    items.append(sql_head)
                n += 1
                items.append(" (%d, %d, '%s', '%s', '%s', '%s', %d, '%s')," %\
                        (int(key), int(cm['id_pr']), cm['repo'], cm['from_user'], cm['to_user'], cm['body'].replace('\'', '\"'), cm['isApproved'], cm['submitDate'])) 
                						
            insert_sqls.append(' '.join(items)[:-1])            
        ####Test
        #print("Comments Table Insert SQL: \n %s \n %s" % (insert_sqls[0], insert_sqls[1]))       
        self.execute_sqls(insert_sqls)
		
	
	


		
