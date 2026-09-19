import joblib
import pandas as pd
import numpy as np
import shap

class FraudDetector:
    def __init__(self):
        self.model = joblib.load('fraud_model.pkl')
        self.encoders = joblib.load('encoders.pkl')
        self.features = self.encoders['features']
        self.explainer = shap.TreeExplainer(self.model)
        print("✅ Modèle et explainer SHAP chargés")

    def _preprocess(self, transaction: dict) -> pd.DataFrame:
        """Transforme une transaction brute en features pour le modèle."""
        df = pd.DataFrame([transaction])
        
        def safe_transform(le, value):
            try:
                return le.transform([value])[0]
            except ValueError:
                return -1
        
        df['pays_carte_enc'] = safe_transform(self.encoders['le_pays_carte'], transaction['pays_carte'])
        df['pays_ip_enc'] = safe_transform(self.encoders['le_pays_ip'], transaction['pays_ip'])
        df['type_marchand_enc'] = safe_transform(self.encoders['le_type'], transaction['type_marchand'])
        
        df['pays_different'] = int(transaction['pays_carte'] != transaction['pays_ip'])
        df['montant_log'] = np.log1p(transaction['montant'])
        df['heure_suspecte'] = int(transaction['heure'] in [1, 2, 3, 4, 5, 23])
        
        return df[self.features]

    def _extract_shap_values(self, shap_values, X):
        """
        Extrait un vecteur 1D de valeurs SHAP pour la classe 'fraude'.
        Gère toutes les formes possibles retournées par SHAP.
        """
        sv = shap_values
        
        # Cas 1 : liste de deux arrays (ancien format binaire)
        if isinstance(sv, list):
            sv = sv[1]  # classe fraude
        
        # Cas 2 : array 3D (nouveau format SHAP >= 0.40)
        if isinstance(sv, np.ndarray) and sv.ndim == 3:
            # shape (n_samples, n_features, n_classes) -> on prend la classe 1
            sv = sv[:, :, 1]
        
        # Cas 3 : array 2D (n_samples, n_features) -> on prend la première ligne
        if isinstance(sv, np.ndarray) and sv.ndim == 2:
            sv = sv[0]
        
        # Maintenant sv doit être 1D de longueur = nombre de features
        sv = np.array(sv).flatten()
        
        # Sécurité : s'assurer que la taille correspond
        if len(sv) != len(self.features):
            raise ValueError(
                f"Taille SHAP ({len(sv)}) != nombre de features ({len(self.features)})"
            )
        
        return sv

    def predict(self, transaction: dict) -> dict:
        """Prédit le score de fraude et génère les explications SHAP."""
        X = self._preprocess(transaction)
        
        # --- Prédiction ---
        proba = float(self.model.predict_proba(X)[0][1])
        is_fraud = proba > 0.5
        
        # --- Explicabilité SHAP ---
        try:
            shap_values = self.explainer.shap_values(X)
            sv = self._extract_shap_values(shap_values, X)
            
            # Créer la liste (feature, impact) et trier
            feature_importance = list(zip(self.features, [float(v) for v in sv]))
            feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            
        except Exception as e:
            print(f"⚠️ Erreur SHAP : {e}")
            feature_importance = [(f, 0.0) for f in self.features]
        
        # --- Explications lisibles ---
        explanations = self._generate_explanations(
            transaction, feature_importance[:5]
        )
        
        return {
            'score_risque': proba,
            'est_fraude': is_fraud,
            'explications': explanations,
            'top_features': [
                {'feature': f, 'impact': v}
                for f, v in feature_importance[:5]
            ]
        }
    
    def _generate_explanations(self, transaction, top_features):
        """Convertit les valeurs SHAP en phrases lisibles."""
        explications = []
        labels = {
            'montant': 'Montant de la transaction',
            'montant_log': 'Montant (log)',
            'heure': 'Heure de la transaction',
            'heure_suspecte': 'Heure suspecte (nuit)',
            'pays_carte_enc': 'Pays de la carte',
            'pays_ip_enc': 'Pays de l\'IP',
            'type_marchand_enc': 'Type de marchand',
            'pays_different': 'Incohérence pays carte/IP',
            'nb_tentatives': 'Nombre de tentatives',
            'anciennete_client_jours': 'Ancienneté du client',
            'distance_km': 'Distance géographique',
            'utilisation_vpn': 'Utilisation d\'un VPN'
        }
        
        for feature, impact in top_features:
            if abs(impact) < 0.01:
                continue
            direction = "augmente" if impact > 0 else "diminue"
            signe = "🔴" if impact > 0 else "🟢"
            label = labels.get(feature, feature)
            explications.append(
                f"{signe} {label} {direction} le risque (impact: {impact:+.3f})"
            )
        
        if not explications:
            explications.append("✅ Aucun facteur de risque significatif détecté")
        
        return explications


# Instance globale
detector = FraudDetector()