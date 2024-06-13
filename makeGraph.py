import pandas as pd
import numpy as np
import networkx as nx
from netgraph import Graph

df = pd.read_csv('queryResult-2008.csv', index_col=0)

print(df)

G = nx.Graph()

"""
for index, row in df.iterrows():
    print(index, row['A'], row['B'])
"""

for index, row in df.iterrows():
    affil_list = str(row['affilname']).lower().split(';')
    for affil_from in affil_list:
        for affil_to in affil_list:
            if affil_from == affil_to:
                continue
            G.add_edge(affil_from, affil_to)

pos = nx.spring_layout(G)

Graph(G, node_layout=pos, edge_layout='curved')