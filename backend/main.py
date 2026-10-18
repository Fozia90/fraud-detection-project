from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime
from ml_service import detector  # <-- L'import crucial
import os
import pandas as pd
import time
import logging

# --- Configuration du logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud-api")

app = FastAPI(
    title="API Détection de Fraude IA",
    version="2.0.0",
    description="API de détection de fraude e-commerce basée sur le Machine Learning et l'explicabilité SHAP",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEYS = {
    "demo-key-12345": "client_demo",
    "admin-key-67890": "client_admin"
}

async def verify_api_key(x_api_key: str = Header(..., description="Clé API du client")):
    if x_api_key not in API_KEYS:
        logger.warning(f"Tentative d'accès avec clé invalide : {x_api_key[:8]}...")
        raise HTTPException(status_code=401, detail="API Key invalide ou manquante")
    return API_KEYS[x_api_key]


# --- Modèles Pydantic ---
class Transaction(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "montant": 3500, "pays_carte": "FR", "pays_ip": "NG",
                "heure": 3, "type_marchand": "Crypto", "nb_tentatives": 4,
                "anciennete_client_jours": 5, "distance_km": 5000, "utilisation_vpn": True
            }
        }
    )
    montant: float = Field(..., gt=0)
    pays_carte: str = Field(..., min_length=2, max_length=2)
    pays_ip: str = Field(..., min_length=2, max_length=2)
    heure: int = Field(..., ge=0, le=23)
    type_marchand: str
    nb_tentatives: int = Field(default=1, ge=1, le=20)
    anciennete_client_jours: int = Field(default=365, ge=0)
    distance_km: float = Field(default=0, ge=0)
    utilisation_vpn: bool = Field(default=False)


class TopFeature(BaseModel):
    feature: str
    impact: float


class ReponseFraude(BaseModel):
    transaction_id: str
    timestamp: str
    score_risque: float = Field(..., ge=0, le=1)
    est_fraude: bool
    niveau_risque: str
    explications: List[str]
    top_features: List[TopFeature]


def get_niveau_risque(score: float) -> str:
    if score < 0.3:
        return "faible"
    elif score < 0.6:
        return "moyen"
    return "élevé"


# ==========================================
# ENDPOINTS DE BASE
# ==========================================

@app.get("/")
def root():
    return {"message": "API Détection de Fraude v2.0", "status": "ok"}


@app.get("/api/v1/health")
def health():
    try:
        model_ok = detector.model is not None
        return {
            "status": "healthy" if model_ok else "degraded",
            "model_loaded": model_ok,
            "best_model": detector.best_model_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service indisponible : {str(e)}")


@app.get("/api/v1/verify-key")
def verify_key(client: str = Depends(verify_api_key)):
    return {"valid": True, "client": client}


@app.post("/api/v1/predict", response_model=ReponseFraude)
async def analyser_transaction(transaction: Transaction, client: str = Depends(verify_api_key)):
    transaction_id = f"TRX-{int(time.time() * 1000)}"
    
    try:
        result = detector.predict(transaction.model_dump())
        
        return ReponseFraude(
            transaction_id=transaction_id,
            timestamp=datetime.utcnow().isoformat(),
            score_risque=result["score_risque"],
            est_fraude=result["est_fraude"],
            niveau_risque=get_niveau_risque(result["score_risque"]),
            explications=result["explications"],
            top_features=[TopFeature(**f) for f in result["top_features"]]
        )
    except Exception as e:
        logger.error(f"[{transaction_id}] Erreur : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")


# ==========================================
# ENDPOINTS POUR LES MODÈLES (NOUVEAU)
# ==========================================

@app.get("/api/v1/models/comparison", tags=["Modèles"])
def get_models_comparison():
    """Retourne le tableau comparatif des 4 modèles."""
    csv_path = os.path.join("models", "comparaison_modeles.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Aucune comparaison disponible. Lancez train_models.py")
    
    df = pd.read_csv(csv_path)
    return {
        "modeles": df.to_dict(orient="records"),
        "meilleur_modele": detector.best_model_name,
        "modele_en_production": detector.best_model_name,
    }

@app.get("/api/v1/models/available", tags=["Modèles"])
def list_models():
    """Liste tous les modèles entraînés et disponibles."""
    models_dir = "models"
    if not os.path.exists(models_dir):
        return {"modeles": []}
    
    fichiers = [f for f in os.listdir(models_dir) if f.endswith('.pkl') and f not in ['encoders.pkl', 'scaler.pkl']]
    return {
        "modeles": [f.replace('.pkl', '') for f in fichiers],
        "en_production": detector.best_model_name,
    }