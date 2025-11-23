# Objectif — Standardiser et nettoyer le texte brut avant le découpage (Normalisation + NLP)

# Étape 1 — Importer les librairies de nettoyage
import re                                                                       # import : charger le module standard | re : module d'expressions régulières (Regex) pour chercher des motifs complexes
import ftfy                                                                     # import : charger la librairie externe | ftfy : "Fix Text For You", répare l'encodage Unicode cassé (ex: "Ã©" -> "é")
from cleantext import clean                                                     # from : importer depuis un package | cleantext : librairie de nettoyage de bruit | import : commande | clean : fonction principale de nettoyage
import spacy                                                                    # import : charger la librairie NLP | spacy : traitement du langage naturel industriel

# Étape 2 — Charger le modèle linguistique (Optimisation - On le charge une seule fois au démarrage pour éviter de le recharger à chaque appel (Pattern Singleton))
try:                                                                            # try : tenter d'exécuter le bloc suivant
    nlp = spacy.load("fr_core_news_md")                                         # nlp : objet modèle linguistique | = : assignation | spacy.load(...) : charger le cerveau français téléchargé plus tôt
except OSError:                                                                 # except : si une erreur survient (modèle non trouvé)
    print("⚠️ Modèle Spacy 'fr_core_news_md' introuvable. Téléchargement...")   # print : alerter l'utilisateur
    from spacy.cli import download                                              # from : importer l'outil de ligne de commande interne
    download("fr_core_news_md")                                                 # download(...) : télécharger le modèle automatiquement
    nlp = spacy.load("fr_core_news_md")                                         # nlp : recharger le modèle maintenant qu'il est là

# Étape 3 — Définir la fonction de nettoyage de base (Niveau 1)
def clean_text_basic(text: str) -> str:                                         # def : définir fonction | clean_text_basic : nom | text : entrée brute | -> : retour | str : texte propre
    """Nettoyage rapide : encodage et espaces."""
    if not text:                                                                # if : condition | not text : si le texte est vide ou None
        return ""                                                               # return : renvoyer une chaîne vide immédiatement

    # 1. Réparation de l'encodage (Mojibake)
    text = ftfy.fix_text(text)                                                  # text : variable mise à jour | ftfy.fix_text(...) : fonction magique qui détecte et répare les erreurs UTF-8

    # 2. Nettoyage du bruit avec clean-text
    text = clean(                                                               # text : mise à jour | clean(...) : appel de la librairie
        text,                                                                   # text : entrée
        fix_unicode=True,                                                       # fix_unicode : standardiser les caractères spéciaux
        to_ascii=False,                                                         # to_ascii : False pour GARDER les accents français (très important !)
        lower=False,                                                            # lower : False pour garder les Majuscules (important pour les noms propres)
        no_line_breaks=False,                                                   # no_line_breaks : False pour garder les paragraphes
        no_urls=False,                                                          # no_urls : garder les liens (utile pour la source)
        no_emails=False,                                                        # no_emails : garder les emails
        no_phone_numbers=False,                                                 # no_phone_numbers : garder les numéros
        replace_with_url="<URL>",                                               # replace... : (inactif ici car no_urls=False) options de remplacement si activé
        replace_with_email="<EMAIL>",                                           # replace... : options de remplacement
        replace_with_phone_number="<PHONE>"                                     # replace... : options de remplacement
    )

    # 3. Suppression des espaces multiples (Regex)
    # Remplace "Bonjour    mon   ami" par "Bonjour mon ami"
    text = re.sub(r'\s+', ' ', text).strip()                                    # re.sub(...) : substitution regex | \s+ : chercher 1 ou plusieurs espaces/tabs/sauts | ' ' : remplacer par 1 seul espace | .strip() : nettoyer début/fin

    return text                                                                 # return : renvoyer le texte propre

# Étape 4 — Définir la fonction de segmentation intelligente (Niveau 2) - Cette fonction est cruciale pour le Chunking plus tard car elle empêche de couper une phrase au milieu
def split_into_sentences(text: str) -> list[str]:                               # def : fonction | split_into_sentences : nom explicite | -> : retour | list[str] : liste de phrases
    """Découpe un texte en phrases grammaticalement correctes grâce à Spacy."""
    if not text:                                                                # if : sécurité vide
        return []                                                               # return : liste vide

    doc = nlp(text)                                                             # doc : objet document analysé par Spacy | nlp(...) : lance l'analyse linguistique (comprend la grammaire)
    
    sentences = [sent.text.strip() for sent in doc.sents]                       # sentences : liste résultat | [ ... ] : compréhension de liste | sent.text : contenu de la phrase | for sent in doc.sents : pour chaque phrase trouvée par l'IA. On extrait les phrases (sents) détectées par le modèle
    
    return sentences                                                            # return : renvoyer la liste des phrases