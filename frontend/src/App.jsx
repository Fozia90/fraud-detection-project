import { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://127.0.0.1:8000/api/v1/predict';
const API_KEY = 'demo-key-12345';

const PAYS = [
  { code: 'FR', nom: 'France' },
  { code: 'US', nom: 'USA' },
  { code: 'GB', nom: 'Royaume-Uni' },
  { code: 'DE', nom: 'Allemagne' },
  { code: 'NG', nom: 'Nigeria' },
  { code: 'RU', nom: 'Russie' },
  { code: 'CN', nom: 'Chine' },
  { code: 'UA', nom: 'Ukraine' },
];

const TYPES_MARCHAND = [
  'Vêtements',
  'Électronique',
  'Crypto',
  'Jeux d\'argent',
  'Alimentation',
  'Voyage',
  'Luxe',
  'Abonnement',
];

function App() {
  const [transaction, setTransaction] = useState({
    montant: 150,
    pays_carte: 'FR',
    pays_ip: 'FR',
    heure: 14,
    type_marchand: 'Vêtements',
    nb_tentatives: 1,
    anciennete_client_jours: 365,
    distance_km: 10,
    utilisation_vpn: false,
  });

  const [resultat, setResultat] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setTransaction({
      ...transaction,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const analyser = async () => {
    setLoading(true);
    setErreur(null);
    setResultat(null);

    try {
      const payload = {
        ...transaction,
        montant: parseFloat(transaction.montant),
        heure: parseInt(transaction.heure),
        nb_tentatives: parseInt(transaction.nb_tentatives),
        anciennete_client_jours: parseInt(transaction.anciennete_client_jours),
        distance_km: parseFloat(transaction.distance_km),
        utilisation_vpn: Boolean(transaction.utilisation_vpn),
      };

      const response = await axios.post(API_URL, payload, {
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': API_KEY,
        },
      });

      setResultat(response.data);
    } catch (error) {
      console.error('Erreur API', error);
      if (error.response) {
        setErreur(`Erreur ${error.response.status} : ${error.response.data.detail || 'Erreur serveur'}`);
      } else {
        setErreur('Impossible de contacter l\'API. Vérifiez que le backend est lancé.');
      }
    }
    setLoading(false);
  };

  const resetForm = () => {
    setTransaction({
      montant: 150,
      pays_carte: 'FR',
      pays_ip: 'FR',
      heure: 14,
      type_marchand: 'Vêtements',
      nb_tentatives: 1,
      anciennete_client_jours: 365,
      distance_km: 10,
      utilisation_vpn: false,
    });
    setResultat(null);
    setErreur(null);
  };

  const chargerExempleFraude = () => {
    setTransaction({
      montant: 3500,
      pays_carte: 'FR',
      pays_ip: 'NG',
      heure: 3,
      type_marchand: 'Crypto',
      nb_tentatives: 4,
      anciennete_client_jours: 5,
      distance_km: 5000,
      utilisation_vpn: true,
    });
  };

  const getScoreColor = (score) => {
    if (score < 0.3) return 'bg-green-500';
    if (score < 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getScoreLabel = (score) => {
    if (score < 0.3) return 'Faible';
    if (score < 0.6) return 'Moyen';
    return 'Élevé';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-3xl">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            🛡️ Détection de Fraude IA
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Analysez une transaction e-commerce en temps réel grâce au Machine Learning
          </p>
        </div>

        {/* Boutons rapides */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={chargerExempleFraude}
            className="text-xs bg-red-50 text-red-600 px-3 py-1.5 rounded-full hover:bg-red-100 transition border border-red-200"
          >
            🚨 Charger un exemple de fraude
          </button>
          <button
            onClick={resetForm}
            className="text-xs bg-gray-50 text-gray-600 px-3 py-1.5 rounded-full hover:bg-gray-100 transition border border-gray-200"
          >
            🔄 Réinitialiser
          </button>
        </div>

        {/* Formulaire */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Montant (€)</label>
            <input
              type="number"
              name="montant"
              value={transaction.montant}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Heure (0-23)</label>
            <input
              type="number"
              name="heure"
              min="0"
              max="23"
              value={transaction.heure}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pays Carte</label>
            <select
              name="pays_carte"
              value={transaction.pays_carte}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {PAYS.map((p) => (
                <option key={p.code} value={p.code}>{p.nom}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pays IP</label>
            <select
              name="pays_ip"
              value={transaction.pays_ip}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {PAYS.map((p) => (
                <option key={p.code} value={p.code}>{p.nom}</option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Type de Marchand</label>
            <select
              name="type_marchand"
              value={transaction.type_marchand}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {TYPES_MARCHAND.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tentatives</label>
            <input
              type="number"
              name="nb_tentatives"
              min="1"
              value={transaction.nb_tentatives}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ancienneté client (jours)</label>
            <input
              type="number"
              name="anciennete_client_jours"
              min="0"
              value={transaction.anciennete_client_jours}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Distance (km)</label>
            <input
              type="number"
              name="distance_km"
              min="0"
              value={transaction.distance_km}
              onChange={handleChange}
              className="w-full rounded-lg border-gray-300 shadow-sm p-2.5 border focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="utilisation_vpn"
              checked={transaction.utilisation_vpn}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <label className="ml-2 text-sm font-medium text-gray-700">Utilisation d'un VPN</label>
          </div>
        </div>

        {/* Bouton analyser */}
        <button
          onClick={analyser}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition font-semibold disabled:bg-blue-300 disabled:cursor-not-allowed shadow-md"
        >
          {loading ? '⏳ Analyse en cours...' : '🔍 Analyser la transaction'}
        </button>

        {/* Message d'erreur */}
        {erreur && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            ⚠️ {erreur}
          </div>
        )}

        {/* Résultat */}
        {resultat && (
          <div
            className={`mt-6 p-5 rounded-xl border-2 ${
              resultat.est_fraude
                ? 'bg-red-50 border-red-300'
                : 'bg-green-50 border-green-300'
            }`}
          >
            <h2 className="text-xl font-bold flex items-center gap-2">
              {resultat.est_fraude ? '🚨 FRAUDE DÉTECTÉE' : '✅ Transaction Sûre'}
            </h2>

            {/* Barre de score */}
            <div className="mt-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium text-gray-700">Score de risque</span>
                <span className="font-bold">
                  {(resultat.score_risque * 100).toFixed(1)}% — {getScoreLabel(resultat.score_risque)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-3 rounded-full transition-all duration-700 ${getScoreColor(resultat.score_risque)}`}
                  style={{ width: `${resultat.score_risque * 100}%` }}
                />
              </div>
            </div>

            {/* Explications SHAP */}
            <div className="mt-5">
              <h3 className="font-semibold text-sm text-gray-800 mb-2">
                📊 Explications du modèle (SHAP) :
              </h3>
              <ul className="space-y-1.5">
                {resultat.explications.map((exp, i) => (
                  <li key={i} className="text-sm text-gray-700 bg-white/60 px-3 py-1.5 rounded-md">
                    {exp}
                  </li>
                ))}
              </ul>
            </div>

            {/* Top features (optionnel) */}
            {resultat.top_features && resultat.top_features.length > 0 && (
              <details className="mt-4">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                  Voir les détails techniques (impacts SHAP)
                </summary>
                <div className="mt-2 text-xs font-mono bg-white/70 p-3 rounded-md space-y-1">
                  {resultat.top_features.map((f, i) => (
                    <div key={i} className="flex justify-between">
                      <span>{f.feature}</span>
                      <span className={f.impact > 0 ? 'text-red-600' : 'text-green-600'}>
                        {f.impact > 0 ? '+' : ''}{f.impact.toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;