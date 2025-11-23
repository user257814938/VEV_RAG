<!-- 🚩 GUIDE DE DÉMARRAGE RAPIDE : Moteur LLM VEV Agent

Ce document regroupe toutes les étapes critiques et les options de configuration nécessaires pour initialiser le modèle Qwen (Phase 4) et lancer l'application Streamlit.

1. Téléchargement et Placement du Modèle LLM (GGUF)

L'Agent VEV est configuré pour utiliser les modèles au format GGUF (optimisé pour CPU via llama-cpp-python). Le modèle par défaut est le Qwen 3 (4 Milliards de paramètres).

1.1 Fichier à Acquérir :

Fichier : Qwen3-4B-Q4_K_M.gguf (environ 2.5 Go)

Lien Direct de Référence : Qwen/Qwen3-4B-GGUF sur Hugging Face

1.2 Procédure de Placement :

Sur la page Hugging Face, accédez à l'onglet "Files and versions".

Trouvez et téléchargez le fichier Qwen3-4B-Q4_K_M.gguf.

Dossier Cible : Placez le fichier téléchargé exactement ici dans votre arborescence de projet : vev_rag/models/llm/
(Le code src/generation/llm_engine.py lira ce chemin.)

2. Configuration du Modèle (Modification de src/core/config.py)

Si vous téléchargez un modèle différent (ex: un modèle 7B ou un autre nom), vous devez le déclarer dans le fichier de configuration principal.

Ouvrir le Fichier : Ouvrez le fichier src/core/config.py.

Trouver la Clé : Localisez la variable LLM_MODEL_FILE dans la section "Paramètres du LLM (Génération)".

Mettre à Jour la Valeur : Remplacez le nom du modèle par défaut par le nom exact de votre nouveau fichier .gguf.

Exemple de Modification dans src/core/config.py :

# ANCIEN
LLM_MODEL_FILE = "qwen3-4b-instruct-q4_k_m.gguf"

# NOUVEAU (Si votre fichier s'appelle exactement 'Qwen-4B-v1.gguf')
LLM_MODEL_FILE = "Qwen-4B-v1.gguf"


3. Lancement Final de l'Application

Une fois le fichier .gguf placé et la configuration vérifiée, l'erreur FATALE au démarrage disparaîtra.

Ouvrez le Terminal à la racine du projet (vev_rag).

Lancez l'application Streamlit en utilisant la commande principale.

🚀 Commandes de Lancement :

Pour garantir le démarrage, utilisez l'une de ces deux commandes :

streamlit run app.py


OU (méthode la plus fiable si la commande ci-dessus ne fonctionne pas)

python -m streamlit run app.py


Si l'application ne démarre pas, vérifiez que votre environnement virtuel est activé et que toutes les dépendances de requirements.txt sont installées. -->