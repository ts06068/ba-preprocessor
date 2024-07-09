import crossref_commons.retrieval
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
import pybliometrics
import pybliometrics.scopus
from crossref_commons.relations import get_related
import crossref_commons

pybliometrics.scopus.init()
ab = AbstractRetrieval("10.1016/j.jacc.2023.11.003", view='FULL') # apply FULL view to fetch references

print(ab.affiliation)
print(ab.citedby_count)
print(ab.citedby_link)

print(crossref_commons.retrieval.get_publication_as_json('10.5621/sciefictstud.40.2.0382'))