#!/usr/bin/env python
import os
import subprocess
import sys

def main():
    # Get PORT from environment, default to 8000
    port = os.environ.get('PORT', '8000')
    
    print(f"Environment PORT variable: {os.environ.get('PORT', 'NOT SET')}")
    print(f"Using port: {port}")
    print(f"Port type: {type(port)}")
    
    # Validate port
    try:
        port_int = int(port)
        if port_int <= 0 or port_int > 65535:
            print(f"Invalid port number: {port_int}, using default 8000")
            port = '8000'
    except ValueError:
        print(f"Port is not a valid integer: {port}, using default 8000")
        port = '8000'
    
    print(f"Final port to use: {port}")
    
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
