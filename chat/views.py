import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from decouple import AutoConfig
config = AutoConfig()

PINECONE_URL = config('PINECONE_URL')
PINECONE_API_KEY = config('PINECONE_API_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')
SENSITIVE_KEYWORDS = [
    'personal medical history', 'specific diagnosis', 'private health details',
    'explicit content', 'identifying information', 'confidential test results',
    'personal contact', 'exact location', 'private conversations'
]

# List of known services and general information related to sexual and reproductive health
KNOWN_SERVICES = [
    'contraception', 'family planning', 'STI prevention', 'HIV testing',
    'pregnancy care', 'menstrual health', 'sexual education', 'reproductive rights',
    'gender health', 'adolescent health'
]

# Function to provide general information when a sensitive topic is detected
def generate_general_info(service):
    general_responses = {
        'contraception': 'Ishema ryanjye provides information about various contraceptive methods. We can discuss general options, but for personalized advice, please consult a healthcare provider.',
        'family planning': 'We offer general information about family planning methods and resources. For specific medical advice, we recommend speaking with a healthcare professional.',
        'STI prevention': 'We can provide general information about STI prevention methods and safe practices. For testing and specific concerns, please visit a healthcare facility.',
        'HIV testing': 'We can share general information about HIV testing options. For testing services and confidential results, please visit a healthcare facility or testing center.',
        'pregnancy care': 'We provide general information about pregnancy care. For personal medical advice, please consult with a healthcare provider.',
        'menstrual health': 'We offer information about menstrual health and hygiene. For specific concerns, we recommend speaking with a healthcare provider.',
        'sexual education': 'We provide age-appropriate sexual education information. For specific questions, we encourage speaking with trusted adults or healthcare providers.',
        'reproductive rights': 'We can discuss general information about reproductive rights and access to healthcare services.',
        'gender health': 'We provide information about gender health and related services. For personal support, we recommend consulting with healthcare professionals.',
        'adolescent health': 'We offer general information about adolescent health and development. For specific concerns, we encourage speaking with trusted adults or healthcare providers.'
    }
    return general_responses.get(service, f'Ishema ryanjye provides information about sexual and reproductive health. For specific questions about "{service}", we recommend consulting a healthcare provider.')

# Modify the sensitive check to provide general information
def contains_sensitive_info(prompt):
    for keyword in SENSITIVE_KEYWORDS:
        if keyword.lower() in prompt.lower():
            return True
    return False

def detect_service_query(prompt):
    for service in KNOWN_SERVICES:
        if service.lower() in prompt.lower():
            return service
    return None

# Humanistic response generator for sensitive or know-how related queries
def generate_humanistic_response(service):
    general_info = generate_general_info(service)
    return f"""
    It seems like you're asking for specific details related to "{service}". While we can't share proprietary or confidential information, I can tell you that {general_info}
    
    If you need more detailed insights, feel free to contact us directly at support@mlcorporateservices.com or call us at +250-123-456789. We're always here to help!
    """


# Helper to fetch embeddings
def get_embedding(text):
    embedding_url = 'https://api.openai.com/v1/embeddings'
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        'model': 'text-embedding-ada-002',
        'input': text
    }
    
    try:
        # Add timeout and SSL verification settings
        response = requests.post(
            embedding_url, 
            json=body, 
            headers=headers,
            timeout=30,
            verify=True
        )
        if response.status_code == 200:
            return response.json().get('data')[0].get('embedding', [])
        else:
            # Handle embedding API errors and return it
            return {'error': f"OpenAI Embedding Error: {response.status_code} - {response.text}"}
    except requests.exceptions.SSLError as e:
        return {'error': f"SSL Error connecting to OpenAI: {str(e)}"}
    except requests.exceptions.ConnectionError as e:
        return {'error': f"Connection Error to OpenAI: {str(e)}"}
    except requests.exceptions.Timeout as e:
        return {'error': f"Timeout Error connecting to OpenAI: {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error calling OpenAI: {str(e)}"}

# Helper to query Pinecone
def query_pinecone(query_embedding):
    # Validate vector dimensions
    if not isinstance(query_embedding, list):
        return {'error': 'Query embedding must be a list'}
    
    if not query_embedding:
        return {'error': 'Query embedding cannot be empty'}
    
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': PINECONE_API_KEY
    }
    body = {
        'vector': query_embedding,
        'topK': 5,
        'includeMetadata': True
    }

    try:
        response = requests.post(PINECONE_URL, json=body, headers=headers)
        
        if response.status_code != 200:
            return {'error': f"Pinecone API returned status code {response.status_code}: {response.text}"}
            
        if not response.text.strip():
            return {'error': 'Pinecone API returned empty response'}
            
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            return {'error': f"Failed to parse Pinecone response: {str(e)}"}
        
        if 'matches' in data and data['matches']:
            contexts = []
            for match in data['matches']:
                # Debug: print the match structure to understand metadata
                print(f"DEBUG - Match structure: {match}")
                
                # Try different possible metadata keys
                content = (
                    match['metadata'].get('content') or 
                    match['metadata'].get('text') or 
                    match.get('metadata', {}).get('page_content') or
                    str(match.get('metadata', {}))
                )
                if content and content != '{}':
                    contexts.append(content)
            if contexts:
                return "\n".join(contexts)
            else:
                return {'error': f'No relevant content found in Pinecone matches. Match count: {len(data["matches"])}'}
        else:
            return {'error': 'No matches found in Pinecone response'}
            
    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to connect to Pinecone: {str(e)}"}



@csrf_exempt
@api_view(['POST'])
def handle_chat_bot_request(request):
    last_prompt = request.data.get('last_prompt')
    conversation_history = request.data.get('conversation_history', [])

    # Check for sensitive information
    detected_service = detect_service_query(last_prompt)
    if contains_sensitive_info(last_prompt) or detected_service:
        if detected_service:
            # Generate a humanistic response with general info and support
            response = generate_humanistic_response(detected_service)
        else:
            response = "We value confidentiality and cannot share certain sensitive details publicly. However, we can assist you with services or general information. Please contact us at support@mlcorporateservices.com or call us at +250-123-456789 for assistance."
        
        return Response({
            'success': True,
            'result': response
        })
    
    if "J'utilise le français" in last_prompt:
        conversation_history.append({
            'role': 'system',
            'content': (
                "Merci d'avoir choisi le français. Comment puis-je vous aider aujourd'hui ? "
                "N'hésitez pas à poser des questions sur nos services."
            )
        })
    else:
        # Proceed with the normal English response
        conversation_history.append({
            'role': 'system',
            'content': (
                "You are Ishema ryanjye, a chatbot that ONLY provides information from the loaded Ishema ryanjye handbook and sexual reproductive health data. "
                "You must ONLY answer based on the provided context from the handbook. "
                "Do NOT use general knowledge or information outside of what's provided in the context. "
                "If the provided context doesn't contain enough information to answer the question, say 'I can only answer based on the information in the Ishema ryanjye handbook.'"
            )
        })

    conversation_history.append({
        'role': 'user',
        'content': last_prompt
    })

    query_embedding = get_embedding(last_prompt)
    if isinstance(query_embedding, dict) and 'error' in query_embedding:
        return Response({
            'success': False,
            'message': "Unable to process your question due to technical issues. Please try again later."
        }, status=500)

    pinecone_context = query_pinecone(query_embedding)
    if isinstance(pinecone_context, dict) and 'error' in pinecone_context:
        # If no relevant data found, inform the user
        return Response({
            'success': True,
            'result': "I can only provide information based on the Ishema ryanjye handbook and sexual reproductive health data that has been loaded. I don't have information about your specific question. Please try asking about topics covered in the handbook."
        })

    if pinecone_context:
        conversation_history.append({
            'role': 'system',
            'content': f"Based on the Ishema ryanjye handbook and sexual reproductive health data: \n{pinecone_context}\n\nOnly provide information based on this content. Do not add general knowledge outside of this context."
        })
    else:
        # No context found
        return Response({
            'success': True,
            'result': "I can only answer questions based on the information in the Ishema ryanjye handbook. Please ask about topics covered in the handbook."
        })

    openai_body = {
        'model': 'gpt-3.5-turbo',
        'messages': conversation_history,
        'temperature': 0.7
    }
    
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions', 
            json=openai_body, 
            headers=headers,
            timeout=30,
            verify=True
        )
        if response.status_code == 200:
            result = response.json().get('choices')[0]['message']['content']
            # Ensure we only provide responses based on loaded data
            if not result.strip():
                result = "I can only provide information based on the Ishema ryanjye handbook. Please ask a specific question about the content in the handbook."
            return Response({'success': True, 'result': result})
        else:
            return Response({
                'success': False,
                'message': f"OpenAI API Error: {response.status_code} - {response.text}"
            }, status=500)
    except requests.exceptions.SSLError as e:
        return Response({
            'success': False,
            'message': "Technical issues connecting to AI service. Please try again later."
        }, status=500)
    except requests.exceptions.ConnectionError as e:
        return Response({
            'success': False,
            'message': "Connection issues. Please try again later."
        }, status=500)
    except Exception as e:
        return Response({
            'success': False,
            'message': f"Unexpected error: {str(e)}"
        }, status=500)



@api_view(['GET'])
def load_chat_bot_base_configuration(request):
    response = {
        'botStatus': 1,
        'StartUpMessage': (
            "Hello! I'm Ishema ryanjye, your friendly chatbot focused on sexual and reproductive health awareness. "
            "How can I help you today?'."
        ),
        'fontSize': '16',
        'userAvatarURL': 'https://learnwithhasan.com/wp-content/uploads/2023/09/pngtree-businessman-user-avatar-wearing-suit-with-red-tie-png-image_5809521.png',
        'botImageURL': 'https://mlcorporateservices.com/wp-content/uploads/2022/09/cropped-Mlydie_-1.png',
        'commonButtons': [
            {'buttonText': "J'utilise le français", 'buttonPrompt': 'J utilise le français'},
            {'buttonText': 'What services do you offer?', 'buttonPrompt': 'What services do you offer?'},
            {'buttonText': 'How can I contact you?', 'buttonPrompt': 'How can I contact you?'}
        ]
    }
    return JsonResponse(response)
