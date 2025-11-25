# Objectif — Charger : 
# 1. Textes simples (TXT, MD) -> Nativement (Rapide)
# 2. Docs complexes & Tableaux (PDF, DOCX, XLSX, CSV) -> Docling (Intelligent)

import logging
from pathlib import Path
from typing import Tuple
from docling.document_converter import DocumentConverter
from src.core.schemas import SourceMetadata

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation Docling
try:
    converter = DocumentConverter()
except Exception as e:
    logger.error(f"Failed to init Docling: {e}")
    converter = None

def load_document(file_path: str) -> Tuple[str, SourceMetadata]:
    path_obj = Path(file_path)

    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # ✨ CAS 1 : Texte pur (TXT, MD)
    # On utilise Python natif pour la vitesse. Pas de mise en page à analyser.
    if path_obj.suffix.lower() in [".txt", ".md"]:
        logger.info(f"Loading Text/Markdown file (native): {file_path}")
        
        try:
            with open(path_obj, "r", encoding="utf-8", errors="replace") as f:
                text_content = f.read()
            
            metadata = SourceMetadata(
                source_type=path_obj.suffix.lower().replace(".", ""),
                source_path=str(path_obj.absolute()),
                title=path_obj.stem
            )
            return text_content, metadata
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise e

    # 🏗️ CAS 2 : Documents structurés & Tableurs (PDF, DOCX, XLSX, CSV)
    # Docling va transformer les fichiers Excel et CSV en jolis tableaux Markdown.
    if converter is None:
        raise RuntimeError("Docling converter is not initialized.")

    logger.info(f"Processing structured document via Docling: {file_path}...")

    try:
        # Docling détecte automatiquement le format (Excel, CSV, PDF...)
        result = converter.convert(file_path)
        
        # Conversion en Markdown (les tableaux Excel deviendront : | A | B | ...)
        markdown_text = result.document.export_to_markdown()

        metadata = SourceMetadata(
            source_type=path_obj.suffix.lower().replace(".", ""),
            source_path=str(path_obj.absolute()),
            title=path_obj.stem
        )

        logger.info(f"Successfully converted {file_path}")
        return markdown_text, metadata

    except Exception as e:
        logger.error(f"Error converting {file_path}: {e}")
        raise e