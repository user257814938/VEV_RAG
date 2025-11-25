# Objectif — Créer l'interface web de l'agent VEV Agent en utilisant Streamlit. Gérer l'upload de fichiers, le chat et l'affichage des sources.

# Étape 1 — Importer les dépendances de l'interface et du moteur
import streamlit as st                                                          # import : charger la librairie | streamlit : framework d'interface web Python | as st : alias conventionnel
import logging                                                                  # import : charger le module standard | logging : gestion des journaux
from pathlib import Path                                                        # from : importer le chemin | pathlib : gestion des chemins
from typing import Optional                                                     # from : importer le typage | typing : module types | Optional : type pour gérer l'absence
from time import time                                                           # from : importer depuis le module temps | time : fonction pour mesurer la durée d'exécution
import shutil                                                                   # import : pour la suppression de dossiers (clear cache)

# Importer les classes de la logique métier (Le Cœur du RAG est dans main.py)
from src.core.config import RAW_DIR                                             # from : importer la constante | src.core.config : configuration | RAW_DIR : chemin du dossier brut
from src.core.schemas import GeneratedAnswer                                    # from : importer le schéma | src.core.schemas : notre objet réponse structurée
from src.retrieval.cache import init_semantic_cache                             # from : importer le cache | src.retrieval.cache : fonction d'initialisation du cache
from main import VEVAgent                                                       # from : importer la classe de l'agent | main : fichier principal | VEVAgent : l'orchestrateur du RAG

# Étape 2 — Configuration de la page Streamlit
st.set_page_config(page_title="VEV Agent", layout="wide")                       # st.set_page_config : configurer la page | page_title : titre onglet | layout="wide" : utilise toute la largeur

# Étape 3 — Mise en cache et initialisation de l'Agent (Singleton) - Streamlit s'assure que cette fonction n'est exécutée qu'une seule fois au démarrage
@st.cache_resource(show_spinner=True)                                           # @st.cache_resource : met le résultat en cache (sert de Singleton) | show_spinner=True : affiche un chargement
def initialize_agent() -> Optional[VEVAgent]:                                   # def : définir la fonction | initialize_agent : nom | -> : retour | Optional[VEVAgent] : l'objet agent ou rien
    """Initialise tous les composants du RAG et les met en cache."""
    try:                                                                        # try : bloc de sécurité
        agent = VEVAgent()                                                      # agent : instance de l'agent (charge LLM, Embedder, LanceDB...)
        agent.cache = init_semantic_cache(embedder=agent.embedder)              # agent.cache : initialisation du cache GPTCache
        return agent                                                            # return : renvoyer l'agent prêt
    except RuntimeError:                                                        # except : si l'agent n'a pas pu démarrer (modèle LLM manquant)
        return None                                                             # return : renvoyer None

# Étape 4 — Fonction pour gérer l'upload de documents locaux
def handle_file_upload(agent: VEVAgent):                                        # def : définir la fonction | handle_file_upload : gestion de l'upload
    uploaded_file = st.sidebar.file_uploader(                                   # uploaded_file : objet fichier | st.sidebar.file_uploader : widget d'upload dans la barre latérale
        "Upload Document (TXT, MD, PDF, DOCX, XLSX, CSV)",                                     # "Upload..." : label mis à jour avec TXT
        type=["txt", "md", "pdf", "docx", "xlsx", "csv"],                                            # type : extensions acceptées (ajout de "txt")
        key="file_uploader"                                                     # key : identifiant unique
    )
    
    if uploaded_file is not None:                                               # if : si un fichier est sélectionné
        temp_path = RAW_DIR / uploaded_file.name                                # temp_path : chemin pour sauvegarder le fichier
        with open(temp_path, "wb") as f:                                        # with open(...) : ouvrir le fichier en écriture binaire
            f.write(uploaded_file.read())                                       # f.write(...) : écrire le contenu du fichier uploadé

        with st.spinner(f"Indexing {uploaded_file.name}..."):                   # with st.spinner : afficher un spinner de chargement
            try:                                                                # try : tenter l'ingestion
                agent.ingest_document(str(temp_path))                           # agent.ingest_document(...) : lancer le pipeline complet
                st.sidebar.success(f"Successfully indexed {uploaded_file.name}!") # st.sidebar.success : message de succès
            except Exception as e:                                              # except : si l'ingestion échoue
                st.sidebar.error(f"Error during ingestion: {e}")                # st.sidebar.error : message d'erreur

# Étape 5 — Fonction pour afficher les sources (Reranked Chunks)
def display_sources(response: GeneratedAnswer):                                 # def : définir la fonction | display_sources : afficher les sources
    if response.sources:                                                        # if : si la réponse contient des sources
        st.markdown("### Sources Utilisées")                                    # st.markdown : afficher un titre Markdown
        for src in response.sources:                                            # for : boucle sur chaque source
            score = src.score                                                   # score : score de pertinence
            page = src.chunk.metadata.page_number                               # page : numéro de page
            title = src.chunk.metadata.title                                    # title : titre du document
            
            # Affichage de chaque source
            st.code(                                                            # st.code : afficher le texte du chunk (pour la visibilité)
                src.chunk.text[:200] + "..." if len(src.chunk.text) > 200 else src.chunk.text, # src.chunk.text : contenu du morceau (tronqué à 200) | len(...) : longueur
                language="markdown"                                             # language="markdown" : pour un rendu léger
            )
            st.caption(f"**Score de pertinence (Rerank):** {score:.4f} | **Source:** {title} | **Page:** {page}") # st.caption : afficher les métadonnées

# Étape 6 — Logique principale de l'Interface
st.title("🤖 VEV Agent")                                                        # st.title : titre principal (Nouveau Nom)
st.subheader("High-Performance Local RAG Engine")                               # st.subheader : sous-titre

agent = initialize_agent()                                                      # agent : initialisation de l'agent (ne se fait qu'une fois)

# Affichage des messages d'état
if agent is None:                                                               # if : si l'agent n'a pas pu démarrer
    st.error("FATAL ERROR: LLM Qwen model not loaded. Check if the GGUF file is in `models/llm/` and named correctly.") # st.error : message d'erreur critique
    st.stop()                                                                   # st.stop() : arrêter l'exécution Streamlit

# --- Sidebar (Ingestion) ---
st.sidebar.header("📁 Ingestion & Indexation")                                  # st.sidebar.header : titre de la barre latérale
handle_file_upload(agent)                                                       # handle_file_upload : afficher l'upload de fichier

# Ingestion URL manuelle
with st.sidebar.expander("Indexer une URL"):                                    # with st.sidebar.expander : créer un bloc déroulant
    url_to_ingest = st.text_input("URL à scraper", key="url_input")             # url_to_ingest : champ pour l'URL
    if st.button("Indexer URL"):                                                # if : bouton d'indexation
        if url_to_ingest.startswith("http"):                                    # if : vérification du format (doit commencer par http)
            with st.spinner(f"Indexing {url_to_ingest}..."):                    # with st.spinner : spinner de chargement
                agent.ingest_document(url_to_ingest)                            # agent.ingest_document(...) : ingestion web
                st.success(f"URL successfully indexed: {url_to_ingest}")        # st.success : message de succès
        else:                                                                   # else : si le format n'est pas bon
            st.warning("Veuillez entrer une URL valide (commençant par http).") # st.warning : avertissement

st.sidebar.markdown(f"**Status:** LanceDB contains {agent.vector_store.table.count_rows()} chunks.") # st.sidebar.markdown : afficher le nombre de chunks

# --- Clear Cache Section ---
st.sidebar.markdown("---")
st.sidebar.header("🗑️ Gestion du Cache")

with st.sidebar.expander("Vider les Caches"):
    st.write("⚠️ **Attention** : Cette action est irréversible !")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Cache Réponses", help="Vider le cache sémantique (réponses RAG)", use_container_width=True):
            try:
                cache_path = Path("models/lancedb_cache")
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                    st.success("✅ Cache sémantique vidé !")
                    st.rerun()
                else:
                    st.info("ℹ️ Cache déjà vide")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
    
    with col2:
        if st.button("🗄️ Cache Documents", help="Vider la base vectorielle (tous les documents)", use_container_width=True):
            try:
                db_path = Path("data/lancedb")
                if db_path.exists():
                    shutil.rmtree(db_path)
                    st.success("✅ Base vectorielle vidée !")
                    st.rerun()
                else:
                    st.info("ℹ️ Base déjà vide")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
    
    if st.button("🚨 Tout Vider", help="Vider tous les caches (réponses + documents)", type="primary", use_container_width=True):
        try:
            cleared = []
            cache_path = Path("models/lancedb_cache")
            db_path = Path("data/lancedb")
            
            if cache_path.exists():
                shutil.rmtree(cache_path)
                cleared.append("Cache sémantique")
            
            if db_path.exists():
                shutil.rmtree(db_path)
                cleared.append("Base vectorielle")
            
            if cleared:
                st.success(f"✅ Nettoyé : {', '.join(cleared)}")
                st.rerun()
            else:
                st.info("ℹ️ Tous les caches sont déjà vides")
        except Exception as e:
            st.error(f"❌ Erreur : {e}")

# --- Chat Principal (Recherche) ---
query = st.chat_input("Posez votre question à VEV Agent...")                    # query : champ de saisie du chat

if query:                                                                       # if : si l'utilisateur a entré une question
    st.chat_message("user").write(query)                                        # st.chat_message("user").write(...) : afficher la bulle utilisateur
    
    # Exécuter le pipeline RAG
    try:                                                                        # try : bloc de sécurité
        start_time_total = time()                                               # start_time_total : enregistrer le temps total
        
        # Le pipeline d'appel : Cache -> HyDE -> LanceDB -> Rerank -> Qwen
        response = agent.ask_query(query)                                       # response : appel à la fonction principale RAG
        
        end_time_total = time()                                                 # end_time_total : temps final
        
        # Affichage de la réponse LLM
        with st.chat_message("assistant"):                                      # with st.chat_message("assistant") : bulle de réponse
            st.info(response.answer)                                            # st.info : afficher la réponse générée par Qwen
            
            # Affichage des temps et statut
            st.caption(f"Process Time: {end_time_total - start_time_total:.2f}s | Status: Complete") # st.caption : afficher le temps de réponse
            
            # Affichage des sources
            display_sources(response)                                           # display_sources : afficher les chunks utilisés

    except Exception as e:                                                      # except : si une erreur critique se produit
        with st.chat_message("assistant"):
            st.error(f"Une erreur critique est survenue durant la recherche. Détails : {e}")