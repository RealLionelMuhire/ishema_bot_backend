#!/usr/bin/env python3
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Fetch keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
INDEX_NAME = "ishema-ryanjye-hpo"  # Use existing index

# Print configuration info
print("=== Configuration Check ===")
print(f"OpenAI API Key: {'✓ Set' if OPENAI_API_KEY else '✗ Missing'}")
print(f"Pinecone API Key: {'✓ Set' if PINECONE_API_KEY else '✗ Missing'}")
print(f"Pinecone Environment: {PINECONE_ENVIRONMENT if PINECONE_ENVIRONMENT else '✗ Missing'}")
print(f"Target Index Name: {INDEX_NAME}")
print("============================\n")

def main():
    global INDEX_NAME  # Allow modification of INDEX_NAME within function
    
    # Load PDF using UnstructuredPDFLoader
    print("Loading data from PDF...")
    loader = UnstructuredPDFLoader("COUNSELLING_CARD_IN_KINYARWANDA[1].pdf")  # Update with your file path
    data = loader.load()

    print(f'Loaded {len(data)} document(s) from the PDF.')
    print(f'Sample content: {data[0].page_content[:200]}')

    # Split data into smaller chunks
    print("Splitting data into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(data)
    print(f'Created {len(texts)} chunks from the document.')

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Initialize Pinecone
    print("Initializing Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Print the index name we're working with
    print(f"Working with index: {INDEX_NAME}")
    
    # List all available indexes
    available_indexes = pc.list_indexes().names()
    print(f"Available indexes: {available_indexes}")

    # Check if the index exists; create it if it doesn't
    if INDEX_NAME not in available_indexes:
        print(f"Index '{INDEX_NAME}' does not exist.")
        
        # Check if there are similar indexes we could use instead
        similar_indexes = [idx for idx in available_indexes if 'ishema' in idx.lower() or 'ryanjye' in idx.lower()]
        if similar_indexes:
            print(f"Found similar indexes: {similar_indexes}")
            print(f"Consider using one of these existing indexes instead of creating a new one.")
            
        print(f"Attempting to create index '{INDEX_NAME}'...")
        try:
            # Try different region formats
            regions_to_try = [
                PINECONE_ENVIRONMENT,  # Original value
                'us-east-1',           # Common AWS region
                'us-west-2',           # Another common region
            ]
            
            for region in regions_to_try:
                if not region:
                    continue
                    
                print(f"Trying region: {region}")
                try:
                    pc.create_index(
                        name=INDEX_NAME,
                        dimension=1536,
                        metric='cosine',
                        spec=ServerlessSpec(
                            cloud='aws',
                            region=region
                        )
                    )
                    print(f"Index '{INDEX_NAME}' created successfully with region '{region}'!")
                    break
                except Exception as region_error:
                    print(f"Failed with region '{region}': {region_error}")
                    continue
            else:
                print("Failed to create index with any region. Using existing similar index if available.")
                if similar_indexes:
                    INDEX_NAME = similar_indexes[0]
                    print(f"Switching to existing index: {INDEX_NAME}")
                else:
                    raise Exception("No suitable index available and cannot create new one")
                    
        except Exception as create_error:
            print(f"Error creating index: {create_error}")
            if similar_indexes:
                INDEX_NAME = similar_indexes[0]
                print(f"Falling back to existing index: {INDEX_NAME}")
            else:
                raise create_error
    else:
        print(f"Index '{INDEX_NAME}' already exists.")
    
    print(f"Accessing the index: {INDEX_NAME}")
    index = pc.Index(name=INDEX_NAME)
    
    # Check current index stats before adding data
    stats = index.describe_index_stats()
    print(f"Index stats before loading data: {stats}")
    print(f"Current vector count in index: {stats.get('total_vector_count', 0)}")

    # Store embeddings in Pinecone using PineconeVectorStore
    print(f"Storing embeddings in Pinecone index '{INDEX_NAME}'...")
    print(f"Number of text chunks to store: {len(texts)}")
    
    try:
        # Store the embeddings
        vector_store = PineconeVectorStore.from_texts(
            texts=[text.page_content for text in texts],
            embedding=embeddings,
            index_name=INDEX_NAME
        )
        print("Embeddings stored successfully!")
        
        # Wait a moment for indexing to complete
        import time
        print("Waiting 3 seconds for indexing to complete...")
        time.sleep(3)
        
        # Check index stats after loading data
        stats_after = index.describe_index_stats()
        print(f"Index stats after loading data: {stats_after}")
        print(f"Final vector count in index: {stats_after.get('total_vector_count', 0)}")
        
        # Test a simple query to verify data is accessible
        print("\nTesting index with a sample query...")
        test_embedding = embeddings.embed_query("how to play")
        query_result = index.query(
            vector=test_embedding,
            top_k=3,
            include_metadata=True
        )
        print(f"Sample query returned {len(query_result.get('matches', []))} matches")
        
        if query_result.get('matches'):
            print("Sample match content preview:")
            for i, match in enumerate(query_result['matches'][:2]):
                content = match.get('metadata', {}).get('text', 'No content found')[:200]
                print(f"  Match {i+1}: {content}...")
        else:
            print("WARNING: No matches found in test query!")
            
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        return

    print(f"\nData has been successfully indexed in Pinecone index '{INDEX_NAME}'.")

if __name__ == "__main__":
    main()
