import React from 'react';
import { Card, Badge, Progress } from '@mantine/core';
import { IconBrain, IconTrendingUp } from '@tabler/icons-react';

const EmergenceMonitor = ({ 
  emergenceScore = 0.559, 
  capabilities = {}, 
  isMonitoring = true 
}) => {
  const getEmergenceLevel = (score) => {
    if (score >= 0.8) return { label: 'High Emergence', color: 'green' };
    if (score >= 0.6) return { label: 'Moderate Emergence', color: 'yellow' };
    if (score >= 0.4) return { label: 'Early Emergence', color: 'orange' };
    return { label: 'Low Emergence', color: 'red' };
  };

  const emergenceLevel = getEmergenceLevel(emergenceScore);

  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4 space-y-4">
      <div className="text-center">
        <div className="flex items-center gap-2 mb-2">
          <IconBrain size={20} className="text-indigo-500" />
          <h3 className="font-semibold text-gray-900">AI Monitoring</h3>
        </div>
        
        <div className="flex items-center gap-2 text-sm mb-2">
          <div className={`w-2 h-2 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-gray-600">
            {isMonitoring ? 'Online' : 'Offline'}
          </span>
        </div>
      </div>

      {/* Emergence Score */}
      <Card className="p-3 bg-gradient-to-r from-indigo-50 to-purple-50">
        <div className="flex items-center gap-2 mb-2">
          <IconTrendingUp size={16} className="text-indigo-500" />
          <span className="text-sm font-medium">Emergence Score</span>
        </div>
        
        <div className="text-2xl font-bold text-indigo-600 mb-1">
          {emergenceScore.toFixed(3)}
        </div>
        
        <Badge 
          size="sm" 
          color={emergenceLevel.color}
          variant="light"
        >
          {emergenceLevel.label}
        </Badge>
      </Card>

      {/* Capabilities */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Capabilities</h4>
        <div className="space-y-2">
          {Object.entries(capabilities).slice(0, 6).map(([key, value]) => (
            <div key={key} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-gray-600 capitalize">
                  {key.replace('_', ' ')}
                </span>
                <span className="font-medium text-gray-900">
                  {(value * 100).toFixed(0)}%
                </span>
              </div>
              <Progress 
                value={value * 100} 
                size="xs"
                color={value > 0.7 ? 'green' : value > 0.5 ? 'yellow' : 'red'}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h4>
        <div className="space-y-2">
          <button className="w-full text-left px-3 py-2 text-xs bg-blue-50 hover:bg-blue-100 rounded-md border border-blue-200 transition-colors">
            <div className="flex items-center gap-2">
              <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
              Start Training Session
            </div>
          </button>
          
          <button className="w-full text-left px-3 py-2 text-xs bg-orange-50 hover:bg-orange-100 rounded-md border border-orange-200 transition-colors">
            <div className="flex items-center gap-2">
              <div className="w-1 h-1 bg-orange-500 rounded-full"></div>
              Run Emergence Test
            </div>
          </button>
          
          <button className="w-full text-left px-3 py-2 text-xs bg-purple-50 hover:bg-purple-100 rounded-md border border-purple-200 transition-colors">
            <div className="flex items-center gap-2">
              <div className="w-1 h-1 bg-purple-500 rounded-full"></div>
              Configure Learning
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmergenceMonitor;

