# Objectif — Implémenter un générateur d'embeddings (vecteurs) ultra-rapide et léger basé sur ONNX Runtime (FastEmbed)

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from typing import List, Sequence                                               # from : importer depuis le typage | typing : module types | List, Sequence : types génériques
import numpy as np                                                              # import : charger le module de calcul | numpy : manipulation des tableaux
from fastembed import TextEmbedding                                             # from : importer depuis la librairie | fastembed : générateur d'embeddings rapide | TextEmbedding : classe principale d'encodage
from src.core.config import EMBEDDING_MODEL_NAME, EMBEDDING_DIM                 # from : importer les constantes | src.core.config : notre fichier de configuration | EMBEDDING_MODEL_NAME, EMBEDDING_DIM : nom et dimension du modèle

# Étape 2 — Configurer le logging
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger du fichier actuel

# Étape 3 — Définir la classe d'Embedding
class FastEmbedder:                                                             # class : définir une classe | FastEmbedder : notre outil d'embedding optimisé
    """Générateur d'embeddings BGE-M3 optimisé ONNX."""
    
    # Étape 3.1 — Constructeur (initialisation)
    def __init__(self):                                                         # def : constructeur | self : instance de la classe
        self.model_name = EMBEDDING_MODEL_NAME                                  # self.model_name : stocker le nom du modèle (BGE-M3)
        self.dimension = EMBEDDING_DIM                                          # self.dimension : stocker la dimension attendue (1024)
        self.model = self._load_model()                                         # self.model : stocker l'instance du modèle | = : assignation | self._load_model() : appel à la fonction de chargement (méthode privée)

    # Étape 3.2 — Méthode de chargement (privée)
    def _load_model(self) -> TextEmbedding:                                     # def : définir une méthode privée | _load_model : chargement du modèle | -> : retour type | TextEmbedding : objet fastembed
        """Charge le modèle d'embeddings une seule fois (Singleton)."""
        logger.info(f"Loading embedding model: {self.model_name}")              # logger.info : afficher le nom du modèle en cours de chargement | f"..." : chaîne formatée
        try:                                                                    # try : tenter d'exécuter le bloc suivant
            # FastEmbed gère le téléchargement automatique du modèle ONNX
            model = TextEmbedding(model_name=self.model_name, onnx_providers=["CPUExecutionProvider"]) # model : instance du modèle | TextEmbedding(...) : constructeur fastembed | model_name : nom du modèle | onnx_providers : forcer l'exécution sur CPU
            logger.info("Embedding model loaded successfully on CPU.")           # logger.info : confirmation de chargement réussi
            return model                                                        # return : renvoyer l'objet modèle
        except Exception as e:                                                  # except : si une erreur se produit | Exception : type d'erreur générique | as e : capturer l'erreur dans 'e'
            logger.error(f"Error loading embedding model: {e}")                 # logger.error : afficher l'erreur | f"..." : chaîne formatée
            raise RuntimeError("Embedder failed to initialize.")                # raise : lever une erreur critique | RuntimeError : type d'erreur

    # Étape 3.3 — Méthode pour encoder une requête
    def embed_query(self, query: str) -> np.ndarray:                            # def : définir la méthode | embed_query : pour encoder une seule requête (question) | -> : retour type | np.ndarray : tableau numpy
        """Encode une seule chaîne de requête."""
        # L'encodage d'une requête est un cas d'usage fréquent
        embeddings = self.model.embed([query])                                  # embeddings : résultat de l'encodage | self.model.embed(...) : méthode d'encodage fastembed | [query] : doit être une liste (fastembed travaille par lot)
        return embeddings[0].astype(np.float32)                                 # return : renvoyer le premier (et unique) vecteur | .astype(np.float32) : assurer le bon format (float32 est le standard pour les DB vectorielles)

    # Étape 3.4 — Méthode pour encoder les documents (chunks)
    def embed_documents(self, documents: Sequence[str]) -> List[np.ndarray]:    # def : définir la méthode | embed_documents : pour encoder une liste de documents (chunks) | -> : retour type | List[np.ndarray] : liste de tableaux numpy
        """Encode une liste de documents (chunks)."""
        logger.info(f"Embedding {len(documents)} documents...")                 # logger.info : afficher le nombre de documents à traiter | f"..." : chaîne formatée
        
        # FastEmbed gère le batching interne pour le CPU, le rendant efficace
        embeddings = self.model.embed(documents)                                # embeddings : liste de vecteurs
        
        # On doit convertir le résultat en liste de tableaux numpy float32
        return [emb.astype(np.float32) for emb in embeddings]                    # return : renvoyer la liste finale de vecteurs

# Étape 4 — Instancier l'embedder (Singleton) - Il est chargé ici pour qu'il soit prêt dès que le programme démarre (latence minimale)
try:                                                                            # try : essayer de charger le modèle
    embedder = FastEmbedder()                                                   # embedder : instance globale de l'embedder
except RuntimeError:                                                            # except : si l'initialisation a échoué (erreur critique)
    embedder = None                                                             # embedder : mettre à None pour éviter les plantages si le modèle est introuvable