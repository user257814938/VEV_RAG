# Objectif — Charger : 
# 1. Textes simples (TXT, MD) -> Nativement (Rapide)
# 2. Docs complexes & Tableaux (PDF, DOCX, XLSX, CSV) -> Docling (Intelligent)
# 3. Audio (MP3, WAV) -> Whisper (via Docling)

import logging
from pathlib import Path
from typing import Tuple
from src.core.schemas import SourceMetadata

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation Docling avec Support Audio & OCR
try:
    from docling.document_converter import DocumentConverter, AudioFormatOption, InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, AsrPipelineOptions
    from docling.datamodel import asr_model_specs
    from docling.pipeline.asr_pipeline import AsrPipeline

    # 1. Config OCR (pour Images & PDF scannés)
    pdf_options = PdfPipelineOptions()
    pdf_options.do_ocr = True
    pdf_options.do_table_structure = True

    # 2. Config Audio (Whisper Turbo)
    asr_options = AsrPipelineOptions()
    asr_options.asr_options = asr_model_specs.WHISPER_TURBO

    # 3. Création du Convertisseur Universel
    converter = DocumentConverter(
        format_options={
            # Audio
            InputFormat.AUDIO: AudioFormatOption(
                pipeline_cls=AsrPipeline,
                pipeline_options=asr_options,
            ),
            # Note: InputFormat.IMAGE est géré par défaut ou via PdfPipelineOptions si nécessaire.
            # On ne le configure pas explicitement ici pour éviter les erreurs de validation.
        }
    )
    logger.info("✅ Docling initialized with Audio (Whisper) & OCR support")

except Exception as e:
    logger.error(f"Failed to init Docling with Audio/OCR: {e}")
    # Fallback simple
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        logger.warning("⚠️ Docling initialized in fallback mode (No Audio/OCR)")
    except Exception as fallback_error:
        logger.error(f"Critical: Failed to init Docling even in fallback: {fallback_error}")
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
        error_msg = str(e)
        if "WinError 2" in error_msg or "No such file or directory: 'ffmpeg'" in error_msg:
            friendly_msg = "❌ FFmpeg is missing! It is required for Audio processing.\n👉 Please install it: `winget install Gyan.FFmpeg` or download from https://ffmpeg.org"
            logger.error(friendly_msg)
            raise RuntimeError(friendly_msg) from e
        
        logger.error(f"Error converting {file_path}: {e}")
        raise e