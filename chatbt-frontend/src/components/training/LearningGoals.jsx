import React, { useState } from 'react';
import { Card, Badge, Progress, Button, TextInput, Textarea } from '@mantine/core';
import { IconTarget, IconPlus, IconCheck, IconClock } from '@tabler/icons-react';

const LearningGoals = ({ goals = [], onCreateGoal, onUpdateGoal }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newGoal, setNewGoal] = useState({ name: '', description: '', priority: 0.5 });

  const handleCreateGoal = () => {
    if (newGoal.name.trim()) {
      onCreateGoal(newGoal);
      setNewGoal({ name: '', description: '', priority: 0.5 });
      setShowCreateForm(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <IconCheck size={16} className="text-green-500" />;
      case 'active': return <IconTarget size={16} className="text-blue-500" />;
      case 'planned': return <IconClock size={16} className="text-gray-500" />;
      default: return <IconClock size={16} className="text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'active': return 'blue';
      case 'planned': return 'gray';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority) => {
    if (priority >= 0.8) return 'red';
    if (priority >= 0.6) return 'orange';
    if (priority >= 0.4) return 'yellow';
    return 'gray';
  };

  return (
    <Card className="p-6 bg-white border border-gray-200" radius="md">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Learning Goals</h3>
        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          size="sm"
          variant="light"
          leftSection={<IconPlus size={16} />}
        >
          Add Goal
        </Button>
      </div>

      {/* Create Goal Form */}
      {showCreateForm && (
        <Card className="p-4 mb-4 bg-gray-50 border border-gray-200" radius="md">
          <div className="space-y-3">
            <TextInput
              label="Goal Name"
              placeholder="Enter learning goal..."
              value={newGoal.name}
              onChange={(e) => setNewGoal({ ...newGoal, name: e.target.value })}
            />
            
            <Textarea
              label="Description"
              placeholder="Describe the learning objective..."
              value={newGoal.description}
              onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
              rows={2}
            />
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority: {(newGoal.priority * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={newGoal.priority}
                onChange={(e) => setNewGoal({ ...newGoal, priority: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleCreateGoal} size="sm">
                Create Goal
              </Button>
              <Button 
                onClick={() => setShowCreateForm(false)} 
                variant="outline" 
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Goals List */}
      <div className="space-y-3">
        {goals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <IconTarget size={48} className="mx-auto mb-2 text-gray-300" />
            <p>No learning goals yet</p>
            <p className="text-sm">Create your first goal to get started</p>
          </div>
        ) : (
          goals.map((goal) => (
            <Card key={goal.id} className="p-4 border border-gray-200" radius="md">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(goal.status)}
                  <h4 className="font-medium text-gray-900">{goal.name}</h4>
                </div>
                <div className="flex gap-2">
                  <Badge 
                    size="xs" 
                    color={getPriorityColor(goal.priority)}
                    variant="light"
                  >
                    P{Math.round(goal.priority * 10)}
                  </Badge>
                  <Badge 
                    size="xs" 
                    color={getStatusColor(goal.status)}
                    variant="light"
                  >
                    {goal.status}
                  </Badge>
                </div>
              </div>
              
              {goal.description && (
                <p className="text-sm text-gray-600 mb-3">{goal.description}</p>
              )}
              
              <div className="space-y-2">
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Progress</span>
                  <span>{Math.round((goal.progress || 0) * 100)}%</span>
                </div>
                <Progress 
                  value={(goal.progress || 0) * 100} 
                  size="sm"
                  color={getStatusColor(goal.status)}
                />
              </div>
            </Card>
          ))
        )}
      </div>
    </Card>
  );
};

export default LearningGoals;

