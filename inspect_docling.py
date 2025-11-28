
import logging
from docling.document_converter import DocumentConverter

# Suppress logs
logging.basicConfig(level=logging.CRITICAL)

try:
    converter = DocumentConverter()
    print("Docling initialized successfully.")
    
    # Try to inspect supported formats if available in the object
    # This is exploratory as I don't have the docs, but often there's a registry or similar.
    if hasattr(converter, 'allowed_formats'):
        print(f"Allowed formats attribute found: {converter.allowed_formats}")
    
    # Check for format_to_backend_map or similar internal structures
    if hasattr(converter, 'format_to_backend_map'):
        print("Supported formats (from format_to_backend_map):")
        for fmt in converter.format_to_backend_map:
            print(f"- {fmt}")
            
    # Also check if we can import InputFormat from docling.datamodel.base_models
    try:
        from docling.datamodel.base_models import InputFormat
        print("\nAll InputFormat enum values:")
        for fmt in InputFormat:
            print(f"- {fmt.name} ({fmt.value})")
    except ImportError:
        print("Could not import InputFormat enum.")

except Exception as e:
    print(f"Error inspecting docling: {e}")
