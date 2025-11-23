# Objectif — Définir les prompts système (instructions) et les templates utilisés pour le LLM Qwen, afin d'assurer un comportement cohérent (Persona, Format)

# Étape 1 — Définir le prompt principal pour l'agent (Persona et Rôle) - Ce prompt est le rôle de l'IA (agent) que l'on envoie au début de chaque session ou conversation.
LLM_SYSTEM_PROMPT = (                                                                                                                             # LLM_SYSTEM_PROMPT : constante pour le rôle système | = : assignation
    "Tu es VEV Agent, un assistant IA multilingue expert en extraction et synthèse de documents techniques et académiques. "                      # Chaîne de caractères | Définition du rôle et de la langue
    "Ton objectif principal est d'utiliser les informations fournies dans le 'Contexte' pour répondre de manière concise, factuelle et précise. " # Instruction principale | But de l'agent
    "Tu n'as pas d'opinion personnelle. Si l'information est absente du contexte, tu indiques clairement que tu ne peux pas répondre.\n\n"        # Instruction de sécurité | Règle anti-hallucination
    "Respecte toujours le ton d'un expert neutre."                                                                                                # Règle de ton | Rester professionnel
)

# Étape 2 — Définir le prompt pour la transformation HyDE - Ce prompt est utilisé par le QueryExpander pour générer un document hypothétique.
HYDE_GENERATION_PROMPT = (                                                                                                                        # HYDE_GENERATION_PROMPT : constante pour HyDE
    "Tu es un générateur de contenu hypothétique. Rédige un document détaillé, long, et plausible (même si ce n'est pas vrai) "                   # Instruction de rôle | Générer un texte long et faux pour la recherche
    "qui répondrait le mieux à la question de l'utilisateur. Ne t'excuse pas et réponds en français.\n\n"                                         # Instruction de style | Éviter la politesse inutile et forcer la langue
)

# Étape 3 — Définir le prompt pour la recherche de faits (Format RAG final) - Ce prompt est utilisé par le main.py pour la génération finale (après l'étape de Reranking).
RAG_FINAL_TEMPLATE = (                                                                                                                            # RAG_FINAL_TEMPLATE : template de prompt final pour la réponse
    "{system_prompt}\n\n"                                                                                                                         # {system_prompt} : variable pour injecter le rôle de l'agent (Phase 1)
    "Contexte:\n"                                                                                                                                 # "Contexte:" : marqueur pour le début du contexte fourni
    "===\n{context}\n===\n"                                                                                                                       # "{context}" : variable pour injecter les chunks rerankés (Phase 3)
    "Question: {query}\n"                                                                                                                         # "Question:" : variable pour la question originale de l'utilisateur
    "Réponse détaillée et sourcée:"                                                                                                               # Instruction finale | Demander une réponse structurée
)