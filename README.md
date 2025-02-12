Flask Secure Chat - README

Description

Flask Secure Chat est une application web permettant l'envoi et la réception de messages en temps réel avec des fonctionnalités de sécurité avancées. Elle inclut un filtrage de mots interdits, un chiffrement des données et un transfert sécurisé des fichiers.

Fonctionnalités

🔐 Authentification des utilisateurs : Permet aux utilisateurs de s'authentifier avant d'accéder au chat.

💬 Envoi de messages en temps réel : Communication instantanée entre les utilisateurs.

🗂️ Création de discussions : Possibilité de créer des discussions privées ou de groupe.

✅ Contrôle de saisie : Vérification des entrées pour éviter les injections et autres attaques.

🚫 Filtrage de mots interdits en temps réel : Empêche l'envoi de messages contenant des mots interdits.

Installation

Clonez le dépôt :

git clone <repository_url>

Accédez au dossier du projet :

cd Secure-Chat

Créez un environnement virtuel et activez-le :

python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

Installez les dépendances 
Démarrez l'application :
python server.py

Sécurité et réseau

1. Filtrage des mots interdits

L'application empêche l'envoi de messages contenant des mots interdits définis . Toute tentative d'envoi est bloquée.

2.transfert de fichiers

Utilisation de file.io pour un partage sécurisé des fichiers.

3. Chiffrement des données

Messages stockés chiffrés 




