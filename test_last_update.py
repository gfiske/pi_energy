#!/usr/bin/python

#test_last_update.py
#this script tests the last update to the energy db
#if it is too long, there's a problem, populate error table

#written on 3/26/14

import MySQLdb
import ConfigParser
import time

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
#do query on trend table
myq = "select timestampdiff(minute, now(), ts1) from trend order by ts1 desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
myq = cursor.fetchone()
diff = myq[0]
db.commit()

# if the time delay is greater than 2 minutes, populate error table
if int(diff) > -11 and int(diff) < -2:
    #it is an error
    myq2 = "insert into error values (DEFAULT, NOW(), 1);"
    cursor.execute(myq2)
    db.commit()
# if the time delay is greater than 30 minutes, restart logging script
elif int(diff) < -30:
    os.system("python /home/pi/pi_energy/db_update_currentcost6.py &")
    myq2 = "insert into error values (DEFAULT, NOW(), 1);"
    cursor.execute(myq2)
    db.commit()
    filename = "/home/pi/db_error_log.txt"
    f = open(filename,"r+")
    f.readlines()
    now = time.localtime(time.time())
    curtime = time.asctime(now)
    f.write("\n")
    f.write(curtime + "\n")
    f.write("Error greater than 30 minutes, restarted db_update_currentcost6" + "\n")
    f.write("\n")
    f.close()
# if no time delay, do nothing, note no error to db
else:
    myq2 = "insert into error values (DEFAULT, NOW(), 0);"
    cursor.execute(myq2)
    db.commit()
db.close()


