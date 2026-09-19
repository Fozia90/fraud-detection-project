import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

print("📊 Chargement des données...")
df = pd.read_csv('transactions.csv')

# --- Feature Engineering ---
# Encodage des variables catégorielles
le_pays_carte = LabelEncoder()
le_pays_ip = LabelEncoder()
le_type = LabelEncoder()

df['pays_carte_enc'] = le_pays_carte.fit_transform(df['pays_carte'])
df['pays_ip_enc'] = le_pays_ip.fit_transform(df['pays_ip'])
df['type_marchand_enc'] = le_type.fit_transform(df['type_marchand'])

# Features dérivées
df['pays_different'] = (df['pays_carte'] != df['pays_ip']).astype(int)
df['montant_log'] = np.log1p(df['montant'])
df['heure_suspecte'] = df['heure'].apply(lambda h: 1 if h in [1,2,3,4,5,23] else 0)

# Colonnes finales pour le modèle
FEATURES = [
    'montant', 'montant_log', 'heure', 'heure_suspecte',
    'pays_carte_enc', 'pays_ip_enc', 'type_marchand_enc',
    'pays_different', 'nb_tentatives', 'anciennete_client_jours',
    'distance_km', 'utilisation_vpn'
]

X = df[FEATURES]
y = df['is_fraud']

# --- Split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Entraînement ---
print("🤖 Entraînement du Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=12,
    class_weight='balanced',  # Important : gérer le déséquilibre
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# --- Évaluation ---
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n📈 Résultats :")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraude']))
print(f"AUC-ROC : {roc_auc_score(y_test, y_proba):.4f}")
print(f"\nMatrice de confusion :\n{confusion_matrix(y_test, y_pred)}")

# --- Sauvegarde ---
joblib.dump(model, 'fraud_model.pkl')
joblib.dump({
    'le_pays_carte': le_pays_carte,
    'le_pays_ip': le_pays_ip,
    'le_type': le_type,
    'features': FEATURES
}, 'encoders.pkl')

print("\n✅ Modèle sauvegardé : fraud_model.pkl")
print("✅ Encodeurs sauvegardés : encoders.pkl")