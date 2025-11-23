# Objectif — Découper le texte intelligemment (Semantic Chunking) en respectant le sens des phrases

# Étape 1 — Importer les dépendances
import numpy as np                                                              # import : charger module calcul | numpy : gestion des tableaux et distances mathématiques
from typing import List, Dict, Any                                              # from : importer typage | typing : types standards
from src.core.schemas import Chunk, SourceMetadata                              # from : importer définitions | src.core.schemas : nos objets Pydantic
from src.indexing.embedder import FastEmbedder                                  # from : importer notre embedder | src.indexing.embedder : (on va le créer juste après, ne vous inquiétez pas si VS Code souligne en rouge pour l'instant)
from src.ingestion.cleaner import split_into_sentences                          # from : importer notre nettoyeur | src.ingestion.cleaner : pour avoir des phrases propres

# Étape 2 — Définir la classe de Chunking Sémantique
class SemanticChunker:                                                          # class : définir classe | SemanticChunker : outil de découpage intelligent
    def __init__(self, embedder: FastEmbedder, threshold: float = 0.5):         # def : constructeur | self : instance | embedder : l'outil qui calcule les vecteurs | threshold : seuil de similarité (0.0 à 1.0) pour décider quand couper
        self.embedder = embedder                                                # self.embedder : stocker l'outil pour l'utiliser plus tard
        self.threshold = threshold                                              # self.threshold : stocker le seuil (plus il est haut, plus on fait de petits chunks)

    def chunk_document(self, text: str, metadata: SourceMetadata) -> List[Chunk]: # def : méthode principale | chunk_document : découpe un texte complet | -> : retour | List[Chunk] : liste d'objets Chunk prêts pour la DB
        """
        Transforme un texte brut en une liste de Chunks sémantiques.
        Algorithme :
        1. Découper en phrases.
        2. Calculer le vecteur de chaque phrase.
        3. Comparer la phrase N avec la phrase N+1.
        4. Si la distance est grande (sujet différent) -> On coupe et on crée un nouveau chunk.
        """
        # 1. Segmentation en phrases (via Spacy)
        sentences = split_into_sentences(text)                                  # sentences : liste de phrases propres
        if not sentences:                                                       # if : sécurité
            return []                                                           # return : rien

        # 2. Calcul des embeddings pour chaque phrase (Batch) - On transforme chaque phrase en vecteur pour comprendre son sens mathématique
        embeddings = self.embedder.embed_documents(sentences)                   # embeddings : liste de vecteurs (un par phrase)
        
        # 3. Analyse des distances (Cosine Similarity) - On calcule la similarité entre chaque phrase et la suivante
        distances = []                                                          # distances : liste pour stocker les écarts de sens
        for i in range(len(embeddings) - 1):                                    # for : boucle sur toutes les phrases sauf la dernière
            current_vec = embeddings[i]                                         # current_vec : vecteur phrase actuelle
            next_vec = embeddings[i + 1]                                        # next_vec : vecteur phrase suivante
            
            # Produit scalaire (Dot Product) car les vecteurs sont normalisés - Plus sim est proche de 1, plus c'est le même sujet
            sim = np.dot(current_vec, next_vec)                                 # sim : score de similarité
            distances.append(1 - sim)                                           # distances : on stocke la "distance" (1 - similarité). Plus c'est grand, plus le sujet change.

        # 4. Regroupement (Clustering)
        chunks: List[Chunk] = []                                                # chunks : liste finale
        current_chunk_sentences = [sentences[0]]                                # current_chunk_sentences : tampon pour construire le chunk en cours (commence avec la 1ère phrase)
        
        for i, dist in enumerate(distances):                                    # for : on parcourt les distances entre phrases
            if dist > self.threshold:                                           # if : SI la distance dépasse le seuil -> CHANGEMENT DE SUJET DÉTECTÉ
                # On clôture le chunk actuel
                chunk_text = " ".join(current_chunk_sentences)                  # chunk_text : on colle toutes les phrases du tampon
                
                # On crée l'objet Chunk
                new_chunk = Chunk(                                              # new_chunk : instance Pydantic
                    text=chunk_text,                                            # text : contenu
                    metadata=metadata,                                          # metadata : source originale
                    chunk_index=len(chunks)                                     # chunk_index : numéro (0, 1, 2...)
                )
                chunks.append(new_chunk)                                        # chunks : ajout à la liste finale
                
                # On vide le tampon et on commence le nouveau chunk avec la phrase suivante
                current_chunk_sentences = [sentences[i + 1]]                    # current_chunk_sentences : reset avec la phrase N+1
            else:                                                               # else : SINON (sujet similaire)
                # On continue d'accumuler les phrases dans le même chunk
                current_chunk_sentences.append(sentences[i + 1])                # current_chunk_sentences : ajout phrase N+1

        # 5. Gestion du dernier chunk (le reste du tampon)
        if current_chunk_sentences:                                             # if : s'il reste des phrases
            chunk_text = " ".join(current_chunk_sentences)                      # chunk_text : fusion
            new_chunk = Chunk(                                                  # new_chunk : création dernier chunk
                text=chunk_text,                                                # text : contenu
                metadata=metadata,                                              # metadata : source
                chunk_index=len(chunks)                                         # chunk_index : numéro final
            )
            chunks.append(new_chunk)                                            # chunks : ajout final

        return chunks                                                           # return : renvoyer tous les chunks créés