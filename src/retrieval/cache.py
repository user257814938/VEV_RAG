# Objectif — Cache sémantique 100% LanceDB (sans FAISS)
#            Si une requête est similaire à une ancienne, on renvoie la réponse direct.

import logging
from typing import Optional
from datetime import datetime

import numpy as np
import lancedb

from src.core.config import MODELS_DIR
from src.indexing.embedder import FastEmbedder

logger = logging.getLogger(__name__)

CACHE_TABLE_NAME = "semantic_cache"


class LanceSemanticCache:
    """Cache sémantique basé sur LanceDB (100% local, zéro FAISS)."""
    
    def __init__(self, db: lancedb.DBConnection, table, embedder: FastEmbedder, threshold: float = 0.90):
        self.db = db                                                            # self.db : connexion à la base LanceDB
        self.table = table                                                      # self.table : table du cache
        self.embedder = embedder                                                # self.embedder : notre FastEmbedder pour encoder les requêtes
        self.threshold = threshold                                              # threshold : seuil cosine (>0.90 = quasi identique)

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcule la similarité cosine entre deux vecteurs."""
        a = a / (np.linalg.norm(a) + 1e-9)                                      # normalisation vecteur a
        b = b / (np.linalg.norm(b) + 1e-9)                                      # normalisation vecteur b
        return float(np.dot(a, b))                                              # produit scalaire = cosine

    def lookup(self, query: str) -> Optional[str]:
        """Retourne une réponse si une requête similaire existe."""
        try:
            q_vec = self.embedder.embed_query(query)                                # q_vec : encoder la requête

            # Recherche Top-1 dans LanceDB
            res = (
                self.table.search(q_vec)
                .limit(1)
                .to_list()
            )

            if not res:                                                             # if : si aucun résultat
                return None

            best = res[0]                                                           # best : meilleur résultat
            best_vec = np.array(best["embedding"], dtype=np.float32)                # best_vec : vecteur du meilleur résultat
            sim = self._cosine(q_vec, best_vec)                                     # sim : similarité cosine

            if sim >= self.threshold:                                               # if : si similarité suffisante
                logger.info(f"Cache hit! Similarity: {sim:.3f}")                    # logger.info : log du cache hit
                return best["answer"]                                               # return : réponse cachée

            logger.info(f"Cache miss (best sim: {sim:.3f})")                        # logger.info : cache miss
            return None
        except Exception as e:
            logger.error(f"⚠️ Cache lookup failed (corruption suspected): {e}")
            return None

    def store(self, query: str, answer: str):
        """Ajoute une entrée au cache."""
        try:
            q_vec = self.embedder.embed_query(query).tolist()                       # q_vec : encoder la requête et convertir en liste
            self.table.add([{                                                       # self.table.add : ajouter une entrée
                "query": query,                                                     # "query" : requête texte
                "answer": answer,                                                   # "answer" : réponse générée
                "embedding": q_vec,                                                 # "embedding" : vecteur de la requête
                "ts": datetime.utcnow().isoformat()                                 # "ts" : timestamp UTC
            }])
            logger.info("Answer stored in cache")                                   # logger.info : confirmation
        except Exception as e:
            logger.error(f"⚠️ Failed to store in cache: {e}")


def init_semantic_cache(embedder: FastEmbedder) -> Optional[LanceSemanticCache]:
    """
    Initialise le cache sémantique LanceDB (100% local, pas de FAISS).
    """
    try:
        cache_dir = MODELS_DIR / "lancedb_cache"                                # cache_dir : dossier du cache
        cache_dir.mkdir(parents=True, exist_ok=True)                            # mkdir : créer le dossier si nécessaire

        db = lancedb.connect(str(cache_dir))                                    # db : connexion à LanceDB

        # Schéma simple pour le cache
        if CACHE_TABLE_NAME in db.table_names():                                # if : si la table existe déjà
            table = db.open_table(CACHE_TABLE_NAME)                             # table : ouvrir la table existante
            logger.info(f"Opened existing cache table ({table.count_rows()} entries)") # logger.info : nombre d'entrées
        else:
            # Créer la table avec un schéma dummy
            table = db.create_table(
                CACHE_TABLE_NAME,
                data=[{
                    "query": "",                                                # query : requête vide (dummy)
                    "answer": "",                                               # answer : réponse vide (dummy)
                    "embedding": [0.0] * embedder.dimension,                    # embedding : vecteur zéro (dummy)
                    "ts": ""                                                    # ts : timestamp vide (dummy)
                }],
                mode="overwrite"
            )
            logger.info("Created new cache table")                              # logger.info : création table

        logger.info("✅ LanceDB semantic cache initialized (FAISS-free)")        # logger.info : succès
        return LanceSemanticCache(db, table, embedder)                          # return : instance du cache

    except Exception as e:                                                      # except : en cas d'erreur
        logger.warning(f"Failed to init LanceDB cache, running without cache: {e}") # logger.warning : avertissement
        return None                                                             # return : None si échec