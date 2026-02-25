import re
import os
from typing import List, Dict, Any
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text content from a PDF file.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""


def read_markdown(md_path: str) -> str:
    """
    Reads and returns the content of a markdown file.
    """
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading Markdown {md_path}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Splits text into chunks for RAG-lite processing.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks


def search_context(query: str, chunks: List[str]) -> List[str]:
    """
    Simple keyword/relevance search across text chunks.
    Returns chunks containing keywords from the query.
    """
    keywords = set(re.findall(r'\w+', query.lower()))
    results = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        # Rank by intersection count
        intersection = keywords.intersection(set(re.findall(r'\w+', chunk_lower)))
        if intersection:
            results.append((len(intersection), chunk))
    
    # Sort by number of keyword matches
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:3]]  # Return top 3 chunks


def extract_claimed_paths(text: str) -> List[str]:
    """
    Extracts likely file paths mentioned in the text (e.g., src/nodes/judges.py).
    """
    # Look for patterns like path/to/file.ext or file.ext
    path_pattern = r'[a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]{2,4}'
    matches = re.findall(path_pattern, text)
    
    # Filter out common false positives and ensure minimum path-like structure
    valid_paths = []
    for match in matches:
        if "/" in match or match.endswith(('.py', '.md', '.json', '.txt', '.pdf', '.yaml', '.yml')):
            if not match.startswith(('http', 'www', '127.')):
                valid_paths.append(match)
    
    return list(set(valid_paths))


def verify_conception_depth(text: str) -> Dict[str, Any]:
    """
    Scans for theoretical terms and analyzes their context for depth.
    """
    terms = [
        "Dialectical Synthesis",
        "Fan-In",
        "Fan-Out",
        "Metacognition",
        "State Synchronization",
        "Constitutional AI",
        "AST Parsing"
    ]
    
    results = {}
    for term in terms:
        # Search for term and the 200 chars around it
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        matches = list(pattern.finditer(text))
        
        excerpts = []
        for match in matches:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            excerpts.append(text[start:end].strip())
        
        results[term] = {
            "count": len(matches),
            "excerpts": excerpts,
            "has_substance": len(matches) > 0 and any(len(ex.split()) > 15 for ex in excerpts)
        }
        
    return results
