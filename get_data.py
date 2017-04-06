from app import loadData
from datetime import datetime
startDate=datetime.strptime("2017-04-01T19:01:12Z", "%Y-%m-%dT%H:%M:%SZ")
endDate=datetime.strptime("2017-04-07T19:01:12Z", "%Y-%m-%dT%H:%M:%SZ")
from app import rackhd_config as rc
loadData.loadData_and_updateDB(startDate, endDate, repos = rc.repos)
