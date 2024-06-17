import pymssql
import pandas
import sys
from tqdm import tqdm
from pmidcite.icite.downloader import get_downloader
import datetime
from dateutil import parser

server = 'localhost'
user = 'sa'
password = 'Password1!'
db = 'ba'
dnldr = get_downloader(details_cites_refs="citations")

conn = pymssql.connect(server, user, password, database=db)
cursor = conn.cursor(as_dict=True)

from_idx = int(sys.argv[1])
to_idx = int(sys.argv[2])

query = f"""
select * from dbo.paper order by citedby_count desc
"""
cursor.execute(query)
rows = cursor.fetchall()

insert_papers_query = 'insert into dbo.paper output Inserted.paper_id values (%s, %s, %s, %s, %s, %s, %s)'
insert_citations_query = 'insert into dbo.citation output Inserted.citing_id values (%s, %s, %s)'
insert_relationships_query = 'insert into dbo.relationship values (%s, %s, %s)'
select_citations_query = 'select citing_id from dbo.citation where doi = (%s)'

rows = rows[from_idx:to_idx+1]

for row in tqdm(rows):
    try:
        source_paper_id = int(row['paper_id'])
        source_pmid = int(row['pmid'])
        source_doi = str(row['doi'])

        if source_pmid == 0:
            continue

        if source_doi == '':
            continue

        now = datetime.datetime.now()

        paper = dnldr.get_paper(source_pmid)
        cited_by = paper.cited_by

        print(f'{source_pmid} is cited by {len(cited_by)} papers')

        if len(cited_by) > 0:
            # search if source is already registered
            cursor.execute(select_citations_query, (source_doi))
            result = cursor.fetchone()
            conn.commit()

            if result is not None:
                source_citing_id = result['citing_id']
            else:
                # append source to citations table
                cursor.execute(insert_citations_query, (source_doi, source_pmid, now))
                source_citing_id = cursor.fetchone()['citing_id']
                conn.commit()

            for cite in cited_by:
                dct = dict(cite.dct)
                target_doi = str(dct['doi'])
                target_title = str(dct['title'])
                target_pub_date = parser.parse(str(dct['year']))
                target_journal = str(dct['journal'])
                target_type_description = 'n/a'
                target_pmid = int(dct['pmid'])
                target_citedby_count = int(dct['num_cites_all'])

                if target_doi == '':
                    continue

                # search if target is already registered
                cursor.execute(select_citations_query, (target_doi))
                result = cursor.fetchone()
                conn.commit()

                if result is not None:
                    target_citing_id = result['citing_id']
                else:
                    # append target to citations table
                    cursor.execute(insert_citations_query, (target_doi, target_pmid, now))
                    target_citing_id = cursor.fetchone()['citing_id']
                    conn.commit()

                # append target to papers table
                """
                cursor.execute(insert_papers_query, (target_doi, target_pmid, target_title, target_pub_date, target_journal, target_type_description, target_citedby_count))
                target_paper_id = cursor.fetchone()['paper_id']
                conn.commit()
                """

                # append both mappings to relationships table
                cursor.execute(insert_relationships_query, (source_citing_id, target_citing_id, 'citing'))
                conn.commit()
                cursor.execute(insert_relationships_query, (target_citing_id, source_citing_id, 'cited'))
                conn.commit()
    except Exception as e:
        print(e)
        continue

cursor.close()
conn.close()