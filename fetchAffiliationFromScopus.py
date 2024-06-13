from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
import pybliometrics
import pybliometrics.scopus

pybliometrics.scopus.init()
ab = AbstractRetrieval("10.1016/j.jacc.2023.11.003", view='FULL') # apply FULL view to fetch references

print(ab.affiliation)
print(ab.citedby_count)
print(ab.ref)