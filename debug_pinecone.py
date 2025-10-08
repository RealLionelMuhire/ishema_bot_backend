#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings

# Load environment variables
load_dotenv()

PINECONE_URL = os.getenv('PINECONE_URL')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def test_data_flow():
    print("=== Testing Pinecone Data Flow ===")
    print(f"PINECONE_URL: {PINECONE_URL}")
    print(f"PINECONE_API_KEY: {'SET' if PINECONE_API_KEY else 'NOT SET'}")
    print(f"OPENAI_API_KEY: {'SET' if OPENAI_API_KEY else 'NOT SET'}")
    
    # Test 1: Generate embedding
    print("\n--- Step 1: Testing OpenAI Embedding ---")
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        test_query = "how to win ishema ryanjye card game"
        print(f"Query: '{test_query}'")
        
        query_embedding = embeddings.embed_query(test_query)
        print(f"✅ Embedding generated: {len(query_embedding)} dimensions")
        
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return
    
    # Test 2: Query Pinecone
    print("\n--- Step 2: Testing Pinecone Query ---")
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': PINECONE_API_KEY
    }
    body = {
        'vector': query_embedding,
        'topK': 3,
        'includeMetadata': True
    }
    
    try:
        response = requests.post(PINECONE_URL, json=body, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pinecone responded successfully")
            print(f"Matches found: {len(data.get('matches', []))}")
            
            if data.get('matches'):
                for i, match in enumerate(data['matches'][:2]):
                    print(f"\n--- Match {i+1} ---")
                    print(f"Score: {match.get('score', 'N/A')}")
                    print(f"ID: {match.get('id', 'N/A')}")
                    metadata = match.get('metadata', {})
                    print(f"Metadata keys: {list(metadata.keys())}")
                    
                    # Try to extract content
                    possible_keys = ['text', 'content', 'page_content', 'source', 'chunk', 'data']
                    content_found = False
                    
                    for key in possible_keys:
                        if key in metadata and metadata[key]:
                            content = str(metadata[key]).strip()
                            print(f"✅ Content in '{key}': {content[:150]}...")
                            content_found = True
                            break
                    
                    if not content_found:
                        print(f"❌ No content found in metadata: {metadata}")
            else:
                print("❌ No matches found in Pinecone response")
        else:
            print(f"❌ Pinecone error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Pinecone request failed: {e}")

if __name__ == "__main__":
    test_data_flow()
