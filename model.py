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
    
    
