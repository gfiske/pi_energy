#db_daily_stats5.py
#this script aggregates statistics from the frame hourly table in the mysql db
#and adds the values to the frame2 table (which is an daily table)

#edited on 9/27/13 to include HVAC data
#edited on 10/22/13 to include mean outdoor temperature

import MySQLdb
import gdata.spreadsheet.service
import base64

#################################
#connect to db
db = MySQLdb.connect("127.0.0.1", "root", 'cXdlcnR5MTYqNQ==\n'.decode('base64'), "energy")

#################################
#do query on frame table
myq = "select date(ts1) ,sum(watthours) / 1000 as 'net', sum(oldpv)/1000 as oldpv, sum(newpv)/1000 as enphase,sum(totalpv) / 1000 as 'total_pv',sum(hvac) / 1000 as 'total_hvac', avg(outtemp) as meanouttemp from frame group by date(ts1) desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
# Fetch a single row using fetchone() method.
myq = cursor.fetchone()

#parse results of query
ts = str(myq[0])
net = str(round(myq[1],2))
oldpv = str(round(myq[2],2))
enphase = str(round(myq[3],2))
totalpv = str(round(myq[4],2))
hvac = str(round(myq[5],2))
meanouttemp = str(round(myq[6],2))
#################################
#update frame table
myquery = "insert into frame2 values (DEFAULT, NOW()," + net + "," + oldpv + "," + enphase + "," + totalpv + "," + hvac + "," + meanouttemp + ");"
cursor = db.cursor()
cursor.execute(myquery)
#disconnect from db server
db.commit()
db.close()


#now send daily info also to google spreadsheet titled daily_energy_from_pi
###############################################################
email = 'amFtZXMuZGVub24uZW5lcmd5QGdtYWlsLmNvbQ=='.decode('base64')
password = 'dGhpc2lzZm9yZW5lcmd5'.decode('base64')
spreadsheet_key = '0Aj5_4a6W2d6JdC1sMU9jZjc1bE9ORU8yTWFKdERUSmc'
worksheet_id = 'od6'

myspreadsheetclient = gdata.spreadsheet.service.SpreadsheetsService()
myspreadsheetclient.email = email
myspreadsheetclient.password = password
myspreadsheetclient.source = 'Example Spreadsheet Writing Application'
myspreadsheetclient.ProgrammaticLogin()
###############################################################
# Prepare the dictionary to write
dict = {}
dict['ts1'] = ts
dict['net'] = net
dict['oldpv'] = oldpv
dict['newpv'] = enphase
dict['totalpv'] = totalpv
dict['hvac'] = hvac
dict['meanouttemp'] = meanouttemp
#print dict

#enter the data into the google spreadsheet
entry = myspreadsheetclient.InsertRow(dict, spreadsheet_key, worksheet_id)
if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
    print "Insert row succeeded."
else:
    print "Insert row failed."