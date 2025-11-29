
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath("."))

from main import VEVAgent
from src.core.config import RAW_DIR
import shutil

def test_image_ingestion():
    # 1. Initialize Agent
    print("Initializing VEV Agent...")
    agent = VEVAgent()
    
    # 2. Define Image Path (using the one uploaded by user)
    image_source = r"C:\Users\Asus Vivobook\.gemini\antigravity\brain\ef3ee2a0-3a62-4efb-b741-d0b06e5863ae\uploaded_image_1764373128374.jpg"
    
    # Copy to RAW_DIR to simulate upload
    image_name = "test_ai_history.jpg"
    target_path = RAW_DIR / image_name
    
    print(f"Copying image to {target_path}...")
    shutil.copy(image_source, target_path)
    
    # 3. Ingest Image
    print(f"Ingesting {image_name} (OCR)...")
    try:
        agent.ingest_document(str(target_path))
        print("Ingestion complete!")
    except Exception as e:
        print(f"Ingestion failed: {e}")
        return

    # 4. Query
    query = "What text is written in the image? Describe the visual elements."
    print(f"\nQuery: {query}")
    
    response = agent.ask_query(query)
    
    print("\nAnswer:")
    print(response.answer)
    
    print("\n📄 Sources used:")
    for src in response.sources:
        print(f"- {src.chunk.metadata.title} (Page {src.chunk.metadata.page_number}): Score {src.score:.4f}")
        print(f"  Content preview: {src.chunk.text[:100]}...")

if __name__ == "__main__":
    test_image_ingestion()
