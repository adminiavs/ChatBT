import React, { useState, useEffect } from 'react';
import { Tabs } from '@mantine/core';
import { useTrainingApi } from '../hooks/useApi.js';
import { useTrainingProgress, useEmergenceMonitoring } from '../hooks/useWebSocket.js';
import TrainingControls from './training/TrainingControls.jsx';
import LearningGoals from './training/LearningGoals.jsx';

const TrainingInterface = () => {
  const [activeTab, setActiveTab] = useState('training');
  const [goals, setGoals] = useState([]);
  const [knowledgeGaps, setKnowledgeGaps] = useState([]);
  const [emergenceTestResults, setEmergenceTestResults] = useState(null);

  const {
    startTraining,
    stopTraining,
    getTrainingProgress,
    getLearningGoals,
    createLearningGoal,
    getKnowledgeGaps,
    runEmergenceTest
  } = useTrainingApi();

  const { progress, status, isTraining } = useTrainingProgress();
  const { emergenceScore, capabilities, lastTest } = useEmergenceMonitoring();

  // Load initial data
  useEffect(() => {
    loadLearningGoals();
    loadKnowledgeGaps();
  }, []);

  // Update emergence test results from WebSocket
  useEffect(() => {
    if (lastTest) {
      setEmergenceTestResults(lastTest);
    }
  }, [lastTest]);

  const loadLearningGoals = async () => {
    try {
      const response = await getLearningGoals();
      setGoals(response.goals || []);
    } catch (error) {
      console.error('Failed to load learning goals:', error);
      // Fallback to default goals
      setGoals([
        {
          id: 1,
          name: 'Master Advanced Pandas Operations',
          priority: 0.9,
          progress: 0.65,
          status: 'active',
          description: 'Develop comprehensive understanding of advanced pandas operations including multi-indexing, groupby operations, and performance optimization.'
        },
        {
          id: 2,
          name: 'Improve Code Quality Assessment',
          priority: 0.8,
          progress: 0.45,
          status: 'planned',
          description: 'Enhance ability to assess and improve code quality, including best practices, maintainability, and performance.'
        },
        {
          id: 3,
          name: 'Cross-Domain Knowledge Transfer',
          priority: 0.7,
          progress: 0.30,
          status: 'planned',
          description: 'Develop skills to transfer knowledge between different programming domains and frameworks.'
        }
      ]);
    }
  };

  const loadKnowledgeGaps = async () => {
    try {
      const response = await getKnowledgeGaps();
      setKnowledgeGaps(response.gaps || []);
    } catch (error) {
      console.error('Failed to load knowledge gaps:', error);
      // Fallback to default gaps
      setKnowledgeGaps([
        { domain: 'python_core', topic: 'metaclasses', severity: 0.7 },
        { domain: 'performance', topic: 'parallel_processing', severity: 0.6 },
        { domain: 'web_development', topic: 'async_frameworks', severity: 0.8 },
        { domain: 'machine_learning', topic: 'model_deployment', severity: 0.5 }
      ]);
    }
  };

  const handleStartTraining = async () => {
    try {
      await startTraining();
    } catch (error) {
      console.error('Failed to start training:', error);
    }
  };

  const handleStopTraining = async () => {
    try {
      await stopTraining();
    } catch (error) {
      console.error('Failed to stop training:', error);
    }
  };

  const handleRunEmergenceTest = async () => {
    try {
      const results = await runEmergenceTest();
      setEmergenceTestResults(results.test_results);
    } catch (error) {
      console.error('Failed to run emergence test:', error);
    }
  };

  const handleConfigureLearning = () => {
    setActiveTab('goals');
  };

  const handleCreateGoal = async (goalData) => {
    try {
      const response = await createLearningGoal(goalData);
      setGoals(prev => [...prev, response.goal]);
    } catch (error) {
      console.error('Failed to create learning goal:', error);
    }
  };

  const handleUpdateGoal = async (goalId, updates) => {
    // Implementation for updating goals
    setGoals(prev => prev.map(goal => 
      goal.id === goalId ? { ...goal, ...updates } : goal
    ));
  };

  return (
    <div className="h-full bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Training Center</h1>
          <p className="text-gray-600">
            Manage AI training sessions, learning goals, and emergence monitoring
          </p>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tabs.List className="mb-6">
            <Tabs.Tab value="training">Training Controls</Tabs.Tab>
            <Tabs.Tab value="goals">Learning Goals</Tabs.Tab>
            <Tabs.Tab value="emergence">Emergence Analysis</Tabs.Tab>
            <Tabs.Tab value="knowledge">Knowledge Gaps</Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="training">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TrainingControls
                isTraining={isTraining}
                progress={progress}
                trainingStatus={status}
                onStartTraining={handleStartTraining}
                onStopTraining={handleStopTraining}
                onRunEmergenceTest={handleRunEmergenceTest}
                onConfigureLearning={handleConfigureLearning}
              />
              
              {/* Training Metrics */}
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Metrics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Emergence Score</span>
                    <span className="font-semibold text-indigo-600">
                      {emergenceScore.toFixed(3)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Active Goals</span>
                    <span className="font-semibold">
                      {goals.filter(g => g.status === 'active').length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Knowledge Gaps</span>
                    <span className="font-semibold">
                      {knowledgeGaps.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Training Progress</span>
                    <span className="font-semibold">
                      {Math.round(progress)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Tabs.Panel>

          <Tabs.Panel value="goals">
            <LearningGoals
              goals={goals}
              onCreateGoal={handleCreateGoal}
              onUpdateGoal={handleUpdateGoal}
            />
          </Tabs.Panel>

          <Tabs.Panel value="emergence">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Emergence Analysis</h3>
              
              {emergenceTestResults ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-indigo-50 rounded-lg">
                      <div className="text-2xl font-bold text-indigo-600">
                        {emergenceTestResults.emergence_score?.toFixed(3) || emergenceScore.toFixed(3)}
                      </div>
                      <div className="text-sm text-gray-600">Emergence Score</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {emergenceTestResults.novel_behaviors?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Novel Behaviors</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">
                        {emergenceTestResults.learning_patterns?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Learning Patterns</div>
                    </div>
                  </div>

                  {emergenceTestResults.novel_behaviors && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Novel Behaviors Detected</h4>
                      <div className="space-y-2">
                        {emergenceTestResults.novel_behaviors.map((behavior, index) => (
                          <div key={index} className="p-3 bg-gray-50 rounded-lg">
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-medium text-gray-900">
                                {behavior.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </span>
                              <span className="text-sm text-gray-500">
                                {(behavior.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">{behavior.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No emergence test results available</p>
                  <p className="text-sm">Run an emergence test to see detailed analysis</p>
                </div>
              )}
            </div>
          </Tabs.Panel>

          <Tabs.Panel value="knowledge">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Knowledge Gaps</h3>
              
              {knowledgeGaps.length > 0 ? (
                <div className="space-y-3">
                  {knowledgeGaps.map((gap, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <span className="font-medium text-gray-900 capitalize">
                            {gap.domain.replace('_', ' ')}
                          </span>
                          <span className="text-gray-500 ml-2">•</span>
                          <span className="text-gray-700 ml-2 capitalize">
                            {gap.topic.replace('_', ' ')}
                          </span>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          gap.severity >= 0.7 
                            ? 'bg-red-100 text-red-800' 
                            : gap.severity >= 0.5 
                            ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {gap.severity >= 0.7 ? 'High' : gap.severity >= 0.5 ? 'Medium' : 'Low'} Priority
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            gap.severity >= 0.7 ? 'bg-red-500' : gap.severity >= 0.5 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${gap.severity * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No knowledge gaps identified</p>
                  <p className="text-sm">The AI system appears to have comprehensive knowledge coverage</p>
                </div>
              )}
            </div>
          </Tabs.Panel>
        </Tabs>
      </div>
    </div>
  );
};

export default TrainingInterface;

