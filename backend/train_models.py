"""
Entraîne 4 modèles de détection de fraude :
- Random Forest
- XGBoost
- SVM
- Logistic Regression

Compare leurs performances et sauvegarde le meilleur.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
import time
from tabulate import tabulate

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix,
    precision_score, recall_score, f1_score, accuracy_score
)
from xgboost import XGBClassifier

# =========================================================
# CONFIGURATION
# =========================================================
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

RANDOM_STATE = 42


def titre(emoji, texte):
    print("\n" + "=" * 70)
    print(f"{emoji}  {texte}")
    print("=" * 70)


# =========================================================
# 1. CHARGEMENT DES DONNÉES
# =========================================================
titre("📊", "CHARGEMENT DES DONNÉES")

df = pd.read_csv('transactions.csv')
print(f"   Nombre de transactions : {len(df):,}")
print(f"   Fraudes                : {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.2f}%)")


# =========================================================
# 2. FEATURE ENGINEERING
# =========================================================
titre("🧬", "FEATURE ENGINEERING")

# Encodage
le_pays_carte = LabelEncoder()
le_pays_ip = LabelEncoder()
le_type = LabelEncoder()

df['pays_carte_enc'] = le_pays_carte.fit_transform(df['pays_carte'])
df['pays_ip_enc'] = le_pays_ip.fit_transform(df['pays_ip'])
df['type_marchand_enc'] = le_type.fit_transform(df['type_marchand'])

# Variables dérivées
df['pays_different'] = (df['pays_carte'] != df['pays_ip']).astype(int)
df['montant_log'] = np.log1p(df['montant'])
df['heure_suspecte'] = df['heure'].apply(lambda h: 1 if h in [1, 2, 3, 4, 5, 23] else 0)

FEATURES = [
    'montant', 'montant_log', 'heure', 'heure_suspecte',
    'pays_carte_enc', 'pays_ip_enc', 'type_marchand_enc',
    'pays_different', 'nb_tentatives', 'anciennete_client_jours',
    'distance_km', 'utilisation_vpn'
]

X = df[FEATURES]
y = df['is_fraud']

print(f"   {len(FEATURES)} features utilisées")
print(f"   Features : {FEATURES}")


# =========================================================
# 3. SPLIT TRAIN / TEST
# =========================================================
titre("✂️", "SPLIT TRAIN / TEST (80% / 20%)")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"   Train : {len(X_train):,} transactions")
print(f"   Test  : {len(X_test):,} transactions")


# =========================================================
# 4. NORMALISATION (nécessaire pour SVM et LogReg)
# =========================================================
titre("📏", "NORMALISATION (StandardScaler)")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("   Moyenne  ≈ 0")
print("   Écart-type ≈ 1")
print("   (Requis pour SVM et Logistic Regression)")


# =========================================================
# 5. DÉFINITION DES 4 MODÈLES
# =========================================================
titre("🤖", "DÉFINITION DES MODÈLES")

models = {
    "Random Forest": {
        "instance": RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            class_weight='balanced',
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        "use_scaled": False,   # Random Forest n'a pas besoin de normalisation
    },
    "XGBoost": {
        "instance": XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=49,   # Ratio normal/fraude ≈ 49
            random_state=RANDOM_STATE,
            eval_metric='logloss',
            n_jobs=-1
        ),
        "use_scaled": False,   # XGBoost gère bien les données non normalisées
    },
    "SVM": {
        "instance": SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            class_weight='balanced',
            probability=True,      # Nécessaire pour predict_proba
            random_state=RANDOM_STATE
        ),
        "use_scaled": True,    # ⚠️ SVM EXIGE la normalisation
    },
    "Logistic Regression": {
        "instance": LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        "use_scaled": True,    # ⚠️ LogReg préfère la normalisation
    },
}

for name, config in models.items():
    print(f"   ✅ {name:25s} → normalisation : {config['use_scaled']}")


# =========================================================
# 6. ENTRAÎNEMENT & ÉVALUATION
# =========================================================
titre("🚀", "ENTRAÎNEMENT DES 4 MODÈLES")

resultats = []

for name, config in models.items():
    print(f"\n   ▶️  Entraînement : {name}...")

    # Choisir les données (normalisées ou pas)
    if config["use_scaled"]:
        X_tr, X_te = X_train_scaled, X_test_scaled
    else:
        X_tr, X_te = X_train, X_test

    # Entraînement
    start = time.time()
    model = config["instance"]
    model.fit(X_tr, y_train)
    train_time = time.time() - start

    # Prédiction
    y_pred = model.predict(X_te)
    y_proba = model.predict_proba(X_te)[:, 1]

    # Métriques
    metrics = {
        "Modèle": name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-Score": f1_score(y_test, y_pred),
        "AUC-ROC": roc_auc_score(y_test, y_proba),
        "Temps (s)": train_time,
    }
    resultats.append(metrics)

    print(f"      ✅ Terminé en {train_time:.2f}s")
    print(f"      AUC-ROC : {metrics['AUC-ROC']:.4f}")
    print(f"      Recall  : {metrics['Recall']:.4f}")

    # Sauvegarder le modèle
    filename = name.lower().replace(" ", "_") + ".pkl"
    filepath = os.path.join(MODELS_DIR, filename)
    joblib.dump(model, filepath)
    print(f"      💾 Sauvegardé : {filepath}")


# =========================================================
# 7. TABLEAU COMPARATIF
# =========================================================
titre("📊", "COMPARAISON DES 4 MODÈLES")

# Convertir en DataFrame pour un joli affichage
df_resultats = pd.DataFrame(resultats)

# Trier par AUC-ROC décroissant
df_resultats = df_resultats.sort_values("AUC-ROC", ascending=False).reset_index(drop=True)

# Afficher le tableau
print("\n" + tabulate(
    df_resultats,
    headers='keys',
    tablefmt='fancy_grid',
    floatfmt=".4f",
    showindex=False
))

# Sauvegarder en CSV
df_resultats.to_csv(os.path.join(MODELS_DIR, "comparaison_modeles.csv"), index=False)
print(f"\n   💾 Tableau sauvegardé : {MODELS_DIR}/comparaison_modeles.csv")


# =========================================================
# 8. SÉLECTION DU MEILLEUR MODÈLE
# =========================================================
titre("🏆", "SÉLECTION DU MEILLEUR MODÈLE")

best_model_name = df_resultats.iloc[0]["Modèle"]
best_auc = df_resultats.iloc[0]["AUC-ROC"]
best_recall = df_resultats.iloc[0]["Recall"]

print(f"   🥇 Meilleur modèle : {best_model_name}")
print(f"   AUC-ROC : {best_auc:.4f}")
print(f"   Recall  : {best_recall:.4f}")

# Sauvegarder le nom du meilleur modèle
with open(os.path.join(MODELS_DIR, "best_model.txt"), "w") as f:
    f.write(best_model_name)

# Sauvegarder les encodeurs et le scaler
joblib.dump({
    'le_pays_carte': le_pays_carte,
    'le_pays_ip': le_pays_ip,
    'le_type': le_type,
    'features': FEATURES,
    'scaler': scaler,
    'best_model_name': best_model_name,
    'use_scaled': models[best_model_name]['use_scaled'],
}, os.path.join(MODELS_DIR, "encoders.pkl"))

print(f"   💾 Encodeurs sauvegardés : {MODELS_DIR}/encoders.pkl")
print(f"   💾 Nom du meilleur modèle : {MODELS_DIR}/best_model.txt")


# =========================================================
# 9. RAPPORT DÉTAILLÉ DU MEILLEUR MODÈLE
# =========================================================
titre(f"📋", f"RAPPORT DÉTAILLÉ — {best_model_name}")

# Recharger le meilleur modèle pour le rapport
best_model = joblib.load(
    os.path.join(MODELS_DIR, best_model_name.lower().replace(" ", "_") + ".pkl")
)

# Utiliser les bonnes données (scaled ou pas)
if models[best_model_name]["use_scaled"]:
    X_te_best = X_test_scaled
else:
    X_te_best = X_test

y_pred_best = best_model.predict(X_te_best)

print("\n📊 Rapport de classification :")
print(classification_report(y_test, y_pred_best, target_names=['Normal', 'Fraude']))

print("\n📊 Matrice de confusion :")
cm = confusion_matrix(y_test, y_pred_best)
print(tabulate(
    [
        ["Vrais Négatifs (TN)", "Faux Positifs (FP)"],
        [cm[0][0], cm[0][1]],
    ],
    tablefmt='fancy_grid'
))
print(tabulate(
    [
        ["Faux Négatifs (FN)", "Vrais Positifs (TP)"],
        [cm[1][0], cm[1][1]],
    ],
    tablefmt='fancy_grid'
))


# =========================================================
# 10. RÉSUMÉ FINAL
# =========================================================
titre("✅", "ENTRAÎNEMENT TERMINÉ")

print(f"""
   📁 Modèles sauvegardés dans : {MODELS_DIR}/
       ├── random_forest.pkl
       ├── xgboost.pkl
       ├── svm.pkl
       ├── logistic_regression.pkl
       ├── scaler.pkl (dans encoders.pkl)
       ├── encoders.pkl
       ├── best_model.txt ({best_model_name})
       └── comparaison_modeles.csv

   🏆 Meilleur modèle : {best_model_name}
   📈 AUC-ROC : {best_auc:.4f}
   📈 Recall  : {best_recall:.4f}

   ➡️  Prochaine étape : lancer uvicorn main:app --reload
""")