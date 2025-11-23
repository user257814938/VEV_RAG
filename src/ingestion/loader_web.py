# Objectif — Charger du contenu depuis une URL web de manière propre et robuste (Scraping)

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger module standard | logging : gestion des logs
import requests                                                                 # import : charger module HTTP | requests : pour télécharger les pages web
import trafilatura                                                              # import : charger module scraping | trafilatura : extracteur de contenu web intelligent (hors ligne)
from typing import Tuple                                                        # from : importer typage | typing : module types | Tuple : retour multiple
from src.core.schemas import SourceMetadata                                     # from : importer définitions | src.core.schemas : notre fichier de structure | SourceMetadata : objet infos

# Étape 2 — Configurer le logger
logger = logging.getLogger(__name__)                                            # logger : enregistreur | = : assignation | logging.getLogger : récupérer logger local

# Étape 3 — Définir la fonction de chargement web
def load_url(url: str) -> Tuple[str, SourceMetadata]:                           # def : fonction | load_url : nom | url : adresse web cible | -> : retour | Tuple[str, SourceMetadata] : texte + infos
    """
    Télécharge une page Web et extrait son contenu textuel principal (sans le bruit HTML).
    """
    logger.info(f"Fetching URL: {url}...")                                      # logger.info : loguer l'action

    try:                                                                        # try : bloc de sécurité
        # 1. Téléchargement de la page (HTML brut)
        downloaded = trafilatura.fetch_url(url)                                 # downloaded : contenu HTML brut | = : assignation | trafilatura.fetch_url(...) : téléchargeur intelligent (gère les headers, user-agent)

        if downloaded is None:                                                  # if : condition échec | is None : si le téléchargement a échoué
            raise ValueError(f"Failed to download URL: {url}")                  # raise : lever erreur

        # 2. Extraction du contenu (Texte propre) - Trafilatura analyse le DOM pour trouver le "vrai" article
        text_content = trafilatura.extract(                                     # text_content : texte final | = : assignation | trafilatura.extract(...) : extracteur
            downloaded,                                                         # downloaded : HTML source
            include_comments=False,                                             # include_comments : ne pas garder les commentaires utilisateurs
            include_tables=True,                                                # include_tables : garder les tableaux (important pour la donnée)
            no_fallback=False                                                   # no_fallback : essayer plusieurs méthodes si la première échoue
        )

        if not text_content:                                                    # if : condition échec | not text_content : si extraction vide
            raise ValueError(f"No content extracted from URL: {url}")           # raise : lever erreur

        # 3. Extraction des métadonnées (Titre, Auteur, Date) - Trafilatura extrait aussi ces infos automatiquement des balises <meta>
        meta_json = trafilatura.extract_metadata(downloaded)                    # meta_json : objet métadonnées brut (JSON-like)

        # 4. Construction de notre objet Metadata standardisé
        title = meta_json.title if meta_json and meta_json.title else url       # title : titre extrait OU url si vide
        author = meta_json.author if meta_json and meta_json.author else None   # author : auteur extrait OU None
        
        metadata = SourceMetadata(                                              # metadata : notre objet Pydantic
            source_type="url",                                                  # source_type : type web
            source_path=url,                                                    # source_path : l'URL d'origine
            title=title,                                                        # title : titre trouvé
            author=author                                                       # author : auteur trouvé
        )

        logger.info(f"Successfully extracted content from {url}")               # logger.info : succès
        return text_content, metadata                                           # return : renvoyer (texte, infos)

    except Exception as e:                                                      # except : capturer toute erreur
        logger.error(f"Error processing URL {url}: {e}")                        # logger.error : loguer erreur
        raise e                                                                 # raise : relancer l'erreur