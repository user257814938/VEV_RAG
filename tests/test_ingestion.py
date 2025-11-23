# Objectif — Tester la robustesse des composants d'Ingestion (loader_doc, loader_web, cleaner) en s'assurant que l'extraction et le nettoyage fonctionnent.

# Étape 1 — Importer les dépendances et les outils du projet
import pytest                                                                   # import : charger le framework de test | pytest : outil d'exécution des tests
from unittest.mock import MagicMock, patch                                      # from : importer les outils de simulation | unittest.mock : module de simulation | MagicMock, patch : classes de simulation
from src.ingestion.cleaner import clean_text_basic, split_into_sentences        # from : importer les fonctions | src.ingestion.cleaner : fonctions de nettoyage
from src.ingestion.loader_doc import load_document                              # from : importer le loader doc | src.ingestion.loader_doc : fonction de chargement PDF/DOCX
from src.ingestion.loader_web import load_url                                   # from : importer le loader web | src.ingestion.loader_web : fonction de chargement URL
from src.core.schemas import SourceMetadata                                     # from : importer le schéma | src.core.schemas : structure de données

# Étape 2 — Test du Nettoyage Basique (ftfy + cleantext)
def test_clean_text_basic_fixes_encoding_and_spaces():                           # def : définir la fonction de test | test_clean_text... : nom explicite
    """Vérifie si ftfy répare les caractères cassés et si regex gère les espaces multiples."""
    # Simuler un texte sale : encodage cassé et multiples espaces
    dirty_text = "Lâ€™été a été chaud.   Il y a des bugs Ã  corriger."      # dirty_text : chaîne de caractères avec des erreurs typiques (ex: 'Ã©' pour 'é')
    expected_clean = "L’été a été chaud. Il y a des bugs à corriger."           # expected_clean : le résultat attendu après nettoyage
    
    clean_output = clean_text_basic(dirty_text)                                 # clean_output : appel de la fonction à tester
    
    assert clean_output == expected_clean                                        # assert : vérification que la sortie correspond à l'attendu

# Étape 3 — Test de la Segmentation Linguistique (Spacy)
def test_split_into_sentences_handles_abbreviations():                           # def : définir la fonction de test | test_split_into... : nom explicite
    """Vérifie si Spacy ne coupe pas les abréviations (M. ou U.S.A.)."""
    text_with_abbreviations = "M. Dupont est arrivé à 10h. Il vit aux U.S.A."   # text_with_abbreviations : texte contenant des points mais ne séparant pas les phrases
    
    sentences = split_into_sentences(text_with_abbreviations)                   # sentences : appel à la segmentation Spacy
    
    assert len(sentences) == 2                                                  # assert : vérifier que seulement 2 phrases ont été trouvées (et non 4)
    assert sentences[0].startswith("M. Dupont")                                 # assert : vérifier que la première phrase est bien conservée

# Étape 4 — Test du Chargement de Document (Simuler Docling) - # Nous simulons le comportement de docling.document_converter.DocumentConverter
@patch('src.ingestion.loader_doc.DocumentConverter')                             # @patch : décorateur pour remplacer Docling par un mock
@patch('src.ingestion.loader_doc.Path')                                         # @patch : décorateur pour remplacer l'objet Path
def test_load_document_success(MockPath, MockConverter):                         # def : définir la fonction de test | MockPath, MockConverter : les objets simulés
    """Vérifie si load_document retourne le texte et les métadonnées correctes après conversion."""
    
    # Configuration du Mock de Path (simuler un fichier existant)
    MockPath.return_value.exists.return_value = True                            # MockPath...exists : simuler que le fichier est présent
    MockPath.return_value.suffix = ".pdf"                                       # MockPath...suffix : simuler l'extension .pdf
    MockPath.return_value.stem = "Rapport_Final"                                # MockPath...stem : simuler le nom du fichier
    MockPath.return_value.absolute.return_value = "/mock/rapport.pdf"           # MockPath...absolute : simuler le chemin absolu

    # Configuration du Mock de Docling (simuler la conversion)
    mock_result = MockConverter.return_value.convert.return_value               # mock_result : objet résultat simulé de Docling
    mock_result.document.export_to_markdown.return_value = "## Contexte du Rapport" # mock_result...export_to_markdown : simuler le texte Markdown de sortie

    # Exécution de la fonction
    markdown_text, metadata = load_document("/mock/rapport.pdf")                # markdown_text, metadata : appel à la fonction load_document
    
    # 1. Vérifier le contenu
    assert markdown_text == "## Contexte du Rapport"                             # assert : vérifier que le texte Markdown est bien le texte simulé
    
    # 2. Vérifier les métadonnées
    assert isinstance(metadata, SourceMetadata)                                 # assert : vérifier que l'objet est bien de type SourceMetadata
    assert metadata.source_type == "pdf"                                        # assert : vérifier que le type est pdf
    assert metadata.title == "Rapport_Final"                                    # assert : vérifier que le titre est bien extrait

# Étape 5 — Test du Chargement Web (Simuler Requêtes HTTP)
@patch('src.ingestion.loader_web.trafilatura.fetch_url')                         # @patch : décorateur pour remplacer l'appel à trafilatura.fetch_url
@patch('src.ingestion.loader_web.trafilatura.extract_metadata')                  # @patch : décorateur pour remplacer l'extraction des métadonnées
@patch('src.ingestion.loader_web.trafilatura.extract')                           # @patch : décorateur pour remplacer l'extraction du contenu
def test_load_url_extracts_content_and_metadata(MockExtract, MockMetadata, MockFetch): # def : définir la fonction de test | MockExtract, MockMetadata, MockFetch : les objets simulés
    """Vérifie si load_url extrait bien le contenu et les métadonnées sans erreur."""
    
    # Configuration des Mocks
    MockFetch.return_value = "<html>...</html>"                                 # MockFetch : simuler le HTML téléchargé
    MockExtract.return_value = "Texte final de l'article."                      # MockExtract : simuler le texte propre de Trafilatura
    mock_meta = MagicMock()                                                     # mock_meta : simuler l'objet métadonnées
    mock_meta.title = "Titre de l'Article"                                      # mock_meta.title : simuler le titre
    mock_meta.author = "Dr. Expert"                                             # mock_meta.author : simuler l'auteur
    MockMetadata.return_value = mock_meta                                       # MockMetadata : l'objet retourné

    # Exécution de la fonction
    text, metadata = load_url("http://test.com")                                # text, metadata : appel à la fonction load_url

    # 1. Vérifier le contenu
    assert text == "Texte final de l'article."                                  # assert : vérifier le contenu
    
    # 2. Vérifier les métadonnées
    assert isinstance(metadata, SourceMetadata)                                 # assert : vérifier le type
    assert metadata.source_type == "url"                                        # assert : vérifier le type de source
    assert metadata.title == "Titre de l'Article"                               # assert : vérifier que le titre a été capturé
    assert metadata.author == "Dr. Expert"                                      # assert : vérifier que l'auteur a été capturé