import pymssql
import pandas

server = 'localhost'
user = 'sa'
password = 'Password1!'
db = 'ba'

conn = pymssql.connect(server, user, password, database=db)
cursor = conn.cursor(as_dict=True)

delete_query = 'delete from dbo.paper'
reseed_query = "dbcc checkident('dbo.paper', reseed, 0)"

cursor.execute(delete_query)
conn.commit()
cursor.execute(reseed_query)
conn.commit()

for year in range(2008, 2025):
    try:
        df = pandas.read_csv(f'queryResult-{year}.csv', encoding='utf-8')
        df = df.rename(columns= {"pubmed_id": "pmid", "coverDate": "pub_date", "publicationName": "journal", "subtype": "type_description"})[['doi', 'pmid', 'title', 'pub_date', 'journal', 'type_description', 'citedby_count']]
        df = df.fillna('')
        query = "INSERT INTO dbo.paper VALUES (%s, %s, %s, %s, %s, %s, %s)"
        sql_data = tuple(map(tuple, df.values))
        cursor.executemany(query, sql_data)
        conn.commit()
    except Exception as e:
        print(e)
        continue

cursor.close()
conn.close()


"""
DELETE T
FROM
(
SELECT *
, DupRank = ROW_NUMBER() OVER (
              PARTITION BY doi
              ORDER BY (SELECT NULL)
            )
FROM dbo.paper
) AS T
WHERE DupRank > 1
"""