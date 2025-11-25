#!/usr/bin/env python3
"""
Script pour vider les caches LanceDB du projet VEV RAG

Usage:
    python clear_cache.py --all              # Vider tous les caches
    python clear_cache.py --semantic         # Vider cache sémantique seulement
    python clear_cache.py --vector           # Vider base vectorielle seulement
"""

import argparse
import shutil
from pathlib import Path

# Chemins des caches
PROJECT_ROOT = Path(__file__).parent
SEMANTIC_CACHE = PROJECT_ROOT / "models" / "lancedb_cache"
VECTOR_DB = PROJECT_ROOT / "data" / "lancedb"


def clear_semantic_cache():
    """Vide le cache sémantique (réponses RAG)"""
    if SEMANTIC_CACHE.exists():
        print(f"🧹 Suppression du cache sémantique: {SEMANTIC_CACHE}")
        shutil.rmtree(SEMANTIC_CACHE)
        print(f"✅ Cache sémantique vidé ({SEMANTIC_CACHE})")
    else:
        print(f"ℹ️  Cache sémantique déjà vide ({SEMANTIC_CACHE})")


def clear_vector_db():
    """Vide la base vectorielle (chunks de documents)"""
    if VECTOR_DB.exists():
        print(f"🧹 Suppression de la base vectorielle: {VECTOR_DB}")
        shutil.rmtree(VECTOR_DB)
        print(f"✅ Base vectorielle vidée ({VECTOR_DB})")
    else:
        print(f"ℹ️  Base vectorielle déjà vide ({VECTOR_DB})")


def main():
    parser = argparse.ArgumentParser(
        description="Vider les caches LanceDB de VEV RAG"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Vider tous les caches (sémantique + vectoriel)"
    )
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Vider uniquement le cache sémantique (réponses)"
    )
    parser.add_argument(
        "--vector",
        action="store_true",
        help="Vider uniquement la base vectorielle (documents)"
    )

    args = parser.parse_args()

    # Si aucun argument, vider tout par défaut
    if not (args.all or args.semantic or args.vector):
        args.all = True

    print("\n" + "="*60)
    print("🗑️  VEV RAG - Nettoyage des Caches LanceDB")
    print("="*60 + "\n")

    if args.all or args.semantic:
        clear_semantic_cache()
        print()

    if args.all or args.vector:
        clear_vector_db()
        print()

    print("="*60)
    print("✅ Nettoyage terminé !")
    print("="*60)
    print("\nℹ️  Les caches seront recréés automatiquement au prochain démarrage.")


if __name__ == "__main__":
    main()
