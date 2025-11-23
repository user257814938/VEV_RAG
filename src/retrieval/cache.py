# Objectif — Implémenter le cache sémantique pour éviter de recalculer les réponses aux questions similaires (latence zéro pour les doublons)

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from typing import Optional                                                     # from : importer depuis le typage | typing : module types | Optional : type pour gérer l'absence de valeur
from gptcache import Cache                                                      # from : importer la librairie cache | gptcache : outil de cache sémantique | Cache : classe principale
from gptcache.manager import CacheBase, VectorBase, get_data_manager            # from : importer des gestionnaires | gptcache.manager : outils pour la base de données du cache
from gptcache.similarity_evaluation import SearchDistanceEvaluation             # from : importer la stratégie | gptcache.similarity_evaluation : utilise la méthode d'évaluation de distance
from gptcache.embedding import Onnx                                             # from : importer Onnx si besoin, mais on utilise Custom
from src.core.config import MODELS_DIR, EMBEDDING_MODEL_NAME, LLM_MAX_TOKENS    # from : importer les constantes | src.core.config : configuration projet | MODELS_DIR, ... : chemins et tailles
from src.indexing.embedder import FastEmbedder                                  # from : importer l'embedder | src.indexing.embedder : notre outil d'encodage FastEmbed

# Étape 2 — Configurer le logging
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger actuel

# Étape 3 — Définir le gestionnaire d'Embeddings pour GPTCache - Il doit savoir comment encoder les requêtes pour le cache
class CustomCacheEmbedder:                                                      # class : définir une classe | CustomCacheEmbedder : adapter FastEmbedder à l'interface de GPTCache
    def __init__(self, embedder: FastEmbedder):                                 # def : constructeur | self : instance | embedder : notre FastEmbedder
        self.embedder = embedder                                                # self.embedder : stocker l'outil
        self.dimension = self.embedder.dimension                                # self.dimension : dimension des vecteurs (1024)

    def to_embeddings(self, data, **kwargs):                                    # def : méthode obligatoire pour GPTCache | to_embeddings : encode la donnée
        """Convertit la requête texte en vecteur."""
        # data doit être le texte de la requête
        embedding = self.embedder.embed_query(data)                             # embedding : vecteur numpy | self.embedder.embed_query(...) : appel à notre méthode d'encodage rapide
        return embedding.tolist()                                               # return : renvoyer le vecteur converti en liste Python (format attendu par le cache)

# Étape 4 — Initialiser le Cache Sémantique
def init_semantic_cache(embedder: FastEmbedder) -> Optional[Cache]:             # def : définir la fonction d'initialisation | init_semantic_cache : nom | -> : retour | Optional[Cache] : objet Cache ou None
    """
    Initialise le cache sémantique avec notre FastEmbedder et un gestionnaire de données local.
    """
    try:                                                                        # try : bloc de sécurité
        # 1. Configuration des chemins
        cache_data_dir = MODELS_DIR / "gptcache_data"                           # cache_data_dir : dossier de stockage du cache (dans models/)
        cache_data_dir.mkdir(parents=True, exist_ok=True)                       # cache_data_dir.mkdir(...) : créer le dossier s'il n'existe pas

        # 2. Configuration de la base de données du cache - Utilisation de SQLite pour les métadonnées (CacheBase) et de FAISS (VecteurBase) pour la recherche de similarité
        cache_base = CacheBase(name='sqlite', sql_url=f"sqlite:///{str(cache_data_dir / 'sqlite.db')}") # cache_base : base de données SQL (où stocker la requête et la réponse)
        vector_base = VectorBase(name=str(cache_data_dir / "faiss.index"))      # vector_base : index vectoriel (où stocker les embeddings de la requête)

        # 3. Création du gestionnaire de données
        data_manager = get_data_manager(                                        # data_manager : objet orchestrateur
            cache_base=cache_base,                                              # cache_base : lien vers la base SQL
            vector_base=vector_base                                             # vector_base : lien vers l'index FAISS
        )

        # 4. Création du cache
        cache = Cache(                                                          # cache : l'objet cache final
            cache_obj=data_manager,                                             # cache_obj : utiliser notre gestionnaire
            similarity_strategy=SearchDistanceEvaluation(),                     # similarity_strategy : utiliser la similarité vectorielle
            embedding_func=CustomCacheEmbedder(embedder),                       # embedding_func : utiliser notre FastEmbedder adapté
            max_size=10000,                                                     # max_size : nombre max d'entrées dans le cache
        )
        logger.info("Semantic Cache initialized with FAISS.")                   # logger.info : confirmation

        return cache                                                            # return : l'objet cache

    except Exception as e:                                                      # except : en cas d'échec
        logger.warning(f"Failed to initialize GPTCache. Running without cache: {e}") # logger.warning : on prévient mais on ne bloque pas le programme
        return None                                                             # return : renvoyer None si échec

# Étape 5 — Instancier le cache (Singleton)
# Nous devons appeler cette fonction après avoir initialisé l'embedder dans le module principal
# cache_manager = init_semantic_cache(embedder)