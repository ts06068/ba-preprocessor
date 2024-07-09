import pybliometrics.scopus
from pybliometrics.scopus import AbstractRetrieval
import pandas as pd
import pymssql
from tqdm import tqdm
import sys
from pymed import PubMed
from dateutil import parser
import json
import os

#pubmed = PubMed(tool="MyTool", email="my@email.address")

server = "localhost"
user = "sa"
password = "Password1!"
db = "ba"

pybliometrics.scopus.init()
conn = pymssql.connect(server, user, password, database=db)
cursor = conn.cursor(as_dict=True)

"""
with open('result2.csv', encoding='utf-8') as rf:
    pmid_list = rf.read().split('\n')
    print(len(pmid_list))
    rf.close()

order = 0
for i in range(0, len(pmid_list), 10000):
    pmid_list_chunk = pmid_list[i:i+10000]
    with open(f'wrong_pub_date_pmids_{order}.csv', 'w', encoding='utf-8') as f:
        pmid_str = '\n'.join(map(str, pmid_list_chunk))
        f.write(pmid_str)
        order += 1
"""

#files = [filename for filename in os.listdir('./') if filename.startswith(f'csv-')]

"""
for f in files:
    try:
        df = pd.read_csv(f, sep=',')
        for i, r in tqdm(df.iterrows(), total=df.shape[0]):
            pmid = r['PMID']
            type_description = 'n/a-'
            pub_date = parser.parse(r['Create Date'])

            update_paper_query = 'update paper set type_description = (%s), pub_date = (%s) where pmid = (%s)'
            cursor.execute(update_paper_query, (type_description, pub_date, pmid))
            conn.commit()
    except Exception as e:
        print(e)
        continue
"""

df = pd.read_csv('ScopusQueryResult-2008-2024.csv', sep=',', low_memory=False)
df = df.iloc[:, 1:]
df = df.fillna(0)
print(df)

update_paper_query = """update paper set 
afid = (%s),
affilname = (%s),
affiliation_city = (%s),
affiliation_country = (%s),
author_count = (%s),
author_names = (%s),
author_ids = (%s),
author_afids = (%s),
description = (%s),
pub_year = (%s),
pii = (%s),
openaccess = (%s),
freetoread = (%s),
freetoreadLabel = (%s),
fund_acr  = (%s),
fund_no = (%s),
fund_sponsor = (%s),
eIssn = (%s),
aggregationType = (%s),
volume = (%s),
issueIdentifier = (%s),
article_number = (%s),
pageRange = (%s)

where pmid = (%s)
"""

for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    try:
        pmid = int(row['pubmed_id'])

        afid = row['afid']
        affilname = row['affilname']
        affiliation_city = row['affiliation_city']
        affiliation_country = row['affiliation_country']
        author_count = row['author_count']
        author_names = row['author_names']
        author_ids = row['author_ids']
        author_afids = row['author_afids']
        description = row['description']
        pub_year = row['pub_year']
        pii = row['pii']
        openaccess = row['openaccess']
        freetoread = row['freetoread']
        freetoreadLabel = row['freetoreadLabel']
        fund_acr = row['fund_acr']
        fund_no = row['fund_no']
        fund_sponsor = row['fund_sponsor']
        eIssn = row['eIssn']
        aggregationType = row['aggregationType']
        volume = row['volume']
        issueIdentifier = row['issueIdentifier']
        article_number = row['article_number']
        pageRange = row['pageRange']

        v = ( \
            afid, affilname, affiliation_city, affiliation_country,
            author_count, author_names, author_ids, author_afids,
            description, pub_year, pii, openaccess, freetoread,
            freetoreadLabel, fund_acr, fund_no, fund_sponsor, eIssn,
            aggregationType, volume, issueIdentifier,
            article_number, pageRange, pmid)

        cursor.execute(update_paper_query, v)
        conn.commit()
    except Exception as e:
        print(e)
        
