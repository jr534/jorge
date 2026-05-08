# Jorge

<img width="100%" alt="Jorge UI" src="https://github.com/user-attachments/assets/0f5768ff-a2af-4d72-ad24-7f232c49beeb" />

<div align="right">
  <img src="https://img.shields.io/badge/-HTML-E34F26?style=flat-square&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/-CSS-1572B6?style=flat-square&logo=css3&logoColor=white"/>
  <img src="https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>
  <img src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/-Apache-D22128?style=flat-square&logo=apache&logoColor=white"/>
  <img src="https://img.shields.io/badge/-sentence_transformers-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-scikit_learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white"/>
  <img src="https://img.shields.io/badge/-yfinance-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-WebSocket-010101?style=flat-square&logo=socketdotio&logoColor=white"/>
  <img src="https://img.shields.io/badge/-asyncio-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-httpx-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-Home_Assistant-41BDF5?style=flat-square&logo=home-assistant&logoColor=white"/>
  <img src="https://img.shields.io/badge/-SSH-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-RAG-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-Mistral_API-FF7000?style=flat-square"/>
  <img src="https://img.shields.io/badge/-cosine_similarity-333?style=flat-square"/>
  <img src="https://img.shields.io/badge/-TTS-333?style=flat-square"/>
</div>

Le projet **Jorge** est un panel intelligent installe sur une ancienne tablette Microsoft Surface. Le front est servi par Apache2, tandis que le backend Python expose un serveur WebSocket sur le port `8765`.

Jorge recupere des flux Atom/RSS, score les articles tech avec des embeddings, affiche les quatre news les plus pertinentes, repond par IA et renvoie une voix synthetisee au front.

La tablette reste posee sur le bureau, allumee 24h/24 avec le programme qui tourne. Pendant la journee, Jorge fait de le récupération de flux Atom et RSS, score les articles "new tech", puis affiche les quatre nouvelles les plus pertinentes.

La partie IA fonctionne comme un assistant contextualise par les articles affiches. Les reponses vocales sont analysees pour choisir une emotion, puis envoyees au front sous forme d'audio encode en base64.

## Stack

- Frontend HTML/CSS/JavaScript servi par Apache2
- Backend Python avec WebSocket
- Mistral API pour la mise en forme des news
- Gemini API pour l'assistant
- `sentence-transformers` et `scikit-learn` pour le scoring semantique
- `edge-tts` pour la synthese vocale
- `yfinance` pour les variations boursieres

## Installation Ubuntu

### 1. Installer les paquets systeme

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip apache2
```

### 2. Recuperer le projet

```bash
cd /opt
sudo git clone https://github.com/jr534/jorge.git
sudo chown -R "$USER":"$USER" /opt/jorge
cd /opt/jorge
```

Si le dossier existe deja:

```bash
cd /opt/jorge
git pull
```

### 3. Creer l'environnement Python

```bash
cd /opt/jorge
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Creer le fichier `.env` a la racine du projet:

```bash
nano /opt/jorge/.env
```

Contenu attendu:

```env
API_KEY_MISTRAL=ta_cle_mistral
API_KEY_GEMINI=ta_cle_gemini
```

Le fichier `.env` est ignore par Git et ne doit pas etre pousse.

### 5. Verifier le dossier audio

```bash
mkdir -p /opt/jorge/wav_output
```

### 6. Lancer le backend manuellement

```bash
cd /opt/jorge
source .venv/bin/activate
python jorge_server.py
```

Le serveur doit afficher:

```text
Serveur WebSocket lance sur ws://<ip>:8765
```

Le backend ecoute sur `0.0.0.0:8765`. Le front actuel se connecte a:

```js
ws://localhost:8765
```

Donc si Apache2 et le backend tournent sur la meme machine que le navigateur, rien d'autre n'est necessaire. Si le navigateur est sur une autre machine, remplace `localhost` dans `Frontend/jorge.html` par l'adresse IP ou le nom DNS du serveur.

## Service systemd pour le backend

Creer le service:

```bash
sudo nano /etc/systemd/system/jorge.service
```

Contenu:

```ini
[Unit]
Description=Jorge WebSocket backend
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/jorge
EnvironmentFile=/opt/jorge/.env
ExecStart=/opt/jorge/.venv/bin/python /opt/jorge/jorge_server.py
Restart=always
RestartSec=5
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

Donner les droits au dossier du projet pour le service:

```bash
sudo chown -R www-data:www-data /opt/jorge
```

Activer et demarrer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jorge.service
sudo systemctl status jorge.service
```

Voir les logs:

```bash
journalctl -u jorge.service -f
```

## Installation du front sur Apache2

### 1. Copier le front dans `/var/www`

```bash
sudo mkdir -p /var/www/jorge
sudo cp -r /opt/jorge/Frontend/* /var/www/jorge/
sudo chown -R www-data:www-data /var/www/jorge
```

### 2. Creer le VirtualHost Apache

```bash
sudo nano /etc/apache2/sites-available/jorge.conf
```

Contenu:

```apache
<VirtualHost *:80>
    ServerName jorge.local
    DocumentRoot /var/www/jorge

    <Directory /var/www/jorge>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/jorge_error.log
    CustomLog ${APACHE_LOG_DIR}/jorge_access.log combined
</VirtualHost>
```

Activer le site:

```bash
sudo a2dissite 000-default.conf
sudo a2ensite jorge.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### 3. Acceder au front

Depuis la machine:

```text
http://localhost/
```

Depuis le reseau local:

```text
http://IP_DU_SERVEUR/
```

Si tu utilises `jorge.local`, ajoute une entree DNS locale ou modifie `/etc/hosts` sur le poste client:

```text
IP_DU_SERVEUR jorge.local
```

## Pare-feu

Si `ufw` est actif:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 8765/tcp
sudo ufw reload
```

## Mise a jour

```bash
cd /opt/jorge
sudo systemctl stop jorge.service
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo cp -r Frontend/* /var/www/jorge/
sudo chown -R www-data:www-data /opt/jorge /var/www/jorge
sudo systemctl restart jorge.service
sudo systemctl reload apache2
```

## Messages WebSocket

### Nouvelles du jour

Server -> Client:

```json
{
  "type": "info/new_news",
  "payload": [
    {
      "titre": "<titre>",
      "resume_actionnable": "<resume de la news>",
      "score": 0
    }
  ]
}
```

### Interaction avec Jorge

Client -> Server:

```json
{
  "type": "jorge/user_request",
  "payload": [
    {
      "demande": "parle-moi plus de l'article sur Nvidia"
    }
  ]
}
```

Server -> Client:

```json
{
  "type": "jorge/rep",
  "payload": [
    {
      "emotion": "naturelle",
      "audio_base64": "<audio encode en base64>"
    }
  ]
}
```

### Liste des émotions

<img width="100%" alt="Émotions Jorge" src="https://github.com/user-attachments/assets/dccd4813-3d79-4afc-bf83-749affb319f2" />
### Bourse

Server -> Client:

```json
{
  "type": "bourse/info",
  "payload": [
    { "name": "Apple", "change": "+0.45%" },
    { "name": "Tesla", "change": "-1.61%" },
    { "name": "Microsoft", "change": "+1.12%" },
    { "name": "Nvidia", "change": "+2.30%" },
    { "name": "Alphabet", "change": "-0.15%" }
  ]
}
```
