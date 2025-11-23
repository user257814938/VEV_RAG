import sys
from pathlib import Path

# Add src to python path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.config import PROJECT_ROOT, LLM_DIR, LLM_MODEL_FILE

print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"LLM_DIR: {LLM_DIR}")
model_path = LLM_DIR / LLM_MODEL_FILE
print(f"Model Path: {model_path}")

if model_path.exists():
    print("SUCCESS: Model file found!")
else:
    print("ERROR: Model file NOT found!")
