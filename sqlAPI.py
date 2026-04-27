import os
import sqlite3


def _mdd_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "mdd.db")


# Get Data
def list_of_processors():
    db_connection = sqlite3.connect(_mdd_db_path())
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  id, url FROM dashboards
                         ''')
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row

def get_farm_info_for_processor(processor_id):
    db_connection = sqlite3.connect(_mdd_db_path())
    cursor = db_connection.cursor()
    qry = cursor.execute('''SELECT  farms.farm_name from farms where farms.processor_id = {}
                         '''.format(processor_id))
    row =[]
    for data in qry.fetchall():
        row.append(data)
    db_connection.close()
    return row


def get_all_farms_with_processors():
    """Return list of (farm_name, processor_name) for Databricks file routing."""
    db_connection = sqlite3.connect(_mdd_db_path())
    cursor = db_connection.cursor()
    qry = cursor.execute(
        """
        SELECT f.farm_name, d.processor_name
        FROM farms f
        JOIN dashboards d ON f.processor_id = d.id
        """
    )
    row = [tuple(r) for r in qry.fetchall()]
    db_connection.close()
    return row


def list_of_processor_names():
    """All processor folder names (from dashboards), including those with no farms yet."""
    db_connection = sqlite3.connect(_mdd_db_path())
    cursor = db_connection.cursor()
    qry = cursor.execute("SELECT processor_name FROM dashboards ORDER BY processor_name")
    row = [r[0] for r in qry.fetchall()]
    db_connection.close()
    return row


'''test_processors = list_of_processors()
for processor in test_processors:
    print(processor)
    farm_info = get_farm_info_for_processor(processor[0])
    print(farm_info)'''