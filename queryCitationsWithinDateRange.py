from pmidcite.icite.downloader import get_downloader
import pmidcite.citation as citation
import pandas as pd

dnldr = get_downloader(details_cites_refs="citations")

pmid = 25712077
paper = dnldr.get_paper(pmid)
cited_by = paper.cited_by

df = pd.DataFrame()

for cite in cited_by:
    dct = dict(cite.dct)
    pmid = int(dct['pmid'])
    doi = str(dct['doi'])
    print(dct)
