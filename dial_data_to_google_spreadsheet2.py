#dial_data_to_google_spreadsheet2.py
#Greg Fiske
#This script writes the data from the pi mysql db to a google spreadsheet
#it is minute level data written for google spreadsheet called home_dials
#Jan 2014
#it's an update to version 1.  This version uses the gspread module

# import the modules
try:
    import MySQLdb
    import gspread
    import base64
    import ConfigParser
except:
    print "Cannot import one or more module"
    sys.exit(1)

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
#try to get the data and set it to local variables
try:

    #get info from the building database
    db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    #do query
    myq = "select netwatts, totalpv, hvac from trend order by ts1 desc limit 1;"
    cursor.execute(myq)
    # Fetch a single row using fetchone() method.
    myq = cursor.fetchone()
    #parse results of query
    net = str(round(myq[0],2))
    pv = str(round(myq[1],2))
    hvac = str(round(myq[2],2))
    db.commit()
    db.close()

except:
    print "query failed"


#enter the data into the google spreadsheet
g = gspread.login(email, password)
worksheet = g.open('home_dials').get_worksheet(0)
worksheet.update_cell(2,1,net)
worksheet.update_cell(2,2,pv)
worksheet.update_cell(2,3,hvac)
print "script finished"
