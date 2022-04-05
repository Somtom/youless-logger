import pandas as pd
import sqlite3 as sql
from datetime import datetime
from config import DB_PATH

def load_data():    
    with sql.connect(DB_PATH) as con:
        df_m = pd.read_sql(
            '''
            SELECT 
                *,
                strftime('%H', time) AS hour,
                strftime('%M', time) AS minute,
                strftime('%Y-%m-%d', time) AS date
            FROM youless_minute
            ''',
            con
        )
        df_m_avg = pd.read_sql(
            '''
            SELECT 
                AVG(energy_consumption) AS avg_energy_consumption,
                strftime('%H', time) AS hour,
                strftime('%M', time) AS minute
            FROM youless_minute
            GROUP BY hour, minute
            ''',
            con
        )
        df_m = pd.merge(
            df_m,
            df_m_avg,
            on=['hour', 'minute']
        )

        df_h = pd.read_sql(
            '''
            SELECT 
                *,
                strftime('%H', time) AS hour,
                strftime('%w', time) AS week_day,
                strftime('%Y-%m-%d', time) AS date
            FROM youless_hour
            ''',
            con
        )
        # We need to fill the current hour with the values from minute
        wh_per_hour = df_m.copy()
        wh_per_hour['time'] = wh_per_hour['date'] + ' ' + wh_per_hour['hour'] + ':00:00'
        wh_per_hour = wh_per_hour.groupby(['time', 'hour']).agg(
            energy_consumption=('energy_consumption', 
            lambda x: round(x.mean()))
        )
        df_h = df_h.set_index(['time', 'hour']).combine_first(wh_per_hour).reset_index()
        df_h['time'] = pd.to_datetime(df_h['time'])

        df_h_avg = pd.read_sql(
            '''
            SELECT 
                AVG(energy_consumption) AS avg_energy_consumption,
                strftime('%H', time) AS hour
            FROM youless_hour
            GROUP BY hour
            ''',
            con
        )
        df_h = pd.merge(
            df_h,
            df_h_avg,
            on='hour'
        )

        df_day = pd.read_sql(
            '''
            SELECT 
                *,
                strftime('%w', time) AS week_day
            FROM youless_day
            ''',
            con
        )
        # We need to fill the current day with the values from the df_h table
        kwh_per_hour = df_h.copy()
        kwh_per_hour['time'] = kwh_per_hour['date'] + ' 00:00:00'
        kwh_per_hour = kwh_per_hour.groupby(['time', 'week_day']).agg(
            energy_consumption=('energy_consumption', 
            lambda x: round(x.sum()/1000, 2))
        )
        df_day = df_day.set_index(['time', 'week_day']).combine_first(kwh_per_hour).reset_index()
        df_day['time'] = pd.to_datetime(df_day['time'])

        df_day_avg_weekday = pd.read_sql(
            '''
            SELECT 
                AVG(energy_consumption) AS avg_energy_consumption_weekday,
                strftime('%w', time) AS week_day
            FROM youless_day
            GROUP BY week_day
            ''',
            con
        )
        df_day = pd.merge(
            df_day,
            df_day_avg_weekday,
            on='week_day'
        )

        df_month = pd.read_sql(
            '''
            SELECT 
                SUM(energy_consumption) AS energy_consumption,
                strftime('%m', time) AS month,
                strftime('%Y', time) AS year
            FROM youless_day
            GROUP BY year, month
            ''',
            con
        )
        df_month['time'] = df_month['year'] + '-' + df_month['month']
        df_month['time'] = df_month['time'].apply(lambda x: datetime.strptime(x, '%Y-%m'))
        
        
        df_h_g = pd.read_sql(
            '''
            SELECT 
                *,
                strftime('%H', time) AS hour,
                strftime('%w', time) AS week_day,
                strftime('%Y-%m-%d', time) AS date
            FROM youless_hour_gas
            ''',
            con
        )
        
        df_h_g_avg = pd.read_sql(
            '''
            SELECT 
                AVG(energy_consumption) AS avg_energy_consumption,
                strftime('%H', time) AS hour
            FROM youless_hour_gas
            GROUP BY hour
            ''',
            con
        )
        df_h_g = pd.merge(
            df_h_g,
            df_h_g_avg,
            on='hour'
        )

        df_day_g = pd.read_sql(
            '''
            SELECT 
                *,
                strftime('%w', time) AS week_day
            FROM youless_day_gas
            ''',
            con
        )
        # We need to fill the current day with the values from the df_h table
        L_per_hour = df_h_g.copy()
        L_per_hour['time'] = L_per_hour['date'] + ' 00:00:00'
        L_per_hour = L_per_hour.groupby(['time', 'week_day']).agg(
            energy_consumption=('energy_consumption', 
            lambda x: round(x.sum()/1000, 2))
        )
        df_day_g = df_day_g.set_index(['time', 'week_day']).combine_first(L_per_hour).reset_index()
        df_day_g['time'] = pd.to_datetime(df_day_g['time'])

        df_day_g_avg_weekday = pd.read_sql(
            '''
            SELECT 
                AVG(energy_consumption) AS avg_energy_consumption_weekday,
                strftime('%w', time) AS week_day
            FROM youless_day_gas
            GROUP BY week_day
            ''',
            con
        )
        df_day_g = pd.merge(
            df_day_g,
            df_day_g_avg_weekday,
            on='week_day'
        )

        df_month_g = pd.read_sql(
            '''
            SELECT 
                SUM(energy_consumption) AS energy_consumption,
                strftime('%m', time) AS month,
                strftime('%Y', time) AS year
            FROM youless_day_gas
            GROUP BY year, month
            ''',
            con
        )
        df_month_g['time'] = df_month_g['year'] + '-' + df_month_g['month']
        df_month_g['time'] = df_month_g['time'].apply(lambda x: datetime.strptime(x, '%Y-%m'))
        
    return {'minute': df_m, 'hour': df_h, 'hour_avg': df_h_avg, 'day': df_day, 'month': df_month, 'hourGas': df_h_g, 'hourGas_avg': df_h_g_avg, 'dayGas': df_day_g, 'monthGas': df_month_g}



