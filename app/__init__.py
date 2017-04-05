from flask import Flask,render_template, make_response, request, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from datetime import datetime
import json
#from io import BytesIO
#import random
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
#from matplotlib.dates import DateFormatter
from config import config

bootstrap = Bootstrap()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config['default'])
    config['default'].init_app(app)

    bootstrap.init_app(app)
	
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app