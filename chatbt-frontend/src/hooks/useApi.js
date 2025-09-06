import { useState, useEffect } from 'react';

// Use relative URLs that work with Vite proxy in development and production
const API_BASE_URL = '/api';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  return { apiCall, loading, error };
};

export const useChatApi = () => {
  const { apiCall, loading, error } = useApi();

  const sendMessage = async (message) => {
    return await apiCall('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  };

  const getStatus = async () => {
    return await apiCall('/status');
  };

  const toggleMonitoring = async () => {
    return await apiCall('/monitoring/toggle', {
      method: 'POST',
    });
  };

  return {
    sendMessage,
    getStatus,
    toggleMonitoring,
    loading,
    error,
  };
};

export const useTrainingApi = () => {
  const { apiCall, loading, error } = useApi();

  const startTraining = async () => {
    return await apiCall('/training/start', {
      method: 'POST',
    });
  };

  const stopTraining = async () => {
    return await apiCall('/training/stop', {
      method: 'POST',
    });
  };

  const getTrainingProgress = async () => {
    return await apiCall('/training/progress');
  };

  const getLearningGoals = async () => {
    return await apiCall('/learning/goals');
  };

  const getKnowledgeGaps = async () => {
    return await apiCall('/learning/gaps');
  };

  const createLearningGoal = async (goalData) => {
    return await apiCall('/learning/goals', {
      method: 'POST',
      body: JSON.stringify(goalData),
    });
  };

  const runEmergenceTest = async () => {
    return await apiCall('/emergence/test', {
      method: 'POST',
    });
  };

  return {
    startTraining,
    stopTraining,
    getTrainingProgress,
    getLearningGoals,
    getKnowledgeGaps,
    createLearningGoal,
    runEmergenceTest,
    loading,
    error,
  };
};

