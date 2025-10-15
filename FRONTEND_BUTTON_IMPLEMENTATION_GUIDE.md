# ISHEMA RYANJYE Chatbot - Button Implementation Guide

## Overview
Implement startup buttons for the ISHEMA RYANJYE chatbot that fetch configuration from the Django backend and provide language/topic selection.

## API Endpoint
**Configuration URL:** `http://127.0.0.1:8000/chat-bot-config/`

**Response Format:**
```json
{
  "StartUpMessage": "Muraho! Welcome to ISHEMA RYANJYE. I'm here to help you with health information and our card game. Choose your language or topic below to get started!",
  "commonButtons": [
    {
      "buttonText": "English",
      "buttonPrompt": "I want to continue in English"
    },
    {
      "buttonText": "Kinyarwanda", 
      "buttonPrompt": "Nshaka gukomeza mu Kinyarwanda"
    },
    {
      "buttonText": "Ishema card game",
      "buttonPrompt": "Tell me about the ISHEMA RYANJYE card game"
    },
    {
      "buttonText": "SRH and Mental health support",
      "buttonPrompt": "What sexual and reproductive health and mental health services do you offer?"
    }
  ]
}
```

## Implementation

### 1. React Component with Hooks
```jsx
import { useState, useEffect } from 'react';

const StartupButtons = ({ onButtonClick, show }) => {
  const [botConfig, setBotConfig] = useState(null);

  useEffect(() => {
    const fetchBotConfig = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/chat-bot-config/');
        const config = await response.json();
        setBotConfig(config);
      } catch (error) {
        console.error('Failed to fetch bot config:', error);
      }
    };
    
    fetchBotConfig();
  }, []);

  if (!show || !botConfig?.commonButtons) return null;

  return (
    <div className="startup-container">
      <div className="welcome-message">
        {botConfig.StartUpMessage}
      </div>
      <div className="startup-buttons">
        {botConfig.commonButtons.map((button, index) => (
          <button
            key={index}
            className="startup-button"
            onClick={() => onButtonClick(button.buttonPrompt)}
          >
            {button.buttonText}
          </button>
        ))}
      </div>
    </div>
  );
};

// Usage in main component
const ChatComponent = () => {
  const [showButtons, setShowButtons] = useState(true);
  const [messages, setMessages] = useState([]);

  const handleButtonClick = (buttonPrompt) => {
    setShowButtons(false);
    const newMessages = [...messages, { role: 'user', content: buttonPrompt }];
    setMessages(newMessages);
    // Send to your streaming chat API here
  };

  return (
    <div className="chat-container">
      <StartupButtons 
        onButtonClick={handleButtonClick}
        show={showButtons}
      />
      {/* Your existing chat messages */}
    </div>
  );
};

export default ChatComponent;
```

### 2. CSS Styling
```css
.startup-container {
  padding: 20px;
  text-align: center;
}

.welcome-message {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.5;
}

.startup-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
  margin: 0 auto;
}

.startup-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.startup-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.startup-button:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .startup-buttons {
    max-width: 100%;
    padding: 0 10px;
  }
  
  .startup-button {
    padding: 12px 20px;
    font-size: 14px;
  }
}
```

### 3. Tailwind CSS Alternative
```jsx
const StartupButtons = ({ onButtonClick, show }) => {
  const [botConfig, setBotConfig] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/chat-bot-config/')
      .then(res => res.json())
      .then(setBotConfig)
      .catch(console.error);
  }, []);

  if (!show || !botConfig?.commonButtons) return null;

  return (
    <div className="p-6 text-center">
      <div className="text-gray-700 mb-6 text-base leading-relaxed">
        {botConfig.StartUpMessage}
      </div>
      <div className="flex flex-col gap-3 max-w-md mx-auto">
        {botConfig.commonButtons.map((button, index) => (
          <button
            key={index}
            onClick={() => onButtonClick(button.buttonPrompt)}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-purple-600 hover:to-blue-500 text-white font-semibold py-3.5 px-6 rounded-full transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg active:translate-y-0 shadow-md"
          >
            {button.buttonText}
          </button>
        ))}
      </div>
    </div>
  );
};
```

### 4. Vue.js Version
```vue
<template>
  <div v-if="show && botConfig?.commonButtons" class="startup-container">
    <div class="welcome-message">
      {{ botConfig.StartUpMessage }}
    </div>
    <div class="startup-buttons">
      <button
        v-for="(button, index) in botConfig.commonButtons"
        :key="index"
        class="startup-button"
        @click="$emit('buttonClick', button.buttonPrompt)"
      >
        {{ button.buttonText }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'StartupButtons',
  props: ['show'],
  emits: ['buttonClick'],
  setup() {
    const botConfig = ref(null);

    onMounted(async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/chat-bot-config/');
        botConfig.value = await response.json();
      } catch (error) {
        console.error('Failed to fetch bot config:', error);
      }
    });

    return { botConfig };
  }
};
</script>
```

### 5. Next.js Integration
```jsx
// pages/chat.js or components/Chat.js
import { useState, useEffect } from 'react';

export default function Chat() {
  const [botConfig, setBotConfig] = useState(null);
  const [showButtons, setShowButtons] = useState(true);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Fetch bot configuration on component mount
    const fetchConfig = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/chat-bot-config/');
        const config = await response.json();
        setBotConfig(config);
      } catch (error) {
        console.error('Failed to fetch bot config:', error);
      }
    };

    fetchConfig();
  }, []);

  const handleButtonClick = async (buttonPrompt) => {
    setShowButtons(false);
    
    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: buttonPrompt }];
    setMessages(newMessages);
    
    // Send to streaming chat API
    try {
      const response = await fetch('http://127.0.0.1:8000/chat-bot/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          model: 'gpt-4o'
        })
      });

      // Handle streaming response here
      // Implementation depends on your streaming setup
      
    } catch (error) {
      console.error('Chat API error:', error);
    }
  };

  if (!botConfig) return <div>Loading...</div>;

  return (
    <div className="chat-container">
      {showButtons && (
        <div className="startup-container">
          <div className="welcome-message">
            {botConfig.StartUpMessage}
          </div>
          <div className="startup-buttons">
            {botConfig.commonButtons.map((button, index) => (
              <button
                key={index}
                className="startup-button"
                onClick={() => handleButtonClick(button.buttonPrompt)}
              >
                {button.buttonText}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Chat messages display */}
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Implementation Checklist
- [ ] Fetch configuration from `/chat-bot-config/` endpoint
- [ ] Display welcome message from `StartUpMessage`
- [ ] Render 4 buttons from `commonButtons` array
- [ ] Handle button clicks to send `buttonPrompt` to chat
- [ ] Hide buttons after user clicks one
- [ ] Style buttons with hover/active states
- [ ] Ensure mobile responsiveness
- [ ] Test with your existing streaming chat API

## Button Behavior
1. **Load**: Buttons appear with welcome message
2. **Click**: Button sends its `buttonPrompt` to chat and hides all buttons
3. **Response**: Chatbot responds based on the selected prompt
4. **Language Selection**: "English"/"Kinyarwanda" buttons set conversation language
5. **Topic Selection**: "Ishema card game"/"SRH and Mental health support" buttons start topic-specific conversations

## Expected Visual Layout
```
┌─────────────────────────────────────┐
│  Muraho! Welcome to ISHEMA RYANJYE. │
│  I'm here to help you with health   │
│  information and our card game.     │
│  Choose your language or topic      │
│  below to get started!              │
├─────────────────────────────────────┤
│  [     English     ]               │
│  [   Kinyarwanda   ]               │
│  [ Ishema card game ]              │
│  [ SRH and Mental health support ] │
└─────────────────────────────────────┘
```

## Testing
Test the implementation by:
1. Loading the page - buttons should appear
2. Clicking "English" - should send "I want to continue in English"
3. Clicking "Kinyarwanda" - should send "Nshaka gukomeza mu Kinyarwanda"
4. Clicking "Ishema card game" - should send game-related prompt
5. Clicking "SRH and Mental health support" - should send health-related prompt
6. Verify buttons hide after selection
7. Confirm chat API receives the correct prompt

Copy this entire document and share with your frontend team for complete implementation guidance.