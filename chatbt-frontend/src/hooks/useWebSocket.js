import { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';

/**
 * Custom hook for WebSocket connections with automatic reconnection
 * Replaces polling with real-time updates
 */
export const useWebSocket = (url = '', options = {}) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = options.maxReconnectAttempts || 5;
  const reconnectDelay = options.reconnectDelay || 1000;

  const connect = useCallback(() => {
    try {
      const socketInstance = io(url, {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true,
        ...options
      });

      socketInstance.on('connect', () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
      });

      socketInstance.on('disconnect', (reason) => {
        console.log('WebSocket disconnected:', reason);
        setIsConnected(false);
        
        // Attempt reconnection for certain disconnect reasons
        if (reason === 'io server disconnect') {
          // Server initiated disconnect, don't reconnect automatically
          setConnectionError('Server disconnected');
        } else {
          // Client-side disconnect or network issue, attempt reconnection
          attemptReconnect();
        }
      });

      socketInstance.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        setConnectionError(error.message);
        setIsConnected(false);
        attemptReconnect();
      });

      // General message handler
      socketInstance.onAny((eventName, data) => {
        setLastMessage({ event: eventName, data, timestamp: Date.now() });
      });

      setSocket(socketInstance);
      return socketInstance;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionError(error.message);
      return null;
    }
  }, [url, options]);

  const attemptReconnect = useCallback(() => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      setConnectionError('Max reconnection attempts reached');
      return;
    }

    const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current); // Exponential backoff
    
    reconnectTimeoutRef.current = setTimeout(() => {
      console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
      reconnectAttemptsRef.current++;
      connect();
    }, delay);
  }, [connect, maxReconnectAttempts, reconnectDelay]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socket) {
      socket.disconnect();
      setSocket(null);
    }
    
    setIsConnected(false);
    setConnectionError(null);
  }, [socket]);

  const emit = useCallback((event, data) => {
    if (socket && isConnected) {
      socket.emit(event, data);
      return true;
    }
    console.warn('Cannot emit: WebSocket not connected');
    return false;
  }, [socket, isConnected]);

  const subscribe = useCallback((event, callback) => {
    if (socket) {
      socket.on(event, callback);
      return () => socket.off(event, callback);
    }
    return () => {};
  }, [socket]);

  // Initialize connection on mount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    socket,
    isConnected,
    connectionError,
    lastMessage,
    connect,
    disconnect,
    emit,
    subscribe,
    reconnectAttempts: reconnectAttemptsRef.current
  };
};

/**
 * Hook specifically for ChatBT real-time updates
 */
export const useChatBTWebSocket = () => {
  const {
    socket,
    isConnected,
    connectionError,
    lastMessage,
    emit,
    subscribe
  } = useWebSocket(''); // Use relative URL for WebSocket

  const [aiStatus, setAiStatus] = useState(null);
  const [trainingProgress, setTrainingProgress] = useState(null);
  const [emergenceData, setEmergenceData] = useState(null);
  const [chatResponse, setChatResponse] = useState(null);

  // Subscribe to AI state updates
  useEffect(() => {
    if (!socket) return;

    const unsubscribers = [
      subscribe('ai_state_update', (data) => {
        setAiStatus(prev => ({ ...prev, ...data }));
      }),

      subscribe('training_started', (data) => {
        setTrainingProgress(prev => ({ ...prev, status: 'started', ...data }));
      }),

      subscribe('training_progress', (data) => {
        setTrainingProgress(prev => ({ ...prev, ...data }));
      }),

      subscribe('training_completed', (data) => {
        setTrainingProgress(prev => ({ ...prev, status: 'completed', ...data }));
      }),

      subscribe('training_stopped', (data) => {
        setTrainingProgress(prev => ({ ...prev, status: 'stopped', ...data }));
      }),

      subscribe('emergence_test_completed', (data) => {
        setEmergenceData(data);
      }),

      subscribe('chat_response', (data) => {
        setChatResponse(data);
      }),

      subscribe('monitoring_toggled', (data) => {
        setAiStatus(prev => ({ ...prev, is_monitoring: data.is_monitoring }));
      })
    ];

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [socket, subscribe]);

  // Subscribe to training updates
  const subscribeToTraining = useCallback(() => {
    return emit('subscribe_training');
  }, [emit]);

  // Subscribe to emergence monitoring
  const subscribeToEmergence = useCallback(() => {
    return emit('subscribe_emergence');
  }, [emit]);

  return {
    isConnected,
    connectionError,
    aiStatus,
    trainingProgress,
    emergenceData,
    chatResponse,
    subscribeToTraining,
    subscribeToEmergence,
    lastMessage
  };
};

/**
 * Hook for training progress with WebSocket instead of polling
 */
export const useTrainingProgress = () => {
  const { trainingProgress, subscribeToTraining, isConnected } = useChatBTWebSocket();
  const [isSubscribed, setIsSubscribed] = useState(false);

  useEffect(() => {
    if (isConnected && !isSubscribed) {
      const success = subscribeToTraining();
      if (success) {
        setIsSubscribed(true);
      }
    }
  }, [isConnected, isSubscribed, subscribeToTraining]);

  return {
    progress: trainingProgress?.progress || 0,
    status: trainingProgress?.status || 'idle',
    isTraining: trainingProgress?.status === 'started' || trainingProgress?.status === 'training',
    lastUpdate: trainingProgress?.timestamp,
    isConnected
  };
};

/**
 * Hook for emergence monitoring with WebSocket
 */
export const useEmergenceMonitoring = () => {
  const { emergenceData, subscribeToEmergence, isConnected, aiStatus } = useChatBTWebSocket();
  const [isSubscribed, setIsSubscribed] = useState(false);

  useEffect(() => {
    if (isConnected && !isSubscribed) {
      const success = subscribeToEmergence();
      if (success) {
        setIsSubscribed(true);
      }
    }
  }, [isConnected, isSubscribed, subscribeToEmergence]);

  return {
    emergenceScore: aiStatus?.emergence_score || emergenceData?.emergence_score || 0.559,
    capabilities: aiStatus?.capabilities || {},
    isMonitoring: aiStatus?.is_monitoring ?? true,
    lastTest: emergenceData,
    isConnected
  };
};

export default useWebSocket;

