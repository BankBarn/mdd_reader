import sqlite3

#FOLLOWER ACCOUNT INFORMATION
def getFollowerCounts(*args, **kwargs):
    timeFilter = kwargs.get('t',"*")
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''Select linkedin.date, linkedin.follower_count, facebook.follower_count, milestone.milestone, linkedin.id, facebook.id, milestone.id
                            from linkedin
                            join facebook on linkedin.date = facebook.date
                            LEFT OUTER join milestone on linkedin.date = milestone.date
                            order by linkedin.date desc''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row
def getFollowerCountsChart(*args, **kwargs):
    timeFilter = kwargs.get('t',"*")
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''Select linkedin.date, linkedin.follower_count, facebook.follower_count, milestone.milestone, linkedin.id, facebook.id, milestone.id
                            from linkedin
                            join facebook on linkedin.date = facebook.date
                            LEFT OUTER join milestone on linkedin.date = milestone.date
                            order by linkedin.date''')
    date = []
    facebook = [] 
    linkedin = []
    for data in qry.fetchall():
        date.append(data[0])
        facebook.append(data[2])
        linkedin.append(data[1])
    db_connection.close()
    return date,facebook, linkedin

#MILESTONE INFORMATION
def addMilestone(dates, milestone,*args, **kwargs):
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO milestone (date, milestone) VALUES ("{}", "{}")'''.format(dates, milestone))
    db_connection.commit()
def deleteMilestone(milestoneID):
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    print(milestoneID)
    cursor.execute('''DELETE FROM milestone WHERE id={}'''.format(milestoneID))
    db_connection.commit()

#LINKEDIN INFORMATION
def updateLinkedin(linkedinID, count):
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    cursor.execute('''UPDATE linkedin SET follower_count={} where id={}'''.format(count, linkedinID))
    db_connection.commit()

#FACEBOOK INFORMATION
def updateFacebook(facebookid, count):
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    cursor.execute('''UPDATE facebook SET follower_count={} where id={}'''.format(int(count), facebookid))
    db_connection.commit()

#GENERAL APIs
def customSelect(table, *args, **kwargs):
    #optional s for select
    #optional w for where
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    select = kwargs.get('s',"*")
    where = kwargs.get('w',"")
    qry = cursor.execute('''SELECT {} FROM {} {}'''.format(select,table,where))
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row
def customUpdate(table,set, *args, **kwargs):
    #optional w for where
    db_connection = sqlite3.connect('followers.db') 
    cursor = db_connection.cursor()
    where = kwargs.get('w',"WHERE 1=1")
    qry = cursor.execute('''UPDATE {} SET {} {}'''.format(table, set, where))
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

#print(getFollowerCountsChart())