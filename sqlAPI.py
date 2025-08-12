import sqlite3

def getEnterpriseAccounts(*args, **kwargs):
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  id, name, url FROM enterprise_customers''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

def addFarm(enterpriseID, MDDid, farmName):
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO farms (name, mddid, enterpriseid) VALUES ("{}", "{}", "{}")'''.format(farmName.replace('"',""), MDDid, enterpriseID))
    db_connection.commit()

def addFarmData(farmName, enterpriseID):
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO farm_data (farm_name, enterprise_id) VALUES ("{}", "{}", "{}")'''.format(farmName, enterpriseID, sourceData))
    db_connection.commit()

def clearFarms():
    db_connection = sqlite3.connect('enterprise.db') 
    cursor = db_connection.cursor()
    cursor.execute('''DELETE FROM farms''')
    db_connection.commit()

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