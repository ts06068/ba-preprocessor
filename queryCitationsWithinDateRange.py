import opencitingpy

client = opencitingpy.client.Client()
dois = ['10.3390/s19020353', '10.1016/j.jacc.2023.11.003']
# get metadata of a list of articles, including title, publication year, number of citing and cited documents, etc.
metadata = client.get_metadata(dois)
