# Objectif — Charger des documents complexes (PDF, DOCX, TXT) et les convertir en Markdown structuré grâce à l'IA (Docling)

# Étape 1 — Importer les dépendances
import logging                                                                  # import : charger le module standard | logging : gestion des journaux d'événements (logs)
from pathlib import Path                                                        # from : importer depuis un package | pathlib : gestion des chemins | import : commande | Path : classe objet chemin
from typing import Tuple                                                        # from : importer depuis le typage | typing : module types | import : commande | Tuple : type pour retourner plusieurs valeurs
from docling.document_converter import DocumentConverter                        # from : importer depuis la librairie externe | docling : outil d'IBM | import : commande | DocumentConverter : classe principale de conversion
from src.core.schemas import SourceMetadata                                     # from : importer depuis notre projet | src.core.schemas : fichier de définitions | import : commande | SourceMetadata : notre objet de métadonnées

# Étape 2 — Configurer le logging (pour voir ce qui se passe)
logging.basicConfig(level=logging.INFO)                                         # logging.basicConfig(...) : configurer l'affichage des logs | level=logging.INFO : afficher les infos importantes
logger = logging.getLogger(__name__)                                            # logger : objet enregistreur | = : assignation | logging.getLogger(__name__) : récupérer le logger du fichier actuel

# Étape 3 — Initialiser le convertisseur (Singleton) - On le crée en dehors de la fonction pour ne pas recharger les modèles à chaque fichier (lourd)
try:                                                                            # try : essayer d'exécuter
    converter = DocumentConverter()                                             # converter : instance du convertisseur | = : assignation | DocumentConverter() : initialisation (télécharge les modèles au 1er lancement)
except Exception as e:                                                          # except : si erreur d'initialisation
    logger.error(f"Failed to init Docling: {e}")                                # logger.error : loguer l'erreur | f"..." : message formaté
    converter = None                                                            # converter : mettre à None pour gérer l'erreur plus tard

# Étape 4 — Fonction principale de chargement
def load_document(file_path: str) -> Tuple[str, SourceMetadata]:                # def : définir fonction | load_document : nom | file_path : chemin fichier | -> : retour | Tuple[str, SourceMetadata] : renvoie (texte, infos)
    """
    Convertit un fichier (PDF/DOCX/TXT) en Markdown structuré et extrait ses métadonnées.
    """
    path_obj = Path(file_path)                                                  # path_obj : objet chemin | = : assignation | Path(file_path) : conversion chaîne vers objet Path

    # 1. Vérification de l'existence
    if not path_obj.exists():                                                   # if : condition | not : négation | .exists() : vérifie si le fichier est là
        raise FileNotFoundError(f"File not found: {file_path}")                 # raise : lever une erreur | FileNotFoundError : type d'erreur | f"..." : message

    # ✨ 2. Gestion TXT avec Python natif (simple et rapide)
    if path_obj.suffix.lower() == ".txt":                                       # if : condition | .suffix : extension | .lower() : minuscule | == ".txt" : test égalité
        logger.info(f"Loading TXT file (native): {file_path}")                  # logger.info : afficher message | "(native)" : indication méthode
        
        try:                                                                    # try : bloc de sécurité
            # Lecture directe avec gestion d'encodage
            with open(path_obj, "r", encoding="utf-8", errors="replace") as f:  # with open(...) : ouvrir le fichier | "r" : lecture | encoding="utf-8" : encodage | errors="replace" : remplacer caractères invalides
                text_content = f.read()                                         # text_content : lire tout le contenu | f.read() : lecture complète
            
            # Métadonnées pour TXT
            metadata = SourceMetadata(                                          # metadata : objet infos source | SourceMetadata(...) : constructeur
                source_type="txt",                                              # source_type : extension "txt"
                source_path=str(path_obj.absolute()),                           # source_path : chemin complet absolu
                title=path_obj.stem                                             # title : nom du fichier sans extension
            )
            
            logger.info(f"Successfully loaded TXT: {file_path}")                 # logger.info : succès
            return text_content, metadata                                       # return : renvoyer le duo (texte, métadonnées)
            
        except Exception as e:                                                  # except : si erreur de lecture
            logger.error(f"Error reading TXT file {file_path}: {e}")            # logger.error : afficher détail erreur
            raise e                                                             # raise : relancer l'erreur

    # 3. Pour PDF/DOCX : utiliser Docling (reste inchangé)
    if converter is None:                                                       # if : condition | converter is None : si l'outil n'est pas chargé
        raise RuntimeError("Docling converter is not initialized.")             # raise : lever erreur critique

    logger.info(f"Processing file: {file_path}...")                             # logger.info : afficher message | "Processing..." : début du travail

    try:                                                                        # try : début du bloc à risque
        # 4. Conversion intelligente : l'IA lit la mise en page (PDF -> Markdown)
        result = converter.convert(file_path)                                   # result : résultat conversion | = : assignation | converter.convert(...) : lance l'analyse Docling
        
        # 5. Export en Markdown. Le markdown préserve les titres (##) et les tableaux (|...|)
        markdown_text = result.document.export_to_markdown()                    # markdown_text : contenu texte final | = : assignation | .export_to_markdown() : méthode d'export structuré

        # 6. Création des métadonnées
        metadata = SourceMetadata(                                              # metadata : objet infos source | = : assignation | SourceMetadata(...) : constructeur défini dans schemas.py
            source_type=path_obj.suffix.lower().replace(".", ""),               # source_type : extension sans point (ex: "pdf") | .suffix : extension | .lower() : minuscule
            source_path=str(path_obj.absolute()),                               # source_path : chemin complet absolu | .absolute() : chemin disque entier
            title=path_obj.stem                                                 # title : nom du fichier sans extension (titre par défaut) | .stem : nom racine
        )

        logger.info(f"Successfully converted {file_path}")                      # logger.info : succès
        return markdown_text, metadata                                          # return : renvoyer le duo (texte, métadonnées)

    except Exception as e:                                                      # except : capture toute erreur pendant la conversion
        logger.error(f"Error converting {file_path}: {e}")                      # logger.error : afficher détail erreur
        raise e                                                                 # raise : relancer l'erreur pour arrêter le programme ou alerter l'utilisateur