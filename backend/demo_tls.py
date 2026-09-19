"""
Démonstration pédagogique du chiffrement TLS.
Objectif : montrer visuellement comment 'FR' devient illisible pour un pirate.
"""

import base64
import os
from colorama import init, Fore, Style

init(autoreset=True)


def titre(emoji, texte, couleur=Fore.CYAN):
    print("\n" + couleur + "=" * 70)
    print(f"{Fore.YELLOW}{emoji}  {Fore.WHITE}{Style.BRIGHT}{texte}")
    print(couleur + "=" * 70 + Style.RESET_ALL)


def demo_chiffrement(donnee_claire: str, nom_donnee: str):
    """Simule le passage d'une donnée en clair → chiffrée → déchiffrée."""

    # ===================================================================
    # 1. CÔTÉ NAVIGATEUR — Donnée en clair
    # ===================================================================
    titre("👤", f"1. NAVIGATEUR — Envoi de '{nom_donnee}'", Fore.CYAN)
    print(f"   {Fore.GREEN}Valeur en clair   : {Style.BRIGHT}{donnee_claire}")
    print(f"   {Fore.GREEN}Visible par       : l'utilisateur uniquement")

    # ===================================================================
    # 2. CHIFFREMENT (simulation TLS)
    # ===================================================================
    titre("🔐", "2. CHIFFREMENT TLS — Ce qui part sur le réseau", Fore.YELLOW)

    # Simulation : encodage Base64 (pédagogique, pas cryptographique)
    donnee_chiffree = base64.b64encode(donnee_claire.encode()).decode()

    print(f"   {Fore.RED}Donnée chiffrée   : {Style.BRIGHT}{donnee_chiffree}")
    print(f"   {Fore.RED}Visible par       : 🕵️  N'IMPORTE QUEL PIRATE sur le réseau !")
    print(f"   {Fore.RED}Le pirate ne peut PAS comprendre : c'est du charabia")

    # ===================================================================
    # 3. SUR LE RÉSEAU — Ce que voit le pirate
    # ===================================================================
    titre("🕵️", "3. SUR LE RÉSEAU — Vue d'un pirate qui intercepte", Fore.MAGENTA)

    print(f"   {Fore.RED}Paquet intercepté :")
    print(f"   {Fore.RED}┌─────────────────────────────────────────┐")
    print(f"   {Fore.RED}│ Host: monsite.com                       │")
    print(f"   {Fore.RED}│ POST /api/v1/predict                    │")
    print(f"   {Fore.RED}│ Body: {donnee_chiffree[:35]:<35} │")
    print(f"   {Fore.RED}│ {donnee_chiffree[35:70]:<40} │")
    print(f"   {Fore.RED}└─────────────────────────────────────────┘")
    print(f"   {Fore.RED}Le pirate voit uniquement du charabia. ")
    print(f"   {Fore.RED}Aucune information exploitable.")

    # ===================================================================
    # 4. DÉCHIFFREMENT CÔTÉ SERVEUR
    # ===================================================================
    titre("🖥️", "4. SERVEUR — Déchiffrement TLS", Fore.GREEN)

    donnee_dechiffree = base64.b64decode(donnee_chiffree.encode()).decode()

    print(f"   {Fore.GREEN}Donnée reçue      : {donnee_chiffree[:40]}...")
    print(f"   {Fore.GREEN}Donnée déchiffrée : {Style.BRIGHT}{donnee_dechiffree}")
    print(f"   {Fore.GREEN}Le serveur retrouve la valeur ORIGINALE")

    # ===================================================================
    # 5. RÉSUMÉ
    # ===================================================================
    titre("✅", "RÉSUMÉ DE LA TRANSFORMATION", Fore.CYAN)
    print(f"   Navigateur : {Fore.GREEN}{donnee_claire}")
    print(f"        ↓ chiffrement TLS")
    print(f"   Réseau     : {Fore.RED}{donnee_chiffree[:40]}...  ← pirate bloqué")
    print(f"        ↓ déchiffrement TLS")
    print(f"   Serveur    : {Fore.GREEN}{donnee_dechiffree}")
    print()


# =======================================================================
# DÉMONSTRATION
# =======================================================================
if __name__ == "__main__":

    titre("🎬", "DÉMONSTRATION DU CHIFFREMENT HTTPS/TLS", Fore.WHITE)

    print(f"""
    {Fore.YELLOW}Scénario :{Fore.WHITE} un utilisateur envoie une transaction
    contenant le pays de sa carte bancaire ({Fore.GREEN}FR{Fore.WHITE}) vers le serveur.
    Voyons ce qu'un pirate voit sur le réseau.
    """)

    # On démontre pour plusieurs données sensibles
    demo_chiffrement("FR", "Pays carte")
    demo_chiffrement("NG", "Pays IP")
    demo_chiffrement("3500", "Montant")
    demo_chiffrement("demo-key-12345", "Clé API")

    titre("🎓", "CONCLUSION", Fore.GREEN)
    print(f"""
    {Fore.GREEN}✅ Grâce à HTTPS/TLS :{Fore.WHITE}
       • Le navigateur envoie les données en clair
       • TLS les chiffre AVANT envoi sur le réseau
       • Le pirate intercepte du charabia illisible
       • Le serveur déchiffre et retrouve les valeurs originales

    {Fore.RED}❌ Sans HTTPS/TLS :{Fore.WHITE}
       • Le pirate verrait 'FR', 'NG', '3500' en clair
       • Il pourrait lire, copier, modifier les données
       • Le système serait totalement vulnérable
    """)