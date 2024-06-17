import pymssql
import pandas
import sys

server = 'localhost'
user = 'sa'
password = 'Password1!'
db = 'ba'

conn = pymssql.connect(server, user, password, database=db)
cursor = conn.cursor(as_dict=True)

from_idx = int(sys.argv[1])
to_idx = int(sys.argv[2])

query = f"""
select * from dbo.papers where paper_id between {from_idx} and {to_idx}
"""
cursor.execute(query)
row = cursor.fetchall()

print(row)

cursor.close()
conn.close()