#db_hourly_stats5.py
#this script aggregates energy statistics from the 10-sec trend table in the mysql db
#it populates the 1 hour frame table

import MySQLdb
import  pywapi
import string
import ConfigParser

#Get outside temp from weather.com or, even better, yahoo
try:
    #weather_com_result = pywapi.get_weather_from_weather_com('02536')
    #C = weather_com_result["current_conditions"]["temperature"]
    yahoo_result = pywapi.get_weather_from_yahoo('02536')
    C = yahoo_result["condition"]["temp"]
    F = float(C)*(9.0/5.0) + 32
except:
    F = 0.0
###############################################################
config = ConfigParser.RawConfigParser()
config.read('/home/pi/gfiske.cfg')
db_user = config.get('section1', 'db_user')
db_passwd = config.get('section1', 'db_passwd')
db_user = db_user.decode('base64','strict')
db_passwd = db_passwd.decode('base64','strict')
###############################################################
#connect to db
db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
myq = "select time, temp, netwatts/count, oldpv/count, newpv/count, totalpv/count, hvac/count from (select max(ts1) as time, count(*) as count, avg(temperature) as temp, sum(netwatts) as netwatts, sum(oldpv) as oldpv, sum(newpv) as newpv, sum(totalpv) as totalpv, sum(hvac) as hvac from trend where date_sub(now(), interval 1 hour) < ts1) as wh;"
cursor = db.cursor()
cursor.execute(myq)
myq = cursor.fetchone()

#parse results of query
myq1 = str(myq[0])
temp = str(round(myq[1],2))
wh = str(round(myq[2],2))
oldpv = str(round(myq[3],2))
newpv = str(round(myq[4],2))
pv = str(round(myq[5],2))
hvac = str(round(myq[6],2))
F = str(F)

#################################
# update frame table
myquery = "insert into frame values (DEFAULT, NOW()," + temp + "," + wh + "," + oldpv + "," + newpv + "," + pv + "," + hvac + "," + F + ");"
cursor = db.cursor()
cursor.execute(myquery)
#disconnect
db.commit()
db.close()
