# 🗺️ Stack Architecture RAG : La Stack "VEV RAG" (Full Local)

Ce document détaille l'architecture complète de votre pipeline RAG. Conçue pour une autonomie totale (**Full Python / CPU**), cette stack privilégie la performance, la robustesse et l'état de l'art technologique.

## 🏗️ Phase 1 : Initialisation & Ingestion de Données

*Cette phase inclut toutes les fondations nécessaires au lancement de l'application et au traitement initial du texte.*

### 1.1 Fondations & Core

- **Dépendances** : `numpy` (2006) + `python-dotenv` (2013) + `requests` (2011) + `huggingface-hub` (2021)
- **Rôle** : Fournir la base de calcul pour l'IA, gérer la configuration des variables d'environnement (`.env`), et effectuer les requêtes HTTP/gestion de modèles.
- **Fichiers** : `src/core/config.py`

### 1.2 Structure du Code (Squelette)

- **Dépendances** : `Dataclasses` (2018) + `Pydantic` (2017)
- **Rôle** : Définir la structure des objets internes et valider les données.
- **Fichier** : `src/core/schemas.py`

### 1.3 Ingestion de Documents (Universal Loader)

- **Dépendance** : `Docling` (IBM, 2024)
- **Rôle** : Conversion de PDF/DOCX en **Markdown structuré**.
- **Fichier** : `src/ingestion/loader_doc.py`

### 1.4 Extraction Web (Connecteur Internet)

- **Dépendances** : `Trafilatura` (2019) + `BeautifulSoup4` (2004)
- **Alternative Connectée** : `Jina Reader` (2024)
- **Rôle** : Extraction de contenu web propre (offline/online).
- **Fichier** : `src/ingestion/loader_web.py`

### 1.5 Normalisation (Hygiène des Données)

- **Dépendances** : `ftfy` (2012) + `Clean-text` (2019)
- **Rôle** : Réparation d'encodage et suppression du bruit.
- **Fichier** : `src/ingestion/cleaner.py`

### 1.6 Nettoyage Linguistique

- **Dépendances** : `Spacy` (2015) + `Regex`
- **Rôle** : Segmentation en phrases grammaticalement correctes.
- **Fichier** : `src/ingestion/cleaner.py`

## ⚙️ Phase 2 : Traitement, Indexation & Stockage

*Transformer le texte en connaissances mathématiques exploitables et le rendre cherchable.*

### 2.1 Chunking (Segmentation Intelligente)

- **Stratégie** : **Semantic Chunking** (2023)
- **Rôle** : Découpage par sens via embeddings.
- **Fichier** : `src/indexing/chunker.py`

### 2.2 Vectorisation (Embeddings)

- **Dépendances** : `FastEmbed` (ONNX) (2023) + `BGE-M3` (2024)
- **Rôle** : Génération de vecteurs rapides sur CPU.
- **Fichier** : `src/indexing/embedder.py`

### 2.3 Stockage Vectoriel & Hybride

- **Base de Données** : `LanceDB` (2023)
- **Rôle** : Base de données Serverless gérant l'hybride (FTS/BM25 + Vectoriel) et la persistance.
- **Fichier** : `src/indexing/vector_store.py`

## 🔍 Phase 3 : Pipeline de Recherche (Raffinement)

*Comprendre la question et affiner les résultats avant la génération.*

### 3.1 Cache Sémantique (Accélérateur)

- **Dépendance** : `GPTCache` (2023)
- **Rôle** : Éviter de recalculer les réponses similaires.
- **Fichier** : `src/retrieval/cache.py`

### 3.2 Transformation de Requête (Query Expansion)

- **Stratégie** : `HyDE` (2022)
- **Rôle** : Amélioration de la requête utilisateur pour la recherche.
- **Fichier** : `src/retrieval/query_expansion.py`

### 3.3 Reranking (Sélection Finale)

- **Modèle** : `MXBai Rerank v2` (2024)
- **Rôle** : Réorganiser les 10 résultats trouvés pour n'en garder que le Top-5 le plus pertinent.
- **Fichier** : `src/retrieval/reranker.py`

## 🧠 Phase 4 : Intelligence & Génération

*Produire la réponse finale.*

### 4.1 Optimisation Matérielle

- **Format** : **GGUF Quantization** (2023)
- **Rôle** : Compression du modèle pour le CPU.
- **Fichier** : `src/generation/llm_engine.py`

### 4.2 LLM (Le Cerveau)

- **Modèle** : `Qwen3-4B-Q4_K_M.gguf` (Instruct) (2025)
- **Rôle** : Le modèle de langage local qui lit les documents et rédige la réponse.
- **Fichier** : `src/generation/llm_engine.py`

## 🛡️ Phase 5 : Contrôle Qualité & Maintenance

*S'assurer que le système ne ment pas et est maintenable.*

### 5.1 Évaluation Continue

- **Framework** : `RAGAS` (2023) + `datasets`
- **Rôle** : Calcule automatiquement des scores de performance (Fidélité, Pertinence).
- **Fichier** : `src/evaluation/ragas_eval.py`

## 🖥️ Phase 6 : Orchestration & Interface Utilisateur

*Déploiement du produit final vers l'utilisateur et gestion du moteur central.*

### 6.1 Orchestration Principale (Le Moteur VEVRAGAgent)

- **Rôle** : Initier le pipeline complet, gérer les erreurs critiques au démarrage et contenir la logique principale de l'agent (`VEVRAGAgent`).
- **Fichier** : `main.py`

### 6.2 Interface Utilisateur

- **Dépendance** : `Streamlit` (2019)
- **Rôle** : Moteur de l'interface utilisateur, gérant le chat, l'upload et l'affichage des résultats.
- **Fichier** : `app.py`
