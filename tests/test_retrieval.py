# Objectif — Tester si le pipeline de recherche (HyDE, LanceDB Search, Reranker) fonctionne et si la pertinence est maintenue.

# Étape 1 — Importer les dépendances et les outils du projet
import pytest                                                                   # import : charger le framework de test | pytest : outil d'exécution des tests
import os                                                                       # import : charger le module système | os : pour manipuler les chemins
from unittest.mock import MagicMock                                             # from : importer un outil de simulation | unittest.mock : module de simulation | MagicMock : classe pour simuler des objets
from src.core.config import RERANK_TOP_K                                        # from : importer la constante | src.core.config : configuration
from src.retrieval.query_expansion import QueryExpander                         # from : importer l'expander | src.retrieval.query_expansion : outil HyDE
from src.retrieval.reranker import Reranker                                     # from : importer le reranker | src.retrieval.reranker : outil MXBai
from src.core.schemas import SearchResult, Chunk, SourceMetadata                # from : importer les schémas | src.core.schemas : structures de données
from main import VEVAgent                                                       # from : importer l'agent | main : classe orchestratrice

# Étape 2 — Définir un Fixture (Données de test simulées) - Les fixtures sont des fonctions qui fournissent des données réutilisables aux tests
@pytest.fixture(scope="session")                                                # @pytest.fixture : décorateur pour définir une donnée réutilisable | scope="session" : la donnée est créée une seule fois
def mock_agent():                                                               # def : définir la fonction | mock_agent : nom de la donnée
    # Simuler le LLMEngine pour les tests (pour ne pas démarrer Qwen !)
    llm_mock = MagicMock()                                                      # llm_mock : objet simulé | MagicMock() : crée une fausse implémentation
    llm_mock.generate.return_value = "This is a hypothetical document about the meaning of life." # llm_mock.generate.return_value : la fausse réponse de Qwen pour HyDE

    # Simuler les résultats de recherche LanceDB (simuler des morceaux de texte)
    def mock_search(query, top_k):                                              # def : définir la fonction de recherche simulée
        chunks = [                                                              # chunks : liste des morceaux simulés
            Chunk(text=f"High score result {i}", metadata=SourceMetadata(source_type="test", source_path="doc.pdf"), chunk_index=i) # Chunk : création de l'objet Chunk
            for i in range(top_k)                                               # for : boucle pour créer 'top_k' morceaux
        ]                                                                       # ] : fin de la liste
        # Retourne des SearchResult avec des scores initiaux (le Reranker les changera)
        return [SearchResult(chunk=c, score=1 - (i/10), rank=i+1) for i, c in enumerate(chunks)] # return : liste de SearchResult avec des scores décroissants

    # Créer une fausse instance de l'agent
    agent = VEVAgent()                                                          # agent : instance de l'agent VEV
    agent.llm = llm_mock                                                        # agent.llm : remplacer le vrai LLM par la simulation
    agent.vector_store.search = mock_search                                     # agent.vector_store.search : remplacer la vraie recherche par la simulation
    
    # Simuler le Reranker (pour avoir un modèle chargé)
    agent.reranker.model = MagicMock()                                          # agent.reranker.model : simuler le modèle MXBai
    agent.reranker.model.predict.return_value = [0.95, 0.20, 0.85, 0.10, 0.75]  # agent.reranker.model.predict.return_value : les scores de pertinence du Reranker
    
    return agent                                                                # return : retourner l'agent simulé

# Étape 3 — Test de l'Expansion de Requête (HyDE)
def test_query_expansion_hyde_generates_two_queries(mock_agent):                 # def : définir la fonction de test | test_query_expansion... : nom explicite
    """Vérifie si HyDE retourne bien la requête originale + le document hypothétique."""
    query = "Quel est le but de ce projet ?"                                    # query : question de test
    expanded = mock_agent.query_expander.expand_query(query)                    # expanded : appel à la fonction HyDE
    
    # 1. Vérifier la quantité de requêtes
    assert len(expanded) == 2                                                   # assert : vérification que la liste contient 2 éléments (Originale + HyDE)
    
    # 2. Vérifier que l'original est là
    assert expanded[0] == query                                                 # assert : vérifier que le premier élément est la requête originale
    
    # 3. Vérifier que le document HyDE a été généré
    assert "hypothetical document" in expanded[1]                                # assert : vérifier que le deuxième élément est le texte simulé du LLM

# Étape 4 — Test du Reranking (Scores et Limite)
def test_reranker_sorts_and_limits_results(mock_agent):                         # def : définir la fonction de test | test_reranker_sorts... : nom
    """Vérifie si le reranker prend bien le TOP_K final avec les bons scores."""
    
    # 1. Préparer des résultats initiaux (plus que le RERANK_TOP_K)
    initial_results = mock_agent.vector_store.search("query", RERANK_TOP_K * 2) # initial_results : 10 résultats simulés
    
    # 2. Lancer le Rerank (les scores sont modifiés par le mock au début de l'étape 2)
    final_results = mock_agent.reranker.rerank("query", initial_results)         # final_results : appel au reranker
    
    # 3. Vérifier la limite
    assert len(final_results) == RERANK_TOP_K                                   # assert : vérifier que la liste finale est bien limitée à 5 (RERANK_TOP_K)
    
    # 4. Vérifier l'ordre des scores (le tri doit se baser sur [0.95, 0.85, 0.75, 0.20, 0.10]) - # Le score de 0.95 doit être en première position (rank 1)
    assert final_results[0].score == 0.95                                       # assert : vérifier que le meilleur score est en première position
    assert final_results[0].rank == 1                                           # assert : vérifier que le rang est 1
    
    # 5. Vérifier le plus mauvais score gardé (le score 0.10 a été filtré)
    assert final_results[-1].score == 0.20                                      # assert : vérifier que le dernier score est le cinquième plus haut

# Étape 5 — Test de l'Intégration du Pipeline (Demander une requête complète)
def test_full_rag_pipeline_returns_generated_answer(mock_agent):                 # def : définir la fonction de test | test_full_rag_pipeline... : nom
    """Vérifie si l'appel final renvoie l'objet GeneratedAnswer avec des sources."""
    
    # 1. Simuler la réponse finale de Qwen
    mock_agent.llm.generate.return_value = "The final answer, based on the sources." # mock_agent.llm.generate.return_value : ce que le LLM va écrire
    
    # 2. Lancer l'appel RAG
    response = mock_agent.ask_query("What is the meaning of life?")             # response : appel à la méthode principale
    
    # 3. Vérifier le type de retour
    assert isinstance(response, GeneratedAnswer)                                 # assert : vérifier que le type de l'objet est bien GeneratedAnswer
    
    # 4. Vérifier que la réponse n'est pas vide et que les sources sont présentes
    assert "final answer" in response.answer                                     # assert : vérifier que la réponse contient le texte simulé du LLM
    assert len(response.sources) == RERANK_TOP_K                                # assert : vérifier que 5 sources ont été utilisées