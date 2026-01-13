# 🚀 Guide de Déploiement Complet - Chatbot UM5

## 📋 Table des Matières

1. [Export depuis Kaggle](#1-export-depuis-kaggle)
2. [Configuration Locale](#2-configuration-locale)
3. [Déploiement Local](#3-déploiement-local)
4. [Déploiement Cloud](#4-déploiement-cloud)
5. [Partage du Lien](#5-partage-du-lien)

---

## 1️⃣ Export depuis Kaggle

### Étape 1.1 : Ajouter le script d'export à votre notebook

À la **fin de votre notebook Kaggle**, ajoutez cette cellule :

```python
# ============================================================================
# EXPORT DES MODÈLES POUR DÉPLOIEMENT
# ============================================================================

import os
import shutil

KAGGLE_OUTPUT = '/kaggle/working'
EXPORT_DIR = f'{KAGGLE_OUTPUT}/deployment_package'
os.makedirs(EXPORT_DIR, exist_ok=True)

# Créer structure
os.makedirs(f'{EXPORT_DIR}/models', exist_ok=True)
os.makedirs(f'{EXPORT_DIR}/data', exist_ok=True)

# Copier modèle Intent
shutil.copytree(
    f'{KAGGLE_OUTPUT}/um5_hybrid_model',
    f'{EXPORT_DIR}/models/um5_hybrid_model'
)

# Copier données RAG
shutil.copy2(f'{KAGGLE_OUTPUT}/vector_database.npz', f'{EXPORT_DIR}/data/')
shutil.copy2(f'{KAGGLE_OUTPUT}/knowledge_base.json', f'{EXPORT_DIR}/data/')

# Créer archive
shutil.make_archive(
    f'{KAGGLE_OUTPUT}/um5_deployment',
    'zip',
    EXPORT_DIR
)

print("✅ Package créé : um5_deployment.zip")
print(f"📥 Téléchargez-le depuis l'onglet Output de Kaggle")
```

### Étape 1.2 : Télécharger le package

1. Exécuter la cellule
2. Aller dans **Output** → **Data**
3. Télécharger `um5_deployment.zip` (~500MB)

---

## 2️⃣ Configuration Locale

### Étape 2.1 : Préparer votre environnement

```bash
# Créer dossier projet
mkdir um5-chatbot-demo
cd um5-chatbot-demo

# Extraire le package Kaggle
unzip um5_deployment.zip

# Structure attendue :
# um5-chatbot-demo/
# ├── models/
# │   └── um5_hybrid_model/
# ├── data/
# │   ├── vector_database.npz
# │   └── knowledge_base.json
```

### Étape 2.2 : Télécharger les fichiers de l'app

Téléchargez depuis mon repo (ou créez localement) :

- `app.py` - Application FastAPI
- `requirements.txt` - Dépendances Python
- `static/index.html` - Interface web
- `Dockerfile` - Configuration Docker (optionnel)

### Étape 2.3 : Installer les dépendances

```bash
# Créer environnement virtuel (recommandé)
python -m venv venv

# Activer
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
```

---

## 3️⃣ Déploiement Local

### Option A : Exécution Directe (Développement)

```bash
# Lancer le serveur
python app.py

# Ou avec uvicorn directement
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Accès :**
- Interface web : http://localhost:8000
- API Documentation : http://localhost:8000/docs
- Health check : http://localhost:8000/health

### Option B : Docker (Production)

```bash
# Build l'image
docker build -t um5-chatbot .

# Lancer le container
docker run -d -p 8000:8000 --name um5-chatbot um5-chatbot

# Vérifier les logs
docker logs -f um5-chatbot

# Arrêter
docker stop um5-chatbot
```

---

## 4️⃣ Déploiement Cloud

### Option 1 : Hugging Face Spaces (GRATUIT, RECOMMANDÉ) 🌟

**Avantages** :
- ✅ Gratuit pour projets publics
- ✅ GPU gratuit disponible
- ✅ URL publique automatique
- ✅ Très facile

**Étapes** :

1. **Créer un compte** : https://huggingface.co/join

2. **Créer un nouveau Space** :
   - Aller sur https://huggingface.co/new-space
   - Nom : `um5-chatbot-demo`
   - SDK : **Gradio** ou **Docker**
   - Licence : MIT
   - Visibilité : Public

3. **Upload les fichiers** :

```bash
# Cloner le repo du Space
git clone https://huggingface.co/spaces/VOTRE_USERNAME/um5-chatbot-demo
cd um5-chatbot-demo

# Copier vos fichiers
cp -r ../um5-chatbot-demo/* .

# Commit et push
git add .
git commit -m "Initial deployment"
git push
```

4. **Attendre le build** (~5-10 min)

5. **Votre lien** : `https://huggingface.co/spaces/VOTRE_USERNAME/um5-chatbot-demo`

---

### Option 2 : Render (GRATUIT avec limitations)

**Avantages** :
- ✅ Gratuit (plan Starter)
- ✅ Facile à configurer
- ✅ Auto-deploy depuis GitHub

**Étapes** :

1. **Créer compte** : https://render.com

2. **Préparer repo GitHub** :
```bash
# Créer repo GitHub et push votre code
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/VOTRE_USERNAME/um5-chatbot.git
git push -u origin main
```

3. **Sur Render.com** :
   - New → Web Service
   - Connect GitHub repo
   - Configuration :
     - Name : `um5-chatbot`
     - Environment : Python 3
     - Build Command : `pip install -r requirements.txt`
     - Start Command : `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

4. **Votre lien** : `https://um5-chatbot.onrender.com`

**⚠️ Limitations du plan gratuit** :
- Se met en veille après 15 min d'inactivité
- Redémarre à la prochaine visite (~30s)
- 750h/mois de runtime

---

### Option 3 : Railway (GRATUIT avec limitations)

**Avantages** :
- ✅ $5 de crédits gratuits/mois
- ✅ Très simple
- ✅ Bonne performance

**Étapes** :

1. **Créer compte** : https://railway.app

2. **New Project** → Deploy from GitHub

3. **Variables d'environnement** (Settings) :
```
PORT=8000
PYTHONUNBUFFERED=1
```

4. **Votre lien** : `https://VOTRE_APP.up.railway.app`

---

### Option 4 : Google Cloud Run (Payant mais gratuit jusqu'à 2M requêtes/mois)

**Avantages** :
- ✅ Très scalable
- ✅ Pay-per-use
- ✅ Tier gratuit généreux

**Étapes** :

```bash
# Installer gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Créer projet
gcloud projects create um5-chatbot --set-as-default

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Build et deploy
gcloud builds submit --tag gcr.io/um5-chatbot/chatbot
gcloud run deploy um5-chatbot \
  --image gcr.io/um5-chatbot/chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Votre lien** : Affiché après le deploy

---

### Option 5 : Azure Web App (Payant, gratuit avec compte étudiant)

Si vous avez **Azure for Students** (100$ de crédits gratuits) :

```bash
# Installer Azure CLI
# https://docs.microsoft.com/cli/azure/install-azure-cli

# Login
az login

# Créer resource group
az group create --name um5-chatbot-rg --location westeurope

# Créer App Service plan (F1 = gratuit)
az appservice plan create \
  --name um5-plan \
  --resource-group um5-chatbot-rg \
  --sku F1 \
  --is-linux

# Deploy from Docker
az webapp create \
  --resource-group um5-chatbot-rg \
  --plan um5-plan \
  --name um5-chatbot-demo \
  --deployment-container-image-name VOTRE_DOCKERHUB_IMAGE

# Ou deploy depuis GitHub
az webapp up --name um5-chatbot-demo --location westeurope
```

---

## 5️⃣ Partage du Lien

### 🎯 Pour une Démonstration Professionnelle

1. **Personnaliser le domaine** (optionnel) :
   - Hugging Face : Gratuit, pas de custom domain
   - Render : Custom domain sur plan payant
   - Railway : Custom domain inclus

2. **Créer une page de présentation** :

```markdown
# 🎓 Chatbot UM5 - Démonstration

## 🔗 Lien de démo : https://VOTRE_LIEN_ICI

## 📊 Caractéristiques

- **Précision** : 89.7%
- **Latence** : ~180ms
- **Architecture** : Hybride (Intent + RAG + LLM)
- **Support** : Multilingue (Fr/Ar/En)

## 🚀 Fonctionnalités

1. Classification d'intention (XLM-RoBERTa)
2. Recherche sémantique (RAG)
3. Fallback intelligent (LLM)

## 📱 Utilisation

1. Ouvrir le lien
2. Poser une question
3. Voir les réponses en temps réel avec métriques

## 📧 Contact

- Email : votre.email@um5.ac.ma
- GitHub : https://github.com/VOTRE_USERNAME/um5-chatbot
```

3. **Partager** :
   - LinkedIn : Post avec screenshot + lien
   - Email prof/jury : Template ci-dessous
   - README GitHub : Ajouter badge de démo

---

## 📧 Template Email pour Jury/Prof

```
Objet : Démonstration - Chatbot Universitaire UM5 (Architecture Hybride)

Bonjour [Nom],

Je vous présente mon projet de fin d'études : un chatbot intelligent pour 
l'Université Mohammed V utilisant une architecture hybride innovante.

🔗 Démo en ligne : https://VOTRE_LIEN

📊 Résultats :
- Précision : 89.7%
- Latence : 180ms
- Architecture : Intent Classification + RAG + LLM Fallback

📂 Documentation complète :
- GitHub : https://github.com/VOTRE_USERNAME/um5-chatbot
- Rapport : [lien vers PDF]

La démo est accessible 24/7 et permet de tester l'ensemble des 
fonctionnalités en temps réel.

N'hésitez pas si vous avez des questions !

Cordialement,
[Votre Nom]
```

---

## 🛠️ Dépannage

### Problème : Modèle trop gros pour déployer

**Solution** : Utiliser un service avec plus de stockage
- Hugging Face : 50GB gratuit
- Google Cloud Run : Storage illimité
- Compresser le modèle (quantization)

### Problème : Latence élevée en production

**Solutions** :
1. Activer GPU (Hugging Face Spaces)
2. Utiliser un CDN pour les assets statiques
3. Implémenter du caching Redis
4. Optimiser avec ONNX Runtime

### Problème : Out of Memory

**Solutions** :
1. Réduire batch_size dans le code
2. Utiliser FP16 (half precision)
3. Upgrader le plan (plus de RAM)

---

## ✅ Checklist de Déploiement

- [ ] Modèles exportés depuis Kaggle
- [ ] Dépendances installées localement
- [ ] Test local réussi (http://localhost:8000)
- [ ] Code pushé sur GitHub
- [ ] Service cloud choisi et configuré
- [ ] Déploiement réussi
- [ ] Tests fonctionnels sur le lien public
- [ ] Documentation README.md à jour
- [ ] Lien partagé avec jury/prof

---

## 📚 Ressources Supplémentaires

- [Documentation FastAPI](https://fastapi.tiangolo.com)
- [Hugging Face Spaces Guide](https://huggingface.co/docs/hub/spaces)
- [Render Deployment Guide](https://render.com/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Bonne chance pour votre démonstration ! 🚀**
