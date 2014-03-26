#db_hourly_stats5.py
#this script aggregates statistics from the trend table in the mysql db
#and adds the values to the frame tables (which is an hourly table)
#It is an update to version 2, it now includes PV stats from both systems


#edited on 9/27/13 to include HVAC data
#edited on 10/21/13 to include outdoor temp
#edited on 12/6/13 to use Yahoo weather instead of weather.com, better temp data

import MySQLdb
import  pywapi
import string

#Get outside temp from weather.com or, even better, yahoo
try:
    #weather_com_result = pywapi.get_weather_from_weather_com('02536')
    #C = weather_com_result["current_conditions"]["temperature"]
    yahoo_result = pywapi.get_weather_from_yahoo('02536')
    C = yahoo_result["condition"]["temp"]
    F = float(C)*(9.0/5.0) + 32
except:
    F = 0.0

#################################
#connect to db
db = MySQLdb.connect("127.0.0.1", "root", 'cXdlcnR5MTYqNQ==\n'.decode('base64'), "energy")

#################################
#do query on trend table
##myq = "select ts1, avg(temperature), sum(netwatts) / count(*) as wh, sum(oldpv) / count(*) as oldpv, sum(newpv) / count(*) as newpv, sum(totalpv) / count(*) as pv, sum(hvac) / count(*) as hvac from trend group by hour(ts1) order by ts1 desc limit 1;"
myq = "select time, temp, netwatts/count, oldpv/count, newpv/count, totalpv/count, hvac/count from (select max(ts1) as time, count(*) as count, avg(temperature) as temp, sum(netwatts) as netwatts, sum(oldpv) as oldpv, sum(newpv) as newpv, sum(totalpv) as totalpv, sum(hvac) as hvac from trend where date_sub(now(), interval 1 hour) < ts1) as wh;"
cursor = db.cursor()
cursor.execute(myq)
# Fetch a single row using fetchone() method.
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
#now update frame table
myquery = "insert into frame values (DEFAULT, NOW()," + temp + "," + wh + "," + oldpv + "," + newpv + "," + pv + "," + hvac + "," + F + ");"
cursor = db.cursor()
cursor.execute(myquery)
#disconnect from db server
db.commit()
db.close()
