import os
import sqlite3


def db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "tillamook.db")


# Get Data
def list_of_farms():
    db_connection = sqlite3.connect(db_path())
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  farm_name, farm_username, farm_password FROM farms
                         ''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

'''farms = list_of_farms()
for farm in farms:
    print(farm)