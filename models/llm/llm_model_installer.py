# -*- coding: utf-8 -*-
# Gestionnaire de modeles LLM pour VEV RAG
# Usage: python models/llm/llm_model_installer.py

from llama_cpp import Llama
import os
import re
from pathlib import Path

# Configuration
LOCAL_DIR = "models/llm"
CONFIG_FILE = "src/core/config.py"

# Catalogue de modeles disponibles
AVAILABLE_MODELS = {
    "1": {
        "NAME": "Qwen2.5-0.5B (Ultra-Leger)",
        "REPO_ID": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "LLM_MODEL_FILE": "qwen2.5-0.5b-instruct-fp16.gguf",
        "SIZE": "~1 GB",
        "LLM_CONTEXT_WINDOW": 4096,
        "LLM_MAX_TOKENS": 512
    },
    "2": {
        "NAME": "Qwen2.5-1.5B (Leger)",
        "REPO_ID": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "LLM_MODEL_FILE": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "SIZE": "~1 GB",
        "LLM_CONTEXT_WINDOW": 4096,
        "LLM_MAX_TOKENS": 1024
    },
    "3": {
        "NAME": "Qwen3-4B (Recommande)",
        "REPO_ID": "Qwen/Qwen3-4B-GGUF",
        "LLM_MODEL_FILE": "Qwen3-4B-Q4_K_M.gguf",
        "SIZE": "~2.6 GB",
        "LLM_CONTEXT_WINDOW": 8200,
        "LLM_MAX_TOKENS": 1024
    },
    "4": {
        "NAME": "TinyLlama-1.1B (Tres leger)",
        "REPO_ID": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
        "LLM_MODEL_FILE": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "SIZE": "~650 MB",
        "LLM_CONTEXT_WINDOW": 2048,
        "LLM_MAX_TOKENS": 512
    }
}


def list_installed_models():
    """Liste tous les modeles GGUF installes."""
    print("\n" + "="*60)
    print("MODELES INSTALLES")
    print("="*60)
    
    gguf_files = list(Path(LOCAL_DIR).glob("*.gguf"))
    
    if not gguf_files:
        print("Aucun modele installe.\n")
        return []
    
    # Lire le modele actuel dans config.py
    current_model = None
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'LLM_MODEL_FILE\s*=\s*"([^"]*)"', content)
            if match:
                current_model = match.group(1)
    except:
        pass
    
    models = []
    for idx, filepath in enumerate(gguf_files, 1):
        size_gb = filepath.stat().st_size / 1e9
        is_active = " [ACTIF]" if filepath.name == current_model else ""
        print(f"{idx}. {filepath.name}{is_active}")
        print(f"   Taille: {size_gb:.2f} GB")
        models.append(filepath.name)
    
    print()
    return models


def delete_model():
    """Supprime un modele installe."""
    models = list_installed_models()
    
    if not models:
        return
    
    try:
        choice = input("Numero du modele a supprimer (0 pour annuler): ")
        
        if choice == "0":
            print("Annule.\n")
            return
        
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            model_to_delete = models[idx]
            model_path = Path(LOCAL_DIR) / model_to_delete
            
            # Lire le modele actuel
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'LLM_MODEL_FILE\s*=\s*"([^"]*)"', content)
                current_model = match.group(1) if match else None
            
            if model_to_delete == current_model:
                print(f"\nERREUR: Impossible de supprimer le modele actif ({model_to_delete})")
                print("Changez d'abord le modele actif.\n")
                return
            
            confirm = input(f"\nConfirmez la suppression de {model_to_delete} ? (o/n): ")
            if confirm.lower() in ['o', 'oui', 'y', 'yes']:
                model_path.unlink()
                print(f"Modele supprime: {model_to_delete}\n")
            else:
                print("Annule.\n")
        else:
            print("Numero invalide.\n")
    except ValueError:
        print("Entree invalide.\n")


def install_model():
    """Installe un nouveau modele."""
    print("\n" + "="*60)
    print("CATALOGUE DE MODELES")
    print("="*60)
    
    for key, model in AVAILABLE_MODELS.items():
        print(f"{key}. {model['NAME']}")
        print(f"   Fichier: {model['LLM_MODEL_FILE']}")
        print(f"   Taille: {model['SIZE']}")
        print(f"   Contexte: {model['LLM_CONTEXT_WINDOW']} tokens")
        print(f"   Max tokens: {model['LLM_MAX_TOKENS']} tokens\n")
    
    choice = input("Choisissez un modele a installer (0 pour annuler): ")
    
    if choice == "0":
        print("Annule.\n")
        return
    
    if choice not in AVAILABLE_MODELS:
        print("Choix invalide.\n")
        return
    
    model = AVAILABLE_MODELS[choice]
    model_path = Path(LOCAL_DIR) / model['LLM_MODEL_FILE']
    
    # Verifier si deja installe
    if model_path.exists():
        print(f"\nLe modele {model['LLM_MODEL_FILE']} est deja installe.")
        change = input("Voulez-vous le definir comme modele actif ? (o/n): ")
        if change.lower() in ['o', 'oui', 'y', 'yes']:
            update_config(model)
        return
    
    # Creer le dossier si necessaire
    os.makedirs(LOCAL_DIR, exist_ok=True)
    
    # Telecharger
    print(f"\nTelechargement de {model['NAME']}...")
    print(f"Taille: {model['SIZE']} (peut prendre plusieurs minutes)")
    
    try:
        Llama.from_pretrained(
            repo_id=model['REPO_ID'],
            filename=model['LLM_MODEL_FILE'],
            local_dir=LOCAL_DIR
        )
        print(f"Modele telecharge avec succes dans {LOCAL_DIR}/\n")
        
        # Mettre a jour config.py avec tous les parametres
        update_config(model)
        
    except Exception as e:
        print(f"\nERREUR lors du telechargement: {e}\n")


def update_config(model):
    """Met a jour le fichier config.py avec tous les parametres du modele."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Si model est un string (ancien code), convertir en dict pour compatibilite
        if isinstance(model, str):
            filename = model
            # Mise a jour simple sans context/max_tokens
            content = re.sub(
                r'LLM_MODEL_FILE\s*=\s*"[^"]*"',
                f'LLM_MODEL_FILE = "{filename}"',
                content
            )
        else:
            # Mise a jour complete avec tous les parametres
            filename = model['LLM_MODEL_FILENAME']
            
            # 1. Remplacer LLM_MODEL_FILE
            content = re.sub(
                r'LLM_MODEL_FILE\s*=\s*"[^"]*"',
                f'LLM_MODEL_FILE = "{filename}"',
                content
            )
            
            # 2. Remplacer LLM_CONTEXT_WINDOW
            content = re.sub(
                r'LLM_CONTEXT_WINDOW\s*=\s*\d+',
                f'LLM_CONTEXT_WINDOW = {model["LLM_CONTEXT_WINDOW"]}',
                content
            )
            
            # 3. Remplacer LLM_MAX_TOKENS
            content = re.sub(
                r'LLM_MAX_TOKENS\s*=\s*\d+',
                f'LLM_MAX_TOKENS = {model["LLM_MAX_TOKENS"]}',
                content
            )
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Config mise a jour:")
        print(f"  - Modele actif: {filename}")
        if isinstance(model, dict):
            print(f"  - Context window: {model['LLM_CONTEXT_WINDOW']} tokens")
            print(f"  - Max tokens: {model['LLM_MAX_TOKENS']} tokens\n")
        else:
            print()
        
    except Exception as e:
        print(f"ERREUR lors de la mise a jour du config: {e}\n")


def change_active_model():
    """Change le modele actif dans config.py."""
    models = list_installed_models()
    
    if not models:
        return
    
    try:
        choice = input("Numero du modele a activer (0 pour annuler): ")
        
        if choice == "0":
            print("Annule.\n")
            return
        
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            # Pour change_active_model, on passe juste le filename
            # car on ne connait pas les autres parametres
            update_config(models[idx])
        else:
            print("Numero invalide.\n")
    except ValueError:
        print("Entree invalide.\n")


def main_menu():
    """Menu principal."""
    while True:
        print("\n" + "="*60)
        print("GESTIONNAIRE DE MODELES LLM - VEV RAG")
        print("="*60)
        print("1. Installer un nouveau modele")
        print("2. Lister les modeles installes")
        print("3. Changer le modele actif")
        print("4. Supprimer un modele")
        print("0. Quitter")
        print("="*60)
        
        choice = input("\nVotre choix: ")
        
        if choice == "1":
            install_model()
        elif choice == "2":
            list_installed_models()
            input("Appuyez sur Entree pour continuer...")
        elif choice == "3":
            change_active_model()
        elif choice == "4":
            delete_model()
        elif choice == "0":
            print("\nAu revoir!\n")
            break
        else:
            print("\nChoix invalide.\n")


if __name__ == "__main__":
    main_menu()
