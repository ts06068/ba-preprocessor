import json
import pymssql
from tqdm import tqdm
from dateutil import parser
import sys
import os
import datetime
from dateutil import parser

"""
journal_id (in altmetric)
JAC: 4f6fa4f63cf058f610002f57
EHJ: 4f6fa6173cf058f610007331
CIR: 4f6fa5e63cf058f6100057f2
"""

server = "localhost"
user = "sa"
password = "Password1!"
db = "ba"

conn = pymssql.connect(server, user, password, database=db)
cursor = conn.cursor(as_dict=True)

journal_id = sys.argv[1]

file_path = f'altmetricQueryResult/{journal_id}'
files = [filename for filename in os.listdir(file_path)]

for filename in tqdm(files):
    with open(f'{file_path}/{filename}', 'r', encoding='utf-8') as f:
        r = json.loads(f.read())
        mention_sources = list(r['data'])
        references = list(r['included'])
        
        for mention_source in mention_sources:
            post_id, post_type, post_external_id, post_source, post_date, post_title, post_url, post_summary, profile_id, profile_type = (None, None, None, None, None, None, None, None, None, None)
            mention_source_keys = dict.keys(mention_source)
            if 'id' in mention_source_keys:
                post_id = mention_source['id']
            if 'type' in mention_source_keys:
                post_type = mention_source['type']
            if 'attributes' in mention_source_keys:
                attributes = dict(mention_source['attributes'])
            if 'relationships' in mention_source_keys:
                relationships = dict(mention_source['relationships'])
            
            attributes_keys = attributes.keys()
            relationships_keys = relationships.keys()

            if 'external-id' in attributes_keys:
                post_external_id = attributes['external-id']
            if 'post-type' in attributes_keys:
                post_source = attributes['post-type']
            if 'posted-on' in attributes_keys:
                post_date = attributes['posted-on']
            if 'title' in attributes_keys:
                post_title = attributes['title']
            if 'url' in attributes_keys:
                post_url = attributes['url']
            if 'summary' in attributes_keys:
                post_summary = attributes['summary']
            
            # get profile_id
            if 'author' in relationships_keys:
                author = dict(relationships['author'])
                if 'data' in author.keys():
                    author_data = dict(author['data'])
                    if 'id' in author_data.keys():
                        profile_id = str(author_data['id'])
            
                        # get profile_type
                        if profile_id is not None:
                            profile_search_result = dict(next(item for item in references if str(item['id'])==profile_id))
                            if 'attributes' in profile_search_result.keys():
                                if 'profile-type' in dict.keys(profile_search_result['attributes']):
                                    profile_type = profile_search_result['attributes']['profile-type']
            
            
            # get list of mentioning article ids
            if 'research-outputs' in relationships_keys:
                research_outputs = list(relationships['research-outputs'])

            mention_targets = []

            # for each original article, find its pubmed-id
            for research_output in research_outputs:
                if 'data' in dict.keys(research_output):
                    if 'id' in dict.keys(research_output['data']):
                        research_output_id = research_output['data']['id']
                if research_output_id is not None:
                    research_output_search_result = dict(next(item for item in references if item['id']==research_output_id))
                    research_output_attributes = dict(research_output_search_result['attributes'])
                    if 'identifiers' in research_output_attributes.keys():
                        research_output_search_result_identifier = research_output_attributes['identifiers']
                    if 'pubmed-ids' in dict.keys(research_output_search_result_identifier):
                        research_output_pmid = list(research_output_search_result_identifier['pubmed-ids'])[0]
                        if 'altmetric-score' in research_output_attributes.keys():
                            research_output_altmetric_score = research_output_attributes['altmetric-score']

                            mention_targets.append({'pmid': research_output_pmid, 'altmetric-score': research_output_altmetric_score})

            insert_mention_query = "insert into mention values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            select_mention_query = "select * from mention where post_id = (%s)"
            insert_mention_relationship_query = "insert into mention_relationship values (%s, %s, %s, %s)"
            update_paper_query = "update paper set altmetric_score = (%s) where pmid = (%s)"
            select_paper_query = "select paper_id from paper where pmid = (%s)"

            """
            insert into mention table
            """

            if post_date is None:
                post_date = '1900/1/1'

            post_date = parser.parse(post_date)
            cursor.execute(insert_mention_query, (post_id, post_type, post_external_id, post_source, post_date, post_title, post_url, post_summary, profile_id, profile_type))
            conn.commit()

            """
            for each mention target, obtain its paper_id from paper table and
            insert into mention_relationship table
            """

            for mention_target in mention_targets:
                pmid = mention_target['pmid']
                altmetric_score = mention_target['altmetric-score']
                cursor.execute(update_paper_query, (altmetric_score, pmid))
                conn.commit()

                cursor.execute(select_paper_query, (pmid))
                result = cursor.fetchone()
                access_date = datetime.datetime.now()

                if result is None:
                    cursor.execute(insert_mention_relationship_query, (post_id, 0, access_date, pmid))
                    conn.commit()
                else:
                    target_paper_id = result['paper_id']
                    cursor.execute(insert_mention_relationship_query, (post_id, target_paper_id, access_date, pmid))
                    conn.commit()
        f.close()