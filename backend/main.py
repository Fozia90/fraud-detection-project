from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from ml_service import detector
import time
import logging

# --- Configuration du logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud-api")

# --- Initialisation de l'app ---
app = FastAPI(
    title="API Détection de Fraude IA",
    version="2.0.0",
    description="API de détection de fraude e-commerce basée sur le Machine Learning et l'explicabilité SHAP",
    contact={"name": "Équipe Data Science"}
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentification simple par API Key ---
API_KEYS = {
    "demo-key-12345": "client_demo",
    "admin-key-67890": "client_admin"
}

async def verify_api_key(x_api_key: str = Header(..., description="Clé API du client")):
    if x_api_key not in API_KEYS:
        logger.warning(f"Tentative d'accès avec clé invalide : {x_api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="API Key invalide ou manquante"
        )
    return API_KEYS[x_api_key]


# --- Modèles Pydantic ---
class Transaction(BaseModel):
    """Représente une transaction e-commerce à analyser."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "montant": 3500,
                "pays_carte": "FR",
                "pays_ip": "NG",
                "heure": 3,
                "type_marchand": "Crypto",
                "nb_tentatives": 4,
                "anciennete_client_jours": 5,
                "distance_km": 5000,
                "utilisation_vpn": True
            }
        }
    )
    
    montant: float = Field(..., gt=0, description="Montant de la transaction en euros")
    pays_carte: str = Field(..., min_length=2, max_length=2, description="Code ISO du pays de la carte (ex: FR)")
    pays_ip: str = Field(..., min_length=2, max_length=2, description="Code ISO du pays de l'IP (ex: NG)")
    heure: int = Field(..., ge=0, le=23, description="Heure de la transaction (0-23)")
    type_marchand: str = Field(..., description="Catégorie du marchand")
    nb_tentatives: int = Field(default=1, ge=1, le=20, description="Nombre de tentatives de paiement")
    anciennete_client_jours: int = Field(default=365, ge=0, description="Ancienneté du client en jours")
    distance_km: float = Field(default=0, ge=0, description="Distance entre IP et adresse de facturation")
    utilisation_vpn: bool = Field(default=False, description="Le client utilise-t-il un VPN ?")


class TopFeature(BaseModel):
    """Feature avec son impact SHAP."""
    feature: str
    impact: float


class ReponseFraude(BaseModel):
    """Réponse de l'API d'analyse de fraude."""
    transaction_id: str
    timestamp: str
    score_risque: float = Field(..., ge=0, le=1, description="Score de risque entre 0 et 1")
    est_fraude: bool
    niveau_risque: str = Field(..., description="Niveau : faible, moyen ou élevé")
    explications: List[str]
    top_features: List[TopFeature]


# --- Fonctions utilitaires ---
def get_niveau_risque(score: float) -> str:
    """Détermine le niveau de risque en fonction du score."""
    if score < 0.3:
        return "faible"
    elif score < 0.6:
        return "moyen"
    return "élevé"


# --- Endpoints ---

@app.get("/", tags=["Général"])
def root():
    """Point d'entrée de l'API."""
    return {
        "message": "API Détection de Fraude v2.0",
        "status": "ok",
        "documentation": "/docs"
    }


@app.get("/api/v1/health", tags=["Général"])
def health():
    """Vérifie l'état de santé de l'API et du modèle."""
    try:
        # Vérifier que le modèle est bien chargé
        model_ok = detector.model is not None
        return {
            "status": "healthy" if model_ok else "degraded",
            "model_loaded": model_ok,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service indisponible : {str(e)}")


@app.get("/api/v1/verify-key", tags=["Authentification"])
def verify_key(client: str = Depends(verify_api_key)):
    """Vérifie que la clé API est valide."""
    return {"valid": True, "client": client}


@app.post("/api/v1/predict", response_model=ReponseFraude, tags=["Prédiction"])
async def analyser_transaction(
    transaction: Transaction,
    request: Request,
    client: str = Depends(verify_api_key)
):
    """
    Analyse une transaction e-commerce et retourne :
    
    - **score_risque** : Probabilité de fraude (0 à 1)
    - **est_fraude** : Décision binaire (True si score > 0.5)
    - **niveau_risque** : Faible, moyen ou élevé
    - **explications** : Raisons lisibles de la décision (SHAP)
    - **top_features** : Détails techniques des impacts SHAP
    """
    transaction_id = f"TRX-{int(time.time() * 1000)}"
    
    logger.info(
        f"[{transaction_id}] Analyse - Client: {client} | "
        f"Montant: {transaction.montant}€ | "
        f"Pays carte: {transaction.pays_carte} → IP: {transaction.pays_ip}"
    )
    
    try:
        # Prédiction via le service ML
        result = detector.predict(transaction.model_dump())
        
        # Enrichissement de la réponse
        response = ReponseFraude(
            transaction_id=transaction_id,
            timestamp=datetime.utcnow().isoformat(),
            score_risque=result["score_risque"],
            est_fraude=result["est_fraude"],
            niveau_risque=get_niveau_risque(result["score_risque"]),
            explications=result["explications"],
            top_features=[
                TopFeature(feature=f["feature"], impact=f["impact"])
                for f in result["top_features"]
            ]
        )
        
        logger.info(
            f"[{transaction_id}] Résultat - Score: {response.score_risque:.3f} | "
            f"Fraude: {response.est_fraude} | Niveau: {response.niveau_risque}"
        )
        
        return response
        
    except KeyError as e:
        logger.error(f"[{transaction_id}] Erreur de données : {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Donnée manquante ou invalide : {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{transaction_id}] Erreur serveur : {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse : {str(e)}"
        )


# --- Endpoint bonus : analyse par lot (batch) ---
@app.post("/api/v1/predict/batch", tags=["Prédiction"])
async def analyser_batch(
    transactions: List[Transaction],
    client: str = Depends(verify_api_key)
):
    """
    Analyse plusieurs transactions en une seule requête.
    Limité à 100 transactions par appel.
    """
    if len(transactions) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 transactions par requête"
        )
    
    resultats = []
    for i, tx in enumerate(transactions):
        try:
            result = detector.predict(tx.model_dump())
            resultats.append({
                "index": i,
                "transaction_id": f"TRX-{int(time.time() * 1000)}-{i}",
                "score_risque": result["score_risque"],
                "est_fraude": result["est_fraude"],
                "niveau_risque": get_niveau_risque(result["score_risque"]),
                "explications": result["explications"]
            })
        except Exception as e:
            resultats.append({
                "index": i,
                "erreur": str(e)
            })
    
    return {
        "total": len(transactions),
        "analyses": resultats
    }