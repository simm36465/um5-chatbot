#!/usr/bin/env python3
"""
Application Web FastAPI pour le Chatbot UM5
Interface de démonstration avec API REST
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import torch
import numpy as np
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import time
from typing import Dict, List, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {

    'model_path': 'output/um5_hybrid_model',
    'vector_db_path': 'output/vector_database.npz',
    'knowledge_base_path': 'output/knowledge_base.json',
    'intent_threshold': 0.6,
    'similarity_threshold': 0.7,
    'top_k': 3,
}

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class QueryRequest(BaseModel):
    """Requête utilisateur"""
    message: str
    language: Optional[str] = "fr"

class QueryResponse(BaseModel):
    """Réponse du chatbot"""
    answer: str
    method: str  # "intent", "rag", "fallback"
    confidence: float
    intent: Optional[str] = None
    sources: Optional[List[Dict]] = None
    latency_ms: float

# ============================================================================
# CLASSE CHATBOT
# ============================================================================

class HybridChatbot:
    """Chatbot hybride pour inférence"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info("🚀 Initialisation du chatbot...")
        logger.info(f"   Device: {self.device}")
        
        # Charger le modèle Intent
        logger.info("📥 Chargement du modèle d'intention...")
        self.tokenizer = XLMRobertaTokenizer.from_pretrained(config['model_path'])
        self.model = XLMRobertaForSequenceClassification.from_pretrained(
            config['model_path']
        ).to(self.device)
        self.model.eval()
        
        # Charger les mappings
        with open(f"{config['model_path']}/label_mappings.json", 'r') as f:
            mappings = json.load(f)
            self.id2label = {int(k): v for k, v in mappings['id2label'].items()}
        
        # Charger la base vectorielle
        logger.info("📥 Chargement de la base vectorielle...")
        vector_data = np.load(config['vector_db_path'])
        self.embeddings = vector_data['embeddings']
        
        # Charger la base de connaissances
        with open(config['knowledge_base_path'], 'r', encoding='utf-8') as f:
            self.knowledge_base = json.load(f)
        
        logger.info(f"   ✅ {len(self.knowledge_base)} paires Q-A chargées")
        
        # Charger le modèle d'embedding
        logger.info("📥 Chargement du modèle d'embedding...")
        self.embedding_model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        )
        
        # Charger les réponses par défaut
        self._load_intent_templates()
        
        logger.info("✅ Chatbot prêt!")
    
    def _load_intent_templates(self):
        """Charger les templates de réponses par intention"""
        self.intent_templates = {
            'inscription': """Pour vous inscrire à l'Université Mohammed V :

📋 **Étapes** :
1. Visitez le portail : www.um5.ac.ma/inscription
2. Préparez vos documents (baccalauréat, relevé de notes)
3. Période d'inscription : Juillet - Septembre

📧 **Contact** : inscription@um5.ac.ma
📞 **Téléphone** : +212 5XX-XX-XX-XX""",

            'bourses': """Informations sur les bourses à l'UM5 :

💰 **Types de bourses** :
- Bourse d'Excellence (≥14/20)
- Bourse Sociale (conditions de ressources)
- Bourse de Recherche (Master/Doctorat)

📅 **Candidature** : Septembre - Octobre
📧 **Contact** : bourses@um5.ac.ma""",

            'emploi_du_temps': """Consultation de l'emploi du temps :

🗓️ **Accès** :
- Portail étudiant : student.um5.ac.ma
- Application mobile UM5
- Affichage dans votre faculté

📱 **Notifications** : Activez les alertes dans l'app""",

            'bibliotheque': """Bibliothèque Universitaire :

📚 **Horaires** :
- Lundi - Vendredi : 8h00 - 18h00
- Samedi : 9h00 - 13h00

🌐 **Ressources en ligne** : bibliotheque.um5.ac.ma
📧 **Contact** : bibliotheque@um5.ac.ma""",

            'default': """Je suis désolé, je n'ai pas pu trouver d'information précise pour votre question.

📞 **Contacts utiles** :
- Info générale : info@um5.ac.ma
- Standard : +212 5XX-XX-XX-XX

💡 Essayez de reformuler votre question ou contactez directement le service concerné."""
        }
    
    def classify_intent(self, text: str) -> tuple:
        """Classifier l'intention"""
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=128,
            truncation=True,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            confidence, pred_idx = torch.max(probs, dim=1)
        
        intent = self.id2label[pred_idx.item()]
        return intent, confidence.item()
    
    def search_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """Recherche par similarité"""
        # Encoder la requête
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculer les similarités
        similarities = cosine_similarity(
            [query_embedding], 
            self.embeddings
        )[0]
        
        # Top-K
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'question': self.knowledge_base[idx]['question'],
                'answer': self.knowledge_base[idx]['answer'],
                'intent': self.knowledge_base[idx]['intent'],
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def process_query(self, query: str) -> Dict:
        """Pipeline principal"""
        start_time = time.time()
        
        # 1. Classification d'intention
        intent, confidence = self.classify_intent(query)
        
        # 2. Décision de routing
        if confidence >= self.config['intent_threshold']:
            # Haute confiance → Réponse directe
            answer = self.intent_templates.get(intent, self.intent_templates['default'])
            
            response = {
                'answer': answer,
                'method': 'intent_classification',
                'confidence': confidence,
                'intent': intent,
                'sources': None,
                'latency_ms': (time.time() - start_time) * 1000
            }
        else:
            # Basse confiance → RAG
            similar_docs = self.search_similar(query, top_k=self.config['top_k'])
            best_similarity = max([doc['similarity'] for doc in similar_docs])
            
            if best_similarity >= self.config['similarity_threshold']:
                # Bon match RAG
                answer = similar_docs[0]['answer']
                
                response = {
                    'answer': answer,
                    'method': 'rag_retrieval',
                    'confidence': best_similarity,
                    'intent': intent,
                    'sources': similar_docs,
                    'latency_ms': (time.time() - start_time) * 1000
                }
            else:
                # Fallback
                answer = f"""Je ne suis pas certain de bien comprendre votre question.

**Voici ce qui pourrait vous aider :**

{similar_docs[0]['answer'][:200]}...

📞 **Pour plus d'informations** :
- Email : info@um5.ac.ma
- Téléphone : +212 5XX-XX-XX-XX"""
                
                response = {
                    'answer': answer,
                    'method': 'fallback',
                    'confidence': best_similarity,
                    'intent': intent,
                    'sources': similar_docs,
                    'latency_ms': (time.time() - start_time) * 1000
                }
        
        return response

# ============================================================================
# APPLICATION FASTAPI
# ============================================================================

app = FastAPI(
    title="UM5 Hybrid Chatbot API",
    description="API de démonstration pour le chatbot universitaire UM5",
    version="1.0.0"
)

# CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le chatbot (global)
chatbot = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global chatbot
    chatbot = HybridChatbot(CONFIG)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec interface de chat"""
    with open('static/index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": chatbot is not None,
        "device": str(chatbot.device) if chatbot else "N/A"
    }

@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """Endpoint principal de chat"""
    try:
        if not chatbot:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        
        # Traiter la requête
        response = chatbot.process_query(request.message)
        
        return QueryResponse(**response)
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Statistiques du modèle"""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    return {
        "model_info": {
            "intent_model": "XLM-RoBERTa-base",
            "embedding_model": "MPNet-Base-V2",
            "knowledge_base_size": len(chatbot.knowledge_base),
            "device": str(chatbot.device)
        },
        "thresholds": {
            "intent_confidence": CONFIG['intent_threshold'],
            "similarity": CONFIG['similarity_threshold']
        }
    }

# Monter les fichiers statiques
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    logger.warning("Static directory not found")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("🚀 Démarrage du serveur UM5 Chatbot")
    print("="*70)
    print("\n📍 URL : http://localhost:8000")
    print("📍 API Docs : http://localhost:8000/docs")
    print("\n⏹️  Arrêter : Ctrl+C\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
