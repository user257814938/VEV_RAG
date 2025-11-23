# Objectif — Implémenter le moteur LLM local pour la génération de texte (réponse finale et HyDE) en utilisant llama-cpp-python (GGUF)

# Étape 1 — Importer les dépendances
import os
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from pathlib import Path                                                        # from : importer depuis un package | pathlib : gestion moderne des chemins | Path : classe objet chemin
from typing import Optional                                                     # from : importer depuis le typage | typing : module types | Optional : type pour gérer l'absence de valeur
from llama_cpp import Llama                                                     # from : importer le moteur LLM | llama_cpp : librairie d'inférence GGUF | Llama : classe principale du modèle
from src.core.config import LLM_DIR, LLM_MODEL_FILE, LLM_CONTEXT_WINDOW, LLM_MAX_TOKENS # from : importer les constantes | src.core.config : notre configuration | LLM_DIR, ... : chemins et tailles

# Étape 2 — Configurer le logging
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger actuel

# Étape 3 — Définir la classe du Moteur LLM
class LLMEngine:                                                                # class : définir une classe | LLMEngine : outil pour interagir avec le modèle
    
    # Étape 3.1 — Constructeur (Chargement du modèle)
    def __init__(self):                                                         # def : constructeur | self : instance de la classe
        model_path = LLM_DIR / LLM_MODEL_FILE                                   # model_path : chemin complet du fichier GGUF | LLM_DIR : dossier | / : concaténation | LLM_MODEL_FILE : nom du fichier
        
        if not model_path.exists():                                             # if : si le fichier GGUF n'est pas dans le dossier
            logger.error(f"LLM model file not found at: {model_path}")          # logger.error : message critique
            raise FileNotFoundError("GGUF model file not found. Please download Qwen 2.5 3B GGUF into models/llm/ directory.") # raise : lever erreur | FileNotFoundError : le fichier est manquant
        
        logger.info(f"Loading LLM from {model_path}...")                        # logger.info : afficher le modèle en cours de chargement
        try:                                                                    # try : tenter d'exécuter le bloc suivant
            # Llama.cpp est optimisé pour utiliser tous les cœurs CPU disponibles
            self.model = Llama(                                                 # self.model : instance du modèle chargé
                model_path=str(model_path),                                     # model_path : chemin du fichier GGUF
                n_ctx=LLM_CONTEXT_WINDOW,                                       # n_ctx : taille max de la fenêtre de contexte (mémoire)
                n_threads=os.cpu_count(),                                       # n_threads : utiliser tous les cœurs CPU disponibles
                verbose=False                                                   # verbose : désactiver les messages d'inférence bruyants
            )
            logger.info(f"LLM Qwen loaded successfully. Context size: {LLM_CONTEXT_WINDOW}") # logger.info : confirmation de chargement réussi
        except Exception as e:                                                  # except : si une erreur survient
            logger.error(f"Failed to load Llama-cpp model: {e}")                # logger.error : afficher l'erreur
            self.model = None                                                   # self.model : mettre à None si échec

    # Étape 3.2 — Méthode de génération
    def generate(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.6) -> str: # def : définir la méthode | generate : fonction principale de génération | max_tokens : limite de la réponse | temperature : créativité
        """Génère une réponse textuelle en utilisant le modèle chargé."""
        if not self.model:                                                      # if : si le modèle n'a pas pu être chargé
            logger.error("LLM engine is inactive.")                             # logger.error : prévenir l'utilisateur
            return "Error: LLM model not available."                            # return : renvoyer un message d'erreur

        max_tokens = max_tokens or LLM_MAX_TOKENS                               # max_tokens : utiliser la valeur passée OU la valeur par défaut du config.py
        
        # Le format ChatML est le format optimal pour Qwen (prompt système/utilisateur)
        messages = [                                                            # messages : liste formatée pour le modèle
            {"role": "user", "content": prompt}                                 # "role": "user" : le rôle de l'utilisateur | "content": prompt : le texte à traiter
        ]                                                                       # ] : fin de la liste messages

        try:                                                                    # try : tenter l'inférence
            response = self.model.create_chat_completion(                       # response : résultat de l'inférence
                messages=messages,                                              # messages=messages : la requête formatée
                max_tokens=max_tokens,                                          # max_tokens : limite de la réponse
                temperature=temperature,                                        # temperature : niveau de créativité (0.0=déterministe, 1.0=créatif)
                stream=False                                                    # stream=False : attendre la réponse complète (pas de streaming)
            )
            # Extrait le texte généré par le LLM
            generated_text = response['choices'][0]['message']['content']       # generated_text : extraction du contenu de la réponse
            return generated_text                                               # return : renvoyer le texte propre

        except Exception as e:                                                  # except : si l'inférence échoue (souvent OOM, Out Of Memory)
            logger.error(f"LLM Generation failed: {e}")                         # logger.error : afficher l'erreur
            return "Error: Generation failed due to internal LLM error (possibly out of context memory)." # return : renvoyer un message d'erreur explicite

# Étape 4 — Instancier le moteur (Singleton) - On le charge une fois au démarrage du programme
try:                                                                            # try : essayer de charger le modèle
    llm_engine = LLMEngine()                                                    # llm_engine : instance globale du moteur LLM
except FileNotFoundError:                                                       # except : si le fichier modèle n'est pas trouvé
    llm_engine = None                                                           # llm_engine : mettre à None

except Exception:                                                               # except : si une autre erreur survient pendant le chargement
    llm_engine = None                                                           # llm_engine : mettre à None