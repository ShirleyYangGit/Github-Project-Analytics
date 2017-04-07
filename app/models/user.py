# -*- coding: utf-8 -*-
import datetime
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO 
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from app.sqlite import SQLiteDB

class User(object):
    """    
    """

    def __init__(self, name, teamName):
        self.name = name
        self.teamName = teamName
        self.db = SQLiteDB()

    def get_pr_rank(self, startDate, endDate, repos = None, isMerged=None):
        """get the pr count rank in all users
        args:
            startDate: 
            endDate
            repos: rackhd repository
            isMerged: True or False (pr be merged or not)
        return:
            the len(less count)/len(result)*100
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            items = []
            items.append("select user, count(*) Count from PullRequests where")
            if isMerged == None:            
                items.append("createDate >= '%s'" % startDate)
                items.append("and createDate < '%s'" % endDate)            
            else:
                items.append("merged == '%s'" % isMerged)
                items.append("and endDate >= '%s'" % startDate)
                items.append("and endDate < '%s'" % endDate)                
            if repos != None:
                items.append("and repo in (" )
                buffer_repo = None
                for repo in repos:
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo) 
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            items.append("group by user order by Count")
            select_sql = ' '.join(items)            
            #print(select_sql)                
            result = self.db.getResult(select_sql)
            if result[0][0] == None:
                print("result is None. Select sql may be wrong!")
            for line in result:
                if line[0] == self.name:
                    user_info = line
                    break
            beat_rank = round(result.index(user_info)/len(result)*100, 2)    
            #print(beat_rank)
            return beat_rank
        except Exception as e:
            print ("Error: %s" % e)
        
    def get_comments_rank(self, startDate, endDate, repos = None):
        """get the comments count rank in all users
        args:
            startDate: 
            endDate
            repos: rackhd repository
        return:
            the len(less count)/len(result)*100
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            items = []
            items.append("select from_user, count(*) Count from Comments where")    
            items.append("submitDate >= '%s'" % startDate)
            items.append("and submitDate < '%s'" % endDate)
            if repos != None:
                items.append("and repo in (" )
                buffer_repo = None
                for repo in repos:
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo) 
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            items.append("group by from_user order by Count")
            select_sql = ' '.join(items)            
            #print(select_sql)                
            result = self.db.getResult(select_sql)
            if result[0][0] == None:
                print("result is None. Comments Table is Null. Or select sql may be wrong!")
            for line in result:
                if line[0] == self.name:
                    user_info = line
                    break
            beat_rank = round(result.index(user_info)/len(result)*100, 2)    
            #print(beat_rank)
            return beat_rank
        except Exception as e:
            print ("Error: %s" % e)

    def get_three_top_review_to(self, startDate, endDate, repos = None):
        """get the three top users who he or her reviews to 
        args:
            startDate: 
            endDate
            repos: rackhd repository
        return:
            the three top (user, count)
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            items = []
            items.append("select to_user, count(*) Count from Comments where from_user != to_user and from_user = '%s'" % self.name)    
            items.append("and submitDate >= '%s'" % startDate)
            items.append("and submitDate < '%s'" % endDate)
            if repos != None:
                items.append("and repo in (" )
                buffer_repo = None
                for repo in repos:
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo) 
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            items.append("group by to_user order by Count DESC")
            select_sql = ' '.join(items)            
            #print(select_sql)                
            result = self.db.getResult(select_sql)
            if result[0][0] == None:
                print("result is None. Comments Table is Null. Or select sql may be wrong!")   
            #print(result)
            return result[0:3]
        except Exception as e:
            print ("Error: %s" % e)
            
    def get_three_top_review_from(self, startDate, endDate, repos = None):
        """get the three top users that he or her be reviewed from 
        args:
            startDate: 
            endDate
            repos: rackhd repository
        return:
            the three top (user, count)
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            items = []
            items.append("select from_user, count(*) Count from Comments where from_user != to_user and to_user = '%s'" % self.name)    
            items.append("and submitDate >= '%s'" % startDate)
            items.append("and submitDate < '%s'" % endDate)
            if repos != None:
                items.append("and repo in (" )
                buffer_repo = None
                for repo in repos:
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo) 
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            items.append("group by from_user order by Count DESC")
            select_sql = ' '.join(items)            
            #print(select_sql)                
            result = self.db.getResult(select_sql)
            if result[0][0] == None:
                print("result is None. Comments Table is Null. Or select sql may be wrong!")   
            #print(result[0:15])
            return result[0:3]
        except Exception as e:
            print ("Error: %s" % e)
            
    def get_pr_count(self, startDate = None, endDate = None, repos = None, isMerged=None):
        """ get user commit pr count
        args:
            startDate:
            endDate:
            repos: rackhd repository
            isMerged: True or False (pr be merged or not)
        return:
            the count of pr
        """
        #count = SQLiteDB().selectUserPRcount(self.name, startDate, endDate, repos)
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            items = []
            items.append("select count(*) from PullRequests where user = '%s'" % self.name)
            if isMerged == None:            
                if startDate != None:
                    items.append("and createDate >= '%s'" % startDate)
                if endDate != None:
                    items.append("and createDate < '%s'" % endDate)            
            else:
                items.append("and merged == '%s'" % isMerged)
                if startDate != None:
                    items.append("and endDate >= '%s'" % startDate)
                if endDate != None:
                    items.append("and endDate < '%s'" % endDate)                
            if repos != None:
                items.append("and repo in (" )
                buffer_repo = None
                for repo in repos:
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo)  #add the previous repo
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            select_sql = ' '.join(items)                            
            result = self.db.getResult(select_sql)
            if result[0][0] == None:
                return 0.0
            else:
                return result[0][0]				
        except Exception as e:
            print ("Error: %s" % e)

    def get_comments_count(self, startDate = None, endDate = None, repos = None):
        """get review comments count
        args:
            startDate:
            endDate:
            repos: rackhd repository
        return:
            the count of comments
        """
        if self.db == None:
            self.db = SQLiteDB()
        try: 
            items = []
            items.append("select count(*) from Comments where from_user = '%s'" % self.name)
            if startDate != None :
                items.append("and submitDate >= '%s'" % startDate)
            if endDate != None :
                items.append("and submitDate < '%s'" % endDate)
            if repos != None :
                items.append("and repo in (" )
                buffer_repo = None
                for repo in repos:                    
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo)  #add the previous repo
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            select_sql = ' '.join(items)  
            result = self.db.getResult(select_sql)
            if result[0][0] == None:
                return 0.0
            else:
                return result[0][0]
        except Exception as e:
            print ("Error: %s" % e)
    
    def get_avg_duration(self, startDate = None, endDate = None, repos = None):
        """get avg duration of pull requests 
        args:
            startDate:
            endDate:
            repos: rackhd repository
        return:
            the prs avg duration        
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:     
            items = []
            items.append("select avg(julianday(endDate)-julianday(createDate)) from PullRequests where user = '%s' " % self.name)
            if startDate != None :
                items.append("and createDate >= '%s' " % startDate)
            if endDate != None :
                items.append("and createDate < '%s' " % endDate)
            if repos != None :
                items.append("and repo in ( " )
                buffer_repo = None
                for repo in repos:
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo)  #add the previous repo
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            select_sql = ' '.join(items)
            result = self.db.getResult(select_sql)
            if result[0][0] == None:  
                return 0.0
            else:
                return result[0][0]
        except Exception as e:
            print ("Error: %s" % e)
            
    def get_pr_duration(self, startDate = None, endDate = None, repos = None):
        """get pull requests' duration list
        args:
            startDate:
            endDate:
            repos: rackhd repository
        return: 
            all pr duration list
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:
            items = []
            items.append("select julianday(endDate)-julianday(createDate) from PullRequests where user = '%s' " % self.name)
            if startDate != None :
                items.append("and createDate >= '%s' " % startDate)
            if endDate != None :
                items.append("and createDate < '%s' " % endDate)
            if repos != None :
                items.append("and repo in ( " )
                buffer_repo = None
                for repo in repos:
                    # 添加上一个repo
                    if buffer_repo != None:
                        items.append("'%s'," % buffer_repo) #add the previous repo
                    buffer_repo = repo                
                items.append("'%s')" % buffer_repo) 
            select_sql = ' '.join(items)
            result = self.db.getResult(select_sql)
            if len(result)!= 0:
                return [x[0] for x in result]
            else:        
                return result        
        except Exception as e:
            print ("Error: %s" % e)