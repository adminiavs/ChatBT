"""
Code Critic Specialist - Advanced Code Quality Analysis and Error Detection

This specialist focuses on:
- Bug detection and error identification
- Code quality analysis and improvement suggestions
- Security vulnerability detection
- Performance bottleneck identification
- Code smell detection and refactoring suggestions
- Best practices enforcement
- Testing and maintainability analysis
"""

import ast
import re
import sys
import time
import inspect
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class IssueType(Enum):
    """Types of code issues"""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    TESTING = "testing"
    DOCUMENTATION = "documentation"

class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class CodeIssue:
    """Represents a code issue found by the critic"""
    issue_type: IssueType
    severity: Severity
    title: str
    description: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    fix_example: Optional[str] = None
    explanation: Optional[str] = None
    references: Optional[List[str]] = None

@dataclass
class CriticRule:
    """Represents a code analysis rule"""
    rule_id: str
    name: str
    issue_type: IssueType
    severity: Severity
    description: str
    pattern: Optional[str] = None
    ast_node_types: Optional[List[str]] = None
    check_function: Optional[str] = None

class CodeCriticSpecialist:
    """
    Code Critic Specialist with comprehensive code analysis capabilities
    Detects bugs, security issues, performance problems, and quality issues
    """
    
    def __init__(self):
        self.rules = self._initialize_rules()
        self.issue_patterns = self._initialize_issue_patterns()
        self.security_patterns = self._initialize_security_patterns()
        self.performance_patterns = self._initialize_performance_patterns()
        self.analysis_history = []
        
    def _initialize_rules(self) -> List[CriticRule]:
        """Initialize comprehensive set of analysis rules"""
        rules = []
        
        # Bug detection rules
        rules.extend(self._get_bug_detection_rules())
        
        # Security analysis rules
        rules.extend(self._get_security_rules())
        
        # Performance analysis rules
        rules.extend(self._get_performance_rules())
        
        # Maintainability rules
        rules.extend(self._get_maintainability_rules())
        
        # Style and best practices rules
        rules.extend(self._get_style_rules())
        
        # Testing rules
        rules.extend(self._get_testing_rules())
        
        return rules
    
    def _get_bug_detection_rules(self) -> List[CriticRule]:
        """Bug detection and error-prone pattern rules"""
        return [
            CriticRule(
                rule_id="BUG001",
                name="Mutable Default Arguments",
                issue_type=IssueType.BUG,
                severity=Severity.HIGH,
                description="Function uses mutable object as default argument",
                ast_node_types=["FunctionDef"],
                check_function="check_mutable_defaults"
            ),
            
            CriticRule(
                rule_id="BUG002",
                name="Bare Except Clause",
                issue_type=IssueType.BUG,
                severity=Severity.MEDIUM,
                description="Bare except clause catches all exceptions including system exits",
                ast_node_types=["ExceptHandler"],
                check_function="check_bare_except"
            ),
            
            CriticRule(
                rule_id="BUG003",
                name="Variable Used Before Assignment",
                issue_type=IssueType.BUG,
                severity=Severity.HIGH,
                description="Variable may be used before assignment",
                ast_node_types=["Name"],
                check_function="check_uninitialized_variables"
            ),
            
            CriticRule(
                rule_id="BUG004",
                name="Division by Zero Risk",
                issue_type=IssueType.BUG,
                severity=Severity.HIGH,
                description="Potential division by zero without proper checking",
                ast_node_types=["BinOp"],
                check_function="check_division_by_zero"
            ),
            
            CriticRule(
                rule_id="BUG005",
                name="Infinite Loop Risk",
                issue_type=IssueType.BUG,
                severity=Severity.CRITICAL,
                description="Loop condition may never become false",
                ast_node_types=["While", "For"],
                check_function="check_infinite_loops"
            ),
            
            CriticRule(
                rule_id="BUG006",
                name="Resource Leak",
                issue_type=IssueType.BUG,
                severity=Severity.HIGH,
                description="File or resource opened but not properly closed",
                ast_node_types=["Call"],
                check_function="check_resource_leaks"
            ),
            
            CriticRule(
                rule_id="BUG007",
                name="String Formatting Errors",
                issue_type=IssueType.BUG,
                severity=Severity.MEDIUM,
                description="Potential string formatting errors or mismatches",
                ast_node_types=["BinOp", "Call"],
                check_function="check_string_formatting"
            ),
            
            CriticRule(
                rule_id="BUG008",
                name="List Modification During Iteration",
                issue_type=IssueType.BUG,
                severity=Severity.HIGH,
                description="Modifying list while iterating over it",
                ast_node_types=["For"],
                check_function="check_list_modification_during_iteration"
            )
        ]
    
    def _get_security_rules(self) -> List[CriticRule]:
        """Security vulnerability detection rules"""
        return [
            CriticRule(
                rule_id="SEC001",
                name="SQL Injection Risk",
                issue_type=IssueType.SECURITY,
                severity=Severity.CRITICAL,
                description="Potential SQL injection vulnerability",
                pattern=r"execute\s*\(\s*['\"].*%.*['\"]",
                check_function="check_sql_injection"
            ),
            
            CriticRule(
                rule_id="SEC002",
                name="Command Injection Risk",
                issue_type=IssueType.SECURITY,
                severity=Severity.CRITICAL,
                description="Potential command injection vulnerability",
                ast_node_types=["Call"],
                check_function="check_command_injection"
            ),
            
            CriticRule(
                rule_id="SEC003",
                name="Hardcoded Secrets",
                issue_type=IssueType.SECURITY,
                severity=Severity.HIGH,
                description="Hardcoded passwords, API keys, or secrets",
                pattern=r"(password|secret|key|token)\s*=\s*['\"][^'\"]+['\"]",
                check_function="check_hardcoded_secrets"
            ),
            
            CriticRule(
                rule_id="SEC004",
                name="Unsafe Deserialization",
                issue_type=IssueType.SECURITY,
                severity=Severity.HIGH,
                description="Unsafe deserialization of untrusted data",
                ast_node_types=["Call"],
                check_function="check_unsafe_deserialization"
            ),
            
            CriticRule(
                rule_id="SEC005",
                name="Path Traversal Risk",
                issue_type=IssueType.SECURITY,
                severity=Severity.HIGH,
                description="Potential path traversal vulnerability",
                ast_node_types=["Call"],
                check_function="check_path_traversal"
            ),
            
            CriticRule(
                rule_id="SEC006",
                name="Weak Random Number Generation",
                issue_type=IssueType.SECURITY,
                severity=Severity.MEDIUM,
                description="Using weak random number generation for security purposes",
                ast_node_types=["Call"],
                check_function="check_weak_random"
            )
        ]
    
    def _get_performance_rules(self) -> List[CriticRule]:
        """Performance analysis rules"""
        return [
            CriticRule(
                rule_id="PERF001",
                name="Inefficient Loop",
                issue_type=IssueType.PERFORMANCE,
                severity=Severity.MEDIUM,
                description="Loop could be optimized with list comprehension or built-in function",
                ast_node_types=["For"],
                check_function="check_inefficient_loops"
            ),
            
            CriticRule(
                rule_id="PERF002",
                name="String Concatenation in Loop",
                issue_type=IssueType.PERFORMANCE,
                severity=Severity.HIGH,
                description="String concatenation in loop is O(n²), use join() instead",
                ast_node_types=["For", "While"],
                check_function="check_string_concatenation_in_loop"
            ),
            
            CriticRule(
                rule_id="PERF003",
                name="Inefficient Membership Testing",
                issue_type=IssueType.PERFORMANCE,
                severity=Severity.MEDIUM,
                description="Using list for membership testing instead of set",
                ast_node_types=["Compare"],
                check_function="check_inefficient_membership"
            ),
            
            CriticRule(
                rule_id="PERF004",
                name="Unnecessary List Creation",
                issue_type=IssueType.PERFORMANCE,
                severity=Severity.LOW,
                description="Creating list when generator would suffice",
                ast_node_types=["ListComp"],
                check_function="check_unnecessary_list_creation"
            ),
            
            CriticRule(
                rule_id="PERF005",
                name="Inefficient Dictionary Access",
                issue_type=IssueType.PERFORMANCE,
                severity=Severity.LOW,
                description="Multiple dictionary lookups for same key",
                ast_node_types=["Subscript"],
                check_function="check_inefficient_dict_access"
            ),
            
            CriticRule(
                rule_id="PERF006",
                name="Global Variable Access in Loop",
                issue_type=IssueType.PERFORMANCE,
                severity=Severity.LOW,
                description="Accessing global variables in tight loops",
                ast_node_types=["For", "While"],
                check_function="check_global_access_in_loop"
            )
        ]
    
    def _get_maintainability_rules(self) -> List[CriticRule]:
        """Code maintainability rules"""
        return [
            CriticRule(
                rule_id="MAINT001",
                name="Function Too Long",
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                description="Function is too long and should be broken down",
                ast_node_types=["FunctionDef"],
                check_function="check_function_length"
            ),
            
            CriticRule(
                rule_id="MAINT002",
                name="Too Many Arguments",
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                description="Function has too many parameters",
                ast_node_types=["FunctionDef"],
                check_function="check_too_many_arguments"
            ),
            
            CriticRule(
                rule_id="MAINT003",
                name="Deep Nesting",
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                description="Code is too deeply nested",
                ast_node_types=["If", "For", "While", "With"],
                check_function="check_deep_nesting"
            ),
            
            CriticRule(
                rule_id="MAINT004",
                name="Magic Numbers",
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                description="Magic numbers should be named constants",
                ast_node_types=["Constant", "Num"],
                check_function="check_magic_numbers"
            ),
            
            CriticRule(
                rule_id="MAINT005",
                name="Duplicate Code",
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                description="Duplicate code blocks detected",
                check_function="check_duplicate_code"
            ),
            
            CriticRule(
                rule_id="MAINT006",
                name="Complex Boolean Expression",
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                description="Boolean expression is too complex",
                ast_node_types=["BoolOp"],
                check_function="check_complex_boolean"
            )
        ]
    
    def _get_style_rules(self) -> List[CriticRule]:
        """Style and best practices rules"""
        return [
            CriticRule(
                rule_id="STYLE001",
                name="Missing Docstring",
                issue_type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                description="Function or class missing docstring",
                ast_node_types=["FunctionDef", "ClassDef"],
                check_function="check_missing_docstring"
            ),
            
            CriticRule(
                rule_id="STYLE002",
                name="Unused Variable",
                issue_type=IssueType.STYLE,
                severity=Severity.LOW,
                description="Variable assigned but never used",
                ast_node_types=["Assign"],
                check_function="check_unused_variables"
            ),
            
            CriticRule(
                rule_id="STYLE003",
                name="Unused Import",
                issue_type=IssueType.STYLE,
                severity=Severity.LOW,
                description="Import statement not used",
                ast_node_types=["Import", "ImportFrom"],
                check_function="check_unused_imports"
            ),
            
            CriticRule(
                rule_id="STYLE004",
                name="Inconsistent Naming",
                issue_type=IssueType.STYLE,
                severity=Severity.LOW,
                description="Variable or function naming doesn't follow conventions",
                ast_node_types=["FunctionDef", "Name"],
                check_function="check_naming_conventions"
            )
        ]
    
    def _get_testing_rules(self) -> List[CriticRule]:
        """Testing-related rules"""
        return [
            CriticRule(
                rule_id="TEST001",
                name="Missing Test Coverage",
                issue_type=IssueType.TESTING,
                severity=Severity.MEDIUM,
                description="Function lacks corresponding test",
                ast_node_types=["FunctionDef"],
                check_function="check_test_coverage"
            ),
            
            CriticRule(
                rule_id="TEST002",
                name="Assertion Without Message",
                issue_type=IssueType.TESTING,
                severity=Severity.LOW,
                description="Assertion without descriptive message",
                ast_node_types=["Assert"],
                check_function="check_assertion_messages"
            ),
            
            CriticRule(
                rule_id="TEST003",
                name="Test Method Too Long",
                issue_type=IssueType.TESTING,
                severity=Severity.MEDIUM,
                description="Test method is too long and tests multiple things",
                ast_node_types=["FunctionDef"],
                check_function="check_test_method_length"
            )
        ]
    
    def _initialize_issue_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize common issue patterns"""
        return {
            'common_bugs': [
                {
                    'pattern': r'if\s+.*=\s+.*:',
                    'description': 'Assignment in if condition (should be ==)',
                    'severity': Severity.HIGH,
                    'fix': 'Use == for comparison, = for assignment'
                },
                {
                    'pattern': r'except\s*:',
                    'description': 'Bare except clause',
                    'severity': Severity.MEDIUM,
                    'fix': 'Specify exception types to catch'
                },
                {
                    'pattern': r'\.close\(\)',
                    'description': 'Manual resource closing (use context manager)',
                    'severity': Severity.LOW,
                    'fix': 'Use with statement for automatic resource management'
                }
            ],
            'performance_issues': [
                {
                    'pattern': r'for.*in.*:\s*.*\+=.*',
                    'description': 'String concatenation in loop',
                    'severity': Severity.HIGH,
                    'fix': 'Use str.join() for multiple concatenations'
                },
                {
                    'pattern': r'if.*in\s*\[.*\]:',
                    'description': 'Membership testing with list',
                    'severity': Severity.MEDIUM,
                    'fix': 'Use set for O(1) membership testing'
                }
            ]
        }
    
    def _initialize_security_patterns(self) -> List[Dict[str, Any]]:
        """Initialize security vulnerability patterns"""
        return [
            {
                'pattern': r'eval\s*\(',
                'description': 'Use of eval() with untrusted input',
                'severity': Severity.CRITICAL,
                'cwe': 'CWE-95',
                'fix': 'Use ast.literal_eval() for safe evaluation'
            },
            {
                'pattern': r'exec\s*\(',
                'description': 'Use of exec() with untrusted input',
                'severity': Severity.CRITICAL,
                'cwe': 'CWE-95',
                'fix': 'Avoid exec() or validate input thoroughly'
            },
            {
                'pattern': r'subprocess\..*shell=True',
                'description': 'Shell injection vulnerability',
                'severity': Severity.HIGH,
                'cwe': 'CWE-78',
                'fix': 'Use shell=False and pass arguments as list'
            },
            {
                'pattern': r'pickle\.loads?\(',
                'description': 'Unsafe deserialization',
                'severity': Severity.HIGH,
                'cwe': 'CWE-502',
                'fix': 'Use JSON or validate pickle data source'
            }
        ]
    
    def _initialize_performance_patterns(self) -> List[Dict[str, Any]]:
        """Initialize performance issue patterns"""
        return [
            {
                'pattern': r'range\(len\(',
                'description': 'Using range(len()) instead of enumerate',
                'impact': 'Readability and slight performance',
                'fix': 'Use enumerate() for index-value pairs'
            },
            {
                'pattern': r'\.keys\(\).*in\s',
                'description': 'Unnecessary .keys() call',
                'impact': 'Minor performance overhead',
                'fix': 'Check membership directly on dictionary'
            },
            {
                'pattern': r'list\(.*\.keys\(\)\)',
                'description': 'Converting dict_keys to list unnecessarily',
                'impact': 'Memory and performance overhead',
                'fix': 'Use dict_keys directly or iterate'
            }
        ]
    
    def analyze_code(self, code: str, filename: str = "unknown") -> Dict[str, Any]:
        """
        Comprehensive code analysis for bugs, security, performance, and quality
        """
        try:
            tree = ast.parse(code)
            
            analysis = {
                'filename': filename,
                'issues': [],
                'summary': {
                    'total_issues': 0,
                    'by_type': defaultdict(int),
                    'by_severity': defaultdict(int)
                },
                'metrics': self._calculate_code_metrics(tree, code),
                'timestamp': time.time()
            }
            
            # Run all analysis rules
            for rule in self.rules:
                issues = self._apply_rule(rule, tree, code)
                analysis['issues'].extend(issues)
            
            # Pattern-based analysis
            pattern_issues = self._analyze_patterns(code)
            analysis['issues'].extend(pattern_issues)
            
            # Update summary
            analysis['summary']['total_issues'] = len(analysis['issues'])
            for issue in analysis['issues']:
                analysis['summary']['by_type'][issue.issue_type.value] += 1
                analysis['summary']['by_severity'][issue.severity.value] += 1
            
            # Store in history
            self.analysis_history.append(analysis)
            
            return analysis
            
        except SyntaxError as e:
            return {
                'filename': filename,
                'syntax_error': str(e),
                'issues': [CodeIssue(
                    issue_type=IssueType.BUG,
                    severity=Severity.CRITICAL,
                    title="Syntax Error",
                    description=f"Syntax error: {e}",
                    line_number=e.lineno,
                    column=e.offset
                )],
                'summary': {'total_issues': 1, 'by_type': {'bug': 1}, 'by_severity': {'critical': 1}}
            }
    
    def _apply_rule(self, rule: CriticRule, tree: ast.AST, code: str) -> List[CodeIssue]:
        """Apply a specific rule to the code"""
        issues = []
        
        if rule.check_function:
            check_method = getattr(self, rule.check_function, None)
            if check_method:
                try:
                    rule_issues = check_method(tree, code, rule)
                    issues.extend(rule_issues)
                except Exception as e:
                    logger.error(f"Error applying rule {rule.rule_id}: {e}")
        
        return issues
    
    def _analyze_patterns(self, code: str) -> List[CodeIssue]:
        """Analyze code using regex patterns"""
        issues = []
        
        # Check security patterns
        for pattern_info in self.security_patterns:
            matches = re.finditer(pattern_info['pattern'], code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append(CodeIssue(
                    issue_type=IssueType.SECURITY,
                    severity=pattern_info['severity'],
                    title=pattern_info['description'],
                    description=f"Security issue: {pattern_info['description']}",
                    line_number=line_num,
                    code_snippet=match.group(),
                    suggestion=pattern_info['fix']
                ))
        
        # Check performance patterns
        for pattern_info in self.performance_patterns:
            matches = re.finditer(pattern_info['pattern'], code)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append(CodeIssue(
                    issue_type=IssueType.PERFORMANCE,
                    severity=Severity.LOW,
                    title=pattern_info['description'],
                    description=f"Performance issue: {pattern_info['description']}",
                    line_number=line_num,
                    code_snippet=match.group(),
                    suggestion=pattern_info['fix']
                ))
        
        return issues
    
    def _calculate_code_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate various code quality metrics"""
        metrics = {
            'lines_of_code': len(code.splitlines()),
            'functions': 0,
            'classes': 0,
            'complexity': 0,
            'max_nesting_depth': 0,
            'avg_function_length': 0,
            'docstring_coverage': 0
        }
        
        function_lengths = []
        functions_with_docstrings = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 1
                function_lengths.append(func_lines)
                
                # Check for docstring
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    functions_with_docstrings += 1
            
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
            
            # Calculate cyclomatic complexity
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                metrics['complexity'] += 1
        
        if function_lengths:
            metrics['avg_function_length'] = sum(function_lengths) / len(function_lengths)
        
        if metrics['functions'] > 0:
            metrics['docstring_coverage'] = functions_with_docstrings / metrics['functions']
        
        return metrics
    
    # Rule implementation methods
    def check_mutable_defaults(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for mutable default arguments"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(CodeIssue(
                            issue_type=rule.issue_type,
                            severity=rule.severity,
                            title=rule.name,
                            description="Function uses mutable object as default argument",
                            line_number=node.lineno,
                            suggestion="Use None as default and create mutable object inside function",
                            fix_example="def func(arg=None):\n    if arg is None:\n        arg = []"
                        ))
        
        return issues
    
    def check_bare_except(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for bare except clauses"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(CodeIssue(
                    issue_type=rule.issue_type,
                    severity=rule.severity,
                    title=rule.name,
                    description="Bare except clause catches all exceptions including system exits",
                    line_number=node.lineno,
                    suggestion="Specify exception types to catch",
                    fix_example="except (ValueError, TypeError) as e:"
                ))
        
        return issues
    
    def check_resource_leaks(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for potential resource leaks"""
        issues = []
        
        # Look for open() calls not in with statements
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'open'):
                
                # Check if it's inside a with statement
                parent = node
                in_with = False
                while hasattr(parent, 'parent'):
                    parent = parent.parent
                    if isinstance(parent, ast.With):
                        in_with = True
                        break
                
                if not in_with:
                    issues.append(CodeIssue(
                        issue_type=rule.issue_type,
                        severity=rule.severity,
                        title=rule.name,
                        description="File opened but not using context manager",
                        line_number=node.lineno,
                        suggestion="Use 'with' statement for automatic resource management",
                        fix_example="with open('file.txt') as f:\n    content = f.read()"
                    ))
        
        return issues
    
    def check_string_concatenation_in_loop(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for string concatenation in loops"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Look for string concatenation in loop body
                for child in ast.walk(node):
                    if (isinstance(child, ast.AugAssign) and 
                        isinstance(child.op, ast.Add)):
                        issues.append(CodeIssue(
                            issue_type=rule.issue_type,
                            severity=rule.severity,
                            title=rule.name,
                            description="String concatenation in loop is O(n²)",
                            line_number=child.lineno,
                            suggestion="Use str.join() for multiple concatenations",
                            fix_example="result = ''.join(items)"
                        ))
        
        return issues
    
    def check_sql_injection(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for SQL injection vulnerabilities"""
        issues = []
        
        # Look for string formatting in SQL queries
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for execute() calls with string formatting
                if (hasattr(node.func, 'attr') and 
                    node.func.attr in ['execute', 'executemany']):
                    
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                            # String formatting with %
                            issues.append(CodeIssue(
                                issue_type=rule.issue_type,
                                severity=rule.severity,
                                title=rule.name,
                                description="Potential SQL injection via string formatting",
                                line_number=node.lineno,
                                suggestion="Use parameterized queries",
                                fix_example="cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
                            ))
        
        return issues
    
    def check_command_injection(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for command injection vulnerabilities"""
        issues = []
        
        dangerous_functions = ['os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        func_name = f"{node.func.value.id}.{node.func.attr}"
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id
                
                if func_name in dangerous_functions:
                    # Check for shell=True or string arguments
                    has_shell_true = any(
                        isinstance(kw.value, ast.Constant) and kw.value.value is True
                        for kw in node.keywords if kw.arg == 'shell'
                    )
                    
                    if has_shell_true or any(isinstance(arg, (ast.Str, ast.Constant)) for arg in node.args):
                        issues.append(CodeIssue(
                            issue_type=rule.issue_type,
                            severity=rule.severity,
                            title=rule.name,
                            description="Potential command injection vulnerability",
                            line_number=node.lineno,
                            suggestion="Use shell=False and pass arguments as list",
                            fix_example="subprocess.run(['ls', '-l'], shell=False)"
                        ))
        
        return issues
    
    def check_function_length(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for overly long functions"""
        issues = []
        max_length = 50  # configurable threshold
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno
                    if length > max_length:
                        issues.append(CodeIssue(
                            issue_type=rule.issue_type,
                            severity=rule.severity,
                            title=rule.name,
                            description=f"Function '{node.name}' is {length} lines long (max recommended: {max_length})",
                            line_number=node.lineno,
                            suggestion="Break function into smaller, more focused functions"
                        ))
        
        return issues
    
    def check_too_many_arguments(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Check for functions with too many arguments"""
        issues = []
        max_args = 7  # configurable threshold
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_args = (len(node.args.args) + 
                             len(node.args.posonlyargs) + 
                             len(node.args.kwonlyargs))
                
                if total_args > max_args:
                    issues.append(CodeIssue(
                        issue_type=rule.issue_type,
                        severity=rule.severity,
                        title=rule.name,
                        description=f"Function '{node.name}' has {total_args} parameters (max recommended: {max_args})",
                        line_number=node.lineno,
                        suggestion="Consider using a configuration object or breaking into smaller functions"
                    ))
        
        return issues
    
    # Additional check methods would be implemented here...
    def check_uninitialized_variables(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for uninitialized variable check"""
        return []
    
    def check_division_by_zero(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for division by zero check"""
        return []
    
    def check_infinite_loops(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for infinite loop check"""
        return []
    
    def check_string_formatting(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for string formatting check"""
        return []
    
    def check_list_modification_during_iteration(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for list modification check"""
        return []
    
    def check_hardcoded_secrets(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for hardcoded secrets check"""
        return []
    
    def check_unsafe_deserialization(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for unsafe deserialization check"""
        return []
    
    def check_path_traversal(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for path traversal check"""
        return []
    
    def check_weak_random(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for weak random check"""
        return []
    
    def check_inefficient_loops(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for inefficient loops check"""
        return []
    
    def check_inefficient_membership(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for inefficient membership check"""
        return []
    
    def check_unnecessary_list_creation(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for unnecessary list creation check"""
        return []
    
    def check_inefficient_dict_access(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for inefficient dict access check"""
        return []
    
    def check_global_access_in_loop(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for global access in loop check"""
        return []
    
    def check_deep_nesting(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for deep nesting check"""
        return []
    
    def check_magic_numbers(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for magic numbers check"""
        return []
    
    def check_duplicate_code(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for duplicate code check"""
        return []
    
    def check_complex_boolean(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for complex boolean check"""
        return []
    
    def check_missing_docstring(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for missing docstring check"""
        return []
    
    def check_unused_variables(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for unused variables check"""
        return []
    
    def check_unused_imports(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for unused imports check"""
        return []
    
    def check_naming_conventions(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for naming conventions check"""
        return []
    
    def check_test_coverage(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for test coverage check"""
        return []
    
    def check_assertion_messages(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for assertion messages check"""
        return []
    
    def check_test_method_length(self, tree: ast.AST, code: str, rule: CriticRule) -> List[CodeIssue]:
        """Placeholder for test method length check"""
        return []
    
    def get_rules_by_type(self, issue_type: IssueType) -> List[CriticRule]:
        """Get all rules for a specific issue type"""
        return [rule for rule in self.rules if rule.issue_type == issue_type]
    
    def get_rules_by_severity(self, severity: Severity) -> List[CriticRule]:
        """Get all rules for a specific severity level"""
        return [rule for rule in self.rules if rule.severity == severity]
    
    def suggest_fixes(self, issues: List[CodeIssue]) -> List[Dict[str, str]]:
        """Generate fix suggestions for identified issues"""
        fixes = []
        
        for issue in issues:
            if issue.suggestion:
                fixes.append({
                    'issue_title': issue.title,
                    'suggestion': issue.suggestion,
                    'fix_example': issue.fix_example or '',
                    'severity': issue.severity.value,
                    'type': issue.issue_type.value
                })
        
        return fixes
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable analysis report"""
        report = []
        report.append(f"Code Analysis Report for {analysis['filename']}")
        report.append("=" * 50)
        
        summary = analysis['summary']
        report.append(f"Total Issues: {summary['total_issues']}")
        
        if summary['by_severity']:
            report.append("\nIssues by Severity:")
            for severity, count in summary['by_severity'].items():
                report.append(f"  {severity.title()}: {count}")
        
        if summary['by_type']:
            report.append("\nIssues by Type:")
            for issue_type, count in summary['by_type'].items():
                report.append(f"  {issue_type.title()}: {count}")
        
        if 'metrics' in analysis:
            metrics = analysis['metrics']
            report.append(f"\nCode Metrics:")
            report.append(f"  Lines of Code: {metrics['lines_of_code']}")
            report.append(f"  Functions: {metrics['functions']}")
            report.append(f"  Classes: {metrics['classes']}")
            report.append(f"  Complexity: {metrics['complexity']}")
            report.append(f"  Docstring Coverage: {metrics['docstring_coverage']:.1%}")
        
        if analysis['issues']:
            report.append("\nDetailed Issues:")
            for i, issue in enumerate(analysis['issues'][:10], 1):  # Show first 10
                report.append(f"\n{i}. {issue.title} ({issue.severity.value})")
                report.append(f"   Line {issue.line_number}: {issue.description}")
                if issue.suggestion:
                    report.append(f"   Suggestion: {issue.suggestion}")
        
        return "\n".join(report)
    
    def generate_training_data(self) -> List[Dict[str, str]]:
        """Generate training data from rules and patterns"""
        training_data = []
        
        for rule in self.rules:
            # Basic rule explanation
            training_data.append({
                'input': f"What does the {rule.name} rule check for?",
                'output': f"The {rule.name} rule checks for {rule.description.lower()}. This is a {rule.severity.value} severity {rule.issue_type.value} issue.",
                'rule_id': rule.rule_id,
                'category': rule.issue_type.value,
                'difficulty': 'intermediate'
            })
            
            # How to fix question
            training_data.append({
                'input': f"How do I fix {rule.name} issues?",
                'output': f"To fix {rule.name} issues: {rule.description}. This helps prevent {rule.issue_type.value} problems in your code.",
                'rule_id': rule.rule_id,
                'category': rule.issue_type.value,
                'difficulty': 'beginner'
            })
        
        # Add pattern-based examples
        for category, patterns in self.issue_patterns.items():
            for pattern_info in patterns:
                training_data.append({
                    'input': f"What's wrong with this pattern: {pattern_info['pattern']}?",
                    'output': f"This pattern indicates: {pattern_info['description']}. {pattern_info['fix']}",
                    'category': category,
                    'difficulty': 'intermediate'
                })
        
        return training_data


# Example usage and testing
if __name__ == "__main__":
    critic = CodeCriticSpecialist()
    
    # Test code with various issues
    test_code = """
def bad_function(items=[]):  # Mutable default
    result = ""
    for item in items:
        result += str(item)  # String concatenation in loop
    
    try:
        risky_operation()
    except:  # Bare except
        pass
    
    return result

def another_function():
    password = "hardcoded_secret"  # Security issue
    
    if True:  # Always true condition
        if True:
            if True:  # Deep nesting
                print("deeply nested")
"""
    
    analysis = critic.analyze_code(test_code, "test.py")
    print(f"Found {analysis['summary']['total_issues']} issues")
    
    # Generate report
    report = critic.generate_report(analysis)
    print(report)
    
    # Generate training data
    training_data = critic.generate_training_data()
    print(f"Generated {len(training_data)} training examples")

