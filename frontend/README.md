# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.


## 🚀 Fonctionnalités

- **4 Modèles ML comparés** : Random Forest, XGBoost, SVM, Logistic Regression.
- **Sélection automatique** du meilleur modèle basé sur l'AUC-ROC.
- **Explicabilité SHAP** : chaque décision est justifiée (pourquoi c'est une fraude).
- **API Sécurisée** : FastAPI avec validation Pydantic et clé API.
- **Interface React** : Design sombre et tableau de bord des performances.

## 🏗️ Architecture

- **Backend** : Python, FastAPI, Scikit-Learn, XGBoost, SHAP.
- **Frontend** : React, Vite, Tailwind CSS, Axios.
- **Données** : Génération synthétique de 50 000 transactions (Faker + NumPy).