#!/usr/bin/env python
import os
import subprocess
import sys

def main():
    # Get PORT from environment, default to 8000
    port = os.environ.get('PORT', '8000')
    
    print(f"Starting server on port {port}")
    
    # Run migrations
    print("Running migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=False)
    
    # Collect static files
    print("Collecting static files...")
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=False)
    
    # Start gunicorn
    print("Starting gunicorn...")
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        'ml_chatbot.wsgi:application'
    ]
    
    os.execvp('gunicorn', cmd)

if __name__ == '__main__':
    main()
