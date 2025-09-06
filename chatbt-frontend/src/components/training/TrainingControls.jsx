import React from 'react';
import { Button, Card, Progress, Badge } from '@mantine/core';
import { IconPlay, IconPause, IconStop, IconBrain, IconSettings } from '@tabler/icons-react';

const TrainingControls = ({ 
  isTraining = false, 
  progress = 0, 
  onStartTraining, 
  onStopTraining, 
  onRunEmergenceTest, 
  onConfigureLearning,
  trainingStatus = 'idle'
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'training': return 'blue';
      case 'completed': return 'green';
      case 'error': return 'red';
      case 'paused': return 'yellow';
      default: return 'gray';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'training': return 'Training in Progress';
      case 'completed': return 'Training Completed';
      case 'error': return 'Training Error';
      case 'paused': return 'Training Paused';
      case 'starting': return 'Starting Training...';
      default: return 'Ready to Train';
    }
  };

  return (
    <Card className="p-6 bg-white border border-gray-200" radius="md">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Training Controls</h3>
        <Badge 
          color={getStatusColor(trainingStatus)}
          variant="light"
          size="sm"
        >
          {getStatusLabel(trainingStatus)}
        </Badge>
      </div>

      {/* Training Progress */}
      {(isTraining || progress > 0) && (
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Training Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress 
            value={progress} 
            size="md" 
            color="blue"
            animated={isTraining}
          />
        </div>
      )}

      {/* Control Buttons */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <Button
          onClick={isTraining ? onStopTraining : onStartTraining}
          disabled={trainingStatus === 'starting'}
          loading={trainingStatus === 'starting'}
          color={isTraining ? 'red' : 'blue'}
          variant={isTraining ? 'outline' : 'filled'}
          leftSection={isTraining ? <IconStop size={16} /> : <IconPlay size={16} />}
          fullWidth
        >
          {isTraining ? 'Stop Training' : 'Start Training'}
        </Button>

        <Button
          onClick={onRunEmergenceTest}
          disabled={isTraining}
          variant="outline"
          color="orange"
          leftSection={<IconBrain size={16} />}
          fullWidth
        >
          Emergence Test
        </Button>
      </div>

      {/* Configuration Button */}
      <Button
        onClick={onConfigureLearning}
        variant="light"
        color="purple"
        leftSection={<IconSettings size={16} />}
        fullWidth
      >
        Configure Learning
      </Button>
    </Card>
  );
};

export default TrainingControls;

