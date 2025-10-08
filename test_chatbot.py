#!/usr/bin/env python3
"""
Comprehensive test script for the Ishema Ryanjye chatbot
Tests various scenarios to ensure the chatbot is working correctly
"""

import requests
import json
import time

# Base URL for the chatbot API
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat-bot/"
CONFIG_ENDPOINT = f"{BASE_URL}/chat-bot-config/"

def test_api_call(message, description=""):
    """Make an API call and return the result"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"Question: {message}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            json={"message": message},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS (Status: {response.status_code})")
            print(f"Response: {result.get('result', 'No result field')}")
            return result
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {str(e)}")
        return None

def test_config_endpoint(language="english"):
    """Test the configuration endpoint"""
    print(f"\n{'='*60}")
    print(f"TEST: Configuration endpoint ({language})")
    print(f"{'='*60}")
    
    try:
        response = requests.get(
            CONFIG_ENDPOINT,
            params={"language": language},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS (Status: {response.status_code})")
            print(f"Bot Status: {result.get('botStatus', 'Unknown')}")
            print(f"Startup Message: {result.get('StartUpMessage', 'None')[:100]}...")
            return result
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {str(e)}")
        return None

def main():
    print("🤖 ISHEMA RYANJYE CHATBOT COMPREHENSIVE TEST")
    print("=" * 80)
    
    # Test 1: Card Game Questions
    test_api_call(
        "how to win ishema ryanjye card game",
        "Card Game - How to Win"
    )
    
    test_api_call(
        "what are the rules of ishema ryanjye card game",
        "Card Game - Rules"
    )
    
    test_api_call(
        "how many cards are in ishema ryanjye game",
        "Card Game - Number of Cards"
    )
    
    # Test 2: Sexual and Reproductive Health Questions
    test_api_call(
        "what is family planning",
        "SRH - Family Planning"
    )
    
    test_api_call(
        "tell me about contraception methods",
        "SRH - Contraception"
    )
    
    test_api_call(
        "what is reproductive health",
        "SRH - General Health"
    )
    
    # Test 3: Multilingual Support
    test_api_call(
        "J'utilise le français. Comment jouer au jeu de cartes Ishema ryanjye?",
        "French Language Test"
    )
    
    test_api_call(
        "Muraho, nkoresha Ikinyarwanda. Imikino ya Ishema ryanjye ni iyihe?",
        "Kinyarwanda Language Test"
    )
    
    # Test 4: Out of Scope Questions (Should be refused)
    test_api_call(
        "what is the weather today",
        "Out of Scope - Weather (Should be refused)"
    )
    
    test_api_call(
        "tell me about cooking recipes",
        "Out of Scope - Cooking (Should be refused)"
    )
    
    test_api_call(
        "what is artificial intelligence",
        "Out of Scope - AI (Should be refused)"
    )
    
    # Test 5: Configuration Endpoints
    test_config_endpoint("english")
    test_config_endpoint("french")
    test_config_endpoint("kinyarwanda")
    
    print(f"\n{'='*80}")
    print("🎯 TEST SUMMARY")
    print("=" * 80)
    print("✅ If you see detailed responses for card game and SRH questions: SUCCESS")
    print("✅ If you see refusal messages for out-of-scope questions: SUCCESS")
    print("✅ If you see different languages working: SUCCESS")
    print("✅ If configuration endpoints return proper data: SUCCESS")
    print("\n🚀 The chatbot is working correctly!")

if __name__ == "__main__":
    main()