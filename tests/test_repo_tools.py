import tempfile
import sys
import os
from src.tools.repo_tools import clone_repository, extract_git_history, analyze_code_structure

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def test_forensic_tools():
    # Use the current project repository for testing
    cwd = os.getcwd()
    print(f"Testing forensic tools in: {cwd}")
    
    # 1. Test AST Analysis on current project
    print("\n--- Testing AST Analysis ---")
    structure = analyze_code_structure(cwd)
    print(f"Found Models: {structure['models']}")
    print(f"Found TypedDicts: {structure['typed_dicts']}")
    print(f"Found StateGraphs: {structure['stategraphs']}")
    print(f"Annotated Reducers: {structure['annotated_reducers']}")

    # 2. Test Sandboxed Clone 
    print("\n--- Testing Sandboxed Clone ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = "https://github.com/martha-ketsela-mengistu/automation-auditor"
        print(f"Cloning {repo_url} to {tmpdir}")
        if clone_repository(repo_url, tmpdir):
            print("Clone successful!")
            history = extract_git_history(tmpdir)
            print(f"Git History (first 5 lines): {history[:5]}")
        else:
            print("Clone failed.")

if __name__ == "__main__":
    test_forensic_tools()
