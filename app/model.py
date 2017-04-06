# -*- coding: utf-8 -*-
import datetime
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO 
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from .sqlite import SQLiteDB
             
    
class Organization(object):
    """rackhd and no_rackhd organization
    """
    def __init__(self):
        self.rackhd = Team("rackhd", [])
        self.no_rackhd = Team("no_rackhd", [])
        self.db = SQLiteDB()
        self.set_rackhd()
        self.set_no_rackhd()
    
    def set_rackhd(self):
        """select all users from USERS table and set rackhd members
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            sql = "select distinct userName from USERS"                         
            result = self.db.getResult(sql)
            if result[0][0] != None:
                team_members = [x[0] for x in result]
                self.rackhd.set_team_members(team_members)
            else:
                print ("USERS table is empty")
        except Exception as e:
            print ("Error: %s" % e)
    
    def set_no_rackhd(self):
        """select from DB and set the no_rackhd members
        """
        if self.db == None:
            self.db = SQLiteDB()
        try:          
            sql = "select distinct user from PullRequests where user NOT IN (select distinct userName from USERS)"                         
            result = self.db.getResult(sql)
            if result[0][0] != None:
                team_members = [x[0] for x in result]
                self.no_rackhd.set_team_members(team_members)
            else:
                print(" select sql may wrong, or pull request don't have no_rackhd members' pr")
        except Exception as e:
            print ("Error: %s" % e)
    
    def draw_pr_count_monthly(self, startDate, endDate, repos=None):
        """ 1.1 draw pr count monthly with rackhd and no-rackhd
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        month, rackhd_created_count = self.rackhd.get_pr_count_monthly(startDate, endDate, repos)
        _, rackhd_merged_count = self.rackhd.get_pr_count_monthly(startDate, endDate, repos, isMerged=True)
        _, rackhd_unmerged_count = self.rackhd.get_pr_count_monthly(startDate, endDate, repos, isMerged=False)        
        _, no_rackhd_created_count = self.no_rackhd.get_pr_count_monthly(startDate, endDate, repos)
        _, no_rackhd_merged_count = self.no_rackhd.get_pr_count_monthly(startDate, endDate, repos, isMerged=True)
        _, no_rackhd_unmerged_count = self.no_rackhd.get_pr_count_monthly(startDate, endDate, repos, isMerged=False)
        ind = np.linspace(0.5, 9.5, len(month))
#        y_ind = range(0, max(rackhd_created_count)+200, 100)
        fig, ax = plt.subplots(figsize = (12, 6))
        plt.plot(ind, rackhd_created_count, 'r--^', linewidth=1, label='rackhd create pr count')
        plt.plot(ind, rackhd_merged_count, 'r-*', linewidth=1, label='rackhd merged pr count')
        plt.plot(ind, rackhd_unmerged_count, 'r-.o', linewidth=1, label='rackhd unmerged pr count')
        plt.plot(ind, no_rackhd_created_count, 'c--^', linewidth=1, label='norackhd create pr count')
        plt.plot(ind, no_rackhd_merged_count, 'c-*', linewidth=1, label='norackhd merged pr count')
        plt.plot(ind, no_rackhd_unmerged_count, 'c-.o', linewidth=1, label='norackhd unmerged pr count')
        plt.xticks(ind, month, rotation=30)
#        plt.yticks(y_ind)
        plt.xlabel('Month')
        plt.ylabel('PR Count')
        plt.title('PR Count Monthly')
        plt.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()
    
    def draw_comments_monthly(self, startDate, endDate, repos=None):
        """ 1.2 draw review count monthly with rackhd and no-rackhd
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        month, rackhd_comments_count = self.rackhd.get_comments_count_monthly(startDate, endDate, repos)
        _, no_rackhd_comments_count = self.no_rackhd.get_comments_count_monthly(startDate, endDate, repos)
        x_ind = np.linspace(0.5, 9.5, len(month))
        y_ind = range(0, max(rackhd_comments_count+no_rackhd_comments_count)+400, 100)
        fig, ax = plt.subplots(figsize = (12, 6))
        plt.plot(x_ind, rackhd_comments_count, 'r--^', linewidth=1, label='rackhd comments count')
        plt.plot(x_ind, no_rackhd_comments_count, 'c--^', linewidth=1, label='norackhd comments count')
        plt.xticks(x_ind, month, rotation=30)
        plt.yticks(y_ind)
        plt.xlabel('Month')
        plt.ylabel('Review Count')
        plt.title('Review Count Monthly')
        plt.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()		


class Team(object):
    """
    """
    def __init__(self, teamName, team_members):
        """init this class
        args:
            teamName: str
            team_members: str list
        """
        self.name = teamName
        self.team_members = [User(userName, teamName) for userName in team_members]

    def set_team_members(self, team_members):
        self.team_members = [User(userName, self.name) for userName in team_members]

    def datetime_offset_by_month(self, startDate, endDate):
        """splite time by month
        args:
            startDate: if it's "2016-11-11 00:00:00"
            endDate: if it's "2017-01-20 00:00:00"
        return:
            datalist: [("2016-11-11 00:00:00", "2016-12-01 00:00:00"),("2016-12-01 00:00:00", "2017-01-01 00:00:00"),("2017-01-01 00:00:00", "2017-01-20 00:00:00")]
        """
        datelist = []
        if startDate.year == endDate.year and startDate.month == endDate.month:
            datelist.append((startDate, endDate))
        else:
            datetime1 = startDate
            while datetime1 < endDate:            
                q, r = divmod(datetime1.month, 12)
                datetime2 = datetime.datetime(datetime1.year+q, r+1, 1)
                if datetime2 < endDate:
                    datelist.append((datetime1, datetime2))
                else:
                    datelist.append((datetime1, endDate))
                datetime1 = datetime2
        return datelist
   
    def get_pr_count_monthly(self, startDate, endDate, repos=None, isMerged=None):
        """get pr count monthly
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        return:
            (month, count)  
        """
        count_monthly = {}
        datelist = self.datetime_offset_by_month(startDate, endDate)
        for datetuple in datelist:  
            key = '%d-%d' % (datetuple[0].year, datetuple[0].month)
            count_monthly[key] = 0
            for user in self.team_members:
                count_monthly[key] += user.get_pr_count(datetuple[0], datetuple[1], repos, isMerged)
        month, count = zip(*sorted(count_monthly.items(), key = lambda x: x[0], reverse = False))        
        return month, count            
             
    def get_comments_count_monthly(self, startDate, endDate, repos=None):
        """get Team Review comments count monthly
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        return:
            (month, count)         
        """
        count_monthly = {}
        datelist = self.datetime_offset_by_month(startDate, endDate)
        for datetuple in datelist:  
            key = '%d-%d' % (datetuple[0].year, datetuple[0].month)
            count_monthly[key] = 0
            for user in self.team_members:
                count_monthly[key] += user.get_comments_count(datetuple[0], datetuple[1], repos)
        month, count = zip(*sorted(count_monthly.items(), key = lambda x: x[0], reverse = False))       
        return month, count        
     
    def get_avg_duration_monthly(self, startDate, endDate, repos=None):
        """get all team prs' average duration monthly
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        return:
            (month, duration_list) 
        """
        pass
        duration_monthly = {}
        datelist = self.datetime_offset_by_month(startDate, endDate)
        for datetuple in datelist:
            key = '%d-%d' % (datetuple[0].year, datetuple[0].month)
            durations = []
            durations.clear()
            for user in self.team_members:                  
                durations += (user.get_pr_duration(datetuple[0], datetuple[1], repos))
            if not durations:
                continue
            duration_monthly[key] = round(sum(durations) / len(durations) , 2)
        if duration_monthly:
            month, duration_list = zip(*sorted(duration_monthly.items(), key = lambda x: x[0], reverse = False))
            return month, duration_list
        else:
            return (),()
        
    def get_pr_count_member(self, startDate, endDate, repos):
        """ get created_pr count of each member
        args:
            startDate:
            endDate:
            repos:
        return:
            users: list of team members
            pr_count: list of pr count , 对应上面的user
        """
        result = {}
        for user in self.team_members:
            result[user.name] = user.get_pr_count(startDate, endDate, repos)
        users, pr_count = zip(*sorted(result.items(), key = lambda x: x[1], reverse = True))   
        return users, pr_count
          
    def get_comments_count_member(self, startDate, endDate, repos):
        """get comments count of each member in Team
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        return:
            (users, review_count)        
        """
        result = {}
        for user in self.team_members:
            result[user.name] = user.get_comments_count(startDate, endDate, repos)
        users, review_count = zip(*sorted(result.items(), key = lambda x: x[1], reverse = True))
        return users, review_count
    
    def get_avg_duration_member(self, startDate, endDate, repos):
        """get prs' avg duration of each member in Team
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        return:
            (users, durations)
        """
        result = {}
        for user in self.team_members:
            result[user.name] = user.get_avg_duration(startDate, endDate, repos)
        users, durations = zip(*sorted(result.items(), key = lambda x: x[1], reverse = True))
        return users, durations       
    
#==============================================================================
# 绘图    
#==============================================================================
    def draw_team_pr_count_monthly(self, startDate, endDate, repos=None):
        """2.1 draw team PR count monthly
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        month, created_count = self.get_pr_count_monthly(startDate, endDate, repos)
        _, merged_count = self.get_pr_count_monthly(startDate, endDate, repos, isMerged=True)
        _, unmerged_count = self.get_pr_count_monthly(startDate, endDate, repos, isMerged=False)
        #ind = np.linspace(0.5, 9.5, len(month))
        ind = np.linspace(0.5, 9.5, len(month))
        fig, ax = plt.subplots(figsize = (12, 6))
        plt.plot(ind, created_count, 'r--^', linewidth=1, label='create pr count')
        plt.plot(ind, merged_count, 'b-*', linewidth=1, label='merged pr count')
        plt.plot(ind, unmerged_count, 'c-.o', linewidth=1, label='unmerged pr count')
        plt.xticks(ind, month, rotation=30)
        plt.xlabel('Month')
        plt.ylabel('PR Count')
        plt.title('%s PR Count Monthly ' % self.name)
        plt.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()
        
    def draw_team_comments_count_monthly(self, startDate, endDate, repos=None):
        """2.2 draw team review comments count monthly
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        month, comments_count = self.get_comments_count_monthly(startDate, endDate, repos)
        x_ind = np.linspace(0.5, 9.5, len(month))
        y_ind = range(0, max(comments_count)+200, 100)
        fig, ax = plt.subplots(figsize = (12, 6))
        plt.plot(x_ind, comments_count, 'b--^', linewidth=1, label='comments count')
        plt.xticks(x_ind, month, rotation=30)
        plt.yticks(y_ind)
        plt.xlabel('Month')
        plt.ylabel('Review Count')
        plt.title('%s Review Count Monthly ' % self.name)
        plt.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()		

    def draw_team_avg_duration_monthly(self, startDate, endDate, repos=None):
        """2.3 draw team prs' average duration monthly
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        month, duration_list = self.get_avg_duration_monthly(startDate, endDate, repos)
        x_ind = np.linspace(0.5, 9.5, len(month))
        #y_ind = range(0, max(comments_count)+200, 100)
        fig, ax = plt.subplots(figsize = (12, 6))
        plt.plot(x_ind, duration_list, 'b--o', linewidth=1, label='pr duration')
        plt.xticks(x_ind, month, rotation=30)
        #plt.yticks(y_ind)
        plt.xlabel('Month')
        plt.ylabel('PR Average Duration (day)')
        plt.title('%s PR Average Duration Monthly ' % self.name)
        plt.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()		
        
        
    def draw_pr_count_member(self, startDate, endDate, repos=None):
        """2.4 draw commit pr count of each member
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        users, pr_count = self.get_pr_count_member(startDate, endDate, repos)        
        width = 0.4
        ind = np.linspace(0.5, 9.5, len(users))
        fig, ax = plt.subplots(figsize = (12, 6))
        opacity = 0.4
        plt.bar(ind-width/2, pr_count, width, alpha=opacity, color='b', label='PR Count')
        for xy in zip(ind-width/4, pr_count):
            plt.annotate(xy[1], xy=xy, xytext=(xy[0],xy[1]+1))  # 文本标注
        plt.xticks(ind, users, rotation=30)
        plt.xlabel('Team User')
        plt.ylabel('PR Count')
        plt.title('Pull Request count of each user')  
        ax.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()
    
    def draw_comments_count_member(self, startDate, endDate, repos=None):
        """2.5 draw review comments count of each member
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        users, review_count = self.get_comments_count_member(startDate, endDate, repos)
        width = 0.4
        ind = np.linspace(0.5, 9.5, len(users))
        fig, ax = plt.subplots(figsize = (12, 6))
        opacity = 0.4
        plt.bar(ind-width/2, review_count, width, alpha=opacity, color='c', label='Review Count')        
        for xy in zip(ind-width/4, review_count):
            plt.annotate(xy[1], xy=xy, xytext=(xy[0],xy[1]+1))  # 文本标注
        plt.xticks(ind, users, rotation=30)
        plt.xlabel('Team User')
        plt.ylabel('Review Count')
        plt.title('Review count of each user')
        ax.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()
        
    def draw_avg_duration_member(self, startDate, endDate, repos=None):
        """2.6 draw prs' duration of each member
        args:
            startDate: 
            endDate:
            repos: rackhd repository
        """
        users, durations = self.get_avg_duration_member(startDate, endDate, repos)
        width = 0.4
        ind = np.linspace(0.5, 9.5, len(users))
        fig, ax = plt.subplots(figsize = (12, 6))
        opacity = 0.4
        plt.bar(ind-width/2, durations, width, alpha=opacity, color='r', label='Average Duration')
        for xy in zip(ind-width/4, durations):
            plt.annotate(round(xy[1], 2), xy=xy, xytext=(xy[0],xy[1]))  # 文本标注
        plt.xticks(ind, users, rotation=30)
        plt.xlabel('Team User')
        plt.ylabel('PR Average Duration (day)')
        plt.title('PR Average Duration of each user')
        ax.legend()

        canvas=FigureCanvas(fig)
        png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()
                
        

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