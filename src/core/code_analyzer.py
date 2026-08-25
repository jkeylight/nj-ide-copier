"""
Code Analyzer - Analyzes code structure using AST parsing.

Provides Python code analysis including imports extraction, function/class
listing, and cyclomatic complexity calculation.
"""

import ast
from typing import Dict, List, Optional


class CodeAnalyzer:
    """Analyzes code structure using Python AST parsing."""

    def analyze_python_code(self, code: str) -> Dict:
        """Parse and analyze Python code structure."""
        try:
            tree = ast.parse(code)
            return {
                "status": "success",
                "imports": self.extract_imports(tree),
                "functions": self.extract_functions(tree),
                "classes": self.extract_classes(tree),
                "complexity": self.calculate_complexity(tree),
            }
        except SyntaxError as e:
            return {
                "status": "error",
                "error": str(e),
                "line": e.lineno,
                "offset": e.offset,
            }

    def extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract all function definitions from AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "lineno": node.lineno,
                    "decorators": [
                        d.id if isinstance(d, ast.Name)
                        else (d.attr if isinstance(d, ast.Attribute) else "")
                        for d in node.decorator_list
                    ],
                    "is_async": False,
                })
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "lineno": node.lineno,
                    "decorators": [
                        d.id if isinstance(d, ast.Name)
                        else (d.attr if isinstance(d, ast.Attribute) else "")
                        for d in node.decorator_list
                    ],
                    "is_async": True,
                })
        return functions

    def extract_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract all class definitions from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(f"{ast.dump(base.value)}.{base.attr}")
                classes.append({
                    "name": node.name,
                    "bases": bases,
                    "lineno": node.lineno,
                    "decorators": [
                        d.id if isinstance(d, ast.Name)
                        else (d.attr if isinstance(d, ast.Attribute) else "")
                        for d in node.decorator_list
                    ],
                    "methods": [
                        n.name for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ],
                })
        return classes

    def calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of the code."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
