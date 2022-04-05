import requests
import logging
import sqlite3 as sql
import pandas as pd
from datetime import datetime, timedelta
from config import DB_PATH

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('youless')


GRANULARITY_MAP = {
    'minute': {'ener': 'V?', 'param': 'h', 'reports': 20, 'table': 'youless_minute'},
    'hour': {'ener': 'V?', 'param': 'd', 'reports': 70, 'table': 'youless_hour'},
    'day': {'ener': 'V?', 'param': 'm', 'reports': 12, 'table': 'youless_day'},
    'hourGas': {'ener': 'W?', 'param': 'd', 'reports': 70, 'table': 'youless_hour_gas'},
    'dayGas': {'ener': 'W?', 'param': 'm', 'reports': 12, 'table': 'youless_day_gas'}
}

def convert_data(data):
    res = []
    time_format = '%Y-%m-%dT%H:%M:%S'
    timestamp = datetime.strptime(data['tm'], time_format) 
    for val in data['val']:
        if val and val != '*':
            res.append({
                'time': timestamp,
                'energy_consumption' : float(val.replace(',', '.')),
                'unit': data['un']
            })
        timestamp += timedelta(seconds=data['dt'])
        
    return res


def fetch_data(granularity):
    ener = GRANULARITY_MAP[granularity]['ener']
    param = GRANULARITY_MAP[granularity]['param']
    reports = GRANULARITY_MAP[granularity]['reports']

    logger.info('Fetching new data. Granularity: {}, reports: {}'.format(granularity, reports))
    res = []
    for i in range(reports):
        data = requests.get('http://youless/{ener}{param}={page}&f=j'.format(
            ener=ener,
            param=param,
            page=i+1
        )).json()
        res += convert_data(data)
    logger.info('Received {} entries'.format(len(res)))
    return pd.DataFrame(res)


def table_exists(table, cur):
    query = '''
    SELECT name 
    FROM sqlite_master 
    WHERE 
        type='table'
        AND name='{table_name}'; 
    '''
    listOfTables = cur.execute(query.format(table_name=table)).fetchall()
    return len(listOfTables) > 0


def store_data(df, con):
    cur = con.cursor()
    table = GRANULARITY_MAP[granularity]['table']

    if not table_exists(table, cur): 
        logger.warning('Table {} does not exist. Creating...'.format(table))
        # Just upload all data and create the table
        df.to_sql(table, con, index=False)
        value_count = len(df)
    else:
        # Store to temporary db
        df.to_sql('tmp', con, if_exists='replace', index=False)

        # Update existing data
        query = '''
        UPDATE {table_name} AS old
        SET energy_consumption = (
            SELECT energy_consumption
            FROM tmp
            WHERE time = old.time
            LIMIT 1
        ) 
        WHERE EXISTS (
            SELECT energy_consumption
            FROM tmp
            WHERE time = old.time
        )
        '''
        cur.execute(query.format(table_name=table))
        con.commit()
        logger.info('Updated {} old values'.format(cur.rowcount))

        # Store new data
        query = '''
        INSERT INTO {table_name} (time, energy_consumption, unit)
        SELECT time, energy_consumption, unit
        FROM tmp AS new
        WHERE NOT EXISTS (
            SELECT 1 FROM {table_name} old 
            WHERE old.time = new.time
        );
        '''
        cur = con.cursor()
        cur.execute(query.format(table_name=table))
        con.commit()
        value_count = cur.rowcount
    
    logger.info('Uploaded {} new values'.format(value_count))



if __name__ == '__main__':
    granularity = 'minute'
    with sql.connect(DB_PATH) as con:
        granularity = 'minute'
        df = fetch_data(granularity)
        store_data(df, con)

        granularity = 'hour'
        df = fetch_data(granularity)
        store_data(df, con)

        granularity = 'day'
        df = fetch_data(granularity)
        store_data(df, con)
        
        granularity = 'hourGas'
        df = fetch_data(granularity)
        store_data(df, con)

        granularity = 'dayGas'
        df = fetch_data(granularity)
        store_data(df, con)
