import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

N_SAMPLES = 50000
FRAUD_RATE = 0.02  # 2% de fraudes

# Listes de référence
PAYS = ['FR', 'US', 'GB', 'DE', 'NG', 'RU', 'CN', 'BR', 'IN', 'UA']
PAYS_RISQUE = ['NG', 'RU', 'UA', 'CN']  # Pays à haut risque
TYPES_MARCHAND = ['Vêtements', 'Électronique', 'Crypto', 'Jeux d\'argent', 
                  'Alimentation', 'Voyage', 'Luxe', 'Abonnement']
TYPES_RISQUE = ['Crypto', 'Jeux d\'argent', 'Luxe']
DEVISES = ['EUR', 'USD', 'GBP']

def generer_transaction(is_fraud):
    """Génère une transaction normale ou frauduleuse."""
    
    if is_fraud:
        # Comportement frauduleux
        montant = round(np.random.exponential(scale=800) + 200, 2)  # Montants élevés
        pays_carte = random.choice(['FR', 'US', 'GB', 'DE'])  # Carte "normale"
        pays_ip = random.choice(PAYS_RISQUE)  # IP suspecte
        heure = random.choice([1, 2, 3, 4, 5, 23])  # Heures suspectes
        type_marchand = random.choice(TYPES_RISQUE)
        nb_tentatives = random.randint(2, 5)  # Plusieurs tentatives
        anciennete_client = random.randint(0, 15)  # Client récent
        distance_km = random.uniform(500, 8000)  # Grande distance
        utilisation_vpn = random.choice([True, True, False])  # Souvent VPN
    else:
        # Comportement normal
        montant = round(np.random.lognormal(mean=3.5, sigma=1.2), 2)
        montant = min(montant, 1500)
        pays_carte = random.choice(PAYS)
        # 85% du temps, IP cohérente avec la carte
        if random.random() < 0.85:
            pays_ip = pays_carte
        else:
            pays_ip = random.choice(PAYS)
        heure = int(np.random.normal(14, 4)) % 24  # Autour de 14h
        type_marchand = random.choice(TYPES_MARCHAND)
        nb_tentatives = 1
        anciennete_client = random.randint(30, 3650)
        distance_km = random.uniform(0, 100)
        utilisation_vpn = random.random() < 0.1

    return {
        'montant': montant,
        'pays_carte': pays_carte,
        'pays_ip': pays_ip,
        'heure': heure,
        'type_marchand': type_marchand,
        'nb_tentatives': nb_tentatives,
        'anciennete_client_jours': anciennete_client,
        'distance_km': round(distance_km, 2),
        'utilisation_vpn': int(utilisation_vpn),
        'is_fraud': int(is_fraud)
    }

# Génération
data = []
n_fraudes = int(N_SAMPLES * FRAUD_RATE)
n_normales = N_SAMPLES - n_fraudes

print(f"Génération de {n_normales} transactions normales et {n_fraudes} fraudes...")

for _ in range(n_normales):
    data.append(generer_transaction(is_fraud=False))
    
for _ in range(n_fraudes):
    data.append(generer_transaction(is_fraud=True))

df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Mélanger

# Sauvegarde
df.to_csv('transactions.csv', index=False)
print(f"✅ Dataset créé : {len(df)} transactions")
print(f"Distribution des fraudes :\n{df['is_fraud'].value_counts()}")
print(f"\nAperçu :\n{df.head()}")