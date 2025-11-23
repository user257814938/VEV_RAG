# Objectif — Script pour évaluer la qualité du pipeline RAG (Contrôle Qualité). Utilise Ragas pour mesurer la fidélité et la pertinence.

# Étape 1 — Importer les dépendances et les outils du projet
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
import os                                                                       # import : charger le module système | os : pour vérifier les fichiers
from datasets import Dataset                                                    # from : importer depuis la librairie | datasets : gestion des données | Dataset : classe Dataset pour Ragas
from typing import List, Dict, Any                                              # from : importer depuis le typage | typing : module types
from src.core.config import LLM_CONTEXT_WINDOW                                  # from : importer la constante | src.core.config : pour les tailles de contexte
from src.core.schemas import SearchResult                                       # from : importer le schéma | src.core.schemas : pour la structure de réponse
from main import VEVAgent                                                       # from : importer l'agent | main : fichier principal | VEVAgent : la classe d'orchestration

# Importations Ragas (les moteurs d'évaluation)
from ragas.metrics import faithfulness, answer_relevance, context_recall        # from : importer les métriques | ragas.metrics : les outils de notation
from ragas import evaluate                                                      # from : importer l'outil d'évaluation | ragas : framework | evaluate : fonction principale

# Étape 2 — Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # logging.basicConfig(...) : configuration
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur

# Étape 3 — Définir une fonction pour exécuter l'évaluation
def run_evaluation(agent: VEVAgent, test_data: List[Dict[str, Any]]):           # def : définir la fonction | run_evaluation : nom | agent : instance VEV Agent | test_data : liste de questions/réponses attendues
    """Exécute la boucle RAG et évalue les résultats avec Ragas."""
    
    # 1. Préparation des listes de sortie pour Ragas
    data = {                                                                    # data : dictionnaire pour stocker les résultats
        "question": [],                                                         # "question" : liste des questions posées
        "answer": [],                                                           # "answer" : liste des réponses générées par VEV Agent
        "contexts": [],                                                         # "contexts" : liste des chunks utilisés comme contexte (pour la fidélité)
        "ground_truths": []                                                     # "ground_truths" : liste des réponses réelles (pour l'évaluation de rappel)
    }                                                                           # } : fin du dictionnaire

    # 2. Boucle de génération (Exécution du pipeline RAG sur le jeu de données)
    for sample in test_data:                                                    # for : boucle sur chaque question du jeu de données
        question = sample["question"]                                           # question : récupérer la question
        ground_truth = sample["ground_truth"]                                   # ground_truth : récupérer la réponse attendue
        
        logger.info(f"Processing question: {question}")                         # logger.info : suivi
        
        # Appel au pipeline de l'agent
        response = agent.ask_query(question)                                    # response : objet réponse de VEV Agent
        
        # Extraction du contexte (texte des chunks)
        contexts = [src.chunk.text for src in response.sources]                 # contexts : liste des textes des chunks
        
        # Remplissage des listes
        data["question"].append(question)                                       # data["question"].append : ajouter la question
        data["answer"].append(response.answer)                                  # data["answer"].append : ajouter la réponse de l'IA
        data["contexts"].append(contexts)                                       # data["contexts"].append : ajouter les sources trouvées
        data["ground_truths"].append(ground_truth)                              # data["ground_truths"].append : ajouter la réponse attendue

    # 3. Création du jeu de données Ragas
    ragas_dataset = Dataset.from_dict(data)                                     # ragas_dataset : créer l'objet Dataset (format requis)

    # 4. Exécution de l'évaluation Ragas - Les métriques suivantes utilisent le LLM (Qwen) pour s'auto-évaluer
    result = evaluate(                                                          # result : dictionnaire des scores finaux
        dataset=ragas_dataset,                                                  # dataset : le jeu de données à évaluer
        metrics=[faithfulness, answer_relevance, context_recall],               # metrics : les métriques demandées
        llm=agent.llm,                                                          # llm : utiliser le moteur Qwen pour les notations
        embeddings=agent.embedder                                               # embeddings : utiliser l'embedder FastEmbed pour certaines métriques
    )                                                                           # ) : fin de l'appel

    logger.info("Evaluation results:")                                          # logger.info : affichage des résultats
    print(result)                                                               # print : afficher le dictionnaire de résultats

    return result                                                               # return : retourner les résultats

# Étape 4 — Exemple de jeu de données de test (DOIT ÊTRE REMPLACÉ PAR VOS PROPRES DONNÉES)
# ATTENTION : L'agent doit d'abord indexer les documents qui contiennent les réponses !
EXAMPLE_TEST_SET = [                                                            # EXAMPLE_TEST_SET : liste des exemples de questions
    {
        "question": "Quelle est la principale méthode de stockage de données utilisée par VEV Agent ?", # question : question de test
        "ground_truth": ["LanceDB est utilisé pour le stockage vectoriel."]     # ground_truth : réponse attendue (doit être trouvée dans les documents indexés)
    },                                                                          # } : fin de l'exemple
    {
        "question": "Comment le Reranker améliore-t-il la précision ?",         # question : autre question de test
        "ground_truth": ["Le Reranker utilise MXBai V2 pour réévaluer le Top-10 afin de ne garder que le Top-5 le plus pertinent."] # ground_truth : réponse attendue
    }                                                                           # } : fin de l'exemple
]                                                                               # ] : fin de la liste

# Étape 5 — Fonction d'exécution principale de l'évaluation
if __name__ == "__main__":                                                      # if : condition d'exécution
    logger.info("Starting Ragas Evaluation Script...")                          # logger.info : message de démarrage
    
    # IMPORTANT : Assurez-vous d'avoir indexé les documents AVANT de lancer ce script !
    try:                                                                        # try : bloc de sécurité
        agent = VEVAgent()                                                      # agent : initialisation de l'agent
        
        if agent.vector_store.table.count_rows() == 0:                          # if : vérifier si la base est vide
            logger.error("Database is empty. Please run the ingestion pipeline first via app.py or main.py.") # logger.error : message d'erreur critique
        else:                                                                   # else : si la base n'est pas vide
            run_evaluation(agent, EXAMPLE_TEST_SET)                             # run_evaluation(...) : lancer l'évaluation
            
    except RuntimeError:                                                        # except : si les modèles n'ont pas pu charger
        logger.critical("Cannot run evaluation: Core models are missing.")      # logger.critical : erreur