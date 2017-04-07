# -*- coding: utf-8 -*-
import datetime
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO 
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from app.models.team import Team
from app.sqlite import SQLiteDB

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
