# Objectif — Ce script gère l'orchestration du pipeline (Ingestion, Recherche, Génération) et définit la classe Agent.

# Étape 1 — Importer les dépendances du système et du pipeline
import logging                                                                  # import : charger le module standard | logging : gestion des journaux d'événements
from pathlib import Path                                                        # from : importer depuis un package | pathlib : gestion moderne des chemins | Path : classe objet chemin
from time import time                                                           # from : importer depuis le module temps | time : fonction pour mesurer la durée d'exécution
from typing import List                                                         # from : importer depuis le typage | typing : module types | List : type liste générique

# Importer toutes les classes et Singletons du projet
from src.core.config import RAW_DIR, RERANK_TOP_K                               # from : importer les constantes | src.core.config : configuration | RAW_DIR, RERANK_TOP_K : chemin du dossier brut et taille finale
from src.core.schemas import Chunk, GeneratedAnswer, SearchResult               # from : importer les schémas | src.core.schemas : nos structures de données
from src.generation.llm_engine import llm_engine                                # from : importer le moteur LLM | src.generation.llm_engine : notre instance globale de Qwen (doit être chargée)
from src.indexing.embedder import embedder                                      # from : importer l'embedder | src.indexing.embedder : notre instance FastEmbedder
from src.indexing.chunker import SemanticChunker                                # from : importer le chunker | src.indexing.chunker : outil de découpage intelligent
from src.indexing.vector_store import VectorStore                               # from : importer la DB | src.indexing.vector_store : notre classe LanceDB
from src.ingestion.loader_doc import load_document                              # from : importer l'ingestion | src.ingestion.loader_doc : fonction pour PDF/DOCX
from src.ingestion.loader_web import load_url                                   # from : importer l'ingestion | src.ingestion.loader_web : fonction pour URL
from src.retrieval.cache import init_semantic_cache                             # from : importer le cache | src.retrieval.cache : fonction d'initialisation du cache
from src.retrieval.query_expansion import QueryExpander                         # from : importer l'expander | src.retrieval.query_expansion : outil HyDE
from src.retrieval.reranker import Reranker                                     # from : importer le reranker | src.retrieval.reranker : outil MXBai

# Étape 2 — Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # logging.basicConfig(...) : configuration de base | level : niveau d'affichage | format : format du message
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur

# Étape 3 — Définir la classe de l'agent VEV RAG (Le Cerveau)
class VEVAgent:                                                                 # class : définir une classe | VEVAgent : l'objet principal qui orchestre le RAG

    # Étape 3.1 — Constructeur (Initialisation de tous les outils)
    def __init__(self):                                                         # def : constructeur | self : instance
        if llm_engine is None or embedder is None:                              # if : condition de vérification critique | llm_engine : moteur Qwen | or : ou | embedder : FastEmbedder
            logger.critical("Initialization failed: LLM or Embedder is missing. Check logs for details.") # logger.critical : message d'erreur fatal
            raise RuntimeError("Cannot start VEV Agent without core models.")   # raise : lever une erreur pour stopper l'exécution

        logger.info("Initializing RAG components...")                           # logger.info : début de l'initialisation
        self.embedder = embedder                                                # self.embedder : stocker l'embedder FastEmbedder
        self.llm = llm_engine                                                   # self.llm : stocker le moteur Qwen
        self.vector_store = VectorStore(embedder=self.embedder)                 # self.vector_store : stocker LanceDB (initialisé avec l'embedder)
        self.chunker = SemanticChunker(embedder=self.embedder)                  # self.chunker : stocker le SemanticChunker
        self.query_expander = QueryExpander(llm_engine=self.llm)                # self.query_expander : stocker l'outil HyDE
        self.reranker = Reranker()                                              # self.reranker : stocker le Reranker MXBai
        self.cache = None                                                       # self.cache : initialisé à None ici, puis chargé par app.py
        logger.info("VEV Agent core initialized.")                              # logger.info : message de succès

    # Étape 3.2 — Méthode du Pipeline d'Ingestion
    def ingest_document(self, path_or_url: str):                                # def : définir la méthode | ingest_document : charge et indexe un document
        """Pipeline complet : Charger -> Nettoyer -> Chunker -> Indexer."""
        start_time = time()                                                     # start_time : enregistrer le temps de début

        # 1. Chargement de la source
        if path_or_url.startswith("http"):                                      # if : si le chemin commence par "http" (c'est une URL)
            text, metadata = load_url(path_or_url)                              # text, metadata : appel à la fonction de scraping web
        else:                                                                   # else : sinon (c'est un chemin local)
            text, metadata = load_document(path_or_url)                         # text, metadata : appel à la fonction de chargement doc/pdf

        # 2. Chunking Sémantique
        chunks: List[Chunk] = self.chunker.chunk_document(text, metadata)       # chunks : liste des morceaux | self.chunker.chunk_document(...) : découpage intelligent
        
        if not chunks:                                                          # if : si aucun chunk n'a été créé
            logger.error("No valid chunks created after processing.")           # logger.error : message d'échec
            return                                                              # return : sortir de la fonction

        # 3. Indexation dans LanceDB (l'embedding est calculé ici)
        self.vector_store.add_chunks(chunks)                                    # self.vector_store.add_chunks(...) : ajout à la DB (calcule les embeddings FastEmbed ici)
        
        end_time = time()                                                       # end_time : enregistrer le temps de fin
        logger.info(f"Ingestion successful ({len(chunks)} chunks). Time: {end_time - start_time:.2f}s") # logger.info : succès avec la durée

    # Étape 3.3 — Méthode du Pipeline de Recherche (RAG)
    def ask_query(self, query: str) -> GeneratedAnswer:                         # def : définir la méthode | ask_query : exécute la recherche et la génération | -> : retour | GeneratedAnswer : objet réponse structurée
        """Pipeline complet : Cache -> HyDE -> Recherche -> Rerank -> Génération LLM."""
        start_time = time()                                                     # start_time : enregistrer le temps de début

        # 1. Vérification du Cache Sémantique (Accélérateur)
        if self.cache:                                                          # if : si le cache est actif (doit être mis à jour par app.py)
            cached_answer = self.cache.lookup(query)                            # cached_answer : essayer de trouver la réponse avec lookup() (LanceDB)
            if cached_answer:                                                   # if : si une réponse est trouvée
                logger.info("Cache hit! Returning cached answer.")              # logger.info : succès du cache
                return GeneratedAnswer(query=query, answer=cached_answer, sources=[], processing_time=time() - start_time) # return : renvoyer la réponse du cache immédiatement

        # 2. Transformation de Requête (HyDE)
        queries_to_search = self.query_expander.expand_query(query)             # queries_to_search : requête originale + document HyDE généré
        
        # 3. Recherche Hybride (LanceDB)
        all_results: List[SearchResult] = []                                    # all_results : liste pour stocker tous les résultats
        for q in queries_to_search:                                             # for : boucle sur chaque requête (originale + HyDE)
            results = self.vector_store.search(q, top_k=RERANK_TOP_K * 2)       # results : résultats de LanceDB | top_k * 2 : on prend 2x plus pour le Reranker
            all_results.extend(results)                                         # all_results.extend(...) : ajouter à la liste principale

        # 4. Reranking (Raffinement)
        unique_results = list({r.chunk.id: r for r in all_results}.values())    # unique_results : astuce pour dédupliquer les chunks par leur ID
        
        final_context = self.reranker.rerank(query, unique_results)             # final_context : les 5 meilleurs documents (RERANK_TOP_K)

        if not final_context:                                                   # if : si aucun document pertinent n'a été trouvé
            answer = "Je n'ai pas trouvé d'information pertinente dans les documents indexés pour répondre à cette question." # answer : message d'échec
            return GeneratedAnswer(query=query, answer=answer, sources=[], processing_time=time() - start_time) # return : réponse simple

        # 5. Préparation du Contexte LLM
        context_texts = [res.chunk.text for res in final_context]               # context_texts : extraire le texte des 5 meilleurs chunks
        context_str = "\n---\n".join(context_texts)                             # context_str : fusionner les textes avec un séparateur

        # 6. Génération Finale (RAG)
        rag_prompt = (                                                          # rag_prompt : le prompt final envoyé à Qwen
            "Tu es VEV Agent, un assistant expert en documentation. Utilise UNIQUEMENT le contexte fourni ci-dessous pour répondre à la question.\n" # Rôle et instruction stricte (Nouveau Nom Agent)
            "Contexte:\n"
            f"===\n{context_str}\n===\n"                                        # Contexte fusionné
            f"Question: {query}\n"                                              # Question de l'utilisateur
            "Réponse détaillée:"                                                # Instruction de début de réponse
        )

        final_answer = self.llm.generate(prompt=rag_prompt)                     # final_answer : appel au moteur Qwen
        
        # 7. Mise en Cache de la réponse
        if self.cache:                                                          # if : si le cache est actif
            self.cache.store(query, final_answer)                               # self.cache.store(...) : enregistrer la question/réponse (LanceDB)

        # 8. Renvoyer la réponse structurée
        end_time = time()                                                       # temps final
        return GeneratedAnswer(                                                 # return : objet réponse complet
            query=query,
            answer=final_answer,
            sources=final_context,
            processing_time=end_time - start_time
        )

# Étape 4 — Fonction run_cli() (Pour le débogage)
def run_cli():                                                                  # def : définir la fonction CLI | run_cli : boucle de ligne de commande
    # Ce code n'est plus le point d'entrée principal. Il est là uniquement pour permettre un test rapide sans Streamlit.
    logger.warning("Main script running in CLI mode for debug purposes.")       # logger.warning : avertissement à l'utilisateur
    try:                                                                        # try : tenter d'initialiser
        agent = VEVAgent()                                                      # agent : instance de l'agent
    except RuntimeError:                                                        # except : si l'initialisation échoue
        return                                                                  # return : arrêter la fonction

    while True:                                                                 # while True : boucle infinie
        user_input = input("\n[VEV]> ")                                         # user_input : demander l'entrée utilisateur
        if user_input.lower() in ['quit', 'exit']:                              # if : si l'utilisateur veut quitter
            break                                                               # break : sortir de la boucle

        if user_input.lower().startswith("ingest "):                            # if : si l'utilisateur veut indexer
            source = user_input.split(" ", 1)[1].strip()                        # source : extraire le chemin/URL après "ingest "
            if source:                                                          # if : si la source est non vide
                agent.ingest_document(source)                                   # agent.ingest_document(...) : lancer le pipeline d'ingestion
            continue                                                            # continue : revenir au début de la boucle

        if user_input.strip():                                                  # if : si c'est une question de recherche
            try:                                                                # try : tenter de répondre
                response = agent.ask_query(user_input)                          # response : appel au pipeline RAG
                print("\n🤖 Réponse VEV Agent:")                                # print : afficher le titre réponse
                print(response.answer)                                          # print : afficher la réponse générée
                print(f"\n[Temps: {response.processing_time:.2f}s | Sources utilisées ({len(response.sources)}):]") # print : afficher les métriques
                for src in response.sources:                                    # for : boucle sur les sources
                    print(f"  - (Score {src.score:.4f}) {src.chunk.metadata.title} (Page {src.chunk.metadata.page_number})") # print : afficher les détails de la source
            except Exception as e:                                              # except : si une erreur arrive pendant le chat
                logger.error(f"Error during query processing: {e}")             # logger.error : loguer l'erreur
                print("Une erreur est survenue lors du traitement de la requête.") # print : message utilisateur

# Étape 5 — Exécuter le CLI si le script est lancé directement
if __name__ == "__main__":                                                      # if : condition python standard (script principal)
    run_cli()                                                                   # run_cli() : lancer la boucle de ligne de commande