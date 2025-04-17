import os
import json
import pinecone
from decouple import config
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=config('OPENAI_API_KEY'))

# Initialize Pinecone
pinecone.init(
    api_key=config('PINECONE_API_KEY'),
    environment=config('PINECONE_ENVIRONMENT')
)

# Get or create index
index_name = config('INDEX_NAME')
dimension = 1536  # This is the dimension for text-embedding-ada-002

# Check if index exists, if not create it
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=dimension,
        metric='cosine'
    )

# Connect to the index
index = pinecone.Index(index_name)

def get_embedding(text):
    """Get embedding from OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def upsert_to_pinecone(texts, metadata_list=None):
    """Upsert texts to Pinecone with optional metadata"""
    if metadata_list is None:
        metadata_list = [{} for _ in texts]
    
    # Get embeddings for all texts
    embeddings = [get_embedding(text) for text in texts]
    
    # Prepare vectors for upsert
    vectors = []
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadata_list)):
        vector = {
            'id': f'vec_{i}',
            'values': embedding,
            'metadata': {**metadata, 'text': texts[i]}
        }
        vectors.append(vector)
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors, namespace='default')
    print(f"Upserted {len(vectors)} vectors to Pinecone")

# Example usage with some sample data
sample_texts = [
    "HIV testing is available at all health centers in Rwanda",
    "Condoms are distributed free of charge at health facilities",
    "ARV treatment is provided free of charge to all HIV positive patients",
    "Gender-based violence can be reported at Isange One Stop Centers",
    "Mental health counseling is available at district hospitals",
    "Family planning services are available at health centers",
    "Youth-friendly services are available at selected health facilities",
    "Emergency contraception is available at pharmacies",
    "STI testing and treatment is confidential and free",
    "PEP (Post-Exposure Prophylaxis) is available within 72 hours of exposure"
]

# Add metadata if needed (e.g., location, category, etc.)
sample_metadata = [
    {'category': 'HIV', 'location': 'Rwanda'},
    {'category': 'Prevention', 'location': 'Rwanda'},
    {'category': 'Treatment', 'location': 'Rwanda'},
    {'category': 'GBV', 'location': 'Rwanda'},
    {'category': 'Mental Health', 'location': 'Rwanda'},
    {'category': 'Family Planning', 'location': 'Rwanda'},
    {'category': 'Youth Services', 'location': 'Rwanda'},
    {'category': 'Emergency Care', 'location': 'Rwanda'},
    {'category': 'STI', 'location': 'Rwanda'},
    {'category': 'PEP', 'location': 'Rwanda'}
]

if __name__ == "__main__":
    print("Starting Pinecone population...")
    upsert_to_pinecone(sample_texts, sample_metadata)
    print("Pinecone population completed!")
    
    # Verify the index stats
    print("\nIndex Stats:")
    print(index.describe_index_stats()) 