#!/usr/bin/env python3
"""
Script pour exporter les modèles entraînés depuis Kaggle
À exécuter à la FIN de votre notebook Kaggle
"""

import os
import shutil
from pathlib import Path

def export_models_for_deployment():
    """
    Exporte tous les fichiers nécessaires pour le déploiement
    """
    
    print("="*70)
    print("📦 EXPORT DES MODÈLES POUR DÉPLOIEMENT")
    print("="*70)
    
    # Chemins Kaggle
    KAGGLE_OUTPUT = '/kaggle/working'
    
    # Créer dossier d'export
    EXPORT_DIR = f'{KAGGLE_OUTPUT}/deployment_package'
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Liste des fichiers à exporter
    files_to_export = {
        'models': [
            f'{KAGGLE_OUTPUT}/um5_hybrid_model',  # Modèle XLM-RoBERTa
        ],
        'data': [
            f'{KAGGLE_OUTPUT}/vector_database.npz',  # Embeddings
            f'{KAGGLE_OUTPUT}/knowledge_base.json',  # Base de connaissances
        ],
        'results': [
            f'{KAGGLE_OUTPUT}/hybrid_training_curves.png',
            f'{KAGGLE_OUTPUT}/hybrid_confusion_matrix.png',
            f'{KAGGLE_OUTPUT}/hybrid_classification_report.txt',
        ]
    }
    
    # Copier les fichiers
    print("\n📂 Copie des fichiers...")
    
    for category, files in files_to_export.items():
        category_dir = f'{EXPORT_DIR}/{category}'
        os.makedirs(category_dir, exist_ok=True)
        
        for file_path in files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    # Copier dossier complet
                    dest = f'{category_dir}/{os.path.basename(file_path)}'
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(file_path, dest)
                    print(f"  ✅ {os.path.basename(file_path)}/")
                else:
                    # Copier fichier
                    shutil.copy2(file_path, category_dir)
                    print(f"  ✅ {os.path.basename(file_path)}")
            else:
                print(f"  ⚠️  Non trouvé: {os.path.basename(file_path)}")
    
    # Créer un fichier requirements.txt
    requirements = """# Requirements pour le déploiement
fastapi==0.104.1
uvicorn==0.24.0
transformers==4.35.0
torch==2.1.0
sentence-transformers==2.2.2
numpy==1.24.3
scikit-learn==1.3.0
python-multipart==0.0.6
pydantic==2.5.0
"""
    
    with open(f'{EXPORT_DIR}/requirements.txt', 'w') as f:
        f.write(requirements)
    print(f"  ✅ requirements.txt")
    
    # Créer README
    readme = """# UM5 Hybrid Chatbot - Package de Déploiement

## Contenu

- `models/` : Modèle XLM-RoBERTa entraîné
- `data/` : Base vectorielle et connaissances
- `results/` : Métriques et visualisations

## Instructions de Déploiement

1. Télécharger ce dossier complet
2. Suivre les instructions dans le guide de déploiement
3. Installer les dépendances : `pip install -r requirements.txt`

## Métriques

Voir `results/hybrid_classification_report.txt` pour les performances détaillées.
"""
    
    with open(f'{EXPORT_DIR}/README.md', 'w') as f:
        f.write(readme)
    print(f"  ✅ README.md")
    
    # Créer un fichier zip
    print("\n📦 Création de l'archive...")
    shutil.make_archive(
        f'{KAGGLE_OUTPUT}/um5_chatbot_deployment',
        'zip',
        EXPORT_DIR
    )
    
    print(f"\n✅ Package créé : um5_chatbot_deployment.zip")
    print(f"   Taille : {os.path.getsize(f'{KAGGLE_OUTPUT}/um5_chatbot_deployment.zip') / 1e6:.1f} MB")
    
    print("\n" + "="*70)
    print("📥 TÉLÉCHARGEMENT")
    print("="*70)
    print("\n1. Dans Kaggle, aller dans l'onglet 'Output'")
    print("2. Télécharger 'um5_chatbot_deployment.zip'")
    print("3. Extraire le zip sur votre machine locale")
    print("\n" + "="*70)

if __name__ == "__main__":
    export_models_for_deployment()
