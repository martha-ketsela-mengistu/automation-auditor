import os
from src.tools.doc_tools import read_markdown, chunk_text, search_context, extract_claimed_paths, verify_conception_depth

def test_doc_tools():
    report_path = "reports/interim_report.md"
    print(f"Testing doc tools with: {report_path}")
    
    if not os.path.exists(report_path):
        print(f"Error: {report_path} not found.")
        return

    # 1. Read Markdown
    content = read_markdown(report_path)
    print("\n--- Content Summary ---")
    print(f"Characters: {len(content)}")
    
    # 2. Extract Paths
    print("\n--- Extracted Paths ---")
    paths = extract_claimed_paths(content)
    for p in paths:
        print(f"- {p}")

    # 3. Verify Conception Depth
    print("\n--- Conception Depth Analysis ---")
    depth = verify_conception_depth(content)
    for term, data in depth.items():
        substance = "YES" if data['has_substance'] else "NO"
        print(f"Term: {term:25} | Count: {data['count']} | Substantial: {substance}")
        if data['count'] > 0:
            print(f"  Excerpt: {data['excerpts'][0][:100]}...")

    # 4. Keyword Search
    print("\n--- RAG-lite Search (Query: 'synthesis') ---")
    chunks = chunk_text(content, chunk_size=200, overlap=50)
    results = search_context("synthesis", chunks)
    for i, res in enumerate(results):
        print(f"Result {i+1}: {res.strip()[:100]}...")

if __name__ == "__main__":
    test_doc_tools()
