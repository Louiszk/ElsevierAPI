import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


client = Groq(api_key=os.getenv('API_KEY'))


summary_prompt_template = (
    '''Please write a short one sentence summary of this paper based on this abstract.
  Start with "True" if the paper is primarily about machine learning,
 and with "False" if it's not. Abstract: '''
)

def get_summary(abstract):
    
    summary_prompt = summary_prompt_template + abstract
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": summary_prompt}
        ],
        model="llama-3.1-70b-versatile"
    )
    

    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    file_path = '/full_data.json'

    with open(file_path, 'r') as file:
        papers_data = json.load(file)

    for i, paper in enumerate(papers_data):
        print("Replacing", i, "/", len(papers_data))
        abstract = paper[4]  
        summary = get_summary(abstract)
        paper[4] = summary

    with open('updated_full_data.json', 'w') as file:
        json.dump(papers_data, file, indent=4)