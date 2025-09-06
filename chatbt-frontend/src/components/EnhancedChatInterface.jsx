import React, { useState, useEffect, useRef } from 'react';
import { 
  Container, 
  Paper, 
  TextField, 
  Button, 
  Box, 
  Typography, 
  Chip, 
  Card, 
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Grid,
  Divider,
  Alert,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Send as SendIcon,
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Code as CodeIcon,
  Library as LibraryIcon,
  BugReport as BugReportIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

const EnhancedChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Fetch initial metrics
    fetchMetrics();
    
    // Set up periodic metrics updates
    const metricsInterval = setInterval(fetchMetrics, 30000); // Every 30 seconds
    
    return () => clearInterval(metricsInterval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics');
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data);
        setConnectionStatus('connected');
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setConnectionStatus('error');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message to chat
    const newUserMessage = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response to chat
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response,
        timestamp: new Date().toISOString(),
        orchestrationData: data
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Update metrics after successful response
      fetchMetrics();

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getSpecialistIcon = (specialistName) => {
    switch (specialistName) {
      case 'core_pythonic':
        return <PsychologyIcon />;
      case 'stdlib_specialist':
        return <LibraryIcon />;
      case 'code_critic':
        return <BugReportIcon />;
      default:
        return <CodeIcon />;
    }
  };

  const getSpecialistColor = (specialistName) => {
    switch (specialistName) {
      case 'core_pythonic':
        return 'primary';
      case 'stdlib_specialist':
        return 'secondary';
      case 'code_critic':
        return 'error';
      default:
        return 'default';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const formatSpecialistName = (name) => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderMessage = (message) => {
    if (message.type === 'user') {
      return (
        <Box key={message.id} sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              maxWidth: '70%', 
              bgcolor: 'primary.main', 
              color: 'primary.contrastText' 
            }}
          >
            <Typography variant="body1">{message.content}</Typography>
          </Paper>
        </Box>
      );
    }

    if (message.type === 'error') {
      return (
        <Box key={message.id} sx={{ mb: 2 }}>
          <Alert severity="error">
            {message.content}
          </Alert>
        </Box>
      );
    }

    // Bot message with orchestration data
    const { orchestrationData } = message;
    
    return (
      <Box key={message.id} sx={{ mb: 3 }}>
        <Paper elevation={1} sx={{ p: 2 }}>
          {/* Main Response */}
          <Typography variant="body1" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
            {message.content}
          </Typography>

          {/* Orchestration Details */}
          {orchestrationData && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                  <Typography variant="subtitle2">Analysis Details</Typography>
                  <Chip 
                    label={orchestrationData.query_type} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                  <Chip 
                    label={orchestrationData.response_mode} 
                    size="small" 
                    color="secondary" 
                    variant="outlined"
                  />
                  <Box sx={{ flexGrow: 1 }} />
                  <Tooltip title={`Confidence: ${(orchestrationData.confidence * 100).toFixed(1)}%`}>
                    <Chip 
                      label={`${(orchestrationData.confidence * 100).toFixed(1)}%`}
                      size="small"
                      color={getConfidenceColor(orchestrationData.confidence)}
                      icon={<CheckCircleIcon />}
                    />
                  </Tooltip>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {/* Specialists Used */}
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Specialists Consulted
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {orchestrationData.specialist_details?.map((specialist, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Badge 
                                badgeContent={`${(specialist.confidence * 100).toFixed(0)}%`}
                                color={getConfidenceColor(specialist.confidence)}
                              >
                                <Chip
                                  icon={getSpecialistIcon(specialist.name)}
                                  label={formatSpecialistName(specialist.name)}
                                  color={getSpecialistColor(specialist.name)}
                                  variant="outlined"
                                />
                              </Badge>
                              <Typography variant="caption" color="text.secondary">
                                {specialist.processing_time?.toFixed(3)}s
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Performance Metrics */}
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Performance
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Processing Time
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <SpeedIcon fontSize="small" />
                              <Typography variant="body1">
                                {orchestrationData.processing_time?.toFixed(3)}s
                              </Typography>
                            </Box>
                          </Box>
                          
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Overall Confidence
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={orchestrationData.confidence * 100}
                              color={getConfidenceColor(orchestrationData.confidence)}
                              sx={{ mt: 1 }}
                            />
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Synthesis Notes */}
                  {orchestrationData.synthesis_notes && orchestrationData.synthesis_notes.length > 0 && (
                    <Grid item xs={12}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Analysis Process
                          </Typography>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            {orchestrationData.synthesis_notes.map((note, index) => (
                              <Typography key={index} variant="body2" color="text.secondary">
                                • {note}
                              </Typography>
                            ))}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      {/* Header with System Status */}
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h4" component="h1">
            ChatBT - Enhanced AI Assistant
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label={connectionStatus === 'connected' ? 'Online' : 'Offline'}
              color={connectionStatus === 'connected' ? 'success' : 'error'}
              icon={connectionStatus === 'connected' ? <CheckCircleIcon /> : <ErrorIcon />}
            />
            {systemMetrics && (
              <Tooltip title={`${systemMetrics.system_metrics.total_queries} queries processed`}>
                <Chip 
                  label={`${systemMetrics.specialists_loaded?.length || 0} Specialists`}
                  color="primary"
                  icon={<PsychologyIcon />}
                />
              </Tooltip>
            )}
          </Box>
        </Box>
        
        {systemMetrics && (
          <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Typography variant="body2" color="text.secondary">
              Uptime: {systemMetrics.system_metrics.uptime_formatted}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg Response: {systemMetrics.system_metrics.avg_response_time?.toFixed(3)}s
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Queries: {systemMetrics.system_metrics.total_queries}
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Chat Messages */}
      <Paper elevation={1} sx={{ height: '60vh', overflow: 'auto', p: 2, mb: 2 }}>
        {messages.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%',
            textAlign: 'center'
          }}>
            <PsychologyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Welcome to ChatBT Enhanced!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              I'm powered by multiple AI specialists:
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
              <Chip icon={<PsychologyIcon />} label="Core Pythonic" color="primary" />
              <Chip icon={<LibraryIcon />} label="Standard Library" color="secondary" />
              <Chip icon={<BugReportIcon />} label="Code Critic" color="error" />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Ask me anything about Python programming!
            </Typography>
          </Box>
        ) : (
          <>
            {messages.map(renderMessage)}
            <div ref={messagesEndRef} />
          </>
        )}
      </Paper>

      {/* Input Area */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about Python programming, code analysis, or library usage..."
            disabled={isLoading}
            variant="outlined"
          />
          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            sx={{ minWidth: 'auto', px: 2 }}
          >
            {isLoading ? <LinearProgress /> : <SendIcon />}
          </Button>
        </Box>
        
        {isLoading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              Consulting specialists...
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default EnhancedChatInterface;

