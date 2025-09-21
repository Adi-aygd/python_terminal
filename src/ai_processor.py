"""
AI Processor

This module handles natural language processing to convert plain English
queries into terminal commands.
"""

import re
from typing import List, Dict, Optional, Tuple


class AIProcessor:
    """
    Processes natural language queries and converts them to terminal commands.
    """
    
    def __init__(self):
        """Initialize the AI processor with command patterns."""
        self.command_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Initialize natural language patterns and their corresponding commands.
        
        Returns:
            Dictionary mapping intent types to (pattern, command) tuples
        """
        patterns = {
            'file_listing': [
                (r"(?:show|list|display)\s+(?:me\s+)?(?:the\s+)?(?:files?|contents?|directory)\s*(?:in\s+(.+))?", "ls {path}"),
                (r"(?:what'?s|what\s+is)\s+in\s+(?:the\s+)?(.+)\s+(?:directory|folder)", "ls {path}"),
                (r"list\s+(?:all\s+)?files?\s+in\s+(.+)", "ls {path}"),
                (r"show\s+(?:me\s+)?(?:the\s+)?current\s+directory\s+contents?", "ls"),
            ],
            
            'directory_navigation': [
                (r"(?:go\s+to|change\s+to|navigate\s+to|enter)\s+(?:the\s+)?(.+)\s+(?:directory|folder)", "cd {path}"),
                (r"cd\s+to\s+(.+)", "cd {path}"),
                (r"move\s+to\s+(.+)\s+(?:directory|folder)", "cd {path}"),
                (r"go\s+(?:to\s+)?home", "cd ~"),
                (r"go\s+back\s+(?:to\s+)?parent\s+(?:directory|folder)", "cd .."),
            ],
            
            'directory_creation': [
                (r"(?:create|make|mkdir)\s+(?:a\s+)?(?:new\s+)?(?:directory|folder)\s+(?:called\s+|named\s+)?(.+)", "mkdir {name}"),
                (r"new\s+(?:directory|folder)\s+(.+)", "mkdir {name}"),
                (r"make\s+(?:directory|folder)\s+(.+)", "mkdir {name}"),
                (r"(?:create|make)\s+(?:folder|directory)\s+(?:called\s+|named\s+)?(.+)", "mkdir {name}"),
            ],
            
            'directory_deletion': [
                (r"(?:remove|delete|rm)\s+(?:the\s+)?(?:directory|folder)\s+(?:called\s+|named\s+)?(.+)", "rm -r {target}"),
                (r"(?:delete|remove)\s+(?:folder|directory)\s+(.+)", "rm -r {target}"),
                (r"(?:rm|rmdir)\s+(?:the\s+)?(?:directory|folder)\s+(.+)", "rm -r {target}"),
                (r"^delete\s+([a-zA-Z_][a-zA-Z0-9_]*)$", "rm -rf {target}"),
                (r"^remove\s+([a-zA-Z_][a-zA-Z0-9_]*)$", "rm -rf {target}"),
            ],
            
            'file_creation': [
                (r"(?:create|make|touch)\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+|named\s+)?(.+)", "touch {name}"),
                (r"new\s+file\s+(.+)", "touch {name}"),
                (r"create\s+empty\s+file\s+(.+)", "touch {name}"),
            ],
            
            'file_operations': [
                (r"(?:copy|cp)\s+(.+)\s+to\s+(.+)", "cp {source} {dest}"),
                (r"(?:move|mv|rename)\s+(.+)\s+to\s+(.+)", "mv {source} {dest}"),
                (r"(?:remove|delete|rm)\s+(?:the\s+)?(?:directory|folder)\s+(?:called\s+|named\s+)?(.+)", "rm -r {target}"),
                (r"(?:remove|delete|rm)\s+(?:the\s+)?file\s+(?:called\s+|named\s+)?(.+)", "rm {target}"),
                (r"(?:remove|delete|rm)\s+(?:the\s+)?(.+)", "rm -rf {target}"),
                (r"(?:show|display|cat)\s+(?:the\s+)?(?:contents?\s+of\s+)?(?:file\s+)?(.+)", "cat {file}"),
            ],
            
            'file_search': [
                (r"(?:find|search\s+for|locate)\s+(?:files?\s+)?(?:named\s+|called\s+)?(.+)\s+in\s+(.+)", "find {path} {name}"),
                (r"(?:find|search\s+for|locate)\s+(?:files?\s+)?(?:named\s+|called\s+)?(.+)", "find . {name}"),
                (r"where\s+is\s+(?:the\s+)?(?:file\s+)?(.+)", "find . {name}"),
            ],
            
            'system_info': [
                (r"(?:show|display|what'?s)\s+(?:the\s+)?(?:current\s+)?(?:working\s+)?directory", "pwd"),
                (r"where\s+am\s+i", "pwd"),
                (r"(?:show|list)\s+(?:running\s+)?processes", "ps aux"),
                (r"(?:what\s+)?processes\s+are\s+running", "ps aux"),
                (r"(?:show|display)\s+(?:system\s+)?(?:memory|ram)\s+usage", "free -h"),
                (r"(?:show|display)\s+disk\s+(?:space|usage)", "df -h"),
                (r"(?:show|display)\s+system\s+uptime", "uptime"),
                (r"who\s+(?:am\s+)?i", "whoami"),
                (r"what\s+(?:system|os)\s+am\s+i\s+(?:on|running)", "uname -a"),
            ],
            
            'help_and_info': [
                (r"(?:help|what\s+can\s+(?:i|you)\s+do|show\s+(?:me\s+)?(?:available\s+)?commands)", "help"),
                (r"(?:show|display)\s+(?:command\s+)?history", "history"),
                (r"clear\s+(?:the\s+)?(?:screen|terminal)", "clear"),
            ],
        }
        
        return patterns
    
    def process_query(self, query: str) -> Optional[str]:
        """
        Process a natural language query and return the corresponding command.
        
        Args:
            query: Natural language query from the user
            
        Returns:
            Terminal command string or None if no match found
        """
        query = query.strip().lower()
        
        if not query:
            return None
        
        # Try to match against all patterns
        for intent, pattern_list in self.command_patterns.items():
            for pattern, command_template in pattern_list:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    # Extract captured groups
                    groups = match.groups()
                    
                    # Replace placeholders in command template
                    command = self._format_command(command_template, groups, intent)
                    
                    if command:
                        return command
        
        return None
    
    def _format_command(self, template: str, groups: Tuple, intent: str) -> Optional[str]:
        """
        Format a command template with captured groups.
        
        Args:
            template: Command template string
            groups: Captured groups from regex match
            intent: The intent type
            
        Returns:
            Formatted command string or None if formatting fails
        """
        try:
            # Handle different placeholder patterns
            if '{path}' in template:
                path = groups[0] if groups and groups[0] else '.'
                path = self._clean_path(path)
                return template.replace('{path}', path)
            
            elif '{name}' in template:
                name = groups[0] if groups and groups[0] else ''
                name = self._clean_filename(name)
                if not name:
                    return None
                return template.replace('{name}', name)
            
            elif '{source}' in template and '{dest}' in template:
                if len(groups) >= 2:
                    source = self._clean_path(groups[0])
                    dest = self._clean_path(groups[1])
                    return template.replace('{source}', source).replace('{dest}', dest)
                return None
            
            elif '{target}' in template:
                target = groups[0] if groups and groups[0] else ''
                target = self._clean_path(target)
                if not target:
                    return None
                return template.replace('{target}', target)
            
            elif '{file}' in template:
                file = groups[0] if groups and groups[0] else ''
                file = self._clean_path(file)
                if not file:
                    return None
                return template.replace('{file}', file)
            
            else:
                # No placeholders, return template as-is
                return template
                
        except Exception:
            return None
    
    def _clean_path(self, path: str) -> str:
        """
        Clean and normalize a file path.
        
        Args:
            path: Raw path string
            
        Returns:
            Cleaned path string
        """
        if not path:
            return '.'
        
        # Remove common words that might interfere
        path = re.sub(r'\b(?:the|a|an|this|that)\b\s*', '', path, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        path = ' '.join(path.split())
        
        # Handle quoted paths
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        elif path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
        
        # Convert spaces to underscores if no quotes and contains spaces
        if ' ' in path and not ('"' in path or "'" in path):
            # For simple cases, suggest quoting
            if len(path.split()) <= 3:
                path = f'"{path}"'
        
        return path or '.'
    
    def _clean_filename(self, filename: str) -> str:
        """
        Clean and validate a filename.
        
        Args:
            filename: Raw filename string
            
        Returns:
            Cleaned filename string
        """
        if not filename:
            return ''
        
        # Remove common words
        filename = re.sub(r'\b(?:the|a|an|this|that)\b\s*', '', filename, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        filename = ' '.join(filename.split())
        
        # Handle quoted filenames
        if filename.startswith('"') and filename.endswith('"'):
            filename = filename[1:-1]
        elif filename.startswith("'") and filename.endswith("'"):
            filename = filename[1:-1]
        
        # Convert spaces to underscores or suggest quoting
        if ' ' in filename:
            if len(filename.split()) <= 2:
                filename = f'"{filename}"'
            else:
                filename = filename.replace(' ', '_')
        
        return filename
    
    def get_suggestions(self, query: str) -> List[str]:
        """
        Get command suggestions for a partial or unclear query.
        
        Args:
            query: Partial natural language query
            
        Returns:
            List of suggested commands
        """
        query_lower = query.lower()
        suggestions = []
        
        # Keyword-based suggestions
        if any(word in query_lower for word in ['list', 'show', 'display']):
            suggestions.extend(['ls', 'ls -la', 'pwd', 'ps aux'])
        
        if any(word in query_lower for word in ['create', 'make', 'new']):
            suggestions.extend(['mkdir <directory>', 'touch <file>', 'cp <source> <dest>'])
        
        if any(word in query_lower for word in ['delete', 'remove', 'rm']):
            suggestions.extend(['rm <file>', 'rm -r <directory>', 'rmdir <directory>'])
        
        if any(word in query_lower for word in ['find', 'search', 'locate']):
            suggestions.extend(['find . -name "<pattern>"', 'find <path> -name "<pattern>"'])
        
        if any(word in query_lower for word in ['process', 'running', 'system']):
            suggestions.extend(['ps aux', 'top', 'free -h', 'df -h', 'uptime'])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def is_natural_language_query(self, query: str) -> bool:
        """
        Determine if a query looks like natural language vs a direct command.
        
        Args:
            query: Input query
            
        Returns:
            True if it looks like natural language, False if it looks like a command
        """
        query = query.strip().lower()
        
        # Check for common natural language indicators
        natural_indicators = [
            r'\b(?:show|list|display|what|how|where|find|search|create|make|delete|remove)\b',
            r'\b(?:me|the|a|an|this|that|some|all)\b',
            r'\b(?:can|could|would|should|will)\b',
            r'\?$',  # Ends with question mark
        ]
        
        for pattern in natural_indicators:
            if re.search(pattern, query):
                return True
        
        # Check for direct command patterns (less likely to be natural language)
        command_patterns = [
            r'^[a-zA-Z_-]+(\s+[^\s]+)*$',  # Simple command format
            r'^[a-zA-Z_-]+\s+-[a-zA-Z]+',  # Command with flags
        ]
        
        for pattern in command_patterns:
            if re.match(pattern, query) and not re.search(r'\b(?:show|list|display)\b', query):
                return False
        
        return True
    
    def get_example_queries(self) -> List[str]:
        """
        Get example natural language queries that the processor can handle.
        
        Returns:
            List of example queries
        """
        examples = [
            "show me the files in this directory",
            "create a new folder called projects",
            "copy file.txt to backup folder",
            "find all python files",
            "what processes are running",
            "show system memory usage",
            "go to the home directory",
            "delete the old file",
            "delete project",
            "remove folder called test",
            "delete directory named backup",
            "show me the current directory",
            "list all files including hidden ones",
            "create an empty file called readme.txt",
            "move documents to archive folder",
            "where am I?",
            "what's in the Documents folder?",
            "make a directory named test",
        ]
        
        return examples