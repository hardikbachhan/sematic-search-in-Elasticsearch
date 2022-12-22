try: 
    import json
    import os
    import uuid

    import pandas as pd
    import numpy as np
    
    import elasticsearch
    from elasticsearch import Elasticsearch
    from elasticsearch import helpers
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
        return df
    except Exception as e:
        print(f"Error in reading file: {e}")
        return []

df = readFile("jobs dataset\data job posts.csv")

print(df[:3])
print("-----------------------------------------")

