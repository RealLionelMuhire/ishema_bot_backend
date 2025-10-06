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
INDEX_NAME = "ticochatbot-srhr"

def main():
    # Load PDF using UnstructuredPDFLoader
    print("Loading data from PDF...")
    loader = UnstructuredPDFLoader("ISHEMA_RYANJYE_HANDBOOK-ENGLISH_VERSION-_RBC-WHO-HPO_final.pdf")  # Update with your file path
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

    # Check if the index exists; create it if it doesn't
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',  # Update based on your Pinecone environment
                region=PINECONE_ENVIRONMENT  # Use your specific Pinecone environment
            )
        )
    print("Accessing the index...")
    index = pc.Index(name=INDEX_NAME)

    # Store embeddings in Pinecone using PineconeVectorStore
    print("Storing embeddings in Pinecone...")
    PineconeVectorStore.from_texts(
        texts=[text.page_content for text in texts],
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    print("Data has been successfully indexed in Pinecone.")

if __name__ == "__main__":
    main()
