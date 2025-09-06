import React from 'react';
import { Card, Badge } from '@mantine/core';
import { IconRobot, IconUser } from '@tabler/icons-react';

const ChatMessage = ({ message, isUser, timestamp, capabilities = [] }) => {
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isUser && (
        <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
          <IconRobot size={16} className="text-white" />
        </div>
      )}
      
      <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
        <Card 
          className={`p-3 ${
            isUser 
              ? 'bg-indigo-500 text-white ml-auto' 
              : 'bg-gray-50 border border-gray-200'
          }`}
          radius="md"
        >
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {message}
          </div>
          
          {!isUser && capabilities.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {capabilities.map((capability, index) => (
                <Badge 
                  key={index}
                  size="xs" 
                  variant="light" 
                  color="blue"
                >
                  {capability.replace('_', ' ')}
                </Badge>
              ))}
            </div>
          )}
        </Card>
        
        {timestamp && (
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
          <IconUser size={16} className="text-gray-600" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;

