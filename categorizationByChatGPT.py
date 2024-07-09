from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd
import json
from time import sleep

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

categorize_system_prompt = '''
Your goal is to classify an article based on its title and abstract into 'original article' or other type of articles such as 'review article'.
You also have to provide a 1-sentence summary for your justification.
Eventually, you will output a json object containing the following information:

{
    category: string // category should be either one of 'original article', 'review article', 'guideline', 'commentary', and 'data report'.
    summary: string // 1-sentence summary for your justification
}

Category refers to the type of the given article, like 'original article', 'review article', 'guideline', 'commentary', and 'data report'.

Keep category name simple and use only lower case letters.
Each article must have only one category.
'''

dataset_path = 'BibQueryResult.csv'

df = pd.read_csv(dataset_path, low_memory=False)[["doi", "pubmed_id", "title", "description", "citedby_count (total)"]].fillna('')
df["ChatGPTCategory"] = ''
df["ChatGPTCategory_Summary"] = ''
df["weight"] = 1/(df['citedby_count (total)']+0.1)
df = df[(df['pubmed_id'] != '') & (df['description'] != '')]
df = df.sample(n=50, random_state=1004, weights='weight')
df = df.sort_values(by='citedby_count (total)', ascending=False)
df = df.reset_index(drop=True)
print(df.head())

def get_categories(description):
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    temperature=0.1,
    # This is to enable JSON mode, making sure responses are valid json objects
    response_format={ 
        "type": "json_object"
    },
    messages=[
        {
            "role": "system",
            "content": categorize_system_prompt
        },
        {
            "role": "user",
            "content": description
        }
    ],
    )

    return response.choices[0].message.content

'''
for _, row in df[:5].iterrows():
    title = row['title']
    abstract = row['description']
    description = f'{title}\n\n{abstract}'
    result = get_categories(description)
    print(f"DESCRIPTION: {description}\nRESULT: {result}")
    print("\n\n----------------------------\n\n")
'''

# Creating an array of json tasks

tasks = []

for index, row in df.iterrows():
    title = row['title']
    abstract = row['description']
    description = f'{title}\n\n{abstract}'
    
    task = {
        "custom_id": f"task-{str(index)}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            # This is what you would have in your Chat Completions API call
            "model": "gpt-4o",
            "temperature": 0.1,
            "response_format": { 
                "type": "json_object"
            },
            "messages": [
                {
                    "role": "system",
                    "content": categorize_system_prompt
                },
                {
                    "role": "user",
                    "content": description
                }
            ],
        }
    }
    
    tasks.append(task)

# Creating the file

file_name = "batch_tasks_articles.jsonl"

with open(file_name, 'w') as file:
    for obj in tasks:
        file.write(json.dumps(obj) + '\n')

batches = client.batches.list()

print(batches)

batch_file = client.files.create(
  file=open(file_name, "rb"),
  purpose="batch"
)

batch_job = client.batches.create(
  input_file_id=batch_file.id,
  endpoint="/v1/chat/completions",
  completion_window="24h"
)

status = ''
while True:
    if status == 'completed':
        break

    batch_job = client.batches.retrieve(batch_job.id)
    status = batch_job.status
    print(status)
    sleep(1)

result_file_id = batch_job.output_file_id
result = client.files.content(result_file_id).content

result_file_name = "batch_job_results_articles.jsonl"

with open(result_file_name, 'wb') as file:
    file.write(result)

# Loading data from saved file
results = []
with open(result_file_name, 'r') as file:
    for line in file:
        # Parsing the JSON string into a dict and appending to the list of results
        json_object = json.loads(line.strip())
        results.append(json_object)

with open('printResult.txt', 'w', encoding='utf-8') as f:
    # Reading only the first results
    for res in results:
        task_id = res['custom_id']
        # Getting index from task id
        index = task_id.split('-')[-1]
        result = res['response']['body']['choices'][0]['message']['content']

        row = df.iloc[int(index)]
        title = row['title']
        abstract = row['description']
        description = f'{title}\n\n{abstract}'

        json_object = json.loads(result)
        df.loc[int(index), 'ChatGPTCategory'] = json_object['category']
        df.loc[int(index), 'ChatGPTCategory_Summary'] = json_object['summary']
        
        f.write(f"DESCRIPTION: {description}\nRESULT: {result}")
        f.write("\n\n----------------------------\n\n")

df.to_csv('ChatGPTCategorizationResult.csv', sep=',')