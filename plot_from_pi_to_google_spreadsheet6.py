#!/usr/bin/python

#plot_from_pi_to_google_spreadsheet6.py
#This script writes the data from the pi mysql db to a google spreadsheet
#It summarizes hourly data for display here:
#https://googledrive.com/host/0Bz5_4a6W2d6JMm1GbnFpeHdQVms/Home_Energy/index.html
#https://storage.googleapis.com/gfiske.us/homeEnergy/dials.html
#Jan 2013
#updated Jan 2015 to include tank temp data

#import darksky weather api
#from requests_forecast import Forecast
import forecastio

# import the modules
try:
    import MySQLdb
    import os,sys,time
    from datetime import datetime
    from pytz import timezone        
    import gspread
    #import  pywapi
    import string
    import ConfigParser
    from oauth2client.client import SignedJwtAssertionCredentials
    import json
except:
    print "Cannot import one or more module"
    sys.exit(1)

#Try to get outside temp from my outdoor sensor hooked to the GPIO board
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')
temp_sensor = "/sys/bus/w1/devices/28-03164546d6ff/w1_slave"
def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines
def read_temp():
    lines = temp_raw()
    temp_output = lines[1].find('t=')
    temp_string = lines[1].strip()[temp_output+2:]
    temp_c = float(temp_string) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    temp_f = round(temp_f, 2)
    return str(temp_f) 

try:
    F = read_temp()
except:
    #Get outside temp from weather.com or, even better, forcastio
    F = 50
    #weather_com_result = pywapi.get_weather_from_weather_com('02536')
    #C = weather_com_result["current_conditions"]["temperature"]
    #yahoo_result = pywapi.get_weather_from_yahoo('02536')
    #C = yahoo_result["condition"]["temp"]
    #F = float(C)*(9.0/5.0) + 32
    forecast = forecastio.load_forecast('72348bae4adf606ce385c7782fc681b4', 41.5982, -70.5927)
    current = forecast.currently()
    F = current.temperature    
    F = round(F,1)



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

#get info from the building database
db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
cursor = db.cursor()
myq = "select time, temp, netwatts/count, oldpv/count, newpv/count, totalpv/count, hvac/count from (select max(ts1) as time, count(*) as count, avg(temperature) as temp, sum(netwatts) as netwatts, sum(oldpv) as oldpv, sum(newpv) as newpv, sum(totalpv) as totalpv, sum(hvac) as hvac from trend where date_sub(now(), interval 1 hour) < ts1) as wh;"
myq_avg = "select avg(watthours) from frame where DATE_SUB(ts1, INTERVAL 1 HOUR) and hour(ts1) = (select hour(ts1) from frame order by ts1 desc limit 1) group by hour(ts1);"
myq_temp = "select avg(tankTemp) from temperature where date_sub(ts1, interval 1 hour) and ts1 > date_sub(now(), interval 1 day) group by hour(ts1) order by id desc limit 1;"
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
#parse results of temperature query
cursor.execute(myq_temp)
myq_temp = cursor.fetchone()
myq9 = str(round(myq_temp[0],2))
#disconnect from db server
db.commit()
db.close()

#make timestamp
#convert to US/Eastern time zone
now_utc = datetime.now(timezone('UTC'))
now_eastern = now_utc.astimezone(timezone('US/Eastern'))
myTimeStamp = now_eastern.strftime("%Y-%m-%d %H:%M:%S")

#enter the data into the google spreadsheet
rowToAdd = (time.strftime('%m/%d/%Y'),time.strftime('%H:%M:%S'),myq2,myq3,myq4,myq5,myq6,myq8,myq7,str(F),myq9,myTimeStamp)
json_key = json.load(open('/home/pi/pi_energy/raspPi-e0a08639ebab.json'))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
g = gspread.authorize(credentials)
worksheet = g.open('home_energy_from_pi').get_worksheet(0)
worksheet.append_row(rowToAdd)

