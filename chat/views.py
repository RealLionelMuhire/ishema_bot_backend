import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

from decouple import AutoConfig
config = AutoConfig()

PINECONE_URL = config('PINECONE_URL')
PINECONE_API_KEY = config('PINECONE_API_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')

# Threshold for Pinecone match scores
PINECONE_THRESHOLD = 0.77

# System prompt
SYSTEM_PROMPT = """
You are ISHEMA RYANJYE, a specialized chatbot that provides support and information on two main areas:

1. Sexual and Reproductive Health (SRH) and Mental Health information
2. The ISHEMA RYANJYE card game - rules, gameplay, and support

If asked about your role, respond dynamically and explain: "I am ISHEMA RYANJYE. I provide support and information on sexual reproductive health, mental health, and the ISHEMA RYANJYE card game." Ensure the response adapts to the user's language.

For location-specific data, ask the user for their location before answering. Do not provide information from other sources not in the database. Respond only using database content. Do not guess or provide unrelated information. Keep responses short, focused, and concise.

For unrelated questions outside of SRH, mental health, or the ISHEMA RYANJYE card game, respond politely that you only assist with these specific topics. Always follow up with a question to keep the conversation active.

Ask for clarification if needed. Provide resources if relevant to the user's query. Proactively ask questions to engage the user and ensure they feel supported.

Chatbot Name: ISHEMA RYANJYE
We're dedicated to connecting you with reliable sexual and reproductive health services and supporting the ISHEMA RYANJYE card game community.
"""

# Helper to fetch embeddings
def get_embedding(text):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        'model': 'text-embedding-ada-002',
        'input': text
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            json=body, 
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get('data')[0].get('embedding', [])
        else:
            raise Exception(f"OpenAI Embedding Error: {response.status_code}")
    except Exception as e:
        raise Exception(f"Failed to generate embedding: {str(e)}")

# Helper to query Pinecone
def query_pinecone(query_embedding):
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': PINECONE_API_KEY
    }
    body = {
        'vector': query_embedding,
        'topK': 50,
        'includeMetadata': True
    }

    try:
        response = requests.post(PINECONE_URL, json=body, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Pinecone API error: {response.status_code}")
            
        data = response.json()
        
        if 'matches' in data and data['matches']:
            # Filter matches by threshold
            relevant_matches = [
                match for match in data['matches'] 
                if match.get('score', 0) >= PINECONE_THRESHOLD
            ]
            
            if relevant_matches:
                contexts = []
                for match in relevant_matches:
                    metadata = match.get('metadata', {})
                    content = metadata.get('text') or metadata.get('content') or metadata.get('page_content')
                    if content:
                        contexts.append(str(content).strip())
                
                return '\n'.join(contexts) if contexts else None
        
        return None
            
    except Exception as e:
        raise Exception(f"Failed to query Pinecone: {str(e)}")



@csrf_exempt
@api_view(['POST'])
def handle_chat_bot_request(request):
    try:
        # Extract messages from request
        messages = request.data.get('messages', [])
        model = request.data.get('model', 'gpt-4o')
        
        if not messages or not isinstance(messages, list):
            return Response({'error': 'Invalid messages format'}, status=400)
        
        # Get the last user message
        last_message = messages[-1].get('content') if messages else None
        if not last_message:
            return Response({'error': 'No valid message content found'}, status=400)
        
        # Generate embedding for the last user message
        embedding = get_embedding(last_message)
        
        # Query Pinecone for relevant context
        pinecone_context = query_pinecone(embedding)
        
        # Enhanced messages with system prompt
        enhanced_messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            *messages,
            {'role': 'system', 'content': f'Relevant info: {pinecone_context or "No context available."}'}
        ]
        
        # Stream OpenAI response
        def generate_stream():
            try:
                headers = {
                    'Authorization': f'Bearer {OPENAI_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                openai_body = {
                    'model': model,
                    'messages': enhanced_messages,
                    'temperature': 0.1,
                    'top_p': 0.1,
                    'stream': True
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    json=openai_body,
                    headers=headers,
                    stream=True,
                    timeout=30
                )
                
                if response.status_code != 200:
                    yield f'{json.dumps({"content": "I encountered an issue processing your request. Please try again."})}\n'
                    return
                
                has_content = False
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                if content:
                                    has_content = True
                                    yield f'{json.dumps({"content": content})}\n'
                            except json.JSONDecodeError:
                                continue
                
                # Fallback if no content was streamed
                if not has_content:
                    fallback_message = (
                        "I'm unable to provide a detailed answer based on the current database content." 
                        if pinecone_context else 
                        "I don't know the answer to that."
                    )
                    yield f'{json.dumps({"content": fallback_message})}\n'
                    
            except Exception as e:
                # Fallback response using OpenAI non-streaming
                fallback_messages = [
                    {
                        'role': 'system',
                        'content': 'Respond only using database content. Do not guess or provide unrelated information. Keep responses short, focused, and concise. Ask for clarification if needed.'
                    },
                    {
                        'role': 'user',
                        'content': 'An error occurred, and no context is available. How would you respond?'
                    }
                ]
                
                try:
                    fallback_headers = {
                        'Authorization': f'Bearer {OPENAI_API_KEY}',
                        'Content-Type': 'application/json'
                    }
                    fallback_body = {
                        'model': model,
                        'messages': fallback_messages,
                        'temperature': 0.01,
                        'top_p': 0.01,
                        'max_tokens': 100
                    }
                    
                    fallback_response = requests.post(
                        'https://api.openai.com/v1/chat/completions',
                        json=fallback_body,
                        headers=fallback_headers,
                        timeout=30
                    )
                    
                    if fallback_response.status_code == 200:
                        fallback_content = fallback_response.json().get('choices', [{}])[0].get('message', {}).get('content', 'An unexpected error occurred.')
                    else:
                        fallback_content = 'An unexpected error occurred.'
                        
                    yield f'{json.dumps({"content": fallback_content})}\n'
                    
                except:
                    yield f'{json.dumps({"content": "An unexpected error occurred."})}\n'
        
        return StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )
        
    except Exception as error:
        return Response({'content': 'An unexpected error occurred.'}, status=500)



@api_view(['GET'])
def load_chat_bot_base_configuration(request):
    response = {
        'botStatus': 1,
        'fontSize': '16',
        'userAvatarURL': 'https://learnwithhasan.com/wp-content/uploads/2023/09/pngtree-businessman-user-avatar-wearing-suit-with-red-tie-png-image_5809521.png',
        'botImageURL': 'https://mlcorporateservices.com/wp-content/uploads/2022/09/cropped-Mlydie_-1.png',
        'StartUpMessage': (
            "Muraho! Welcome to ISHEMA RYANJYE. I'm here to help you with health information and our card game. "
            "Choose your language or topic below to get started!"
        ),
        'commonButtons': [
            {'buttonText': 'English', 'buttonPrompt': 'I want to continue in English'},
            {'buttonText': 'Kinyarwanda', 'buttonPrompt': 'Nshaka gukomeza mu Kinyarwanda'},
            {'buttonText': 'Ishema card game', 'buttonPrompt': 'Tell me about the ISHEMA RYANJYE card game'},
            {'buttonText': 'SRH and Mental health support', 'buttonPrompt': 'What sexual and reproductive health and mental health services do you offer?'}
        ]
    }
    
    return JsonResponse(response)
