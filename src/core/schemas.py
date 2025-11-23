# Objectif — Définir les structures de données strictes (Schémas) qui circuleront dans tout le pipeline RAG

# Étape 1 — Importer les outils de typage et validation
from __future__ import annotations                                              # from : importer depuis le futur | __future__ : module de compatibilité | import : commande | annotations : permet d'utiliser le type de la classe dans sa propre définition
from typing import List, Optional, Dict, Any                                    # from : importer depuis le module de typage | typing : module standard | import : commande | List, Optional, Dict, Any : types génériques pour les annotations
from uuid import uuid4                                                          # from : importer depuis le module uuid | uuid : module identifiants uniques | import : commande | uuid4 : fonction pour générer un ID aléatoire
from datetime import datetime                                                   # from : importer depuis le module datetime | datetime : module gestion du temps | import : commande | datetime : classe date et heure
from pydantic import BaseModel, Field                                           # from : importer depuis Pydantic | pydantic : librairie de validation | import : commande | BaseModel : classe mère des modèles | Field : fonction pour configurer les champs

# Étape 2 — Définir les métadonnées d'un document source
class SourceMetadata(BaseModel):                                                # class : définir une classe | SourceMetadata : nom du schéma | (BaseModel) : hérite de Pydantic pour la validation
    """Informations sur l'origine du document (PDF, Web, etc.)"""
    source_type: str                                                            # source_type : type de la source ("pdf", "docx", "url") | : : séparateur type | str : chaîne de caractères
    source_path: str                                                            # source_path : chemin fichier ou URL | : : type | str : chaîne
    page_number: Optional[int] = None                                           # page_number : numéro de page (si PDF) | : : type | Optional[int] : entier ou rien | = : défaut | None : vide
    title: Optional[str] = None                                                 # title : titre du document | : : type | Optional[str] : chaîne ou rien | = : défaut | None : vide
    author: Optional[str] = None                                                # author : auteur du document | : : type | Optional[str] : chaîne ou rien | = : défaut | None : vide
    creation_date: str = Field(default_factory=lambda: datetime.now().isoformat()) # creation_date : date d'ajout | = : assignation | Field(...) : configuration avancée | default_factory : fonction appelée à la création | datetime.now().isoformat() : date actuelle en format texte ISO

# Étape 3 — Définir l'objet atomique : le Chunk (Morceau de texte)
class Chunk(BaseModel):                                                         # class : définir une classe | Chunk : nom de l'objet central du RAG | (BaseModel) : validation Pydantic
    """Un segment de texte avec son vecteur et ses métadonnées."""
    id: str = Field(default_factory=lambda: str(uuid4()))                       # id : identifiant unique du chunk | : : type | str : chaîne | = : assignation | Field(...) : champ auto-généré | uuid4() : génération d'ID aléatoire
    text: str                                                                   # text : contenu textuel du morceau | : : type | str : chaîne
    vector: Optional[List[float]] = None                                        # vector : représentation vectorielle (embedding) | : : type | Optional[List[float]] : liste de nombres décimaux ou rien | = : défaut | None : (sera rempli plus tard)
    metadata: SourceMetadata                                                    # metadata : infos sur la source | : : type | SourceMetadata : lien vers le schéma défini plus haut
    chunk_index: int                                                            # chunk_index : position du morceau dans le document (0, 1, 2...) | : : type | int : entier
    
    # Méthode pour convertir en format compatible LanceDB (qui n'aime pas les objets imbriqués complexes)
    def to_lancedb_dict(self) -> Dict[str, Any]:                                # def : définir une méthode | to_lancedb_dict : nom méthode | self : instance actuelle | -> : retour | Dict[str, Any] : dictionnaire
        return {                                                                # return : renvoyer un dictionnaire
            "id": self.id,                                                      # "id" : clé | self.id : valeur de l'objet
            "text": self.text,                                                  # "text" : clé | self.text : contenu texte
            "vector": self.vector,                                              # "vector" : clé | self.vector : liste de flottants
            "source": self.metadata.source_path,                                # "source" : clé aplatie | self.metadata.source_path : chemin source
            "page": self.metadata.page_number or 0,                             # "page" : clé aplatie | ... or 0 : numéro page ou 0 si vide
            "title": self.metadata.title or "Unknown",                          # "title" : clé aplatie | ... : titre ou par défaut
            "created_at": self.metadata.creation_date                           # "created_at" : clé date
        }                                                                       # } : fin dictionnaire

# Étape 4 — Définir un résultat de recherche
class SearchResult(BaseModel):                                                  # class : définir une classe | SearchResult : objet retourné après une recherche | (BaseModel) : validation
    chunk: Chunk                                                                # chunk : le morceau de texte trouvé | : : type | Chunk : objet complet
    score: float                                                                # score : score de similarité (0 à 1) | : : type | float : nombre décimal
    rank: int                                                                   # rank : rang dans les résultats (1er, 2ème...) | : : type | int : entier

# Étape 5 — Définir une réponse générée par le LLM
class GeneratedAnswer(BaseModel):                                               # class : définir une classe | GeneratedAnswer : réponse finale à l'utilisateur | (BaseModel) : validation
    query: str                                                                  # query : question posée | : : type | str : chaîne
    answer: str                                                                 # answer : réponse générée | : : type | str : chaîne
    sources: List[SearchResult]                                                 # sources : liste des documents utilisés pour répondre | : : type | List[SearchResult] : liste d'objets résultats
    processing_time: float                                                      # processing_time : temps de calcul en secondes | : : type | float : nombre décimal