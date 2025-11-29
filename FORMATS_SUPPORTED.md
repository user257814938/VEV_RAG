# 📊 Analyse Complète des Formats Supportés - VEV RAG

Ce document recense **tous** les formats de fichiers et leur statut de prise en charge dans l'application VEV RAG actuelle.

---

## ✅ Formats Supportés (Testés & Activés)

### 📄 Documents Office & Texte
| Format | Extension | Moteur | Statut |
| :--- | :--- | :--- | :--- |
| **PDF** | `.pdf` | Docling (v2) | ✅ Supporté (avec OCR & Tableaux) |
| **Microsoft Word** | `.docx` | Docling (v2) | ✅ Supporté |
| **Microsoft Excel** | `.xlsx` | Docling (v2) | ✅ Supporté (Conversion en Markdown) |
| **Microsoft PowerPoint** | `.pptx` | Docling (v2) | ✅ Supporté |
| **Texte Brut** | `.txt` | **Python Natif** | ✅ Supporté (Ultra-rapide) |
| **Markdown** | `.md` | **Python Natif** | ✅ Supporté (Ultra-rapide) |
| **CSV** | `.csv` | Docling (v2) | ✅ Supporté |

### 🌐 Web & Documentation
| Format | Extension | Moteur | Statut |
| :--- | :--- | :--- | :--- |
| **HTML / XHTML** | `.html`, `.htm` | Docling (v2) | ✅ Supporté |
| **XML** | `.xml` | Docling (v2) | ✅ Supporté (Générique) |
| **AsciiDoc** | `.adoc`, `.asciidoc` | Docling (v2) | ✅ Supporté |
| **WebVTT** | `.vtt` | Docling (v2) | ✅ Supporté (Sous-titres) |

### 🖼️ Images (avec OCR)
| Format | Extension | Moteur | Statut |
| :--- | :--- | :--- | :--- |
| **PNG** | `.png` | Docling (OCR) | ✅ Supporté |
| **JPEG / JPG** | `.jpg`, `.jpeg` | Docling (OCR) | ✅ Supporté |
| **TIFF** | `.tiff`, `.tif` | Docling (OCR) | ✅ Supporté |
| **BMP** | `.bmp` | Docling (OCR) | ✅ Supporté |
| **WebP** | `.webp` | Docling (OCR) | ✅ Supporté |

### 🎵 Audio (Transcription IA)
| Format | Extension | Moteur | Statut |
| :--- | :--- | :--- | :--- |
| **MP3** | `.mp3` | Whisper Turbo | ✅ Supporté |
| **WAV** | `.wav` | Whisper Turbo | ✅ Supporté |

### 🔬 Formats Spécialisés
| Format | Extension | Moteur | Statut |
| :--- | :--- | :--- | :--- |
| **JATS XML** | `.xml` | Docling (v2) | ✅ Supporté (Articles scientifiques) |
| **USPTO XML** | `.xml` | Docling (v2) | ✅ Supporté (Brevets) |
| **Docling JSON** | `.json` | Docling (v2) | ✅ Supporté (Format natif) |

---

## ❌ Formats Non Supportés (Actuellement)

| Format | Extension | Raison |
| :--- | :--- | :--- |
| **Anciens Word** | `.doc` | Format binaire obsolète (nécessite conversion préalable) |
| **Anciens Excel** | `.xls` | Format binaire obsolète (nécessite conversion préalable) |
| **Anciens PPT** | `.ppt` | Format binaire obsolète (nécessite conversion préalable) |
| **Archives** | `.zip`, `.tar`, `.rar` | Nécessite décompression préalable |
| **Vidéo** | `.mp4`, `.avi`, `.mov` | Pas de pipeline vidéo (extraire l'audio en MP3 d'abord) |
| **Code Source** | `.py`, `.js`, `.java`... | Peut être lu comme `.txt` mais pas optimisé pour le RAG |
| **Ebooks** | `.epub`, `.mobi` | Non supporté nativement par Docling v2 |

---

## 🛠️ Configuration Technique
- **Moteur Principal** : `docling` (v2.63.0+)
- **Moteur Audio** : `whisper-turbo` (via `docling.pipeline.asr_pipeline`)
- **Moteur OCR** : Activé par défaut pour les images et PDF scannés.
- **Exception** : Les fichiers `.txt` et `.md` contournent Docling pour une performance maximale.
