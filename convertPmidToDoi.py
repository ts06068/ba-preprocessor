file_path = 'MajorPubsFrom2008To2024IdList.txt'
new_file_path = 'MajorPubsFrom2008To2024DoiList.txt'
from metapub.convert import pmid2doi
from tqdm import tqdm
import sys

args = sys.argv

from_idx = int(args[1])
to_idx = int(args[2])

with open(file_path, 'r') as f:
    lines = [line.rstrip('\n') for line in f]
    f.close()

print(f'TOTAL: {len(lines)}')

lines = lines[from_idx:to_idx+1]

doi_list = []

for line in tqdm(lines):
    try:
        doi = str.lower(pmid2doi(line))
        doi_list.append(doi)
    except:
        continue

# save
with open(f'MajorPubsFrom2008To2024-{from_idx}-{to_idx}', 'w') as f:
    f_str = ''
    for line in tqdm(doi_list):
        f_str += line + '\n'
    f.write(f_str)
    f.close()