#db_temperature_data1.py
#this script aggregates collects temperature data from the 1wire devices and yahoo weather and updates the temperature table in the mysql db
#it runs every 10 minutes via a chron job

#import darksky weather api
#from requests_forecast import Forecast
import forecastio

import MySQLdb
#import pywapi
import string
import time
import os
import ConfigParser
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import json

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
spreadsheet_name = 'Copy of home_dials new sheet'
###############################################################


#Get outside temp from weather.com or, even better, yahoo
try:
    #weather_com_result = pywapi.get_weather_from_weather_com('02536')
    #C = weather_com_result["current_conditions"]["temperature"]
    #yahoo_result = pywapi.get_weather_from_yahoo('02536')
    #C = yahoo_result["condition"]["temp"]
    #F = float(C)*(9.0/5.0) + 32
    forecast = forecastio.load_forecast('72348bae4adf606ce385c7782fc681b4', 41.5982, -70.5927)
    current = forecast.currently()
    F = current.temperature    
    F = round(F,1)
except:
    F = 50.0

#Get 1wire kitchen temperature
file_name = os.path.join("/","mnt","1wire","28.ED548F050000","temperature")
file_object = open(file_name, 'r')
line = file_object.read()
kitchTemp = (float(line)*1.8)+32.0
kitchTemp = round(kitchTemp, 1)
file_object.close()

#Get 1wire solar tank temperature
file_name = os.path.join("/","mnt","1wire","28.2B9F8F050000","temperature")
file_object = open(file_name, 'r')
line = file_object.read()
tankTemp = (float(line)*1.8)+32.0
tankTemp = round(tankTemp, 1)
file_object.close()


#check to see if either temp sensor failed (reads 185).  If so, use previous value from database
#connect to db
try:
    db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
    myq = "select kitchTemp, tankTemp from temperature order by ts1 desc limit 1;"
    cursor = db.cursor()
    cursor.execute(myq)
    myq = cursor.fetchone()
    kitchTempdb = str(myq[0])
    tankTempdb = str(myq[1])
    db.close()
except Exception, msg:
    print "can't access db"
    print str(msg)

if kitchTemp == 185:
    kitchTemp = kitchTempdb
    kitchTemp = str(kitchTemp)
else:
    kitchTemp = str(kitchTemp)

if tankTemp == 185:
    tankTemp = tankTempdb
    tankTemp = str(tankTemp)
else:
    tankTemp = str(tankTemp)

F = str(F)

#insert data to temperature table in db
try:
    #connect to db
    db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
    myq = "insert into temperature values (DEFAULT, NOW()," + kitchTemp + "," + tankTemp + "," + F + ");"
    cursor = db.cursor()
    cursor.execute(myq)
    db.commit()
    db.close()
except Exception, msg:
    print "Error"
    print str(msg)

#lastly, update live dials
try:
    #g = gspread.login(email, password)
    json_key = json.load(open('/home/pi/pi_energy/raspPi-e0a08639ebab.json'))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
    g = gspread.authorize(credentials)
    worksheet = g.open('Copy of home_dials new sheet').get_worksheet(0)
    worksheet.update_cell(2,4,kitchTemp)
    worksheet.update_cell(2,5,tankTemp)
    worksheet.update_cell(2,6,F)
except Exception, msg:
    print "Error"
    print str(msg)


