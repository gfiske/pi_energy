#test_last_update.py
#this script tests the last update to the energy db
#if it is too long, there's a problem, so it sends an email to the administrator

#written on 3/26/14

import MySQLdb

#connect to db
db = MySQLdb.connect("127.0.0.1", "root", 'cXdlcnR5MTYqNQ==\n'.decode('base64'), "energy")
#do query on trend table
##myq = "select NOW() as now, (select ts1 from trend order by ts1 desc limit 1) as last;"
myq = "select timestampdiff(minute, now(), ts1) from trend order by ts1 desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
# Fetch a single row using fetchone() method.
myq = cursor.fetchone()
#parse results of query
diff = myq[0]
db.commit()
if int(diff) < -2:
    offtime = 1
    myq2 = "insert into error values (DEFAULT, NOW(), 1);"
    cursor.execute(myq2)
    db.commit()
else:
    myq2 = "insert into error values (DEFAULT, NOW(), 0);"
    cursor.execute(myq2)
    db.commit()
    offtime = 0
db.close()


