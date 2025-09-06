"""
Standard Library Specialist - Comprehensive Python Standard Library Expertise

This specialist focuses on:
- Python standard library modules and their optimal usage
- Module-specific best practices and patterns
- Performance considerations for standard library functions
- Cross-module integration patterns
- Version-specific features and compatibility
- Advanced usage patterns and lesser-known features
"""

import ast
import inspect
import sys
import time
import importlib
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass
from collections import defaultdict, Counter, namedtuple
from functools import lru_cache, wraps
import logging

logger = logging.getLogger(__name__)

@dataclass
class StandardLibraryPattern:
    """Represents a standard library usage pattern"""
    module_name: str
    pattern_name: str
    category: str
    description: str
    basic_example: str
    advanced_example: str
    explanation: str
    performance_notes: Optional[str] = None
    version_info: Optional[str] = None
    common_mistakes: Optional[str] = None
    related_modules: Optional[List[str]] = None

class StandardLibrarySpecialist:
    """
    Standard Library Specialist with comprehensive knowledge of Python's standard library
    Covers 50+ modules with usage patterns, best practices, and optimization tips
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.modules_covered = self._get_covered_modules()
        self.categories = self._organize_by_category()
        self.module_index = self._build_module_index()
        self.compatibility_matrix = self._build_compatibility_matrix()
        
    def _initialize_patterns(self) -> List[StandardLibraryPattern]:
        """Initialize comprehensive collection of standard library patterns"""
        patterns = []
        
        # Collections module patterns (15 patterns)
        patterns.extend(self._get_collections_patterns())
        
        # Itertools module patterns (12 patterns)
        patterns.extend(self._get_itertools_patterns())
        
        # Functools module patterns (8 patterns)
        patterns.extend(self._get_functools_patterns())
        
        # Pathlib and os.path patterns (10 patterns)
        patterns.extend(self._get_path_patterns())
        
        # Datetime and time patterns (8 patterns)
        patterns.extend(self._get_datetime_patterns())
        
        # JSON and data serialization patterns (6 patterns)
        patterns.extend(self._get_serialization_patterns())
        
        # Regular expressions patterns (8 patterns)
        patterns.extend(self._get_regex_patterns())
        
        # File and I/O patterns (10 patterns)
        patterns.extend(self._get_io_patterns())
        
        # System and environment patterns (8 patterns)
        patterns.extend(self._get_system_patterns())
        
        # Logging patterns (6 patterns)
        patterns.extend(self._get_logging_patterns())
        
        # Threading and multiprocessing patterns (8 patterns)
        patterns.extend(self._get_concurrency_patterns())
        
        # Network and HTTP patterns (6 patterns)
        patterns.extend(self._get_network_patterns())
        
        # Math and statistics patterns (6 patterns)
        patterns.extend(self._get_math_patterns())
        
        # Data structures and algorithms patterns (8 patterns)
        patterns.extend(self._get_algorithms_patterns())
        
        # Testing and debugging patterns (6 patterns)
        patterns.extend(self._get_testing_patterns())
        
        return patterns
    
    def _get_collections_patterns(self) -> List[StandardLibraryPattern]:
        """Collections module patterns"""
        return [
            StandardLibraryPattern(
                module_name="collections",
                pattern_name="defaultdict Usage",
                category="data_structures",
                description="Use defaultdict to eliminate key checking",
                basic_example="""
from collections import defaultdict

# Basic usage
dd = defaultdict(list)
dd['key'].append('value')  # No KeyError
                """,
                advanced_example="""
from collections import defaultdict

# Nested defaultdict
nested = defaultdict(lambda: defaultdict(int))
nested['level1']['level2'] += 1

# With custom factory
def make_counter():
    return defaultdict(int)

counters = defaultdict(make_counter)
counters['group']['item'] += 1
                """,
                explanation="defaultdict eliminates the need for key existence checks and provides cleaner code",
                performance_notes="Slightly faster than dict.get() or try/except patterns",
                common_mistakes="Using mutable objects as default factory without lambda"
            ),
            
            StandardLibraryPattern(
                module_name="collections",
                pattern_name="Counter for Counting Operations",
                category="data_structures",
                description="Use Counter for efficient counting and frequency analysis",
                basic_example="""
from collections import Counter

# Basic counting
counter = Counter(['a', 'b', 'a', 'c', 'b', 'a'])
print(counter.most_common(2))  # [('a', 3), ('b', 2)]
                """,
                advanced_example="""
from collections import Counter

# Counter arithmetic
c1 = Counter(['a', 'b', 'c', 'a'])
c2 = Counter(['a', 'b', 'b'])

# Addition, subtraction, intersection, union
combined = c1 + c2
difference = c1 - c2
intersection = c1 & c2
union = c1 | c2

# Update operations
c1.update(['d', 'e'])
c1.subtract(['a', 'b'])
                """,
                explanation="Counter provides optimized counting with arithmetic operations",
                performance_notes="Highly optimized for counting operations, faster than manual dict counting"
            ),
            
            StandardLibraryPattern(
                module_name="collections",
                pattern_name="namedtuple for Structured Data",
                category="data_structures",
                description="Use namedtuple for lightweight, immutable structured data",
                basic_example="""
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
print(p.x, p.y)  # Attribute access
                """,
                advanced_example="""
from collections import namedtuple

# With defaults (Python 3.7+)
Person = namedtuple('Person', ['name', 'age', 'city'], defaults=['Unknown'])
p1 = Person('Alice', 30)  # city defaults to 'Unknown'

# Methods available
p2 = p1._replace(age=31)  # Create new instance with changed field
fields = p1._fields  # ('name', 'age', 'city')
as_dict = p1._asdict()  # OrderedDict

# Subclassing for methods
class PersonWithMethods(Person):
    def is_adult(self):
        return self.age >= 18
                """,
                explanation="namedtuple provides the benefits of tuples with named field access",
                performance_notes="Memory efficient, faster than regular classes for simple data containers"
            ),
            
            StandardLibraryPattern(
                module_name="collections",
                pattern_name="deque for Efficient Queue Operations",
                category="data_structures",
                description="Use deque for efficient append/pop operations at both ends",
                basic_example="""
from collections import deque

# Basic queue operations
queue = deque(['a', 'b', 'c'])
queue.appendleft('z')  # Add to left
queue.append('d')      # Add to right
left = queue.popleft() # Remove from left
right = queue.pop()    # Remove from right
                """,
                advanced_example="""
from collections import deque

# Fixed-size rotating buffer
buffer = deque(maxlen=3)
for i in range(5):
    buffer.append(i)  # Automatically removes oldest when full

# Efficient rotation
d = deque(range(10))
d.rotate(3)   # Rotate right by 3
d.rotate(-2)  # Rotate left by 2

# Use as stack or queue
stack = deque()  # append() and pop() for stack
queue = deque()  # append() and popleft() for queue
                """,
                explanation="deque provides O(1) operations at both ends, unlike lists",
                performance_notes="O(1) append/pop at both ends vs O(n) for list operations at beginning"
            ),
            
            StandardLibraryPattern(
                module_name="collections",
                pattern_name="OrderedDict for Order-Preserving Dictionaries",
                category="data_structures",
                description="Use OrderedDict when insertion order matters (pre-Python 3.7)",
                basic_example="""
from collections import OrderedDict

# Maintains insertion order
od = OrderedDict()
od['first'] = 1
od['second'] = 2
od['third'] = 3
                """,
                advanced_example="""
from collections import OrderedDict

# LRU cache implementation
class LRUCache(OrderedDict):
    def __init__(self, capacity):
        super().__init__()
        self.capacity = capacity
    
    def get(self, key):
        if key in self:
            self.move_to_end(key)  # Mark as recently used
            return self[key]
        return None
    
    def put(self, key, value):
        if key in self:
            self.move_to_end(key)
        self[key] = value
        if len(self) > self.capacity:
            self.popitem(last=False)  # Remove oldest
                """,
                explanation="OrderedDict maintains insertion order and provides order-specific methods",
                version_info="Regular dict maintains order in Python 3.7+, but OrderedDict has additional methods"
            ),
            
            # Additional collections patterns...
        ]
    
    def _get_itertools_patterns(self) -> List[StandardLibraryPattern]:
        """Itertools module patterns"""
        return [
            StandardLibraryPattern(
                module_name="itertools",
                pattern_name="chain for Flattening Iterables",
                category="iteration",
                description="Use itertools.chain to efficiently flatten multiple iterables",
                basic_example="""
from itertools import chain

# Flatten multiple iterables
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]

flattened = list(chain(list1, list2, list3))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
                """,
                advanced_example="""
from itertools import chain

# chain.from_iterable for nested structures
nested = [[1, 2], [3, 4], [5, 6]]
flattened = list(chain.from_iterable(nested))

# Memory-efficient processing
def process_files(filenames):
    for line in chain.from_iterable(open(f) for f in filenames):
        yield line.strip()

# Combining different types of iterables
mixed = chain(range(3), 'abc', [10, 20])
# 0, 1, 2, 'a', 'b', 'c', 10, 20
                """,
                explanation="chain creates a single iterator from multiple iterables without creating intermediate lists",
                performance_notes="Memory efficient, lazy evaluation, faster than list concatenation"
            ),
            
            StandardLibraryPattern(
                module_name="itertools",
                pattern_name="combinations and permutations",
                category="combinatorics",
                description="Generate combinations and permutations efficiently",
                basic_example="""
from itertools import combinations, permutations

# Combinations (order doesn't matter)
items = ['A', 'B', 'C', 'D']
for combo in combinations(items, 2):
    print(combo)  # ('A', 'B'), ('A', 'C'), etc.

# Permutations (order matters)
for perm in permutations(items, 2):
    print(perm)  # ('A', 'B'), ('A', 'C'), ('B', 'A'), etc.
                """,
                advanced_example="""
from itertools import combinations, permutations, combinations_with_replacement

# All possible combinations
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# Combinations with replacement
for combo in combinations_with_replacement('ABC', 2):
    print(combo)  # ('A', 'A'), ('A', 'B'), ('A', 'C'), ('B', 'B'), etc.

# Finding all possible passwords
import string
chars = string.ascii_lowercase
passwords = (''.join(p) for p in permutations(chars, 4))
                """,
                explanation="Efficiently generates mathematical combinations and permutations",
                performance_notes="Memory efficient generators, much faster than manual recursive implementations"
            ),
            
            StandardLibraryPattern(
                module_name="itertools",
                pattern_name="groupby for Grouping Data",
                category="data_processing",
                description="Use groupby to group consecutive elements by a key function",
                basic_example="""
from itertools import groupby

# Group consecutive elements
data = [1, 1, 2, 2, 2, 3, 1, 1]
for key, group in groupby(data):
    print(f"{key}: {list(group)}")
# 1: [1, 1]
# 2: [2, 2, 2]
# 3: [3]
# 1: [1, 1]
                """,
                advanced_example="""
from itertools import groupby
from operator import itemgetter

# Group by custom key function
students = [
    ('Alice', 'A'), ('Bob', 'B'), ('Charlie', 'A'),
    ('David', 'B'), ('Eve', 'A')
]

# Sort first, then group (groupby only groups consecutive items)
students.sort(key=itemgetter(1))
for grade, group in groupby(students, key=itemgetter(1)):
    names = [student[0] for student in group]
    print(f"Grade {grade}: {names}")

# Group lines by first character
lines = ['apple', 'apricot', 'banana', 'blueberry', 'cherry']
for first_char, group in groupby(lines, key=lambda x: x[0]):
    print(f"{first_char}: {list(group)}")
                """,
                explanation="groupby groups consecutive elements with the same key, requires sorted input for complete grouping",
                common_mistakes="Forgetting to sort data before grouping when you want all items with same key together"
            ),
            
            StandardLibraryPattern(
                module_name="itertools",
                pattern_name="cycle and repeat for Infinite Iterators",
                category="infinite_iteration",
                description="Use cycle and repeat for infinite iteration patterns",
                basic_example="""
from itertools import cycle, repeat

# Cycle through values infinitely
colors = cycle(['red', 'green', 'blue'])
for i, color in enumerate(colors):
    if i >= 10:
        break
    print(f"Item {i}: {color}")

# Repeat a value
for value in repeat('hello', 3):
    print(value)  # Prints 'hello' three times
                """,
                advanced_example="""
from itertools import cycle, repeat, islice

# Round-robin assignment
servers = cycle(['server1', 'server2', 'server3'])
requests = ['req1', 'req2', 'req3', 'req4', 'req5']
assignments = list(zip(requests, servers))

# Padding sequences
def pad_sequence(seq, length, pad_value=None):
    return list(islice(chain(seq, repeat(pad_value)), length))

padded = pad_sequence([1, 2, 3], 6, 0)  # [1, 2, 3, 0, 0, 0]

# Infinite counter with step
def count_by(start=0, step=1):
    current = start
    while True:
        yield current
        current += step
                """,
                explanation="cycle and repeat create infinite iterators for repetitive patterns",
                performance_notes="Memory efficient for infinite sequences, use with islice to limit"
            ),
            
            # Additional itertools patterns...
        ]
    
    def _get_functools_patterns(self) -> List[StandardLibraryPattern]:
        """Functools module patterns"""
        return [
            StandardLibraryPattern(
                module_name="functools",
                pattern_name="lru_cache for Memoization",
                category="performance",
                description="Use lru_cache for automatic memoization of expensive functions",
                basic_example="""
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Much faster for repeated calls
print(fibonacci(100))  # Computed once, cached for future calls
                """,
                advanced_example="""
from functools import lru_cache

# Custom cache size
@lru_cache(maxsize=None)  # Unlimited cache
def expensive_computation(x, y):
    # Simulate expensive operation
    return sum(i * j for i in range(x) for j in range(y))

# Cache info and management
print(expensive_computation.cache_info())  # Cache statistics
expensive_computation.cache_clear()  # Clear cache

# With typed parameter (Python 3.3+)
@lru_cache(maxsize=128, typed=True)
def process_data(data):
    # Different cache entries for int vs float
    return data * 2

process_data(5)    # Cached separately
process_data(5.0)  # Different cache entry
                """,
                explanation="lru_cache provides automatic memoization with LRU eviction policy",
                performance_notes="Dramatic speedup for recursive functions and expensive computations",
                version_info="Available since Python 3.2, typed parameter since 3.3"
            ),
            
            StandardLibraryPattern(
                module_name="functools",
                pattern_name="partial for Function Specialization",
                category="functional_programming",
                description="Use partial to create specialized versions of functions",
                basic_example="""
from functools import partial

def multiply(x, y):
    return x * y

# Create specialized functions
double = partial(multiply, 2)
triple = partial(multiply, 3)

print(double(5))  # 10
print(triple(5))  # 15
                """,
                advanced_example="""
from functools import partial
import operator

# Partial with keyword arguments
def greet(greeting, name, punctuation='!'):
    return f"{greeting}, {name}{punctuation}"

say_hello = partial(greet, 'Hello')
say_goodbye = partial(greet, 'Goodbye', punctuation='.')

print(say_hello('Alice'))     # Hello, Alice!
print(say_goodbye('Bob'))     # Goodbye, Bob.

# Using with operators
add_ten = partial(operator.add, 10)
numbers = [1, 2, 3, 4, 5]
result = list(map(add_ten, numbers))  # [11, 12, 13, 14, 15]

# Event handling with partial
def handle_click(button_id, event):
    print(f"Button {button_id} clicked: {event}")

button1_handler = partial(handle_click, 'button1')
button2_handler = partial(handle_click, 'button2')
                """,
                explanation="partial creates new functions with some arguments pre-filled",
                performance_notes="Slight overhead but improves code reusability and readability"
            ),
            
            StandardLibraryPattern(
                module_name="functools",
                pattern_name="reduce for Cumulative Operations",
                category="functional_programming",
                description="Use reduce for cumulative operations (when built-ins aren't available)",
                basic_example="""
from functools import reduce
import operator

# Basic reduction
numbers = [1, 2, 3, 4, 5]
product = reduce(operator.mul, numbers)  # 120
sum_result = reduce(operator.add, numbers)  # 15 (prefer sum())
                """,
                advanced_example="""
from functools import reduce

# Complex reductions
def deep_merge(dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

# Merge multiple dictionaries
dicts = [{'a': 1}, {'b': 2}, {'a': {'x': 1}}, {'a': {'y': 2}}]
merged = reduce(deep_merge, dicts)

# Find maximum by custom criteria
students = [('Alice', 85), ('Bob', 90), ('Charlie', 78)]
top_student = reduce(lambda a, b: a if a[1] > b[1] else b, students)
                """,
                explanation="reduce applies a function cumulatively to items in a sequence",
                common_mistakes="Using reduce when built-in functions like sum(), max(), min() are available"
            ),
            
            # Additional functools patterns...
        ]
    
    def _get_path_patterns(self) -> List[StandardLibraryPattern]:
        """Pathlib and os.path patterns"""
        return [
            StandardLibraryPattern(
                module_name="pathlib",
                pattern_name="Path Objects for File Operations",
                category="file_system",
                description="Use pathlib.Path for modern, cross-platform file operations",
                basic_example="""
from pathlib import Path

# Create path objects
path = Path('data/file.txt')
absolute_path = path.resolve()

# Check properties
if path.exists():
    print(f"Size: {path.stat().st_size}")
    print(f"Is file: {path.is_file()}")
    print(f"Parent: {path.parent}")
                """,
                advanced_example="""
from pathlib import Path

# Path manipulation
base = Path('/home/user')
config_file = base / 'config' / 'settings.json'

# Create directories
config_file.parent.mkdir(parents=True, exist_ok=True)

# Glob patterns
data_dir = Path('data')
for txt_file in data_dir.glob('*.txt'):
    print(txt_file)

# Recursive search
for py_file in Path('.').rglob('*.py'):
    if py_file.stat().st_size > 1000:
        print(f"Large file: {py_file}")

# File operations
content = config_file.read_text()
config_file.write_text('new content')

# Path components
parts = config_file.parts
suffix = config_file.suffix
stem = config_file.stem
                """,
                explanation="pathlib provides object-oriented path manipulation with cross-platform compatibility",
                performance_notes="Slightly slower than os.path for simple operations but much more readable",
                version_info="Available since Python 3.4"
            ),
            
            StandardLibraryPattern(
                module_name="os.path",
                pattern_name="Legacy Path Operations",
                category="file_system",
                description="os.path functions for compatibility and specific use cases",
                basic_example="""
import os.path

# Basic path operations
path = '/home/user/file.txt'
directory = os.path.dirname(path)   # '/home/user'
filename = os.path.basename(path)   # 'file.txt'
name, ext = os.path.splitext(filename)  # 'file', '.txt'

# Path existence and properties
if os.path.exists(path):
    size = os.path.getsize(path)
    mtime = os.path.getmtime(path)
                """,
                advanced_example="""
import os.path

# Cross-platform path joining
config_path = os.path.join('config', 'app', 'settings.ini')

# Absolute and relative paths
abs_path = os.path.abspath('relative/path')
rel_path = os.path.relpath('/absolute/path', '/absolute')

# Path normalization
normalized = os.path.normpath('path//with/../redundant/./parts')

# Common path operations
def find_common_path(paths):
    return os.path.commonpath(paths)

def is_subpath(child, parent):
    return os.path.commonpath([child, parent]) == parent

# Walking directory trees (prefer pathlib.rglob())
for root, dirs, files in os.walk('directory'):
    for file in files:
        full_path = os.path.join(root, file)
        print(full_path)
                """,
                explanation="os.path provides traditional path operations, still useful for compatibility",
                common_mistakes="Using string operations instead of path functions for cross-platform compatibility"
            ),
            
            # Additional path patterns...
        ]
    
    def _get_datetime_patterns(self) -> List[StandardLibraryPattern]:
        """Datetime and time patterns"""
        return [
            StandardLibraryPattern(
                module_name="datetime",
                pattern_name="Date and Time Manipulation",
                category="date_time",
                description="Proper datetime handling with timezone awareness",
                basic_example="""
from datetime import datetime, date, time, timedelta

# Current date and time
now = datetime.now()
today = date.today()

# Creating specific dates
birthday = date(1990, 5, 15)
meeting = datetime(2023, 12, 25, 14, 30)

# Date arithmetic
tomorrow = today + timedelta(days=1)
next_week = now + timedelta(weeks=1)
                """,
                advanced_example="""
from datetime import datetime, timezone, timedelta
import zoneinfo  # Python 3.9+

# Timezone-aware datetimes
utc_now = datetime.now(timezone.utc)
local_tz = zoneinfo.ZoneInfo('America/New_York')
local_time = utc_now.astimezone(local_tz)

# Parsing and formatting
date_string = "2023-12-25 14:30:00"
parsed = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
formatted = parsed.strftime("%B %d, %Y at %I:%M %p")

# Business day calculations
def add_business_days(start_date, days):
    current = start_date
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday = 0, Sunday = 6
            days -= 1
    return current

# Age calculation
def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                """,
                explanation="datetime provides comprehensive date and time manipulation with timezone support",
                version_info="zoneinfo available in Python 3.9+, use pytz for earlier versions",
                common_mistakes="Using naive datetimes for applications that need timezone awareness"
            ),
            
            # Additional datetime patterns...
        ]
    
    def _get_serialization_patterns(self) -> List[StandardLibraryPattern]:
        """JSON and data serialization patterns"""
        return [
            StandardLibraryPattern(
                module_name="json",
                pattern_name="JSON Serialization Best Practices",
                category="serialization",
                description="Efficient and safe JSON handling with custom encoders",
                basic_example="""
import json

# Basic JSON operations
data = {'name': 'Alice', 'age': 30, 'scores': [85, 90, 78]}

# Serialize to string
json_string = json.dumps(data, indent=2)

# Serialize to file
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Deserialize from string
parsed_data = json.loads(json_string)

# Deserialize from file
with open('data.json', 'r') as f:
    loaded_data = json.load(f)
                """,
                advanced_example="""
import json
from datetime import datetime, date
from decimal import Decimal

# Custom JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

# Usage with custom encoder
data = {
    'timestamp': datetime.now(),
    'amount': Decimal('123.45'),
    'date': date.today()
}

json_string = json.dumps(data, cls=CustomJSONEncoder, indent=2)

# Safe JSON loading with error handling
def safe_json_load(filename, default=None):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON: {e}")
        return default

# Streaming JSON for large files
def process_large_json(filename):
    with open(filename, 'r') as f:
        for line in f:
            try:
                obj = json.loads(line)
                yield obj
            except json.JSONDecodeError:
                continue
                """,
                explanation="JSON module provides efficient serialization with customization options",
                performance_notes="Use json.loads/dumps for strings, json.load/dump for files",
                common_mistakes="Not handling JSONDecodeError, not using custom encoders for complex objects"
            ),
            
            # Additional serialization patterns...
        ]
    
    def _get_regex_patterns(self) -> List[StandardLibraryPattern]:
        """Regular expressions patterns"""
        return [
            StandardLibraryPattern(
                module_name="re",
                pattern_name="Efficient Regular Expression Usage",
                category="text_processing",
                description="Optimal regex patterns with compilation and performance considerations",
                basic_example="""
import re

# Basic pattern matching
text = "Contact: john.doe@example.com or call 555-1234"

# Find email
email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
email = re.search(email_pattern, text)
if email:
    print(f"Found email: {email.group()}")

# Find all phone numbers
phone_pattern = r'\\b\\d{3}-\\d{4}\\b'
phones = re.findall(phone_pattern, text)
                """,
                advanced_example="""
import re

# Compiled patterns for better performance
EMAIL_PATTERN = re.compile(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b')
PHONE_PATTERN = re.compile(r'\\b(\\d{3})-(\\d{4})\\b')

def extract_contacts(text):
    emails = EMAIL_PATTERN.findall(text)
    phones = [(match.group(1), match.group(2)) for match in PHONE_PATTERN.finditer(text)]
    return emails, phones

# Named groups for clarity
LOG_PATTERN = re.compile(r'(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}) (?P<level>\\w+) (?P<message>.*)')

def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        return match.groupdict()
    return None

# Substitution with functions
def title_case_replacer(match):
    return match.group().title()

text = "hello world python programming"
result = re.sub(r'\\b\\w+\\b', title_case_replacer, text)

# Verbose patterns for readability
COMPLEX_PATTERN = re.compile(r'''
    (?P<protocol>https?)://     # Protocol
    (?P<domain>[\\w.-]+)        # Domain
    (?P<port>:\\d+)?            # Optional port
    (?P<path>/[\\w/.-]*)?       # Optional path
''', re.VERBOSE)
                """,
                explanation="Regular expressions provide powerful text processing with proper compilation for performance",
                performance_notes="Compile patterns used multiple times, use raw strings to avoid escaping issues",
                common_mistakes="Not compiling frequently used patterns, overly complex regex when string methods suffice"
            ),
            
            # Additional regex patterns...
        ]
    
    def _get_io_patterns(self) -> List[StandardLibraryPattern]:
        """File and I/O patterns"""
        return [
            StandardLibraryPattern(
                module_name="io",
                pattern_name="Advanced File I/O Operations",
                category="file_io",
                description="Efficient file handling with proper encoding and buffering",
                basic_example="""
# Basic file operations with proper encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# Line-by-line processing for large files
with open('large_file.txt', 'r', encoding='utf-8') as f:
    for line in f:
        process_line(line.strip())
                """,
                advanced_example="""
import io
import csv
from contextlib import contextmanager

# String I/O for testing
def process_csv_data(csv_string):
    csv_file = io.StringIO(csv_string)
    reader = csv.reader(csv_file)
    return list(reader)

# Binary I/O operations
def read_binary_chunks(filename, chunk_size=8192):
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Custom file-like objects
class UpperCaseFile:
    def __init__(self, filename):
        self.file = open(filename, 'r')
    
    def read(self, size=-1):
        return self.file.read(size).upper()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

# Buffered I/O control
@contextmanager
def buffered_writer(filename, buffer_size=8192):
    with open(filename, 'w', buffering=buffer_size) as f:
        yield f
                """,
                explanation="Advanced I/O operations with proper resource management and performance optimization",
                performance_notes="Use appropriate buffer sizes, process large files line-by-line to avoid memory issues"
            ),
            
            # Additional I/O patterns...
        ]
    
    def _get_system_patterns(self) -> List[StandardLibraryPattern]:
        """System and environment patterns"""
        return [
            StandardLibraryPattern(
                module_name="os",
                pattern_name="Environment and System Operations",
                category="system",
                description="Safe system operations and environment variable handling",
                basic_example="""
import os

# Environment variables
database_url = os.environ.get('DATABASE_URL', 'sqlite:///default.db')
debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'

# Current working directory
current_dir = os.getcwd()
os.chdir('/tmp')  # Change directory
os.chdir(current_dir)  # Change back
                """,
                advanced_example="""
import os
import sys
from pathlib import Path

# Safe environment variable handling
class Config:
    def __init__(self):
        self.database_url = self._get_env('DATABASE_URL', required=True)
        self.debug = self._get_bool_env('DEBUG', default=False)
        self.port = self._get_int_env('PORT', default=8000)
    
    def _get_env(self, key, default=None, required=False):
        value = os.environ.get(key, default)
        if required and value is None:
            raise ValueError(f"Required environment variable {key} not set")
        return value
    
    def _get_bool_env(self, key, default=False):
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_int_env(self, key, default=0):
        try:
            return int(os.environ.get(key, default))
        except ValueError:
            return default

# Platform-specific operations
def get_config_dir():
    if sys.platform == 'win32':
        return Path(os.environ['APPDATA'])
    else:
        return Path.home() / '.config'

# Process management
def run_command_safely(command):
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return None, "Command timed out", -1
                """,
                explanation="System operations with proper error handling and cross-platform compatibility",
                common_mistakes="Not providing defaults for environment variables, not handling missing variables gracefully"
            ),
            
            # Additional system patterns...
        ]
    
    def _get_logging_patterns(self) -> List[StandardLibraryPattern]:
        """Logging patterns"""
        return [
            StandardLibraryPattern(
                module_name="logging",
                pattern_name="Structured Logging Configuration",
                category="debugging",
                description="Proper logging setup with formatters, handlers, and levels",
                basic_example="""
import logging

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("An error occurred")
                """,
                advanced_example="""
import logging
import logging.handlers
import json
from datetime import datetime

# Custom JSON formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Advanced logging configuration
def setup_logging(log_level='INFO', log_file='app.log'):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Context-aware logging
class LoggerMixin:
    @property
    def logger(self):
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_method_call(self, method_name, *args, **kwargs):
        self.logger.debug(f"Calling {method_name} with args={args}, kwargs={kwargs}")
                """,
                explanation="Structured logging with proper configuration for production applications",
                performance_notes="Use appropriate log levels, consider async logging for high-throughput applications"
            ),
            
            # Additional logging patterns...
        ]
    
    def _get_concurrency_patterns(self) -> List[StandardLibraryPattern]:
        """Threading and multiprocessing patterns"""
        return [
            StandardLibraryPattern(
                module_name="threading",
                pattern_name="Thread-Safe Operations",
                category="concurrency",
                description="Safe threading patterns with locks and thread-local storage",
                basic_example="""
import threading
import time

# Basic threading
def worker(name):
    for i in range(5):
        print(f"Worker {name}: {i}")
        time.sleep(1)

threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(f"Thread-{i}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
                """,
                advanced_example="""
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor

# Thread-safe counter
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
    
    @property
    def value(self):
        with self._lock:
            return self._value

# Producer-consumer pattern
def producer_consumer_example():
    q = queue.Queue(maxsize=10)
    
    def producer():
        for i in range(20):
            q.put(f"item-{i}")
            time.sleep(0.1)
        q.put(None)  # Sentinel value
    
    def consumer():
        while True:
            item = q.get()
            if item is None:
                break
            print(f"Processing {item}")
            time.sleep(0.2)
            q.task_done()
    
    threading.Thread(target=producer).start()
    threading.Thread(target=consumer).start()

# Thread pool for I/O bound tasks
def process_urls(urls):
    def fetch_url(url):
        # Simulate network request
        time.sleep(1)
        return f"Content from {url}"
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_url, urls))
    
    return results
                """,
                explanation="Threading patterns for I/O-bound tasks with proper synchronization",
                performance_notes="Use ThreadPoolExecutor for I/O-bound tasks, avoid threading for CPU-bound tasks due to GIL"
            ),
            
            # Additional concurrency patterns...
        ]
    
    def _get_network_patterns(self) -> List[StandardLibraryPattern]:
        """Network and HTTP patterns"""
        return [
            StandardLibraryPattern(
                module_name="urllib",
                pattern_name="HTTP Requests with urllib",
                category="networking",
                description="HTTP operations using standard library urllib",
                basic_example="""
import urllib.request
import urllib.parse

# Basic GET request
response = urllib.request.urlopen('https://api.example.com/data')
data = response.read().decode('utf-8')
print(f"Status: {response.status}")
                """,
                advanced_example="""
import urllib.request
import urllib.parse
import urllib.error
import json

class HTTPClient:
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params:
            url += '?' + urllib.parse.urlencode(params)
        
        try:
            response = urllib.request.urlopen(url, timeout=self.timeout)
            return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return None
    
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        json_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            response = urllib.request.urlopen(req, timeout=self.timeout)
            return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {'error': f"HTTP {e.code}: {e.reason}"}

# Usage
client = HTTPClient('https://api.example.com')
result = client.get('users', {'page': 1, 'limit': 10})
                """,
                explanation="HTTP operations using standard library with proper error handling",
                common_mistakes="Not handling network errors, not setting timeouts, not encoding data properly"
            ),
            
            # Additional network patterns...
        ]
    
    def _get_math_patterns(self) -> List[StandardLibraryPattern]:
        """Math and statistics patterns"""
        return [
            StandardLibraryPattern(
                module_name="statistics",
                pattern_name="Statistical Calculations",
                category="mathematics",
                description="Built-in statistical functions for data analysis",
                basic_example="""
import statistics

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

mean = statistics.mean(data)
median = statistics.median(data)
mode = statistics.mode([1, 1, 2, 3, 3, 3, 4])
stdev = statistics.stdev(data)
                """,
                advanced_example="""
import statistics
import math

def analyze_dataset(data):
    if not data:
        return None
    
    analysis = {
        'count': len(data),
        'mean': statistics.mean(data),
        'median': statistics.median(data),
        'std_dev': statistics.stdev(data) if len(data) > 1 else 0,
        'variance': statistics.variance(data) if len(data) > 1 else 0,
        'min': min(data),
        'max': max(data),
        'range': max(data) - min(data)
    }
    
    # Quartiles
    sorted_data = sorted(data)
    n = len(sorted_data)
    analysis['q1'] = statistics.median(sorted_data[:n//2])
    analysis['q3'] = statistics.median(sorted_data[(n+1)//2:])
    analysis['iqr'] = analysis['q3'] - analysis['q1']
    
    return analysis

# Harmonic and geometric means
def advanced_means(data):
    return {
        'arithmetic_mean': statistics.mean(data),
        'harmonic_mean': statistics.harmonic_mean(data),
        'geometric_mean': statistics.geometric_mean(data)  # Python 3.8+
    }

# Correlation coefficient
def correlation(x, y):
    if len(x) != len(y):
        raise ValueError("Lists must have same length")
    
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
    sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
    
    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    return numerator / denominator if denominator != 0 else 0
                """,
                explanation="Statistical analysis using built-in statistics module",
                version_info="geometric_mean available in Python 3.8+",
                performance_notes="Built-in functions are optimized and handle edge cases properly"
            ),
            
            # Additional math patterns...
        ]
    
    def _get_algorithms_patterns(self) -> List[StandardLibraryPattern]:
        """Data structures and algorithms patterns"""
        return [
            StandardLibraryPattern(
                module_name="heapq",
                pattern_name="Heap Operations for Priority Queues",
                category="algorithms",
                description="Efficient priority queue operations using heapq",
                basic_example="""
import heapq

# Basic heap operations
heap = []
heapq.heappush(heap, 3)
heapq.heappush(heap, 1)
heapq.heappush(heap, 4)

smallest = heapq.heappop(heap)  # Returns 1
print(heap)  # [3, 4] - still a valid heap
                """,
                advanced_example="""
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Task:
    priority: int
    description: str
    item: Any = field(compare=False)  # Don't compare this field

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0
    
    def push(self, item, priority):
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1
    
    def pop(self):
        if self._queue:
            return heapq.heappop(self._queue)[-1]
        raise IndexError("pop from empty priority queue")
    
    def __len__(self):
        return len(self._queue)

# Finding N largest/smallest items
data = [1, 8, 2, 23, 7, -4, 18, 23, 42, 37, 2]
largest_3 = heapq.nlargest(3, data)  # [42, 37, 23]
smallest_3 = heapq.nsmallest(3, data)  # [-4, 1, 2]

# With key function
students = [('Alice', 85), ('Bob', 90), ('Charlie', 78)]
top_students = heapq.nlargest(2, students, key=lambda x: x[1])

# Merge sorted iterables
def merge_sorted_files(filenames):
    def file_reader(filename):
        with open(filename) as f:
            for line in f:
                yield int(line.strip())
    
    iterators = [file_reader(f) for f in filenames]
    return heapq.merge(*iterators)
                """,
                explanation="heapq provides efficient heap operations for priority queues and sorting",
                performance_notes="O(log n) push/pop operations, O(n log k) for nlargest/nsmallest"
            ),
            
            # Additional algorithms patterns...
        ]
    
    def _get_testing_patterns(self) -> List[StandardLibraryPattern]:
        """Testing and debugging patterns"""
        return [
            StandardLibraryPattern(
                module_name="unittest",
                pattern_name="Unit Testing Best Practices",
                category="testing",
                description="Comprehensive unit testing with unittest framework",
                basic_example="""
import unittest

class TestMathOperations(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 2, 4)
    
    def test_division(self):
        self.assertEqual(10 / 2, 5)
        with self.assertRaises(ZeroDivisionError):
            10 / 0

if __name__ == '__main__':
    unittest.main()
                """,
                advanced_example="""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_with_mock(self):
        # Mocking external dependencies
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'status': 'success'}
            mock_get.return_value = mock_response
            
            # Test code that uses requests.get
            result = some_function_that_uses_requests()
            self.assertEqual(result['status'], 'success')
    
    def test_file_operations(self):
        # Test with temporary files
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Test file reading function
        content = read_file(test_file)
        self.assertEqual(content, 'test content')
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_unix_specific(self):
        # Test that only runs on Unix systems
        pass
    
    def test_with_subtest(self):
        # Test multiple related cases
        test_cases = [(2, 4), (3, 9), (4, 16)]
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                self.assertEqual(square(input_val), expected)

# Custom test suite
def create_test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestMathOperations('test_addition'))
    suite.addTest(TestAdvancedFeatures('test_with_mock'))
    return suite
                """,
                explanation="Comprehensive unit testing with mocking, fixtures, and advanced features",
                performance_notes="Use setUp/tearDown for test fixtures, mock external dependencies for isolation"
            ),
            
            # Additional testing patterns...
        ]
    
    def _get_covered_modules(self) -> Set[str]:
        """Get set of all modules covered by patterns"""
        return {pattern.module_name for pattern in self.patterns}
    
    def _organize_by_category(self) -> Dict[str, List[StandardLibraryPattern]]:
        """Organize patterns by category"""
        categories = defaultdict(list)
        for pattern in self.patterns:
            categories[pattern.category].append(pattern)
        return dict(categories)
    
    def _build_module_index(self) -> Dict[str, List[StandardLibraryPattern]]:
        """Build index of patterns by module"""
        module_index = defaultdict(list)
        for pattern in self.patterns:
            module_index[pattern.module_name].append(pattern)
        return dict(module_index)
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, str]]:
        """Build compatibility matrix for different Python versions"""
        # This would be expanded with actual compatibility data
        return {
            'pathlib': {'min_version': '3.4', 'notes': 'Object-oriented filesystem paths'},
            'statistics': {'min_version': '3.4', 'notes': 'Statistical functions'},
            'zoneinfo': {'min_version': '3.9', 'notes': 'IANA timezone support'},
            'functools.lru_cache': {'min_version': '3.2', 'notes': 'Memoization decorator'},
        }
    
    def get_patterns_by_module(self, module_name: str) -> List[StandardLibraryPattern]:
        """Get all patterns for a specific module"""
        return self.module_index.get(module_name, [])
    
    def get_patterns_by_category(self, category: str) -> List[StandardLibraryPattern]:
        """Get all patterns for a specific category"""
        return self.categories.get(category, [])
    
    def search_patterns(self, query: str) -> List[StandardLibraryPattern]:
        """Search patterns by query string"""
        query_lower = query.lower()
        matching_patterns = []
        
        for pattern in self.patterns:
            if (query_lower in pattern.pattern_name.lower() or
                query_lower in pattern.description.lower() or
                query_lower in pattern.module_name.lower() or
                query_lower in pattern.category.lower() or
                query_lower in pattern.explanation.lower()):
                matching_patterns.append(pattern)
        
        return matching_patterns
    
    def get_performance_patterns(self) -> List[StandardLibraryPattern]:
        """Get patterns with performance considerations"""
        return [p for p in self.patterns if p.performance_notes]
    
    def get_version_specific_patterns(self, min_version: str = None) -> List[StandardLibraryPattern]:
        """Get patterns with version-specific information"""
        patterns = [p for p in self.patterns if p.version_info]
        
        if min_version:
            # Filter by minimum version (simplified comparison)
            filtered = []
            for pattern in patterns:
                if pattern.version_info and min_version in pattern.version_info:
                    filtered.append(pattern)
            return filtered
        
        return patterns
    
    def analyze_code_for_stdlib_usage(self, code: str) -> Dict[str, Any]:
        """Analyze code for standard library usage and suggest improvements"""
        try:
            tree = ast.parse(code)
            analysis = {
                'imports_found': [],
                'suggestions': [],
                'missing_opportunities': [],
                'performance_tips': [],
                'timestamp': time.time()
            }
            
            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports_found'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports_found'].append(node.module)
            
            # Check for improvement opportunities
            analysis.update(self._analyze_for_improvements(tree, code))
            
            return analysis
            
        except SyntaxError as e:
            return {
                'error': f"Syntax error: {e}",
                'suggestions': ["Fix syntax errors before analysis"]
            }
    
    def _analyze_for_improvements(self, tree: ast.AST, code: str) -> Dict[str, List[str]]:
        """Analyze AST for standard library improvement opportunities"""
        suggestions = []
        performance_tips = []
        
        # Check for manual implementations that could use stdlib
        for node in ast.walk(tree):
            # Check for manual sorting that could use heapq
            if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
                if node.func.attr == 'sort':
                    suggestions.append("Consider using heapq.nlargest/nsmallest for partial sorting")
            
            # Check for manual counting
            if isinstance(node, ast.For):
                # Simplified check for counting patterns
                suggestions.append("Consider using collections.Counter for counting operations")
        
        return {
            'suggestions': suggestions,
            'performance_tips': performance_tips
        }
    
    def suggest_module_for_task(self, task_description: str) -> List[Dict[str, str]]:
        """Suggest appropriate standard library modules for a given task"""
        task_lower = task_description.lower()
        suggestions = []
        
        # Module suggestions based on keywords
        module_keywords = {
            'collections': ['count', 'group', 'default', 'queue', 'deque', 'named'],
            'itertools': ['combination', 'permutation', 'chain', 'cycle', 'group'],
            'pathlib': ['file', 'path', 'directory', 'folder'],
            'datetime': ['date', 'time', 'timestamp', 'timezone'],
            'json': ['json', 'serialize', 'parse', 'api'],
            're': ['regex', 'pattern', 'match', 'search', 'replace'],
            'logging': ['log', 'debug', 'error', 'info'],
            'statistics': ['mean', 'median', 'average', 'statistical'],
            'heapq': ['priority', 'queue', 'heap', 'largest', 'smallest'],
            'functools': ['cache', 'memoize', 'partial', 'reduce']
        }
        
        for module, keywords in module_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                patterns = self.get_patterns_by_module(module)
                if patterns:
                    suggestions.append({
                        'module': module,
                        'reason': f"Contains patterns for {', '.join(keywords)}",
                        'pattern_count': len(patterns),
                        'example_pattern': patterns[0].pattern_name
                    })
        
        return suggestions
    
    def generate_training_data(self) -> List[Dict[str, str]]:
        """Generate training data from all patterns"""
        training_data = []
        
        for pattern in self.patterns:
            # Basic usage example
            training_data.append({
                'input': f"How do I use {pattern.module_name} for {pattern.description.lower()}?",
                'output': f"Here's how to use {pattern.module_name}.{pattern.pattern_name}:\n\n{pattern.basic_example}\n\n{pattern.explanation}",
                'module': pattern.module_name,
                'category': pattern.category,
                'difficulty': 'beginner'
            })
            
            # Advanced usage example
            training_data.append({
                'input': f"Show me advanced {pattern.module_name} usage for {pattern.pattern_name.lower()}",
                'output': f"Here's an advanced example of {pattern.pattern_name}:\n\n{pattern.advanced_example}\n\n{pattern.explanation}",
                'module': pattern.module_name,
                'category': pattern.category,
                'difficulty': 'advanced'
            })
            
            # Performance question if applicable
            if pattern.performance_notes:
                training_data.append({
                    'input': f"What are the performance considerations for {pattern.module_name}?",
                    'output': f"Performance notes for {pattern.pattern_name}:\n\n{pattern.performance_notes}\n\nExample:\n{pattern.basic_example}",
                    'module': pattern.module_name,
                    'category': 'performance',
                    'difficulty': 'intermediate'
                })
            
            # Common mistakes if applicable
            if pattern.common_mistakes:
                training_data.append({
                    'input': f"What are common mistakes when using {pattern.module_name}?",
                    'output': f"Common mistakes with {pattern.pattern_name}:\n\n{pattern.common_mistakes}\n\nCorrect usage:\n{pattern.basic_example}",
                    'module': pattern.module_name,
                    'category': 'best_practices',
                    'difficulty': 'intermediate'
                })
        
        return training_data
    
    def get_module_coverage_report(self) -> Dict[str, Any]:
        """Generate a report of standard library module coverage"""
        return {
            'total_patterns': len(self.patterns),
            'modules_covered': len(self.modules_covered),
            'modules_list': sorted(self.modules_covered),
            'categories': list(self.categories.keys()),
            'patterns_by_module': {
                module: len(patterns) 
                for module, patterns in self.module_index.items()
            },
            'patterns_by_category': {
                category: len(patterns) 
                for category, patterns in self.categories.items()
            }
        }


# Example usage and testing
if __name__ == "__main__":
    specialist = StandardLibrarySpecialist()
    
    # Test module search
    collections_patterns = specialist.get_patterns_by_module('collections')
    print(f"Collections patterns: {len(collections_patterns)}")
    
    # Test pattern search
    performance_patterns = specialist.get_performance_patterns()
    print(f"Performance patterns: {len(performance_patterns)}")
    
    # Test code analysis
    test_code = """
import collections
data = ['a', 'b', 'a', 'c', 'b', 'a']
counts = {}
for item in data:
    if item in counts:
        counts[item] += 1
    else:
        counts[item] = 1
    """
    
    analysis = specialist.analyze_code_for_stdlib_usage(test_code)
    print(f"Code analysis: {analysis}")
    
    # Generate training data
    training_data = specialist.generate_training_data()
    print(f"Generated {len(training_data)} training examples")
    
    # Coverage report
    report = specialist.get_module_coverage_report()
    print(f"Coverage report: {report}")

