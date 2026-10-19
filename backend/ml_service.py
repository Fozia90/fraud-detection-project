# import os
# import joblib
# import pandas as pd
# import numpy as np
# import shap

# MODELS_DIR = "models"


# class FraudDetector:
#     def __init__(self):
#         # Charger les encodeurs et métadonnées
#         encoders = joblib.load(os.path.join(MODELS_DIR, "encoders.pkl"))
#         self.encoders = encoders
#         self.le_pays_carte = encoders['le_pays_carte']
#         self.le_pays_ip = encoders['le_pays_ip']
#         self.le_type = encoders['le_type']
#         self.features = encoders['features']
#         self.scaler = encoders['scaler']
#         self.best_model_name = encoders['best_model_name']
#         self.use_scaled = encoders['use_scaled']

#         # Charger le meilleur modèle
#         filename = self.best_model_name.lower().replace(" ", "_") + ".pkl"
#         self.model = joblib.load(os.path.join(MODELS_DIR, filename))

#         print(f"✅ Modèle chargé : {self.best_model_name}")
#         print(f"   Normalisation : {'OUI' if self.use_scaled else 'NON'}")

#         # SHAP uniquement pour les modèles basés sur les arbres
#         self.supports_shap = self.best_model_name in ["Random Forest", "XGBoost"]
#         if self.supports_shap:
#             try:
#                 self.explainer = shap.TreeExplainer(self.model)
#                 print("   ✅ Explicabilité SHAP activée")
#             except Exception as e:
#                 print(f"   ⚠️ SHAP désactivé : {e}")
#                 self.supports_shap = False
#         else:
#             print(f"   ⚠️ SHAP non supporté pour {self.best_model_name}")

#     def _preprocess(self, transaction: dict) -> pd.DataFrame:
#         """Transforme une transaction brute en features."""

#         titre("📥", "ÉTAPE 1 — DONNÉE BRUTE")
#         for k, v in transaction.items():
#             print(f"   {k:30s} = {v}")

#         df = pd.DataFrame([transaction])

#         # Encodage
#         titre("🔄", "ÉTAPE 2 — ENCODAGE")
#         def safe_transform(le, value, nom):
#             try:
#                 r = le.transform([value])[0]
#                 print(f"   {nom:25s} '{value}' → {r}")
#                 return r
#             except ValueError:
#                 print(f"   {nom:25s} '{value}' → -1 (inconnu)")
#                 return -1

#         df['pays_carte_enc'] = safe_transform(self.le_pays_carte, transaction['pays_carte'], "pays_carte")
#         df['pays_ip_enc'] = safe_transform(self.le_pays_ip, transaction['pays_ip'], "pays_ip")
#         df['type_marchand_enc'] = safe_transform(self.le_type, transaction['type_marchand'], "type_marchand")

#         # Feature engineering
#         titre("🧬", "ÉTAPE 3 — FEATURE ENGINEERING")
#         df['pays_different'] = int(transaction['pays_carte'] != transaction['pays_ip'])
#         df['montant_log'] = np.log1p(transaction['montant'])
#         df['heure_suspecte'] = int(transaction['heure'] in [1, 2, 3, 4, 5, 23])
#         print(f"   pays_different  = {df['pays_different'][0]}")
#         print(f"   montant_log     = {df['montant_log'][0]:.4f}")
#         print(f"   heure_suspecte  = {df['heure_suspecte'][0]}")

#         # Vecteur final
#         X = df[self.features]
#         titre("🎯", "ÉTAPE 4 — VECTEUR FINAL")
#         print(f"   {X.values[0].tolist()}")

#         # Normalisation si nécessaire
#         if self.use_scaled:
#             titre("📏", "ÉTAPE 5 — NORMALISATION (StandardScaler)")
#             X_scaled = self.scaler.transform(X)
#             X = pd.DataFrame(X_scaled, columns=self.features)
#             print(f"   Vecteur normalisé : {X.values[0].tolist()}")

#         return X

#     def predict(self, transaction: dict) -> dict:
#         X = self._preprocess(transaction)

#         # Prédiction
#         titre("🧠", f"PRÉDICTION — {self.best_model_name}")
#         proba = float(self.model.predict_proba(X)[0][1])
#         is_fraud = proba > 0.5
#         print(f"   Score : {proba:.4f} ({proba*100:.2f}%)")
#         print(f"   Décision : {'🚨 FRAUDE' if is_fraud else '✅ SÛRE'}")

#         # SHAP (si supporté)
#         feature_importance = [(f, 0.0) for f in self.features]

#         if self.supports_shap:
#             titre("🔍", "EXPLICABILITÉ (SHAP)")
#             try:
#                 shap_values = self.explainer.shap_values(X)
#                 sv = shap_values
#                 if isinstance(sv, list):
#                     sv = sv[1]
#                 if isinstance(sv, np.ndarray) and sv.ndim == 3:
#                     sv = sv[:, :, 1]
#                 if isinstance(sv, np.ndarray) and sv.ndim == 2:
#                     sv = sv[0]
#                 sv = np.array(sv).flatten()

#                 feature_importance = list(zip(self.features, [float(v) for v in sv]))
#                 feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)

#                 for f, v in feature_importance[:5]:
#                     signe = "🔴" if v > 0 else "🟢"
#                     print(f"   {signe}  {f:28s} : {v:+.4f}")
#             except Exception as e:
#                 print(f"   ⚠️ Erreur SHAP : {e}")

#         # Explications
#         titre("📝", "EXPLICATIONS LISIBLES")
#         explanations = self._generate_explanations(feature_importance[:5])
#         for e in explanations:
#             print(f"   {e}")

#         return {
#             'score_risque': proba,
#             'est_fraude': is_fraud,
#             'explications': explanations,
#             'top_features': [
#                 {'feature': f, 'impact': v}
#                 for f, v in feature_importance[:5]
#             ]
#         }

#     def _generate_explanations(self, top_features):
#         labels = {
#             'montant': 'Montant',
#             'montant_log': 'Montant (log)',
#             'heure': 'Heure',
#             'heure_suspecte': 'Heure suspecte',
#             'pays_carte_enc': 'Pays carte',
#             'pays_ip_enc': 'Pays IP',
#             'type_marchand_enc': 'Type marchand',
#             'pays_different': 'Incohérence pays',
#             'nb_tentatives': 'Tentatives',
#             'anciennete_client_jours': 'Ancienneté client',
#             'distance_km': 'Distance',
#             'utilisation_vpn': 'VPN'
#         }
#         explications = []
#         for feature, impact in top_features:
#             if abs(impact) < 0.01:
#                 continue
#             direction = "augmente" if impact > 0 else "diminue"
#             signe = "🔴" if impact > 0 else "🟢"
#             label = labels.get(feature, feature)
#             explications.append(f"{signe} {label} {direction} le risque ({impact:+.3f})")

#         if not explications:
#             explications.append("✅ Aucun facteur de risque significatif")

#         return explications


# def titre(emoji, texte):
#     print("\n" + "=" * 60)
#     print(f"{emoji}  {texte}")
#     print("=" * 60)


# detector = FraudDetector()


import os
import joblib
import pandas as pd
import numpy as np
import shap

MODELS_DIR = "models"

def titre(emoji, texte):
    print("\n" + "=" * 60)
    print(f"{emoji}  {texte}")
    print("=" * 60)

class FraudDetector:
    def __init__(self):
        # 1. Charger les encodeurs et le scaler
        encoders_path = os.path.join(MODELS_DIR, "encoders.pkl")
        if not os.path.exists(encoders_path):
            raise FileNotFoundError("Fichier encoders.pkl introuvable. Avez-vous lancé train_models.py ?")
        
        encoders = joblib.load(encoders_path)
        self.le_pays_carte = encoders['le_pays_carte']
        self.le_pays_ip = encoders['le_pays_ip']
        self.le_type = encoders['le_type']
        self.features = encoders['features']
        self.scaler = encoders['scaler']
        self.best_model_name = encoders['best_model_name']
        self.use_scaled = encoders['use_scaled']

        # 2. Charger UNIQUEMENT le meilleur modèle (Économie de RAM)
        filename = self.best_model_name.lower().replace(" ", "_") + ".pkl"
        model_path = os.path.join(MODELS_DIR, filename)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle {filename} introuvable.")
            
        self.model = joblib.load(model_path)

        print(f"✅ Modèle chargé : {self.best_model_name}")
        print(f"   Normalisation : {'OUI' if self.use_scaled else 'NON'}")

        # 3. SHAP (Uniquement si c'est un modèle à base d'arbres)
        self.supports_shap = self.best_model_name in ["Random Forest", "XGBoost"]
        if self.supports_shap:
            try:
                self.explainer = shap.TreeExplainer(self.model)
                print("   ✅ Explicabilité SHAP activée")
            except Exception as e:
                print(f"   ⚠️ SHAP désactivé (erreur) : {e}")
                self.supports_shap = False
        else:
            print(f"   ⚠️ SHAP non supporté pour {self.best_model_name}")

    def _preprocess(self, transaction: dict) -> pd.DataFrame:
        """Transforme une transaction brute en features."""
        df = pd.DataFrame([transaction])

        # Encodage sécurisé
        def safe_transform(le, value):
            try:
                return le.transform([value])[0]
            except ValueError:
                return -1

        df['pays_carte_enc'] = safe_transform(self.le_pays_carte, transaction['pays_carte'])
        df['pays_ip_enc'] = safe_transform(self.le_pays_ip, transaction['pays_ip'])
        df['type_marchand_enc'] = safe_transform(self.le_type, transaction['type_marchand'])

        # Feature engineering
        df['pays_different'] = int(transaction['pays_carte'] != transaction['pays_ip'])
        df['montant_log'] = np.log1p(transaction['montant'])
        df['heure_suspecte'] = int(transaction['heure'] in [1, 2, 3, 4, 5, 23])

        X = df[self.features]

        # Normalisation si nécessaire
        if self.use_scaled:
            X_scaled = self.scaler.transform(X)
            X = pd.DataFrame(X_scaled, columns=self.features)

        return X

    def predict(self, transaction: dict) -> dict:
        X = self._preprocess(transaction)

        # 1. Prédiction
        proba = float(self.model.predict_proba(X)[0][1])
        is_fraud = proba > 0.5

        feature_importance = [(f, 0.0) for f in self.features]

        # 2. SHAP
        if self.supports_shap:
            try:
                shap_values = self.explainer.shap_values(X)
                sv = shap_values
                if isinstance(sv, list): sv = sv[1]
                if isinstance(sv, np.ndarray) and sv.ndim == 3: sv = sv[:, :, 1]
                if isinstance(sv, np.ndarray) and sv.ndim == 2: sv = sv[0]
                
                sv = np.array(sv).flatten()
                feature_importance = list(zip(self.features, [float(v) for v in sv]))
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            except Exception as e:
                print(f"⚠️ Erreur SHAP : {e}")

        # 3. Explications lisibles
        explanations = self._generate_explanations(feature_importance[:5])

        return {
            'score_risque': proba,
            'est_fraude': is_fraud,
            'explications': explanations,
            'top_features': [{'feature': f, 'impact': v} for f, v in feature_importance[:5]]
        }

    def _generate_explanations(self, top_features):
        labels = {
            'montant': 'Montant', 'montant_log': 'Montant (log)',
            'heure': 'Heure', 'heure_suspecte': 'Heure suspecte',
            'pays_carte_enc': 'Pays carte', 'pays_ip_enc': 'Pays IP',
            'type_marchand_enc': 'Type marchand', 'pays_different': 'Incohérence pays',
            'nb_tentatives': 'Tentatives', 'anciennete_client_jours': 'Ancienneté client',
            'distance_km': 'Distance', 'utilisation_vpn': 'VPN'
        }
        explications = []
        for feature, impact in top_features:
            if abs(impact) < 0.01: continue
            direction = "augmente" if impact > 0 else "diminue"
            signe = "🔴" if impact > 0 else "🟢"
            label = labels.get(feature, feature)
            explications.append(f"{signe} {label} {direction} le risque ({impact:+.3f})")

        if not explications:
            explications.append("✅ Aucun facteur de risque significatif")
        return explications

# Instance globale (sera chargée une seule fois au démarrage de Render)
detector = FraudDetector()