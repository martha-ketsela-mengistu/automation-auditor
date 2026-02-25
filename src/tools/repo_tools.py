import ast
import os
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path


def clone_repository(repo_url: str, target_dir: str) -> bool:
    """
    Clones a GitHub repository into a target directory.
    Uses subprocess.run for safety and captures errors.
    """
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def extract_git_history(repo_path: str) -> List[str]:
    """
    Extracts the git commit history: git log --oneline --reverse.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--oneline", "--reverse","--pretty=format:%H|%at|%an|%s", "--date=iso"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting git history: {e.stderr}")
        return []


class CodeStructureVisitor(ast.NodeVisitor):
    """
    AST Visitor to identify Pydantic models, TypedDicts, and LangGraph components.
    """
    def __init__(self):
        self.found_models = []
        self.found_typed_dicts = []
        self.found_stategraphs = []
        self.annotated_reducers = []

    def visit_ClassDef(self, node):
        # Check for Pydantic BaseModel or TypedDict
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id == 'BaseModel':
                    self.found_models.append(node.name)
                elif base.id == 'TypedDict':
                    self.found_typed_dicts.append(node.name)
            elif isinstance(base, ast.Attribute):
                if base.attr == 'BaseModel' or base.attr == 'TypedDict':
                    self.found_models.append(node.name) if 'BaseModel' in base.attr else self.found_typed_dicts.append(node.name)
        
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Check for StateGraph instantiation
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'StateGraph':
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.found_stategraphs.append(target.id)
            elif isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'StateGraph':
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.found_stategraphs.append(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        # Check for Annotated with reducers
        if isinstance(node.annotation, ast.Subscript):
            if isinstance(node.annotation.value, ast.Name) and node.annotation.value.id == 'Annotated':
                self.annotated_reducers.append(ast.unparse(node))
        self.generic_visit(node)


def analyze_code_structure(repo_path: str) -> Dict[str, Any]:
    """
    Performs AST parsing on Python files within the repository.
    """
    stats = {
        "models": [],
        "typed_dicts": [],
        "stategraphs": [],
        "annotated_reducers": []
    }
    
    repo_root = Path(repo_path)
    for py_file in repo_root.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                visitor = CodeStructureVisitor()
                visitor.visit(tree)
                
                stats["models"].extend(visitor.found_models)
                stats["typed_dicts"].extend(visitor.found_typed_dicts)
                stats["stategraphs"].extend(visitor.found_stategraphs)
                stats["annotated_reducers"].extend(visitor.annotated_reducers)
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
            
    return stats
