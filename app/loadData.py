# -*- coding: utf-8 -*-

import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from datetime import datetime
import json

from . import rackhd_config as rc
from . import _JSONEncoder as je
from . import sqlite


def iter_request_data(pr_url, headers):
    """ Iteration url data
    """
    url = pr_url
    while url is not None:
        sys.stdout.write(".")
        sys.stdout.flush()

        #print ("--url--:", url)        
        #requests.packages.urllib.util.ssl_.DEFAULT_CIPHERS = 'RSA+3DES' 
        r = requests.get(url, headers = headers)
        url = None
        #print("url header: ", r.headers)
        
        if "link" in r.headers:
            link_header = r.headers["Link"]
            link_header = link_header.split(",")
                            
            for lh in link_header:
                clh = lh.rsplit(";")
                if "next" in clh[1]:
                    url = clh[0]
                    url = url.strip()
                    url = url[1:len(url)-1]
        data = r.json()

        for d in data:
            yield d
 
def load_certain_period_data(url, headers, startDate, endDate): 
    """get pull request and comments statistics for a period of time 
    """
    pullRequests = []
    comments = []
   
    for pr in iter_request_data(url, headers):                
        pull_request = {}  
        cms = []              
        if pr['merged_at']:
            pr_merged = True
            pr_end = pr["merged_at"]
        elif pr["state"] == "closed":
            pr_merged = False
            pr_end = pr["closed_at"]
        else:
            pr_merged = False
            pr_end = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
        pr_createDate = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")                    
        pr_endDate = datetime.strptime(pr_end, "%Y-%m-%dT%H:%M:%SZ")   
        # 根据pr_createDate和pr_endDate筛选pr

        if startDate< pr_endDate <= endDate or startDate<= pr_createDate < endDate:
            print startDate, endDate
            print pr_endDate, pr_createDate
            pull_request["id"] = pr["id"]             
            pull_request["user"] = pr["user"]["login"]
            pull_request["number"] = pr["number"]
            pull_request["repo"] = pr["base"]["repo"]["name"]
            pull_request["title"] = pr["title"]
            pull_request["body"] = pr["body"]
            pull_request["state"] = pr["state"]        
            pull_request["merged"] = pr_merged
            pull_request["createDate"] = pr_createDate
            pull_request["endDate"] = pr_endDate
             
            # comments info —— issuse comments url
            issuse_comments_url = pr["comments_url"]         
            issuse_comments, icm_count = get_comments(issuse_comments_url, headers)
            cms += issuse_comments
            # comments info —— pull requests review comments url
            review_cmments_url = pr["review_comments_url"]
            review_comments, rcm_count= get_comments(review_cmments_url, headers)
            cms += review_comments
            # review info url
            review_url = pr['url'] + "/reviews"   
            reviews, re_count = get_pullRequest_review(review_url, headers)     
            cms += reviews
            
            for cm in cms:
                cm['id_pr'] = pull_request["id"]
                cm['to_user'] = pull_request["user"]
                cm['repo'] = pull_request["repo"]
                if cm['isApproved'] == 1:
                    pass                
                elif ("👍" in cm['body'] or "+1" in cm['body']) and cm['from_user'] != cm['to_user']:   
                    cm['isApproved'] = 1
            
            pull_request["comments_count"] = icm_count + rcm_count + re_count  
            pullRequests.append(pull_request) 
            comments += cms
    return pullRequests, comments    
    
def get_comments(url, headers):
    """get issue or review comments
    """
    comments = []
    for cm in iter_request_data(url, headers):    
        comment = {}
        comment['from_user'] = cm["user"]["login"]
        if comment['from_user'] in ['JenkinsRHD', 'houndci-bot']:
            continue
        comment['id'] = cm["id"]
        comment['body'] = cm["body"].replace('\'', '\"')
        comment['submitDate'] = datetime.strptime(cm["updated_at"], "%Y-%m-%dT%H:%M:%SZ")  
        comment['isApproved'] = 0
        comments.append(comment)
    return comments, len(comments)

def get_pullRequest_review(url, headers):    
    """ get reviews info
    """
    reviews = []
    for rew in iter_request_data(url, headers):
        review = {}
        review['id'] = rew["id"]
        review['from_user'] = rew["user"]["login"]
        if review['from_user'] in ['JenkinsRHD', 'houndci-bot']:
            continue
        review['body'] = rew["body"].replace('\'', '\"')
        review['submitDate'] = datetime.strptime(rew["submitted_at"], "%Y-%m-%dT%H:%M:%SZ")          
        if rew["state"] == 'APPROVED':
            review['isApproved'] = 1
        else:
            review['isApproved'] = 0
        reviews.append(review)
    return reviews, len(reviews)

def get_pr_data(repos):
    """read repo txt file
    """
    data = {}
    for rp in repos:
        f = open('data/%s.txt' % rp, 'r')
        data.update(json.loads(f.read(), object_hook = je.object_hook))
        f.close()
    return data    



def get_comments_data(data):
    """get comments data from txt file
    args:
        data: read from txt file        
    """
    comments = {}
    for id_pr, pr in data.items():
        new_cm = {}
        new_cm.clear()
        
        new_cm['id_pr'] = id_pr
        new_cm['repo'] = pr['repo']
        new_cm['to_user'] = pr['user']        
        for key,cm in pr['comments'].items():
            new_cm['id'] = key
            new_cm['from_user'] = cm['user']
            new_cm['submitDate'] = cm['updateDate']
            new_cm['body'] = cm['body']
            new_cm['isApproved'] = 0
            if ("👍" in cm['body'] or '+1' in cm['body']) and new_cm['from_user'] != new_cm['to_user']:   
                new_cm['isApproved'] = 1
            comments[new_cm['id']] = new_cm
        for key,rev in pr['reviews'].items():
            new_cm['id'] = key
            new_cm['from_user'] = rev['user']
            new_cm['submitDate'] = rev['submitDate']
            new_cm['body'] = rev['body']
            new_cm['isApproved'] = 0
            if ((rev['state'] == 'APPROVED') or ("+1" in rev['body'] or '👍' in rev['body'])) and new_cm['from_user'] != new_cm['to_user']:
                new_cm['isApproved'] = 1
            comments[new_cm['id']] = new_cm
    return comments  

def updateDB_from_json(repos = rc.repos):
    """update database and the data is from txt file
    """
    db = sqlite.SQLiteDB()
    pr_data = get_pr_data(repos)
    comments = get_comments_data(pr_data)    
    db.insertPullRequestsTBfromJson(pr_data)
    db.insertCommentsTBfromJson(comments)
    db.closeDB()
    
def loadData_and_updateDB(startDate, endDate, repos = rc.repos):
    """update database and the data is load from github
    args:
        startDate:
        endDate:
        repos: rc.repos
    """
    owner = rc.owner
    headers = rc.headers
    db = sqlite.SQLiteDB()
    for rp in repos:
        # request data
        url = "https://api.github.com/repos/%s/%s/pulls?state=all&sort=created&per_page=100" % (owner, rp) 
        pullRequests, comments = load_certain_period_data(url, headers, startDate, endDate)
        db.ReplacedPullRequestTB(pullRequests)
        db.ReplacedCommentsTB(comments)       
    db.closeDB()
