#db_hourly_stats6.py
#this script aggregates energy statistics from the 10-sec trend table and the 10-minute temperature table in the mysql db
#it populates the 1 hour frame table
#an improvement on version 5, includes try statements

import MySQLdb
import  pywapi
import string
import ConfigParser
import time

#Get outside temp from weather.com or, even better, yahoo
#Yahoo crapped out on 4/15/16 so I switched back to weather.com
#Ultimately, this was entirely commented out.  Temp data was taken from temperature table
#which is populated by the dark sky weather API
#try:
    #weather_com_result = pywapi.get_weather_from_weather_com('02536')
    #C = weather_com_result["current_conditions"]["temperature"]
    ##yahoo_result = pywapi.get_weather_from_yahoo('02536')
    ##C = yahoo_result["condition"]["temp"]
    #F = float(C)*(9.0/5.0) + 32
#except:
    #F = 50.0
###############################################################
config = ConfigParser.RawConfigParser()
config.read('/home/pi/gfiske.cfg')
db_user = config.get('section1', 'db_user')
db_passwd = config.get('section1', 'db_passwd')
db_user = db_user.decode('base64','strict')
db_passwd = db_passwd.decode('base64','strict')
###############################################################
try:

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
    
    # collect temperature info from temperature table, instead of old method above using weather APIs
    myq2 = "select avg(outTemp) from temperature where DATE_SUB(NOW(), Interval 1 hour) < ts1 group by dayofmonth(ts1);"
    cursor = db.cursor()
    cursor.execute(myq2)
    myq2 = cursor.fetchone()
    F = str(round(myq2[0],2))

    # update frame table
    insquery = "insert into frame values (DEFAULT, NOW()," + temp + "," + wh + "," + oldpv + "," + newpv + "," + pv + "," + hvac + "," + F + ");"
    cursor = db.cursor()
    cursor.execute(insquery)
    #disconnect
    db.commit()
    db.close()

except Exception, msg:
<<<<<<< HEAD
    print "Error"
=======
    #print "Error"
>>>>>>> b949f98382e3785e4f7eef9f3d6df1974118369c
    #filename = "/home/pi/db_error_log.txt"
    #f = open(filename,"r+")
    #f.readlines()
    #now = time.localtime(time.time())
    #curtime = time.asctime(now)
    #f.write(curtime + "\n")
    #f.write("db_hourly_stats6 error is : " + str(msg) + "\n")
    #f.write("\n")
    #f.close()
    ##Commented out for now....