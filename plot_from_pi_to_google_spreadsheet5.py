#!/usr/bin/python

#plot_from_pi_to_google_spreadsheet5.py
#This script writes the data from the pi mysql db to a google spreadsheet
#It summarizes hourly data for display here:
#https://googledrive.com/host/0Bz5_4a6W2d6JMm1GbnFpeHdQVms/Home_Energy/index.html
#Jan 2013


# import the modules
try:
    import MySQLdb
    import os,sys,time
    import gdata.spreadsheet.service
    import  pywapi
    import string
except:
    print "Cannot import one or more module"
    sys.exit(1)

#Get outside temp from yahoo weather
try:
    yahoo_result = pywapi.get_weather_from_yahoo('02536')
    C = yahoo_result["condition"]["temp"]
    F = float(C)*(9.0/5.0) + 32
except:
    F = 32.0
    C = 0.0

###############################################################
config = ConfigParser.RawConfigParser()
config.read('/home/pi/gfiske.cfg')
db_user = config.get('section1', 'db_user')
db_passwd = config.get('section1', 'db_passwd')
g_user = config.get('section1', 'g_user')
g_passwd = config.get('section1', 'g_passwd')
db_user = db_user.decode('base64','strict')
db_passwd = db_passwd.decode('base64','strict')
email = g_user.decode('base64','strict')
password = g_passwd.decode('base64','strict')[0:15]
spreadsheet_name = 'home_dials'
###############################################################
spreadsheet_key = '0Aj5_4a6W2d6JdEZ2QmZnZmYyRGhaZWhXVGlUcVRQN2c'
worksheet_id = 'od6'
myspreadsheetclient = gdata.spreadsheet.service.SpreadsheetsService()
myspreadsheetclient.email = email
myspreadsheetclient.password = password
myspreadsheetclient.source = 'Example Spreadsheet Writing Application'
myspreadsheetclient.ProgrammaticLogin()
###############################################################
#get info from the building database
db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
cursor = db.cursor()
myq = "select time, temp, netwatts/count, oldpv/count, newpv/count, totalpv/count, hvac/count from (select max(ts1) as time, count(*) as count, avg(temperature) as temp, sum(netwatts) as netwatts, sum(oldpv) as oldpv, sum(newpv) as newpv, sum(totalpv) as totalpv, sum(hvac) as hvac from trend where date_sub(now(), interval 1 hour) < ts1) as wh;"
myq_avg = "select avg(watthours) from frame where DATE_SUB(ts1, INTERVAL 1 HOUR) and hour(ts1) = (select hour(ts1) from frame order by ts1 desc limit 1) group by hour(ts1);"
cursor.execute(myq)
myq = cursor.fetchone()
#parse results of query
myq1 = str(myq[0])
myq2 = str(round(myq[1],2))
myq3 = str(round(myq[2],2))
myq4 = str(round(myq[3],2))
myq5 = str(round(myq[4],2))
myq6 = str(round(myq[5],2))
myq7 = str(round(myq[6],2))
#parse results of average query
cursor.execute(myq_avg)
myq_avg = cursor.fetchone()
myq8 = str(round(myq_avg[0],2))
#disconnect from db server
db.commit()
db.close()

# Prepare the dictionary to write
dict = {}
dict['date'] = time.strftime('%m/%d/%Y')
dict['time'] = time.strftime('%H:%M:%S')
dict['temp'] = myq2
dict['usage'] = myq3
dict['oldpv'] = myq4
dict['newpv'] = myq5
dict['totalpv'] = myq6
dict['avgusage'] = myq8
dict['hvac'] = myq7
dict['outtemp'] = str(F)
#print dict

#enter the data into the google spreadsheet
entry = myspreadsheetclient.InsertRow(dict, spreadsheet_key, worksheet_id)
if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
    print "Insert row succeeded."
else:
    print "Insert row failed."

#delete the oldest record
lfeed = myspreadsheetclient.GetListFeed(key=spreadsheet_key,wksht_id=worksheet_id)
myspreadsheetclient.DeleteRow(lfeed.entry[0])
