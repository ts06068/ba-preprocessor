import pymssql
import pandas

server = 'localhost'
user = 'sa'
password = 'Password1!'
db = 'ba'

conn = pymssql.connect(server, user, password, database=db)
cursor = conn.cursor(as_dict=True)

delete_query = 'delete from dbo.papers'
reseed_query = "dbcc checkident('dbo.papers', reseed, 0)"

cursor.execute(delete_query)
conn.commit()
cursor.execute(reseed_query)
conn.commit()

for year in range(2008, 2025):
    df = pandas.read_csv(f'queryResult-{year}.csv', encoding='utf-8')
    df = df.rename(columns= {"coverDate": "pub_date", "publicationName": "journal", "subtype": "type_description"})[['doi', 'title', 'pub_date', 'journal', 'type_description']]
    df = df.fillna('')
    query = "INSERT INTO dbo.papers VALUES (%s, %s, %s, %s, %s)"
    sql_data = tuple(map(tuple, df.values))
    cursor.executemany(query, sql_data)
    conn.commit()

cursor.close()
conn.close()