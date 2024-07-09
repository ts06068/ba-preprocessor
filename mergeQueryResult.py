import pandas as pd
from tqdm import tqdm
import re
import datetime
from dateutil.parser import parse

df = pd.read_csv(f"queryResult-{2008}.csv", encoding="utf-8")

for year in range(2009, 2025):
    df2 = pd.read_csv(f"queryResult-{year}.csv", encoding="utf-8")
    df = pd.concat([df, df2], axis=0, ignore_index=True)

df['category'] = ''
df['categoryDescription'] = ''
df['pub_year'] = ''
df = df.iloc[:, 1:]
#df = df[df['subtype'] == 'ar']
#df = df[df['publicationName'].isin(['Circulation', 'Journal of the American College of Cardiology', 'European Heart Journal'])]

pattern = re.compile("([A-Z][0-9]+)+")

for index, row in tqdm(df.iterrows(), total=df.shape[0]):

    title = str.lower(row['title'])
    subtype = row['subtype']
    subtype_description = row['subtypeDescription']
    abstract = str(row['description'])
    date = str(row['coverDate'])

    if subtype == 'ar':
        if 'guideline' in title or 'report' in title or 'summary' in title:
            subtype = 'ar-'
            subtype_description = 'Non-Article'

        if abstract == 'nan':
            subtype = 'ar-'
            subtype_description = 'Non-Article'

    df.at[index, 'category'] = subtype
    df.at[index, 'categoryDescription'] = subtype_description
    df.at[index, 'pub_year'] = date.split('-')[0]

print(df[df['category'] == 'ar-'])

df.to_csv(
    "ScopusQueryResult-full-2008-2024.csv",
    sep=','
)

df.drop(labels= ['pubmed_id', 'authkeywords', 'pii', 'creator', 'affilname', 'afid', 'author_ids', 'issueIdentifier', 'volume', 'pageRange', 'article_number', 'eid', 'affiliation_city', 'affiliation_country', 'coverDisplayDate', 'author_names', 'author_count', 'author_afids', 'issn', 'eIssn','source_id', 'aggregationType', 'openaccess', 'freetoread', 'freetoreadLabel', 'fund_acr', 'fund_no', 'fund_sponsor'], axis=1, inplace=True)

df.to_csv(
    "ScopusQueryResult-full-2008-2024-clean.csv",
    sep=','
)