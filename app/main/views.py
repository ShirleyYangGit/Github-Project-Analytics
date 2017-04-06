from flask import Flask,render_template, make_response, request, session, redirect, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from datetime import datetime
import json
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from . import main
from .. import model
from .. import rackhd_config

@main.route("/index.html", methods=['GET'])
@main.route("/index", methods=['GET'])
@main.route("/", methods=['GET'])
def index():
	return render_template('index.html')

@main.route("/global_info", methods=['GET'] )
def global_info(): 
    return render_template('global_info.html')
	
@main.route("/get_global_image", methods=['POST'] )
def get_global_image():
    startDate = request.form['StartDate'] or '2015-10-01'
    endDate = request.form['EndDate'] or datetime.now()
    image_name = request.form['image_name']
    org = model.Organization()

    if type(startDate) == type(""):
        startDate = datetime.strptime(startDate, "%Y-%m-%d")
    if type(endDate) == type(""):
        endDate = datetime.strptime(endDate, "%Y-%m-%d")

    #print("startDate %s, endDate: %s" % (startDate,endDate)	)

    operator = {'image1': org.draw_pr_count_monthly(startDate, endDate),
                'image2': org.draw_comments_monthly(startDate, endDate)}
    image_output = operator[image_name]
    image = base64.b64encode(image_output).decode('UTF-8')
    return make_response(image)  
	
@main.route("/team_info", methods=['GET'])
def team_info():
    team_name = 'Maglev Team'
    return render_template('team_info.html', teamName = team_name)

@main.route("/get_team_image", methods=['POST'] )
def get_team_image():
    teams = rackhd_config.Teams
    repo = rackhd_config.repos    
    team_name = request.form['TeamName'] or 'Maglev Team'
    startDate = request.form['StartDate'] or '2015-10-01'
    endDate = request.form['EndDate'] or datetime.now()
    image_name = request.form['image_name']    
    if type(startDate) == type(""):
        startDate = datetime.strptime(startDate, "%Y-%m-%d")
    if type(endDate) == type(""):
        endDate = datetime.strptime(endDate, "%Y-%m-%d")
    team_members = teams[team_name]	
    #print("startDate %s, endDate: %s" % (startDate,endDate)	)
    t = model.Team(team_name, team_members)	
    operator = {'image1': t.draw_team_pr_count_monthly(startDate, endDate),
                'image2': t.draw_team_comments_count_monthly(startDate, endDate),
                'image3': t.draw_team_avg_duration_monthly(startDate, endDate),
				'image4': t.draw_pr_count_member(startDate, endDate),
                'image5': t.draw_comments_count_member(startDate, endDate),
                'image6': t.draw_avg_duration_member(startDate, endDate)}
    image_output = operator[image_name]
    image = base64.b64encode(image_output).decode('UTF-8')
    return make_response(image)  
	
@main.route("/personal_info", methods=['GET'])
def personal_info(): 
    userName = 'panpan0000' 
    return render_template('personal_info.html', userName = userName)

@main.route("/get_user_info", methods=['POST'])
def get_user_info():
    teams = rackhd_config.Teams
    repo = rackhd_config.repos
    teamName = request.form['TeamName']
    user = request.form['UserName']
    startDate = request.form['StartDate']
    endDate = request.form['EndDate']	    
    if startDate is "":
        startDate = datetime.strptime('2015-10-01T00:00:00Z', "%Y-%m-%dT%H:%M:%SZ")
    if endDate is "":
        endDate = datetime.now()    
    if teamName is "":
        teamName = 'Maglev Team'
    if user is "":
        user = "panpan0000"
    team_members = teams[teamName]
#    print(team_members)
    u = model.User(user, teamName)
    user_data = {}
    user_data['pr_rank'] = u.get_pr_rank(startDate, endDate)
    user_data['comments_rank'] = u.get_comments_rank(startDate, endDate)
    user_data['three_top_review_to'] = u.get_three_top_review_to(startDate, endDate)
    user_data['three_top_review_from'] = u.get_three_top_review_from(startDate, endDate)

    return make_response(json.dumps(user_data))

