# Objectif — Automatiser la création de l'arborescence complète du projet VEV RAG (Dossiers + Fichiers vides)

# Étape 1 — Importer les bibliothèques nécessaires
import os                                                                       # import : charger un module standard | os : module d'interaction avec le système d'exploitation
from pathlib import Path                                                        # from : importer depuis un package | pathlib : module de gestion des chemins orientée objet | import : commande d'importation | Path : classe principale pour manipuler les chemins

# Étape 2 — Définir la fonction de configuration
def create_project_structure():                                                 # def : définir une fonction | create_project_structure : nom explicite de la fonction
    base_dir = Path("vev_rag")                                                  # base_dir : variable contenant le chemin racine | = : opérateur d'assignation | Path : constructeur d'objet chemin | "vev_rag" : nom du dossier principal du projet

    # Étape 3 — Lister les dossiers à créer
    dirs = [                                                                    # dirs : variable liste des répertoires | = : assignation | [ : début de la liste
        "data/raw",                                                             # "data/raw" : chemin pour les fichiers bruts (PDF, DOCX)
        "data/processed",                                                       # "data/processed" : chemin pour les fichiers traités (Markdown)
        "data/lancedb",                                                         # "data/lancedb" : chemin pour la base de données vectorielle
        "models/llm",                                                           # "models/llm" : chemin pour stocker les modèles GGUF
        "models/embeddings",                                                    # "models/embeddings" : chemin pour le cache des modèles d'embedding
        "src/core",                                                             # "src/core" : chemin pour les configurations et schémas
        "src/ingestion",                                                        # "src/ingestion" : chemin pour les scripts de chargement de données
        "src/indexing",                                                         # "src/indexing" : chemin pour les scripts de vectorisation
        "src/retrieval",                                                        # "src/retrieval" : chemin pour la logique de recherche
        "src/generation",                                                       # "src/generation" : chemin pour la génération de texte
        "src/evaluation",                                                       # "src/evaluation" : chemin pour les scripts de tests qualité
        "tests",                                                                # "tests" : chemin pour les tests unitaires
    ]                                                                           # ] : fin de la liste

    # Étape 4 — Lister les fichiers vides à créer
    files = [                                                                   # files : variable liste des fichiers | = : assignation | [ : début de la liste
        "src/__init__.py",                                                      # "src/__init__.py" : fichier pour rendre le dossier importable comme package
        "src/core/config.py",                                                   # "src/core/config.py" : fichier vide pour les paramètres
        "src/core/schemas.py",                                                  # "src/core/schemas.py" : fichier vide pour les définitions Pydantic
        "src/ingestion/loader_doc.py",                                          # "src/ingestion/loader_doc.py" : fichier vide pour Docling
        "src/ingestion/loader_web.py",                                          # "src/ingestion/loader_web.py" : fichier vide pour Trafilatura
        "src/ingestion/cleaner.py",                                             # "src/ingestion/cleaner.py" : fichier vide pour le nettoyage
        "src/indexing/chunker.py",                                              # "src/indexing/chunker.py" : fichier vide pour le découpage
        "src/indexing/embedder.py",                                             # "src/indexing/embedder.py" : fichier vide pour FastEmbed
        "src/indexing/vector_store.py",                                         # "src/indexing/vector_store.py" : fichier vide pour LanceDB
        "src/retrieval/cache.py",                                               # "src/retrieval/cache.py" : fichier vide pour GPTCache
        "src/retrieval/query_expansion.py",                                     # "src/retrieval/query_expansion.py" : fichier vide pour HyDE
        "src/retrieval/reranker.py",                                            # "src/retrieval/reranker.py" : fichier vide pour MXBai
        "src/generation/llm_engine.py",                                         # "src/generation/llm_engine.py" : fichier vide pour Llama.cpp
        "src/generation/prompts.py",                                            # "src/generation/prompts.py" : fichier vide pour les templates de prompt
        "src/evaluation/ragas_eval.py",                                         # "src/evaluation/ragas_eval.py" : fichier vide pour Ragas
        "tests/test_ingestion.py",                                              # "tests/test_ingestion.py" : fichier vide pour tester l'ingestion
        "tests/test_retrieval.py",                                              # "tests/test_retrieval.py" : fichier vide pour tester la recherche
        ".env",                                                                 # ".env" : fichier vide pour les variables d'environnement
        ".gitignore",                                                           # ".gitignore" : fichier pour les exclusions Git
        "main.py",                                                              # "main.py" : fichier principal pour la CLI
        "app.py",                                                               # "app.py" : fichier principal pour Streamlit
        "requirements.txt",                                                     # "requirements.txt" : fichier pour les dépendances
        "README.md",                                                            # "README.md" : fichier pour la documentation
    ]                                                                           # ] : fin de la liste

    print(f"Creating project structure for: {base_dir}")                        # print : afficher un message console | f"..." : formatage de chaîne | base_dir : nom du projet

    # Étape 5 — Créer les dossiers sur le disque
    if not base_dir.exists():                                                   # if : condition | not : opérateur logique non | base_dir.exists() : méthode vérifiant l'existence
        base_dir.mkdir()                                                        # base_dir.mkdir() : créer le dossier racine
        print(f"Created base directory: {base_dir}")                            # print : confirmer la création

    for dir_path in dirs:                                                       # for : boucle pour chaque élément | dir_path : variable temporaire | in : dans | dirs : la liste définie plus haut
        full_path = base_dir / dir_path                                         # full_path : chemin complet | = : assignation | base_dir : racine | / : opérateur de concaténation de chemin | dir_path : sous-dossier
        full_path.mkdir(parents=True, exist_ok=True)                            # full_path.mkdir : créer le dossier | parents=True : créer les dossiers parents si besoin | exist_ok=True : ne pas planter si existe déjà
        print(f"Created directory: {full_path}")                                # print : confirmer la création du dossier

    # Étape 6 — Créer les fichiers vides
    for file_path in files:                                                     # for : boucle pour chaque élément | file_path : variable temporaire | in : dans | files : la liste définie plus haut
        full_path = base_dir / file_path                                        # full_path : chemin complet | = : assignation | base_dir : racine | / : opérateur de concaténation | file_path : nom du fichier
        if not full_path.exists():                                              # if : condition | not : opérateur non | full_path.exists() : méthode vérifiant l'existence
            full_path.touch()                                                   # full_path.touch() : créer le fichier vide (commande système touch)
            print(f"Created file: {full_path}")                                 # print : confirmer la création du fichier

    print("Done! Project structure is ready.")                                  # print : afficher le message de fin

# Étape 7 — Exécuter la fonction principale
if __name__ == "__main__":                                                      # if : condition spéciale python | __name__ : variable interne | == : égalité | "__main__" : exécuté directement
    create_project_structure()                                                  # create_project_structure() : appeler la fonction définie
