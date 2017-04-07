# -*- coding: utf-8 -*-
import datetime
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO 
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from app.models.user import User
from app.sqlite import SQLiteDB

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