# still in progress. for now:
#
# 1. SQL connection (sqlite3)
# 2. .csv 'COVID-19 EFFECTS ON TRADE' database download from stats.govt.nz (requests)
# 3. csv to SQL (pandas)
# 4. func. check columns titles (called to name table columns)
# 5. func. print all rows
# 6. Consults:  6.1. Check traded commodities from New Zealand, in 2021;
#               6.2. Check Countries with which 'milk powder, butter, and cheese'
#                    was traded from New Zealand, in 2021, and their Values;
#               6.3. Check exported Commodities from New Zealand to China and their Values, in 2021.
#                   6.3.1. Set percentages chart of types of commodities exported to China, in 2021
#               [...]
# [...]

import sqlite3 as sq
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

warnings.filterwarnings('ignore')

conn = sq.connect('covidEffectsOnTrade.db')
cur = conn.cursor()
cur.execute('''
        CREATE TABLE IF NOT EXISTS covidEffectsOnTrade
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Direction TEXT,
        Year INT,
        Date TEXT,
        Weekday TEXT,
        Country TEXT,
        Commodity TEXT,
        Transport_Mode TEXT,
        Measure TEXT,
        Value REAL,
        Cumulative REAL)
        ''')

url = 'https://www.stats.govt.nz/assets/Uploads/Effects-of-COVID-19-on-trade/' \
      'Effects-of-COVID-19-on-trade-At-15-December-2021-provisional/Download-data' \
      'effects-of-covid-19-on-trade-at-15-december-2021-provisional.csv'

r = requests.get(url, allow_redirects=True)
open('effects-of-covid-19-on-trade-at-15-december-2021-provisional.csv', 'wb').write(r.content)

data = pd.read_csv(r'effects-of-covid-19-on-trade-at-15-december-2021-provisional.csv')
df = pd.DataFrame(data)
df.to_sql('covidEffectsOnTrade', conn, if_exists='replace')
cur.execute('''SELECT * FROM covidEffectsOnTrade''')
records = cur.fetchall()


def check_columns():  # check columns titles
    for table in df:
        consult = '''PRAGMA table_info({})'''.format(table)
        result = pd.read_sql_query(consult, conn)
        print('Table Schema:', table)
        print('-'*50, '\n')


def print_all():
    for row in records:
        print(row)


# consult n1
print('Traded Commodities from New Zealand, in 2021:\n')
consult_1_2021 = pd.read_sql_query('''SELECT Commodity, Measure, Value, COUNT(*) from covidEffectsOnTrade 
                                    WHERE Year=2021 GROUP BY Commodity''', conn)
consult_1_2021['Commodity'] = consult_1_2021['Commodity'].values
print(consult_1_2021, "\n")

# consult n2
print('Countries with which "milk powder, butter, and cheese"'
      'was traded from New Zealand, in 2021, and their Values:\n')
consult_2_2022 = pd.read_sql_query('''SELECT Direction, Country, Transport_mode, Measure, Value
                                    from covidEffectsOnTrade WHERE Commodity='Milk powder, 
                                    butter, and cheese' and Year=2021 GROUP BY Country''', conn)
consult_2_2022['Country'] = consult_2_2022['Country'].values
print(consult_2_2022, "\n")

# consult n3
print('Check exported Commodities from New Zealand to China and their Values, in 2021:')
consult_3_2022 = pd.read_sql_query('''SELECT Commodity, Measure, Value from covidEffectsOnTrade
WHERE Country='China' and Year=2021 GROUP BY Commodity''', conn)
consult_3_2022['Commodity'] = consult_3_2022['Commodity'].values
print(consult_3_2022)

#  set percentages chart of types of commodities exported to China, in 2021
sns.set_theme(style='whitegrid')
sns.set_color_codes('pastel')
consult_3_2022['percent'] = (consult_3_2022['Value']/consult_3_2022['Value'].sum())*100
f = plt.subplots(figsize=(14, 9))
commodities_china = sns.barplot(y=consult_3_2022['Commodity'], x=consult_3_2022['percent'], color='b')
plt.ylabel('Commodity')
plt.xlabel('\nValues in $')
plt.title('\n% of commodity exported to China, in 2021\n')
print(plt.show())
