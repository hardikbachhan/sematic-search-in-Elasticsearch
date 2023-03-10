try: 
    import json
    import os
    # import uuid

    import pandas as pd
    # import numpy as np
    
    # import elasticsearch
    # from elasticsearch import Elasticsearch
    # from elasticsearch import helpers
    from sentence_transformers import SentenceTransformer, util
    from tqdm import tqdm
    from dotenv import load_dotenv
    load_dotenv("secret.env")
except Exception as e:
    print(f"Some modules missing: {e}")
    
    
# Reading data from jobs dataset
def readFile(filePath):
    try:
        df = pd.read_csv(filePath)
        df = df.fillna("")  # replace none values as Elasticsearch will reject them
        # selecting 19 rows randomly to test code
        df = df.sample(frac=0.1,random_state=200)
        return df
    except Exception as e:
        print(f"Error in reading file: {e}")
        return []



# Vectorize job postings -> to create 384 length vector for, indexing title in Elasticsearch and search query
def vectorize(sentence):
    try:
        model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')
        # print(sentence)
        # Encode input sentence
        sentenceEmbedding = model.encode(sentence)
        return sentenceEmbedding
    except Exception as e:
        print(f"Error occurred during Tokenizing: {e}")
        return None
    
    
def connectToES():
    try:
        from elasticsearch import Elasticsearch
        # Password for the 'elastic' user generated by Elasticsearch
        ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

        # Create the client instance
        client = Elasticsearch(
            "https://localhost:9200",
            ca_certs="./es certificate/http_ca.crt",
            basic_auth=("elastic", ELASTIC_PASSWORD)
        )

        # Successful response!
        resp = client.info()
        # print(resp)
        return client
    except Exception as e:
        print(f"Failed to connect to ElasticSearch Local Instance: {e}")
        return False
        
        
def createVectorField(df):
    try:
        tqdm.pandas()
        df["jobs_vector"] = df["jobpost"].progress_apply(vectorize)
        return df
    except Exception as e:
        print(f"Failed to add vector field in data frame, \n {e}")


def postDataToIndex(es, indexName, df):
    try:
        elk_data = df.to_dict("records")
        # print(es, indexName)
        ingestedDocs = 0
        for job in elk_data:
            try:
                es.index(index = indexName, document = job)
                ingestedDocs += 1
            except Exception as e:
                print(f"error in indexing job: {e}")

        print(f"Successfully ingested {ingestedDocs} documents in {indexName} index")
        return True
    except Exception as e:
        print(f"Error in posting data to index: {e}")
        return False


def absoluteKNN(es, indexName, text):
    try:
        sentenceEmbedding = vectorize(text)
        query = {
            "field": "jobs_vector",
            "k": 10,
            "num_candidates": 10000,
            "query_vector": sentenceEmbedding
        }
        resp = es.search(index = indexName, knn = query)
        return resp
    except Exception as e:
        print(f"{e}")
        

def bruteForceKNN(es, indexName, text):
    try:
        sentenceEmbedding = vectorize(text)
        query = {
            "script_score": {
                "query": {
                    "bool": {
                    "must": [
                        {
                            "match": {
                                "Eligibility": "everyone"
                            }
                        }
                    ]
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'jobs_vector') + 1.0", 
                    "params": {
                        "query_vector": sentenceEmbedding
                    }
                }
            }
        }
        resp = es.search(index = indexName, query = query)
        return resp
    except Exception as e:
        print(f"{e}")


def main():
    
    # df = readFile("jobs dataset\data job posts.csv")
    
    # print(df.head())
    # print(df["Title"])
    print("-----------------------------------------")
    
    # text = df["jobpost"][3]
    # text = "Hey i am looking for web programmer role"
    # print(text)
    # sentenceEmbedding = vectorize(text)
    # print(sentenceEmbedding)
    # print(len(sentenceEmbedding))
    
    # creating vector field in df
    # df = createVectorField(df)
    # print(df)
    print("-----------------------------------------")
    
    # connecting to local Elastic instance
    es = connectToES()
    # indexName = "posting"            # for approximate knn search
    indexName = "posting_brute_force"  # for brute force knn search
    # resp = postDataToIndex(es, indexName, df)
    # print(resp)
    
    
    # approximate knn -> fast, 
    # text = input()
    # resp = absoluteKNN(es, indexName, text)
    # for hit in resp["hits"]["hits"]:
    #     print(hit["_source"]["Title"], hit["_source"]["date"])
    
    
    # brute force knn -> slow, custom implementation allowed, requires hyperparmeter tuning
    text = input()
    resp = bruteForceKNN(es, indexName, text)
    # print(resp)
    for hit in resp["hits"]["hits"]:
        print(hit["_source"]["Title"], hit["_source"]["date"])
    
if __name__ == "__main__":
    main()