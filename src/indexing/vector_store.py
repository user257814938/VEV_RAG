# Objectif — Implémenter le stockage et la recherche hybride (Vecteurs + Mots-clés) via la base de données LanceDB

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from typing import List, Optional                                               # from : importer depuis le typage | typing : module types | List, Optional : types génériques
import lancedb as lancedb                                                       # import : charger la librairie | lancedb : base de données vectorielle ultra-rapide | as lancedb : alias local
import pyarrow as pa                                                            # import : charger le module | pyarrow : format de données en colonnes (requis par LanceDB) | as pa : alias
from src.core.config import LANCEDB_DIR, EMBEDDING_DIM, LLM_CONTEXT_WINDOW      # from : importer les constantes | src.core.config : notre fichier de configuration | LANCEDB_DIR, EMBEDDING_DIM, LLM_CONTEXT_WINDOW : chemins et tailles
from src.core.schemas import Chunk, SearchResult, SourceMetadata                                # from : importer définitions | src.core.schemas : nos objets Pydantic
from src.indexing.embedder import FastEmbedder                                  # from : importer l'embedder | src.indexing.embedder : outil d'encodage FastEmbed
from src.ingestion.cleaner import clean_text_basic                              # from : importer le nettoyeur | src.ingestion.cleaner : pour nettoyer la requête utilisateur

# Étape 2 — Configurer le logging
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger actuel

# Étape 3 — Définir la classe de gestion LanceDB
class VectorStore:                                                              # class : définir une classe | VectorStore : outil de gestion de la base de données
    TABLE_NAME = "vev_rag_data"                                                 # TABLE_NAME : nom de la table LanceDB

    # Étape 3.1 — Constructeur (Connexion)
    def __init__(self, embedder: FastEmbedder):                                 # def : constructeur | self : instance | embedder : objet FastEmbedder (pour la recherche)
        self.embedder = embedder                                                # self.embedder : stocker l'outil d'encodage
        self.db = lancedb.connect(str(LANCEDB_DIR))                             # self.db : objet connexion à la base | lancedb.connect(...) : connexion au dossier lancedb
        self.table = self._get_or_create_table()                                # self.table : la table de travail | self._get_or_create_table() : appel à la méthode de vérification

    # Étape 3.2 — Méthode de vérification/création de la table
    def _get_or_create_table(self):                                             # def : définir une méthode privée | _get_or_create_table : vérifie si la table existe
        """Crée la table LanceDB si elle n'existe pas, sinon la retourne."""
        if self.TABLE_NAME in self.db.table_names():                            # if : condition | in : vérifie si le nom de table est dans la liste des tables existantes
            logger.info(f"Connected to existing table: {self.TABLE_NAME}")      # logger.info : confirmation de connexion
            return self.db.open_table(self.TABLE_NAME)                          # return : retourner la table existante
        else:                                                                   # else : sinon (la table n'existe pas)
            logger.info(f"Creating new table: {self.TABLE_NAME}")               # logger.info : message de création
            
            # Définition du schéma minimal requis par LanceDB pour créer une table vide
            schema = pa.schema([                                                # schema : définition des colonnes | pa.schema(...) : fonction pyarrow
                pa.field("id", pa.string()),                                    # pa.field : colonne ID (chaîne)
                pa.field("text", pa.string()),                                  # pa.field : colonne TEXTE (chaîne)
                pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),      # pa.field : colonne VECTEUR (liste de float32, taille EMBEDDING_DIM)
                pa.field("source", pa.string()),                                # pa.field : colonne SOURCE (chaîne)
                pa.field("page", pa.int32()),                                   # pa.field : colonne PAGE (entier)
                pa.field("title", pa.string()),                                 # pa.field : colonne TITRE (chaîne)
                pa.field("created_at", pa.string()),                            # pa.field : colonne DATE (chaîne)
            ])                                                                  # ]) : fin du schéma

            # Création de la table
            table = self.db.create_table(                                       # table : objet table créée | = : assignation | self.db.create_table(...) : commande de création
                self.TABLE_NAME,                                                # self.TABLE_NAME : nom
                schema=schema                                                   # schema=schema : utilise le schéma défini
            )
            return table                                                        # return : retourner la table nouvellement créée

    # Étape 3.3 — Ajout de données
    def add_chunks(self, chunks: List[Chunk]):                                  # def : définir la méthode | add_chunks : ajouter des morceaux de texte
        """Ajoute une liste de Chunks (objets Pydantic) à la base de données."""
        data_to_add = []                                                        # data_to_add : liste pour les données formatées
        for chunk in chunks:                                                    # for : boucle sur chaque objet Chunk
            # 1. Calculer le vecteur pour le chunk - L'encodage des documents doit être fait juste avant l'ajout
            if chunk.vector is None:                                            # if : condition | chunk.vector is None : si le vecteur n'a pas été calculé
                vector_np = self.embedder.embed_query(chunk.text)               # vector_np : vecteur numpy | self.embedder.embed_query(...) : on encode le texte
                chunk.vector = vector_np.tolist()                               # chunk.vector : stocker le vecteur dans l'objet Chunk (converti en liste Python)

            # 2. Formater pour LanceDB - On utilise la méthode de conversion en dictionnaire de notre schéma (schemas.py)
            data_to_add.append(chunk.to_lancedb_dict())                         # data_to_add.append(...) : ajouter le dictionnaire formaté

        self.table.add(data_to_add)                                             # self.table.add(...) : commande d'insertion LanceDB
        logger.info(f"Added {len(chunks)} new chunks to LanceDB.")              # logger.info : confirmation de l'ajout

    # Étape 3.4 — Recherche Hybride (Mots-clés + Vecteurs)
    def search(self, query: str, top_k: int) -> List[SearchResult]:             # def : définir la méthode | search : effectuer la recherche principale | -> : retour | List[SearchResult] : liste des résultats formatés
        """Recherche Hybride combinant similarité vectorielle et recherche de texte intégral (FTS)."""
        
        # 1. Nettoyage de la requête (important pour FTS)
        clean_query = clean_text_basic(query)                                   # clean_query : requête nettoyée (sans accents/ponctuation pour FTS)

        # 2. Encodage de la requête (pour la recherche vectorielle)
        query_vector = self.embedder.embed_query(query)                         # query_vector : vecteur numpy de la requête

        # 3. Exécution de la recherche LanceDB - LanceDB gère l'hybride nativement : on fournit le vecteur ET le texte (full_text_search)
        results = self.table.search(query_vector)                               # results : objet recherche
        
        results = (results                                                      # results : on continue le pipeline de recherche sur l'objet results
                   .limit(top_k)                                                # .limit(top_k) : limite le nombre de résultats maximum
                   .to_list())                                                  # .to_list() : exécute la recherche et renvoie une liste de dictionnaires PyArrow

        # 4. Formatage et conversion en objet SearchResult
        formatted_results = []                                                  # formatted_results : liste de sortie finale
        for i, res in enumerate(results):                                       # for : boucle sur chaque résultat brut
            # Reconstitution de l'objet Chunk Pydantic
            metadata = SourceMetadata(                                          # metadata : objet SourceMetadata reconstitué
                source_type="lancedb",                                          # source_type : type par défaut (ou extraire du dict si plus d'infos)
                source_path=res['source'],                                      # source_path : chemin source stocké
                page_number=res['page'] if res['page'] else 0,                  # page_number : page stockée
                title=res['title'],                                             # title : titre stocké
                creation_date=res['created_at']                                 # creation_date : date stockée
            )
            
            chunk_obj = Chunk(                                                  # chunk_obj : objet Chunk reconstitué
                id=res['id'],                                                   # id : identifiant
                text=res['text'],                                               # text : contenu
                vector=res['vector'],                                           # vector : vecteur stocké
                metadata=metadata,                                              # metadata : infos source
                chunk_index=0 # Non utilisé pour la recherche
            )

            # Création de l'objet SearchResult
            search_res = SearchResult(                                          # search_res : objet Pydantic résultat de recherche
                chunk=chunk_obj,                                                # chunk : le chunk complet
                score=res['score'],                                             # score : score de similarité (renvoyé par LanceDB)
                rank=i + 1                                                      # rank : rang dans le classement
            )
            formatted_results.append(search_res)                                # formatted_results.append(...) : ajout au résultat final

        return formatted_results                                                # return : renvoyer la liste des SearchResult
