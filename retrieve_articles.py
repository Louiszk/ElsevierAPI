import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('SCIDIR_API_KEY')


def retrieve_abstracts(paper_doi):
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": 'application/json'
    }
    url = f"https://api.elsevier.com/content/article/doi/{paper_doi}"
    response = requests.get(url, headers=headers, timeout=30)
    #print(str(response.json())[:2000])
    
    if response.status_code == 200:
        document_data = response.json()
        if 'full-text-retrieval-response' in document_data:
            core_data = document_data['full-text-retrieval-response'].get('coredata', {})
            description = core_data.get('dc:description')
        
            return description
        return None
    else:
        return {"error": f"{response.status_code} - {response.reason}"}
    

def search_papers_scidir(query):
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": 'application/json',
        "Content-Type": 'application/json' 
    }
    base_url = "https://api.elsevier.com/content/search/sciencedirect"
    data = []
    offset = 0
    show = 25

    while True:
        body = {
            "qs": query,
            "display": {
                "offset": offset,
                "show": show
            }
        }

        print("Making requests", offset)
        time.sleep(0.5)
        response = requests.put(base_url, headers=headers, json=body, timeout=30)
        
        if response.status_code == 200:
            search_results = response.json()
            #print(search_results)
            total_results = int(search_results.get('resultsFound', 0))
            print(total_results)
            if total_results == 0:
                print("No results found for the query.")
                break
            
            entries = search_results.get('results', {})
            
            if not entries:
                break  # Exit the loop if no more entries are found
            
            for entry in entries:
                #print(entry)
                doi = entry.get('doi')
                publication_date = entry.get('publicationDate')
                title = entry.get('title')
                source_title = entry.get('sourceTitle')
                full_title = title if title else "" + (" - " if title and source_title else "") + source_title if source_title else ""
                uri = entry.get('uri')
                if doi:
                    data.append((doi, full_title, publication_date, uri))

            offset += show 
            
            if offset >= total_results:
                break 
        else:
            print(f"Error: {response.status_code} - {response.reason}")
            break

    return data

if __name__ == "__main__":
    META_FILE = 'meta.json'
    DATA_FILE = 'full_data.json'
    if os.path.exists(META_FILE) and os.path.getsize(META_FILE) > 0:
        with open(META_FILE, 'r') as file:
            all_meta = json.load(file)
        print("Loaded DOIs from file:", len(all_meta))
    else:
        query = "machine learning"
        
        all_meta = search_papers_scidir(query)
        all_meta = list(set(all_meta))
        print(len(all_meta))
        
        if all_meta:
            with open(META_FILE, 'w') as file:
                json.dump(all_meta, file)
            print("DOIs saved to file:", len(all_meta))
    
    if all_meta:
        papers_data = []
        for i, dat in enumerate(all_meta):
            print(f"Retrieving Abstract for {i}/{len(all_meta)}")
            abstract = retrieve_abstracts(dat[0])
            if abstract:
                papers_data.append(dat + [abstract])
            time.sleep(0.5)
        
        with open(DATA_FILE, 'w') as file:
            json.dump(papers_data, file)
        print("Full data saved to file:", len(papers_data))

