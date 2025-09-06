import React, { useState } from 'react';
import { MantineProvider, Tabs, Button } from '@mantine/core';
import { IconMessageCircle, IconBrain, IconRobot, IconZap } from '@tabler/icons-react';
import ChatInterface from './components/EnhancedChatInterface.jsx';
import TrainingInterface from './components/TrainingInterface.jsx';
import '@mantine/core/styles.css';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <MantineProvider>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        {/* Navigation Header */}
        <div className="bg-white border-b border-gray-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo and Title */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <IconRobot size={24} className="text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">ChatBT</h1>
                  <p className="text-xs text-gray-500">AI Programming Assistant</p>
                </div>
              </div>

              {/* Navigation Tabs */}
              <Tabs value={activeTab} onChange={setActiveTab}>
                <Tabs.List>
                  <Tabs.Tab 
                    value="chat" 
                    leftSection={<IconMessageCircle size={16} />}
                  >
                    Chat Interface
                  </Tabs.Tab>
                  <Tabs.Tab 
                    value="training" 
                    leftSection={<IconBrain size={16} />}
                  >
                    Training Center
                  </Tabs.Tab>
                </Tabs.List>
              </Tabs>

              {/* Status Indicators */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-gray-600">AI Online</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <IconZap size={16} className="text-yellow-500" />
                  <span className="text-gray-600">Learning Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="h-[calc(100vh-4rem)]">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'training' && <TrainingInterface />}
        </div>
      </div>
    </MantineProvider>
  );
}

export default App;

