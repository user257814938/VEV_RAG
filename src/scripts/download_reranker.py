import os
from sentence_transformers import CrossEncoder
from huggingface_hub import snapshot_download

RERANK_MODEL_NAME = "mixedbread-ai/mxbai-rerank-base-v1"

def download_reranker():
    print(f"Downloading Reranker model: {RERANK_MODEL_NAME}...")
    try:
        # Option 1: Try loading with CrossEncoder which triggers download
        model = CrossEncoder(RERANK_MODEL_NAME)
        print("Successfully loaded (and downloaded) model via CrossEncoder.")
    except Exception as e:
        print(f"CrossEncoder download failed: {e}")
        print("Attempting direct download via huggingface_hub...")
        try:
            # Option 2: Fallback to direct snapshot download
            snapshot_download(repo_id=RERANK_MODEL_NAME)
            print("Successfully downloaded model via huggingface_hub.")
        except Exception as e2:
            print(f"Direct download also failed: {e2}")
            raise e2

if __name__ == "__main__":
    download_reranker()
