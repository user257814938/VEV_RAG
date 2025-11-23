# 🚀 Guide de Déploiement sur GitHub

Ce guide vous explique comment mettre votre projet **VEV RAG** sur GitHub.

## 📋 Prérequis

- [ ] Avoir un compte GitHub ([créer un compte](https://github.com/signup))
- [ ] Avoir Git installé sur votre ordinateur
- [ ] Être dans le dossier du projet

## 🔧 Étape 1 : Initialiser le dépôt Git local

Ouvrez PowerShell dans le dossier du projet et exécutez :

```powershell
# Initialiser le dépôt Git
git init

# Vérifier que .gitignore est bien présent
ls .gitignore
```

## 📝 Étape 2 : Ajouter les fichiers au dépôt

```powershell
# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Vérifier les fichiers qui seront commités
git status
```

> [!IMPORTANT]
> Vérifiez que le fichier `.env` n'apparaît **PAS** dans la liste. Il doit être ignoré pour protéger vos secrets.

## 💾 Étape 3 : Créer le premier commit

```powershell
# Créer le commit initial
git commit -m "Initial commit: VEV RAG project"
```

## 🌐 Étape 4 : Créer un dépôt sur GitHub

1. Allez sur [GitHub](https://github.com)
2. Cliquez sur le bouton **"+"** en haut à droite → **"New repository"**
3. Remplissez les informations :
   - **Repository name** : `vev-rag` (ou le nom de votre choix)
   - **Description** : "Document search tool with semantic search and AI summarization"
   - **Visibility** : Choisissez **Private** ou **Public**
   - ⚠️ **NE COCHEZ PAS** "Initialize with README" (vous en avez déjà un)
4. Cliquez sur **"Create repository"**

## 🔗 Étape 5 : Lier votre dépôt local à GitHub

GitHub vous affichera des commandes. Utilisez celles pour un dépôt existant :

```powershell
# Remplacez VOTRE_USERNAME et VOTRE_REPO par vos valeurs
git remote add origin https://github.com/VOTRE_USERNAME/VOTRE_REPO.git

# Renommer la branche en 'main' (si nécessaire)
git branch -M main

# Pousser le code sur GitHub
git push -u origin main
```

### 🔐 Authentification

Lors du push, GitHub vous demandera de vous authentifier :

- **Option 1 (Recommandée)** : Utilisez un **Personal Access Token**
  1. Allez dans **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
  2. Cliquez sur **"Generate new token"**
  3. Donnez un nom (ex: "VEV RAG Project")
  4. Cochez **"repo"** (accès complet aux dépôts)
  5. Générez et **copiez le token** (vous ne le reverrez plus !)
  6. Utilisez ce token comme mot de passe lors du push

- **Option 2** : Utilisez **GitHub CLI** (`gh auth login`)

## ✅ Étape 6 : Vérifier le déploiement

1. Rafraîchissez la page de votre dépôt GitHub
2. Vous devriez voir tous vos fichiers !
3. Vérifiez que le `.env` n'est **PAS** visible (sécurité ✓)

## 🔄 Mises à jour futures

Pour pousser de nouvelles modifications :

```powershell
# Ajouter les fichiers modifiés
git add .

# Créer un commit avec un message descriptif
git commit -m "Description de vos modifications"

# Pousser sur GitHub
git push
```

## 📚 Fichiers importants

- **`.gitignore`** : Protège vos fichiers sensibles et lourds
- **`README.md`** : Page d'accueil de votre projet sur GitHub
- **`requirements.txt`** : Liste des dépendances Python

## 🛡️ Sécurité

> [!CAUTION]
> **Ne commitez JAMAIS** :
> - Le fichier `.env` (contient des secrets)
> - Les modèles IA (`.gguf`, `.bin`, `.onnx`) - trop lourds
> - Les données dans `data/raw/`, `data/processed/`, `data/lancedb/`
> - Les caches (`__pycache__/`, `.cache/`)

Tous ces fichiers sont déjà protégés par votre `.gitignore` ✓

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :
- Vérifiez que Git est installé : `git --version`
- Consultez la [documentation GitHub](https://docs.github.com)
- Utilisez `git status` pour voir l'état de votre dépôt

---

**Bon déploiement ! 🎉**
