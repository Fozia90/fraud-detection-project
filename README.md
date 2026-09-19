# 🛡️ Détection de Fraude E-commerce par IA

Système complet de détection de fraude en ligne combinant **Machine Learning** (Random Forest) et **explicabilité** (SHAP), exposé via une **API sécurisée** (FastAPI) avec une interface **React**.

---

## 🎯 Fonctionnalités

- ✅ Détection automatique de fraude par Random Forest
- ✅ Score de risque entre 0 et 1
- ✅ Explicabilité des décisions via SHAP
- ✅ API sécurisée (clé API + validation Pydantic)
- ✅ Interface web interactive (React + Tailwind)
- ✅ Analyse par lot (batch de 100 transactions)

---

## 🏗️ Architecture

│ Frontend │ ─────────► │ Backend │ ─────────────► │ Modèle ML │
│ React+Vite │ │ FastAPI │ │ + SHAP │