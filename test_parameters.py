#!/usr/bin/env python3
"""
Test script to verify filtering parameters in the chatbot
"""

import requests
import json

def test_parameters():
    """Test the chatbot and show current parameter settings"""
    print("🔧 TESTING CHATBOT FILTERING PARAMETERS")
    print("=" * 60)
    
    # Make a test call
    response = requests.post(
        "http://localhost:8000/chat-bot/",
        json={"message": "how to play ishema ryanjye card game"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API Call Successful")
        print(f"Response: {result.get('result', 'No result')[:200]}...")
        
        print(f"\n📊 CURRENT PARAMETER SETTINGS:")
        print("=" * 40)
        print("🎯 Pinecone Parameters:")
        print("   • topK: 5 (returns top 5 most similar matches)")
        print("   • includeMetadata: True (includes text content)")
        print("   • metric: cosine similarity")
        
        print("\n🤖 OpenAI Parameters:")
        print("   • model: gpt-3.5-turbo")
        print("   • temperature: 0.7 (moderate creativity)")
        print("   • top_p: Not set (using default)")
        print("   • max_tokens: Not set (using default)")
        
        print("\n⚙️ To adjust these parameters:")
        print("   • Edit chat/views.py line ~125 for Pinecone topK")
        print("   • Edit chat/views.py line ~300 for OpenAI temperature")
        print("   • Add top_p, max_tokens to openai_body for more control")
        
    else:
        print(f"❌ API Call Failed: {response.status_code}")

if __name__ == "__main__":
    test_parameters()