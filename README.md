# Ishema Ryanjye - Sexual and Reproductive Health Support Bot

Ishema Ryanjye is a chatbot designed to provide information and support about sexual and reproductive health (SRH) topics. It offers a safe and supportive environment for users to learn about SRH, get general information, and be directed to appropriate healthcare resources.

## Features

- Sexual and Reproductive Health Information
- Safe and Supportive Environment
- Privacy-Focused Responses
- Healthcare Provider Referrals
- General SRH Education

## Prerequisites

- Python 3.10 or higher
- Django 5.1.2
- Pinecone Account
- OpenAI API Key
- Virtual Environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd ishema_bot_backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-django-secret-key
DEBUG=False  # Set to True for development
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Pinecone Configuration
PINECONE_URL=your-pinecone-url
PINECONE_API_KEY=your-pinecone-api-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Deployment

### Production Deployment

1. Set up your production environment variables
2. Configure your web server (Nginx/Apache)
3. Set up SSL certificates
4. Configure your domain

### Using Gunicorn (recommended for production)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run the server:
```bash
gunicorn ml_chatbot.wsgi:application
```

### Using Docker (optional)

1. Build the Docker image:
```bash
docker build -t ishema-bot .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 ishema-bot
```

## API Endpoints

- `/chat-bot/` - Main chatbot endpoint (POST)
- `/chat-bot/configuration/` - Bot configuration endpoint (GET)

## Security Considerations

- All sensitive information is handled with care
- Personal health information is not stored
- Users are directed to healthcare providers for specific medical advice
- API keys and secrets are stored in environment variables

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For support, email [your-support-email] or open an issue in the repository.
