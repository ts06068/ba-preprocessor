import hashlib
import hmac
import requests
import sys
import json
import datetime

"""
https://www.altmetric.com/explorer/api/research_outputs/mentions
?digest=d805d30270eec37c641a2eca81f04652498e0cad
&filter[journal_id]=4f6fa4f63cf058f610002f57
&filter[published_after]=2008-01-01
&filter[published_before]=2024-07-02
&page[number]=1
&page[size]=1
&key=99a6796c5e2f4bb48dce7c9059b9e41a
"""

"""
journal_id (in altmetric)
JAC: 4f6fa4f63cf058f610002f57
EHJ: 4f6fa6173cf058f610007331
CIR: 4f6fa5e63cf058f6100057f2
"""

"""
https://www.altmetric.com/explorer/api/research_outputs/mentions?digest=9764c8429e2d6d51a08c5d5276b832b02412798e&filter[doi_prefix]=10.1016&filter[published_after]=2024-07-01&filter[published_before]=2024-08-01&filter[title]=Transcatheter,Edge-to-Edge,Repair,for,Treatment,of,Tricuspid,Regurgitation&page[number]=1&page[size]=1&key=99a6796c5e2f4bb48dce7c9059b9e41a
"""

journal_id = sys.argv[1]
starting_page = int(sys.argv[2])

key = b'e10b05dc9c2946ac8ba161742f1e2ccd'
message = f'journal_id|{journal_id}|published_after|2018-01-01|published_before|2024-07-02|type|article'
digester = hmac.new(key, str.encode(message), hashlib.sha1)
digest = digester.hexdigest()

url = f"https://www.altmetric.com/explorer/api/research_outputs/mentions?digest={digest}&filter[journal_id]={journal_id}&filter[published_after]=2018-01-01&filter[published_before]=2024-07-02&filter[type]=article&page[number]={starting_page}&page[size]=100&key=99a6796c5e2f4bb48dce7c9059b9e41a"

"""
original_doc = fetched json result (approx. 500000 entries = 5000 pages)
"""

original_doc = requests.get(url).json()
meta = original_doc['meta']
total_results = meta['response']['total-results']
total_pages = meta['response']['total-pages']

print(total_pages)

"""
while True:
    links = original_doc['links']
    if links' key does not contain 'next': break
    save current doc as json
    go to next link, fetch json and assign it to original_doc
"""

while True:
    try:
        meta = original_doc['meta']
        page = meta['query']['page']['number']
        print(f'current page: {page} / {total_pages}, now: {datetime.datetime.now()}')
        links = dict(original_doc['links'])
        if not 'next' in links.keys():
            break
        with open(f'altmetricQueryResult/{journal_id}/{page}.json', 'w') as f:
            json.dump(original_doc, f, ensure_ascii=True, indent=4)
        next_link = links['next']
        original_doc = requests.get(next_link).json()
    except:
        print("connection failed. Retrying...")
        original_doc = requests.get(next_link).json()
        continue