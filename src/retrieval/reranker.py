# Objectif — Affiner les résultats de recherche en utilisant un modèle de scoring puissant (MXBai Rerank v2) pour filtrer les faux positifs

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from typing import List, Tuple                                                  # from : importer depuis le typage | typing : module types | List, Tuple : types génériques
from sentence_transformers import CrossEncoder                                  # from : importer depuis la librairie | sentence_transformers : framework de modèles sémantiques | CrossEncoder : classe de modèle pour le Reranking
from src.core.config import RERANK_TOP_K                                        # from : importer la constante | src.core.config : configuration projet | RERANK_TOP_K : nombre de résultats finaux à conserver
from src.core.schemas import SearchResult                                       # from : importer le schéma | src.core.schemas : notre objet résultat de recherche

# Étape 2 — Configurer le logging et le modèle
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger actuel
RERANK_MODEL_NAME = "mixedbread-ai/mxbai-rerank-base-v1"                             # RERANK_MODEL_NAME : nom du modèle Reranker (MXBai Base)

# Étape 3 — Définir la classe Reranker
class Reranker:                                                                 # class : définir une classe | Reranker : outil pour réévaluer les documents
    
    # Étape 3.1 — Constructeur (Chargement du modèle)
    def __init__(self):                                                         # def : constructeur | self : instance de la classe
        logger.info(f"Loading Reranker model: {RERANK_MODEL_NAME}")             # logger.info : afficher le modèle en cours de chargement
        try:                                                                    # try : tenter d'exécuter le bloc suivant
            # CrossEncoder charge un modèle pour évaluer la relation paire (query, document)
            self.model = CrossEncoder(RERANK_MODEL_NAME)                        # self.model : instance du modèle | CrossEncoder(...) : constructeur du Reranker
            logger.info("Reranker model loaded successfully.")                   # logger.info : confirmation de chargement réussi
        except Exception as e:                                                  # except : si une erreur survient (problème de téléchargement ou PyTorch)
            logger.error(f"Error loading Reranker model: {e}")                  # logger.error : afficher l'erreur
            self.model = None                                                   # self.model : mettre à None si échec

    # Étape 3.2 — Méthode de Reranking
    def rerank(self, query: str, results: List[SearchResult]) -> List[SearchResult]: # def : définir la méthode | rerank : fonction principale de réévaluation | results : liste des SearchResult trouvés | -> : retour | List[SearchResult] : liste affinée
        """
        Réévalue une liste de SearchResult par rapport à la requête en utilisant un modèle Reranker.
        """
        if not self.model or not results:                                       # if : si le modèle n'est pas chargé OU la liste est vide
            logger.warning("Reranker is inactive or no results to process.")     # logger.warning : on prévient
            return results[:RERANK_TOP_K]                                       # return : renvoyer les premiers résultats sans modification

        # 1. Préparer les paires (Requête, Document) pour le modèle
        pairs = [                                                               # pairs : liste des paires (requête, document)
            (query, result.chunk.text)                                          # (query, result.chunk.text) : format requis par le CrossEncoder
            for result in results                                               # for result in results : pour chaque document trouvé
        ]                                                                       # ] : fin de la liste

        # 2. Calculer les nouveaux scores de pertinence - Le modèle donne un score de 0 à 1 (ou plus, selon le modèle) indiquant la pertinence
        new_scores = self.model.predict(pairs, show_progress_bar=False)         # new_scores : scores de pertinence | self.model.predict(...) : appel au Reranker | show_progress_bar=False : désactiver la barre de chargement

        # 3. Mettre à jour les scores et coupler résultats/scores
        scored_results = []                                                     # scored_results : liste temporaire pour le tri
        for i, score in enumerate(new_scores):                                  # for : boucle sur les nouveaux scores
            result = results[i]                                                 # result : résultat original
            result.score = score.item()                                         # result.score : mise à jour du score | .item() : extraction de la valeur Python native
            scored_results.append(result)                                       # scored_results.append(...) : ajout à la liste

        # 4. Trier les résultats par le nouveau score (du plus pertinent au moins)
        scored_results.sort(key=lambda x: x.score, reverse=True)                # scored_results.sort(...) : tri de la liste | key=lambda x: x.score : clé de tri est le nouveau score | reverse=True : tri descendant

        # 5. Limiter et renvoyer le TOP-K final
        final_results = scored_results[:RERANK_TOP_K]                           # final_results : les RERANK_TOP_K premiers
        logger.info(f"Reranked and kept top {len(final_results)} results.")     # logger.info : confirmation du nombre final
        
        # On met à jour les rangs après le tri
        for i, result in enumerate(final_results):                              # for : boucle pour mettre à jour le rang
            result.rank = i + 1                                                 # result.rank : mise à jour du rang (1, 2, 3...)
            
        return final_results                                                    # return : renvoyer les résultats finaux affinés