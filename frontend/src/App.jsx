import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';
const API_KEY = 'demo-key-12345';

const PAYS = [
  { code: 'FR', nom: 'France' }, { code: 'US', nom: 'USA' },
  { code: 'GB', nom: 'Royaume-Uni' }, { code: 'DE', nom: 'Allemagne' },
  { code: 'NG', nom: 'Nigeria' }, { code: 'RU', nom: 'Russie' },
  { code: 'CN', nom: 'Chine' }, { code: 'UA', nom: 'Ukraine' },
];

const TYPES_MARCHAND = [
  'Vêtements', 'Électronique', 'Crypto', 'Jeux d\'argent',
  'Alimentation', 'Voyage', 'Luxe', 'Abonnement',
];

function App() {
  // --- ÉTATS DU FORMULAIRE ---
  const [transaction, setTransaction] = useState({
    montant: 150, pays_carte: 'FR', pays_ip: 'FR', heure: 14,
    type_marchand: 'Vêtements', nb_tentatives: 1,
    anciennete_client_jours: 365, distance_km: 10, utilisation_vpn: false,
  });
  const [resultat, setResultat] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState(null);

  // --- ÉTATS POUR LA COMPARAISON DES MODÈLES ---
  const [modelsData, setModelsData] = useState(null);

  // Charger la comparaison des modèles au démarrage
  useEffect(() => {
    axios.get(`${API_URL}/api/v1/models/comparison`)
      .then(res => setModelsData(res.data))
      .catch(err => console.error("Erreur modèles:", err));
  }, []);

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

      const response = await axios.post(`${API_URL}/api/v1/predict`, payload, {
        headers: { 'Content-Type': 'application/json', 'x-api-key': API_KEY },
      });
      setResultat(response.data);
    } catch (error) {
      console.error('Erreur API', error);
      setErreur(error.response?.data?.detail || "Impossible de contacter l'API.");
    }
    setLoading(false);
  };

  const chargerExempleFraude = () => {
    setTransaction({
      montant: 3500, pays_carte: 'FR', pays_ip: 'NG', heure: 3,
      type_marchand: 'Crypto', nb_tentatives: 4,
      anciennete_client_jours: 5, distance_km: 5000, utilisation_vpn: true,
    });
  };

  const resetForm = () => {
    setTransaction({
      montant: 150, pays_carte: 'FR', pays_ip: 'FR', heure: 14,
      type_marchand: 'Vêtements', nb_tentatives: 1,
      anciennete_client_jours: 365, distance_km: 10, utilisation_vpn: false,
    });
    setResultat(null);
    setErreur(null);
  };

  // --- STYLES DYNAMIQUES ---
  const getScoreColor = (score) => {
    if (score < 0.3) return 'bg-green-600'; // Vert foncé
    if (score < 0.6) return 'bg-yellow-500';
    return 'bg-red-600';
  };

  return (
    // Fond général Noir/Gris très très foncé
    <div className="min-h-screen bg-neutral-950 text-neutral-200 p-6 font-sans">
      
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* EN-TÊTE */}
        <header className="border-b border-neutral-800 pb-4">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <span className="text-green-500">🛡️</span> Détection de Fraude IA
          </h1>
          <p className="text-neutral-400 mt-1 text-sm">Analyse heuristique et Machine Learning en temps réel</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* COLONNE GAUCHE : FORMULAIRE */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-white">Nouvelle Analyse</h2>
              <button onClick={chargerExempleFraude} className="text-xs bg-red-900/30 text-red-400 border border-red-900 px-3 py-1 rounded hover:bg-red-900/50 transition">
                Charger un exemple
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-xs font-medium text-neutral-400 mb-1">Montant (€)</label>
                <input type="number" name="montant" value={transaction.montant} onChange={handleChange}
                  className="w-full bg-neutral-950 border border-neutral-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-green-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-neutral-400 mb-1">Heure (0-23)</label>
                <input type="number" name="heure" value={transaction.heure} onChange={handleChange}
                  className="w-full bg-neutral-950 border border-neutral-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-green-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-neutral-400 mb-1">Pays Carte</label>
                <select name="pays_carte" value={transaction.pays_carte} onChange={handleChange}
                  className="w-full bg-neutral-950 border border-neutral-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-green-500">
                  {PAYS.map(p => <option key={p.code} value={p.code}>{p.nom}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-neutral-400 mb-1">Pays IP</label>
                <select name="pays_ip" value={transaction.pays_ip} onChange={handleChange}
                  className="w-full bg-neutral-950 border border-neutral-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-green-500">
                  {PAYS.map(p => <option key={p.code} value={p.code}>{p.nom}</option>)}
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-medium text-neutral-400 mb-1">Type de Marchand</label>
                <select name="type_marchand" value={transaction.type_marchand} onChange={handleChange}
                  className="w-full bg-neutral-950 border border-neutral-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-green-500">
                  {TYPES_MARCHAND.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div className="flex gap-4 mb-6">
               <div className="flex-1">
                  <label className="block text-xs font-medium text-neutral-400 mb-1">Distance (km)</label>
                  <input type="number" name="distance_km" value={transaction.distance_km} onChange={handleChange}
                    className="w-full bg-neutral-950 border border-neutral-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-green-500" />
               </div>
               <div className="flex items-end pb-3">
                  <label className="flex items-center gap-2 cursor-pointer text-sm">
                    <input type="checkbox" name="utilisation_vpn" checked={transaction.utilisation_vpn} onChange={handleChange}
                      className="w-4 h-4 accent-green-500" />
                    Utilisation VPN
                  </label>
               </div>
            </div>

            <button onClick={analyser} disabled={loading}
              className="w-full bg-green-700 hover:bg-green-600 text-white font-semibold py-3 rounded-lg transition-colors shadow-lg shadow-green-900/20 disabled:opacity-50">
              {loading ? 'Analyse en cours...' : 'Lancer l\'analyse'}
            </button>

            {erreur && <div className="mt-4 p-3 bg-red-950/50 border border-red-900 text-red-400 text-sm rounded-lg">{erreur}</div>}
          </div>

          {/* COLONNE DROITE : RÉSULTAT */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-xl">
            <h2 className="text-lg font-semibold text-white mb-6">Résultat de l'analyse</h2>
            
            {!resultat && !loading && (
              <div className="h-full flex flex-col items-center justify-center text-neutral-600 py-20">
                <span className="text-5xl mb-4">🔎</span>
                <p>En attente d'une transaction...</p>
              </div>
            )}

            {resultat && (
              <div className="space-y-6 animate-fade-in">
                <div className={`p-4 rounded-lg border ${resultat.est_fraude ? 'bg-red-950/30 border-red-900/50' : 'bg-green-950/30 border-green-900/50'}`}>
                  <h3 className={`text-xl font-bold flex items-center gap-2 ${resultat.est_fraude ? 'text-red-400' : 'text-green-400'}`}>
                    {resultat.est_fraude ? '🚨 FRAUDE DÉTECTÉE' : '✅ TRANSACTION SÛRE'}
                  </h3>
                  <p className="text-sm text-neutral-400 mt-1">ID: {resultat.transaction_id}</p>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-neutral-400">Score de risque</span>
                    <span className="font-bold text-white">{(resultat.score_risque * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-neutral-800 rounded-full h-3">
                    <div className={`h-3 rounded-full ${getScoreColor(resultat.score_risque)}`} 
                         style={{ width: `${resultat.score_risque * 100}%` }}></div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-neutral-300 mb-3">Facteurs explicatifs (SHAP)</h4>
                  <ul className="space-y-2">
                    {resultat.explications.map((exp, i) => (
                      <li key={i} className="text-sm bg-neutral-950 p-3 rounded border border-neutral-800 text-neutral-300">
                        {exp}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* --- SECTION TABLEAU DE COMPARAISON --- */}
        {modelsData && (
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl shadow-xl overflow-hidden mt-8">
            <div className="p-6 border-b border-neutral-800 flex justify-between items-end">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="text-green-500">📊</span> Performance des Modèles
                </h2>
                <p className="text-sm text-neutral-400 mt-1">Comparaison des algorithmes entraînés sur 50 000 transactions.</p>
              </div>
              <div className="text-right">
                <span className="text-xs text-neutral-500 uppercase tracking-wider block mb-1">Modèle en production</span>
                <span className="inline-block bg-green-900/40 text-green-400 border border-green-800 px-3 py-1 rounded-full text-sm font-bold">
                  {modelsData.meilleur_modele}
                </span>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-neutral-950 text-neutral-400 uppercase text-xs">
                  <tr>
                    <th className="px-6 py-4 font-medium">Algorithme</th>
                    <th className="px-6 py-4 font-medium text-right">Accuracy</th>
                    <th className="px-6 py-4 font-medium text-right">Precision</th>
                    <th className="px-6 py-4 font-medium text-right">Recall</th>
                    <th className="px-6 py-4 font-medium text-right">F1-Score</th>
                    <th className="px-6 py-4 font-medium text-right text-green-500">AUC-ROC</th>
                    <th className="px-6 py-4 font-medium text-right">Temps</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800">
                  {modelsData.modeles.map((m, i) => {
                    const isBest = m.Modèle === modelsData.meilleur_modele;
                    return (
                      <tr key={i} className={`hover:bg-neutral-800/50 transition-colors ${isBest ? 'bg-neutral-800/30' : ''}`}>
                        <td className="px-6 py-4 font-medium text-white flex items-center gap-2">
                          {isBest && <span className="text-green-500">🏆</span>}
                          {m.Modèle}
                        </td>
                        <td className="px-6 py-4 text-right text-neutral-300">{m.Accuracy.toFixed(4)}</td>
                        <td className="px-6 py-4 text-right text-neutral-300">{m.Precision.toFixed(4)}</td>
                        <td className="px-6 py-4 text-right text-neutral-300">{m.Recall.toFixed(4)}</td>
                        <td className="px-6 py-4 text-right text-neutral-300">{m['F1-Score'].toFixed(4)}</td>
                        <td className="px-6 py-4 text-right font-bold text-green-400">{m['AUC-ROC'].toFixed(4)}</td>
                        <td className="px-6 py-4 text-right text-neutral-500">{m['Temps (s)'].toFixed(2)}s</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;