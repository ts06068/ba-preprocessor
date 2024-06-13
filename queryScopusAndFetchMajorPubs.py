from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
import pybliometrics
import pybliometrics.scopus
import pandas as pd

pybliometrics.scopus.init()

import sys

year = int(sys.argv[1])

query_str = f'( SRCTITLE ( journal AND of AND the AND american AND college AND of AND cardiology ) OR SRCTITLE ( circulation ) OR SRCTITLE ( european AND heart AND journal ) ) AND ( PUBYEAR = {year} )'
q = pybliometrics.scopus.ScopusSearch(query=query_str, verbose=True, download=True)

df = pd.DataFrame(q.results)

df.to_csv(f'queryResult-{year}.csv', sep=',')