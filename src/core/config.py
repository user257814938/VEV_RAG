# Objectif — Centraliser tous les paramètres, chemins et constantes du projet VEV RAG

# Étape 1 — Importer les outils de gestion de système et de chemin
import os                                                                       # import : charger le module standard | os : interaction avec le système d'exploitation (variables d'env)
from pathlib import Path                                                        # from : importer depuis un package | pathlib : gestion moderne des chemins de fichiers | import : commande d'importation | Path : classe objet pour les chemins
from dotenv import load_dotenv                                                  # from : importer depuis une librairie externe | dotenv : gestion des fichiers .env | import : commande | load_dotenv : fonction pour charger les variables

# Étape 2 — Charger les variables d'environnement
load_dotenv()                                                                   # load_dotenv() : lire le fichier .env à la racine et charger les variables en mémoire

# Étape 3 — Définir les chemins absolus du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent                    # PROJECT_ROOT : constante racine du projet | = : assignation | Path(__file__) : chemin du fichier actuel | .resolve() : chemin absolu | .parent : dossier parent (x3 pour remonter à la racine), on remonte de 3 niveaux : src/core/ -> src/ -> vev_rag/ (racine)

DATA_DIR = PROJECT_ROOT / "data"                                                # DATA_DIR : chemin du dossier données | = : assignation | PROJECT_ROOT : racine | / : concaténation de chemin | "data" : nom du dossier
RAW_DIR = DATA_DIR / "raw"                                                      # RAW_DIR : chemin des documents bruts (PDF/Word)
PROCESSED_DIR = DATA_DIR / "processed"                                          # PROCESSED_DIR : chemin des fichiers Markdown nettoyés
LANCEDB_DIR = DATA_DIR / "lancedb"                                              # LANCEDB_DIR : chemin de stockage de la base vectorielle

MODELS_DIR = PROJECT_ROOT / "models"                                            # MODELS_DIR : chemin du dossier modèles
LLM_DIR = MODELS_DIR / "llm"                                                    # LLM_DIR : sous-dossier pour les fichiers GGUF

# Étape 4 — Définir les paramètres d'embeddings (Vectorisation) des modèles IA
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"                                  # EMBEDDING_MODEL_NAME : nom du modèle sur HuggingFace | "BAAI/bge-m3" : modèle état de l'art multilingue
EMBEDDING_DIM = 768                                                             # EMBEDDING_DIM : dimension des vecteurs de sortie (spécifique à BGE-M3)

# Paramètres du LLM (Génération)
LLM_MODEL_FILE = "Qwen3-4B-Q4_K_M.gguf"                                         # LLM_MODEL_FILE : nom du fichier modèle compressé | gguf : assurez-vous d'avoir téléchargé ce fichier GGUF dans models/llm/ ou laissez None pour téléchargement auto
LLM_CONTEXT_WINDOW = 4096                                                       # LLM_CONTEXT_WINDOW : nombre maximum de tokens en entrée (mémoire à court terme)
LLM_MAX_TOKENS = 1024                                                           # LLM_MAX_TOKENS : nombre maximum de tokens générés en réponse

# Étape 5 — Paramètres du Pipeline RAG
CHUNK_SIZE = 500                                                                # CHUNK_SIZE : taille cible des morceaux de texte (en tokens ou caractères selon la méthode)
CHUNK_OVERLAP = 50                                                              # CHUNK_OVERLAP : zone de recouvrement entre deux morceaux pour garder le contexte
RETRIEVAL_TOP_K = 10                                                            # RETRIEVAL_TOP_K : nombre de documents bruts à récupérer par recherche vectorielle
RERANK_TOP_K = 5                                                                # RERANK_TOP_K : nombre de documents finaux à garder après le tri intelligent (Reranking)

# Étape 6 — Créer les dossiers s'ils n'existent pas (Sécurité)
for path in [RAW_DIR, PROCESSED_DIR, LANCEDB_DIR, LLM_DIR]:                     # for : boucle sur une liste | path : variable temporaire | in : dans | [...] : liste des chemins critiques
    path.mkdir(parents=True, exist_ok=True)                                     # path.mkdir : créer le répertoire | parents=True : créer toute l'arborescence | exist_ok=True : ne pas planter si le dossier existe déjà