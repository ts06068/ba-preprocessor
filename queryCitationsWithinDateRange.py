from pmidcite.icite.downloader import get_downloader
import pmidcite.citation as citation

dnldr = get_downloader(details_cites_refs="all")

pmid = 21173362
paper = dnldr.get_paper(pmid)
cites = paper.cited_by


for cite in cites:
    print(cite.dct)
    continue

print(len(cites))
