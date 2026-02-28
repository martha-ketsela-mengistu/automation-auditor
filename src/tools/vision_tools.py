import base64
import json
import os
import io
from typing import List, Dict, Any
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]:
    """
    Extracts images from a PDF file and saves them to the output directory.
    Returns a list of paths to the extracted images.
    """
    image_paths = []
    try:
        reader = PdfReader(pdf_path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        count = 0
        for page_index, page in enumerate(reader.pages):
            if "/Resources" in page and "/XObject" in page["/Resources"]:
                x_objects = page["/Resources"]["/XObject"]
                for obj_name in x_objects:
                    obj = x_objects[obj_name]
                    if obj["/Subtype"] == "/Image":
                        try:
                            data = obj.get_data()
                            img = Image.open(io.BytesIO(data))
                            img_filename = f"page_{page_index}_img_{count}.png"
                            img_path = output_path / img_filename
                            img.save(img_path)
                            img.close()
                            image_paths.append(str(img_path))
                            count += 1
                        except Exception as e:
                            print(f"Skipping image {obj_name} on page {page_index}: {e}")
                            
        return image_paths
    except Exception as e:
        print(f"Error extracting images from {pdf_path}: {e}")
        return []

def analyze_diagram(image_path: str) -> Dict[str, Any]:
    """
    Analyzes an architectural diagram using a multimodal LLM via Ollama.
    Returns structured analysis of the flow and LangGraph patterns.
    """
    try:
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        vision_llm = ChatOllama(
            model="gpt-oss:120b-cloud",
            base_url="https://ollama.com",
            format="json"
        )

        prompt = """
        Analyze this architectural diagram for an AI swarm system. 
        You must return a JSON object with the following keys:
        - "diagram_type": One of ['accurate LangGraph State Machine diagram', 'sequence diagram', 'generic flowchart boxes']
        - "has_parallel_split": boolean (Does it show multiple branches running at once?)
        - "is_linear_pipeline": boolean (Is it just a straight line from start to end with no branches?)
        - "matches_required_flow": boolean (Does it follow: START -> [Parallel Detectives] -> Aggregation -> [Parallel Judges] -> Synthesis -> END?)
        - "description": A brief explanation of the visual flow.
        - "score": integer 1-5 (5 = Perfect match to the parallel swarm architecture)

        If the diagram shows a simple linear pipeline, the description MUST include the phrase 'Misleading Architecture Visual'.
        """

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data}"},
                },
            ]
        )

        response = vision_llm.invoke([message])
        analysis = json.loads(response.content)
        return analysis

    except Exception as e:
        print(f"Error in vision analysis: {e}")
        # Robust fallback if vision fails
        return {
            "diagram_type": "generic flowchart boxes",
            "has_parallel_split": False,
            "is_linear_pipeline": True,
            "matches_required_flow": False,
            "description": f"Vision analysis failed: {str(e)}",
            "score": 1
        }
