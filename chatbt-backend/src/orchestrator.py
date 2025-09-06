"""
Orchestrator Engine - Coordinates Multiple Specialists for Comprehensive Python Assistance

This orchestrator manages the collaboration between:
- Core Pythonic Specialist: Python fundamentals and best practices
- Standard Library Specialist: Standard library expertise and optimization
- Code Critic Specialist: Error detection and code quality analysis

The orchestrator determines which specialists to consult based on the query type,
coordinates their responses, and synthesizes comprehensive answers.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import re
import ast

from specialists.core_pythonic_specialist import CorePythonicSpecialist
from specialists.standard_library_specialist import StandardLibrarySpecialist
from specialists.code_critic_specialist import CodeCriticSpecialist, IssueType

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of user queries"""
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    LEARNING = "learning"
    BEST_PRACTICES = "best_practices"
    LIBRARY_USAGE = "library_usage"
    GENERAL_PYTHON = "general_python"

class ResponseMode(Enum):
    """Response generation modes"""
    COMPREHENSIVE = "comprehensive"  # All relevant specialists
    FOCUSED = "focused"  # Primary specialist only
    COLLABORATIVE = "collaborative"  # Specialists build on each other
    COMPARATIVE = "comparative"  # Multiple perspectives

@dataclass
class SpecialistResponse:
    """Response from a specialist"""
    specialist_name: str
    response: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    tokens_used: int = 0

@dataclass
class OrchestrationResult:
    """Final orchestrated response"""
    query: str
    query_type: QueryType
    response_mode: ResponseMode
    primary_response: str
    specialist_responses: List[SpecialistResponse]
    synthesis_notes: List[str]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class PythonOrchestrator:
    """
    Orchestrator Engine for coordinating Python specialists
    Provides intelligent routing and response synthesis
    """
    
    def __init__(self):
        # Initialize specialists
        self.core_pythonic = CorePythonicSpecialist()
        self.stdlib_specialist = StandardLibrarySpecialist()
        self.code_critic = CodeCriticSpecialist()
        
        # Query classification patterns
        self.query_patterns = self._initialize_query_patterns()
        
        # Specialist capabilities mapping
        self.specialist_capabilities = self._initialize_capabilities()
        
        # Response history for learning
        self.response_history = []
        
        # Performance metrics
        self.metrics = {
            'total_queries': 0,
            'avg_response_time': 0.0,
            'specialist_usage': defaultdict(int),
            'query_type_distribution': defaultdict(int)
        }
        
        logger.info("Python Orchestrator initialized with all specialists")
    
    def _initialize_query_patterns(self) -> Dict[QueryType, List[str]]:
        """Initialize patterns for query classification"""
        return {
            QueryType.CODE_ANALYSIS: [
                r'analyze.*code',
                r'review.*code',
                r'check.*code',
                r'what.*wrong',
                r'issues.*with',
                r'problems.*in',
                r'bugs.*in',
                r'errors.*in'
            ],
            
            QueryType.CODE_GENERATION: [
                r'write.*code',
                r'generate.*code',
                r'create.*function',
                r'implement.*',
                r'how.*to.*write',
                r'show.*me.*code',
                r'example.*of'
            ],
            
            QueryType.DEBUGGING: [
                r'debug.*',
                r'fix.*error',
                r'solve.*problem',
                r'why.*not.*work',
                r'exception.*',
                r'traceback.*',
                r'error.*message'
            ],
            
            QueryType.OPTIMIZATION: [
                r'optimize.*',
                r'improve.*performance',
                r'make.*faster',
                r'efficient.*way',
                r'better.*approach',
                r'speed.*up',
                r'memory.*usage'
            ],
            
            QueryType.LEARNING: [
                r'learn.*',
                r'understand.*',
                r'explain.*',
                r'what.*is',
                r'how.*does.*work',
                r'difference.*between',
                r'when.*to.*use'
            ],
            
            QueryType.BEST_PRACTICES: [
                r'best.*practice',
                r'pythonic.*way',
                r'recommended.*approach',
                r'good.*practice',
                r'convention.*',
                r'style.*guide',
                r'clean.*code'
            ],
            
            QueryType.LIBRARY_USAGE: [
                r'use.*library',
                r'import.*',
                r'module.*',
                r'package.*',
                r'collections.*',
                r'itertools.*',
                r'functools.*',
                r'pathlib.*',
                r'json.*',
                r'datetime.*'
            ]
        }
    
    def _initialize_capabilities(self) -> Dict[str, List[QueryType]]:
        """Map specialists to their primary capabilities"""
        return {
            'core_pythonic': [
                QueryType.BEST_PRACTICES,
                QueryType.LEARNING,
                QueryType.CODE_GENERATION,
                QueryType.GENERAL_PYTHON
            ],
            
            'stdlib_specialist': [
                QueryType.LIBRARY_USAGE,
                QueryType.OPTIMIZATION,
                QueryType.CODE_GENERATION
            ],
            
            'code_critic': [
                QueryType.CODE_ANALYSIS,
                QueryType.DEBUGGING,
                QueryType.OPTIMIZATION
            ]
        }
    
    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        """
        Classify user query to determine appropriate specialists
        Returns query type and confidence score
        """
        query_lower = query.lower()
        scores = defaultdict(float)
        
        # Pattern-based classification
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    scores[query_type] += 1.0
        
        # Keyword-based scoring
        keywords = {
            QueryType.CODE_ANALYSIS: ['analyze', 'review', 'check', 'issues', 'problems', 'bugs'],
            QueryType.CODE_GENERATION: ['write', 'create', 'generate', 'implement', 'example'],
            QueryType.DEBUGGING: ['debug', 'fix', 'error', 'exception', 'traceback'],
            QueryType.OPTIMIZATION: ['optimize', 'performance', 'faster', 'efficient'],
            QueryType.LEARNING: ['learn', 'explain', 'understand', 'what', 'how'],
            QueryType.BEST_PRACTICES: ['best', 'pythonic', 'practice', 'convention'],
            QueryType.LIBRARY_USAGE: ['library', 'module', 'import', 'collections', 'itertools']
        }
        
        for query_type, words in keywords.items():
            for word in words:
                if word in query_lower:
                    scores[query_type] += 0.5
        
        # Code detection
        if self._contains_code(query):
            scores[QueryType.CODE_ANALYSIS] += 2.0
            scores[QueryType.DEBUGGING] += 1.0
        
        # Determine primary query type
        if not scores:
            return QueryType.GENERAL_PYTHON, 0.5
        
        primary_type = max(scores.items(), key=lambda x: x[1])
        confidence = min(primary_type[1] / 3.0, 1.0)  # Normalize confidence
        
        return primary_type[0], confidence
    
    def _contains_code(self, text: str) -> bool:
        """Check if text contains Python code"""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ',
            'if __name__', 'print(', 'return ',
            '```python', '```'
        ]
        
        return any(indicator in text for indicator in code_indicators)
    
    def determine_specialists(self, query_type: QueryType, query: str) -> List[str]:
        """
        Determine which specialists should handle the query
        Returns list of specialist names in priority order
        """
        specialists = []
        
        # Primary specialist based on query type
        for specialist, capabilities in self.specialist_capabilities.items():
            if query_type in capabilities:
                specialists.append(specialist)
        
        # Always include code critic for code analysis
        if self._contains_code(query) and 'code_critic' not in specialists:
            specialists.append('code_critic')
        
        # Include standard library specialist for optimization queries
        if query_type == QueryType.OPTIMIZATION and 'stdlib_specialist' not in specialists:
            specialists.append('stdlib_specialist')
        
        # Ensure at least one specialist
        if not specialists:
            specialists = ['core_pythonic']
        
        return specialists
    
    def determine_response_mode(self, query_type: QueryType, specialists: List[str]) -> ResponseMode:
        """Determine how to combine specialist responses"""
        if len(specialists) == 1:
            return ResponseMode.FOCUSED
        
        if query_type == QueryType.CODE_ANALYSIS:
            return ResponseMode.COMPREHENSIVE
        elif query_type in [QueryType.LEARNING, QueryType.BEST_PRACTICES]:
            return ResponseMode.COLLABORATIVE
        elif query_type == QueryType.OPTIMIZATION:
            return ResponseMode.COMPARATIVE
        else:
            return ResponseMode.COMPREHENSIVE
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """
        Main orchestration method - processes query through appropriate specialists
        """
        start_time = time.time()
        
        # Classify query
        query_type, classification_confidence = self.classify_query(query)
        
        # Determine specialists and response mode
        specialist_names = self.determine_specialists(query_type, query)
        response_mode = self.determine_response_mode(query_type, specialist_names)
        
        # Get responses from specialists
        specialist_responses = await self._get_specialist_responses(
            query, specialist_names, context or {}
        )
        
        # Synthesize final response
        primary_response, synthesis_notes = self._synthesize_response(
            query, query_type, response_mode, specialist_responses
        )
        
        # Calculate overall confidence
        overall_confidence = self._calculate_confidence(
            classification_confidence, specialist_responses
        )
        
        processing_time = time.time() - start_time
        
        # Create result
        result = OrchestrationResult(
            query=query,
            query_type=query_type,
            response_mode=response_mode,
            primary_response=primary_response,
            specialist_responses=specialist_responses,
            synthesis_notes=synthesis_notes,
            confidence=overall_confidence,
            processing_time=processing_time,
            metadata={
                'specialists_used': specialist_names,
                'classification_confidence': classification_confidence
            }
        )
        
        # Update metrics and history
        self._update_metrics(result)
        self.response_history.append(result)
        
        return result
    
    async def _get_specialist_responses(
        self, 
        query: str, 
        specialist_names: List[str], 
        context: Dict[str, Any]
    ) -> List[SpecialistResponse]:
        """Get responses from specified specialists concurrently"""
        
        # Create tasks for concurrent execution
        tasks = []
        for specialist_name in specialist_names:
            task = self._query_single_specialist(specialist_name, query, context)
            tasks.append(task)
        
        # Execute all specialist queries concurrently
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return valid responses
            valid_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Error querying {specialist_names[i]}: {response}")
                else:
                    valid_responses.append(response)
            
            return valid_responses
        
        return []
    
    async def _query_single_specialist(
        self, 
        specialist_name: str, 
        query: str, 
        context: Dict[str, Any]
    ) -> SpecialistResponse:
        """Query a single specialist and return structured response"""
        start_time = time.time()
        
        try:
            if specialist_name == 'core_pythonic':
                response = await self._query_core_pythonic(query, context)
            elif specialist_name == 'stdlib_specialist':
                response = await self._query_stdlib_specialist(query, context)
            elif specialist_name == 'code_critic':
                response = await self._query_code_critic(query, context)
            else:
                raise ValueError(f"Unknown specialist: {specialist_name}")
            
            processing_time = time.time() - start_time
            
            return SpecialistResponse(
                specialist_name=specialist_name,
                response=response['response'],
                confidence=response.get('confidence', 0.8),
                metadata=response.get('metadata', {}),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error querying {specialist_name}: {e}")
            raise e
    
    async def _query_core_pythonic(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Query the Core Pythonic Specialist"""
        # Extract code if present
        code = self._extract_code_from_query(query)
        
        if code:
            # Analyze code for pythonic patterns
            analysis = self.core_pythonic.analyze_code_for_pythonic_patterns(code)
            suggestions = self.core_pythonic.suggest_pythonic_improvements(code)
            
            response = f"Pythonic Analysis:\n\n"
            if analysis['pythonic_patterns']:
                response += "Good Pythonic patterns found:\n"
                for pattern in analysis['pythonic_patterns'][:3]:
                    response += f"- {pattern['pattern_name']}: {pattern['description']}\n"
            
            if suggestions:
                response += "\nSuggested improvements:\n"
                for suggestion in suggestions[:3]:
                    response += f"- {suggestion['suggestion']}\n"
                    if suggestion.get('example'):
                        response += f"  Example: {suggestion['example']}\n"
            
            return {
                'response': response,
                'confidence': 0.9,
                'metadata': {'analysis': analysis, 'suggestions': suggestions}
            }
        else:
            # Handle general Python questions
            patterns = self.core_pythonic.search_patterns(query)
            if patterns:
                pattern = patterns[0]
                response = f"Regarding {pattern.pattern_name}:\n\n"
                response += f"{pattern.description}\n\n"
                response += f"Example:\n{pattern.example_code}\n"
                if pattern.explanation:
                    response += f"\nExplanation: {pattern.explanation}"
                
                return {
                    'response': response,
                    'confidence': 0.8,
                    'metadata': {'pattern': pattern}
                }
            else:
                return {
                    'response': "I can help with Python fundamentals and best practices. Could you provide more specific details?",
                    'confidence': 0.5,
                    'metadata': {}
                }
    
    async def _query_stdlib_specialist(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Query the Standard Library Specialist"""
        # Check for module suggestions
        suggestions = self.stdlib_specialist.suggest_module_for_task(query)
        
        if suggestions:
            suggestion = suggestions[0]
            response = f"For this task, I recommend using the {suggestion['module']} module:\n\n"
            response += f"Reason: {suggestion['reason']}\n\n"
            
            # Get patterns for the suggested module
            patterns = self.stdlib_specialist.get_patterns_by_module(suggestion['module'])
            if patterns:
                pattern = patterns[0]
                response += f"Example usage:\n{pattern.example}\n"
                if pattern.explanation:
                    response += f"\nExplanation: {pattern.explanation}"
            
            return {
                'response': response,
                'confidence': 0.9,
                'metadata': {'suggestion': suggestion, 'patterns': patterns}
            }
        
        # Check for code analysis
        code = self._extract_code_from_query(query)
        if code:
            analysis = self.stdlib_specialist.analyze_code_for_stdlib_usage(code)
            response = "Standard Library Analysis:\n\n"
            
            if analysis['imports_found']:
                response += f"Standard library imports found: {', '.join(analysis['imports_found'])}\n\n"
            
            if analysis['suggestions']:
                response += "Suggestions for better standard library usage:\n"
                for suggestion in analysis['suggestions'][:3]:
                    response += f"- {suggestion}\n"
            
            return {
                'response': response,
                'confidence': 0.8,
                'metadata': analysis
            }
        
        return {
            'response': "I can help with Python standard library usage and optimization. What specific task are you trying to accomplish?",
            'confidence': 0.5,
            'metadata': {}
        }
    
    async def _query_code_critic(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Query the Code Critic Specialist"""
        code = self._extract_code_from_query(query)
        
        if code:
            analysis = self.code_critic.analyze_code(code, "user_code.py")
            
            response = f"Code Analysis Results:\n\n"
            response += f"Total issues found: {analysis['summary']['total_issues']}\n"
            
            if analysis['summary']['by_severity']:
                response += "\nIssues by severity:\n"
                for severity, count in analysis['summary']['by_severity'].items():
                    response += f"- {severity.title()}: {count}\n"
            
            if analysis['issues']:
                response += "\nTop issues:\n"
                for issue in analysis['issues'][:5]:
                    response += f"- {issue.title} (Line {issue.line_number}): {issue.description}\n"
                    if issue.suggestion:
                        response += f"  Fix: {issue.suggestion}\n"
            
            # Generate fix suggestions
            fixes = self.code_critic.suggest_fixes(analysis['issues'])
            if fixes:
                response += "\nRecommended fixes:\n"
                for fix in fixes[:3]:
                    response += f"- {fix['issue_title']}: {fix['suggestion']}\n"
            
            return {
                'response': response,
                'confidence': 0.95,
                'metadata': {'analysis': analysis, 'fixes': fixes}
            }
        else:
            return {
                'response': "I can analyze your code for bugs, security issues, and quality problems. Please provide the code you'd like me to review.",
                'confidence': 0.6,
                'metadata': {}
            }
    
    def _extract_code_from_query(self, query: str) -> Optional[str]:
        """Extract Python code from user query"""
        # Look for code blocks
        code_block_pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, query, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Look for inline code with def, class, etc.
        lines = query.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if any(line.strip().startswith(keyword) for keyword in ['def ', 'class ', 'import ', 'from ']):
                in_code = True
            
            if in_code:
                code_lines.append(line)
                
                # Stop at empty line or non-code line
                if not line.strip() and code_lines:
                    break
        
        if code_lines:
            code = '\n'.join(code_lines).strip()
            # Validate it's actually Python code
            try:
                ast.parse(code)
                return code
            except SyntaxError:
                pass
        
        return None
    
    def _synthesize_response(
        self, 
        query: str, 
        query_type: QueryType, 
        response_mode: ResponseMode, 
        specialist_responses: List[SpecialistResponse]
    ) -> Tuple[str, List[str]]:
        """Synthesize final response from specialist responses"""
        if not specialist_responses:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question.", []
        
        synthesis_notes = []
        
        if response_mode == ResponseMode.FOCUSED:
            # Single specialist response
            primary_response = specialist_responses[0].response
            synthesis_notes.append(f"Focused response from {specialist_responses[0].specialist_name}")
        
        elif response_mode == ResponseMode.COMPREHENSIVE:
            # Combine all responses
            response_parts = []
            
            for resp in specialist_responses:
                specialist_title = resp.specialist_name.replace('_', ' ').title()
                response_parts.append(f"## {specialist_title} Perspective\n\n{resp.response}")
                synthesis_notes.append(f"Included {resp.specialist_name} analysis")
            
            primary_response = "\n\n".join(response_parts)
        
        elif response_mode == ResponseMode.COLLABORATIVE:
            # Build responses on each other
            primary_response = "Here's a comprehensive analysis:\n\n"
            
            for i, resp in enumerate(specialist_responses):
                if i == 0:
                    primary_response += resp.response
                else:
                    primary_response += f"\n\nAdditionally, {resp.response}"
                
                synthesis_notes.append(f"Integrated {resp.specialist_name} insights")
        
        elif response_mode == ResponseMode.COMPARATIVE:
            # Show different perspectives
            primary_response = "Here are different approaches to consider:\n\n"
            
            for i, resp in enumerate(specialist_responses, 1):
                specialist_title = resp.specialist_name.replace('_', ' ').title()
                primary_response += f"**Approach {i} ({specialist_title}):**\n{resp.response}\n\n"
                synthesis_notes.append(f"Compared {resp.specialist_name} approach")
        
        return primary_response, synthesis_notes
    
    def _calculate_confidence(
        self, 
        classification_confidence: float, 
        specialist_responses: List[SpecialistResponse]
    ) -> float:
        """Calculate overall confidence in the response"""
        if not specialist_responses:
            return 0.0
        
        # Average specialist confidence
        avg_specialist_confidence = sum(r.confidence for r in specialist_responses) / len(specialist_responses)
        
        # Combine with classification confidence
        overall_confidence = (classification_confidence + avg_specialist_confidence) / 2
        
        # Boost confidence if multiple specialists agree
        if len(specialist_responses) > 1:
            overall_confidence = min(overall_confidence * 1.1, 1.0)
        
        return overall_confidence
    
    def _update_metrics(self, result: OrchestrationResult):
        """Update performance metrics"""
        self.metrics['total_queries'] += 1
        
        # Update average response time
        total_time = self.metrics['avg_response_time'] * (self.metrics['total_queries'] - 1)
        total_time += result.processing_time
        self.metrics['avg_response_time'] = total_time / self.metrics['total_queries']
        
        # Update specialist usage
        for resp in result.specialist_responses:
            self.metrics['specialist_usage'][resp.specialist_name] += 1
        
        # Update query type distribution
        self.metrics['query_type_distribution'][result.query_type.value] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        return dict(self.metrics)
    
    def get_specialist_stats(self) -> Dict[str, Any]:
        """Get statistics about specialist usage and performance"""
        stats = {
            'total_specialists': 3,
            'specialist_usage': dict(self.metrics['specialist_usage']),
            'query_type_distribution': dict(self.metrics['query_type_distribution']),
            'avg_response_time': self.metrics['avg_response_time'],
            'total_queries': self.metrics['total_queries']
        }
        
        # Calculate specialist performance
        if self.response_history:
            specialist_performance = defaultdict(list)
            for result in self.response_history:
                for resp in result.specialist_responses:
                    specialist_performance[resp.specialist_name].append({
                        'confidence': resp.confidence,
                        'processing_time': resp.processing_time
                    })
            
            stats['specialist_performance'] = {}
            for specialist, performances in specialist_performance.items():
                stats['specialist_performance'][specialist] = {
                    'avg_confidence': sum(p['confidence'] for p in performances) / len(performances),
                    'avg_processing_time': sum(p['processing_time'] for p in performances) / len(performances),
                    'total_queries': len(performances)
                }
        
        return stats
    
    def generate_training_data(self) -> List[Dict[str, str]]:
        """Generate training data from orchestration patterns"""
        training_data = []
        
        # Query classification examples
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns[:2]:  # Limit examples
                training_data.append({
                    'input': f"How would you classify this query type: '{pattern}'?",
                    'output': f"This query would be classified as {query_type.value} because it matches patterns for {query_type.value} tasks.",
                    'category': 'orchestration',
                    'difficulty': 'intermediate'
                })
        
        # Specialist coordination examples
        training_data.extend([
            {
                'input': 'When should multiple specialists collaborate on a Python question?',
                'output': 'Multiple specialists should collaborate when the query involves multiple aspects like code analysis (Code Critic), library optimization (Standard Library), and best practices (Core Pythonic). This provides comprehensive coverage.',
                'category': 'orchestration',
                'difficulty': 'advanced'
            },
            {
                'input': 'How do you determine which Python specialist to consult?',
                'output': 'Specialist selection is based on query classification using patterns and keywords. Code analysis queries go to Code Critic, library questions to Standard Library Specialist, and general Python questions to Core Pythonic Specialist.',
                'category': 'orchestration',
                'difficulty': 'intermediate'
            }
        ])
        
        return training_data


# Convenience function for easy usage
async def ask_python_question(question: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to ask a Python question and get orchestrated response
    """
    orchestrator = PythonOrchestrator()
    result = await orchestrator.process_query(question, context)
    return result.primary_response


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_orchestrator():
        orchestrator = PythonOrchestrator()
        
        # Test different types of queries
        test_queries = [
            "How do I count items in a list efficiently?",
            "Analyze this code: def bad_func(items=[]): return items.append(1)",
            "What's the most pythonic way to iterate over a dictionary?",
            "How can I optimize this slow code?",
            "Explain list comprehensions vs generator expressions"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = await orchestrator.process_query(query)
            print(f"Type: {result.query_type.value}")
            print(f"Mode: {result.response_mode.value}")
            print(f"Specialists: {[r.specialist_name for r in result.specialist_responses]}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Response: {result.primary_response[:200]}...")
        
        # Show metrics
        print(f"\nMetrics: {orchestrator.get_metrics()}")
    
    # Run test
    asyncio.run(test_orchestrator())

