# Objectif — Améliorer la requête utilisateur en imaginant une réponse (HyDE) pour améliorer la recherche vectorielle

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from typing import List                                                         # from : importer depuis le typage | typing : module types | List : type liste générique
from src.core.config import LLM_CONTEXT_WINDOW                                  # from : importer la constante | src.core.config : configuration projet | LLM_CONTEXT_WINDOW : taille de la fenêtre de contexte
from src.generation.llm_engine import LLMEngine                                 # from : importer le moteur LLM | src.generation.llm_engine : notre classe Llama.cpp (moteur IA)

# Étape 2 — Configurer le logging
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger actuel

# Étape 3 — Définir la classe de transformation
class QueryExpander:                                                            # class : définir une classe | QueryExpander : outil pour améliorer la requête
    
    # Étape 3.1 — Constructeur (initialisation)
    def __init__(self, llm_engine: LLMEngine):                                  # def : constructeur | self : instance | llm_engine : objet moteur LLM (Qwen)
        self.llm = llm_engine                                                   # self.llm : stocker l'instance du moteur IA

    # Étape 3.2 — Méthode principale (utilise HyDE uniquement)
    def expand_query(self, query: str) -> List[str]:                            # def : méthode principale | expand_query : fonction pour l'expansion | -> : retour | List[str] : renvoie la requête originale + le document HyDE
        """
        Génère un document hypothétique (HyDE) pour améliorer la recherche vectorielle.
        Retourne la requête originale plus le document HyDE généré.
        """
        expanded_queries = [query]                                              # expanded_queries : liste des requêtes (commence avec l'originale)

        try:                                                                    # try : bloc de sécurité
            # 1. Définir le prompt - HyDE demande au LLM d'imaginer une réponse détaillée
            hyde_prompt = (                                                     # hyde_prompt : chaîne de prompt
                f"Rédige un document hypothétique, long et détaillé, qui répondrait le mieux à la question : {query}\n\n" # f"..." : instruction pour générer du texte long
                f"Réponds en utilisant un style factuel et ne t'excuse pas de ne pas connaître la réponse, invente-la de manière plausible." # Instruction sur le style (inventer une réponse plausible)
            )

            # 2. Générer le document hypothétique - La recherche vectorielle sera effectuée sur cet *hypothétique* document, pas sur la question courte
            hypothetical_document = self.llm.generate(                          # hypothetical_document : variable pour la réponse du LLM
                prompt=hyde_prompt,                                             # prompt : utiliser l'instruction HyDE
                max_tokens=LLM_CONTEXT_WINDOW,                                  # max_tokens : générer jusqu'à la taille de la fenêtre de contexte
                temperature=0.9                                                 # temperature : 0.9 pour encourager la créativité (nécessaire pour HyDE)
            )
            expanded_queries.append(hypothetical_document)                      # expanded_queries.append(...) : ajout du document hypothétique comme requête de recherche
            logger.info("Generated HyDE document for search.")                  # logger.info : confirmation de l'action

        except Exception as e:                                                  # except : si le LLM échoue
            logger.warning(f"Query expansion (HyDE) failed with LLM: {e}")      # logger.warning : on prévient mais on ne stoppe pas

        # HyDE génère déjà un contenu unique, donc pas besoin de nettoyer les doublons.
        return expanded_queries                                                 # return : renvoyer la requête originale + le document HyDE