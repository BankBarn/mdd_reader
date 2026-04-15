import sqlite3

# Get Data
def list_of_processors():
    db_connection = sqlite3.connect('mdd.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  id, url FROM dashboards
                         ''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

def get_farm_info_for_processor(processor_id):
    db_connection = sqlite3.connect('mdd.db') 
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  farms.farm_name from farms where farms.processor_id = {}
                         '''.format(processor_id))
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

'''test_processors = list_of_processors()
for processor in test_processors:
    print(processor)
    farm_info = get_farm_info_for_processor(processor[0])
    print(farm_info)'''