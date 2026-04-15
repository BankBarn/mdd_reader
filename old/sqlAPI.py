import sqlite3


# Insert Data
def addFarm(enterpriseID, MDDid, farmName):
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO farms (name, mddid, enterpriseid) VALUES ("{}", "{}", "{}")'''.format(farmName.replace('"',""), MDDid, enterpriseID))
    db_connection.commit()

def addFarmData():
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO farm_data (farm_name, enterprise_id) VALUES ("{}", "{}", "{}")'''.format(farmName, enterpriseID, sourceData))
    db_connection.commit()


# Delete Data
def clearFarms():
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    cursor.execute('''DELETE FROM farms''')
    db_connection.commit()


# Get Data
def getEnterpriseImpersonationAccountInfo():
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  enterprise_customers.name, enterprise_user.user_url, enterprise_user.enterprise_id FROM enterprise_user
                         join enterprise_customers on enterprise_customers.id = enterprise_user.enterprise_id
                         ''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

def getFarmsAndEnterprise():
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  enterprise_customers.name, farms.name, farms.mddid FROM farms
                         join enterprise_customers on enterprise_customers.id = farms.enterpriseid
                         ''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row


def getFarmsForDropdowns(enterpriseID):
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  name FROM farms WHERE farms.enterpriseid={}  ORDER BY name ASC'''.format(enterpriseID))
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

def getEnterpriseAccounts(*args, **kwargs):
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  id, name, url FROM enterprise_customers''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row