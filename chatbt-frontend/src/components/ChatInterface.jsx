import React, { useState, useEffect, useRef } from 'react';
import { ScrollArea } from '@mantine/core';
import { useApi } from '../hooks/useApi.js';
import { useChatBTWebSocket } from '../hooks/useWebSocket.js';
import ChatMessage from './chat/ChatMessage.jsx';
import ChatInput from './chat/ChatInput.jsx';
import EmergenceMonitor from './monitoring/EmergenceMonitor.jsx';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm ChatBT, your AI programming assistant with Pandas expertise and self-directed learning capabilities. How can I help you today?",
      isUser: false,
      timestamp: new Date().toISOString(),
      capabilities: ['python_knowledge', 'domain_expertise']
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { sendMessage } = useApi();
  const { aiStatus, chatResponse, isConnected } = useChatBTWebSocket();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle WebSocket chat responses
  useEffect(() => {
    if (chatResponse) {
      setMessages(prev => [...prev, {
        id: Date.now() + Math.random(),
        text: chatResponse.message,
        isUser: false,
        timestamp: chatResponse.timestamp,
        capabilities: chatResponse.capabilities_used || []
      }]);
      setIsLoading(false);
    }
  }, [chatResponse]);

  const handleSendMessage = async (messageText) => {
    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      text: messageText,
      isUser: true,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(messageText);
      
      // If WebSocket didn't handle the response, add it manually
      if (!isConnected) {
        setMessages(prev => [...prev, {
          id: Date.now() + Math.random(),
          text: response.response,
          isUser: false,
          timestamp: response.timestamp,
          capabilities: response.capabilities_used || []
        }]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + Math.random(),
        text: "Sorry, I encountered an error processing your message. Please try again.",
        isUser: false,
        timestamp: new Date().toISOString(),
        capabilities: []
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Emergence Monitor Sidebar */}
      <EmergenceMonitor
        emergenceScore={aiStatus?.emergence_score || 0.559}
        capabilities={aiStatus?.capabilities || {
          python_knowledge: 0.735,
          code_quality: 0.727,
          problem_solving: 0.630,
          learning_efficiency: 0.673,
          knowledge_transfer: 0.697,
          creativity: 0.509,
          debugging: 0.670,
          optimization: 0.624,
          architecture_design: 0.598,
          domain_expertise: 0.598
        }}
        isMonitoring={aiStatus?.is_monitoring ?? true}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">ChatBT</h2>
              <p className="text-sm text-gray-500">AI Programming Assistant with Pandas Expertise</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                <span className="text-gray-600">
                  {isConnected ? 'Online' : 'Offline'}
                </span>
              </div>
              {aiStatus?.emergence_score && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-600">Emergence:</span>
                  <span className="font-medium text-indigo-600">
                    {aiStatus.emergence_score.toFixed(3)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp}
                capabilities={message.capabilities}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Chat Input */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          placeholder="Ask me about Python, Pandas, or my learning capabilities..."
        />

        {/* Status Bar */}
        <div className="bg-gray-50 border-t border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span>Monitoring: {aiStatus?.is_monitoring ? 'Active' : 'Inactive'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

