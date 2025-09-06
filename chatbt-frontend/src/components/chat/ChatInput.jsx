import React, { useState } from 'react';
import { TextInput, Button } from '@mantine/core';
import { IconSend } from '@tabler/icons-react';

const ChatInput = ({ onSendMessage, isLoading = false, placeholder = "Type your message..." }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 bg-white border-t border-gray-200">
      <TextInput
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={isLoading}
        className="flex-1"
        size="md"
        radius="md"
      />
      <Button
        type="submit"
        disabled={!message.trim() || isLoading}
        loading={isLoading}
        size="md"
        radius="md"
        className="bg-indigo-500 hover:bg-indigo-600"
      >
        <IconSend size={16} />
      </Button>
    </form>
  );
};

export default ChatInput;

