
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

# Jorge

Le projet **Jorge** est un panel intelligent installé sur une ancienne tablette Microsoft Surface dont le tactile est défectueux. La tablette reste posée sur mon bureau, allumée 24h/24 avec le programme qui tourne.

La tablette est sous Ubuntu avec l'écran éteint toute la journée. À 18h, si Home Assistant et mes capteurs détectent ma présence dans le bureau, HA envoie à la Surface un ordre de réveil de l'écran via SSH, ainsi qu'un `start` au socket TCP.

Pendant la journée, la Surface fait du polling de flux Atom et RSS. Elle réalise un scoring de tous les articles "new tech", notamment par embedding, pour sortir les quatre news les plus pertinentes. Elle me les affiche à 18h si je suis là.

La partie IA consiste à intégrer un assistant via une sorte de RAG. L'assistant a accès aux quatre articles affichés à l'écran pour contextualiser ses réponses.

Pour donner plus de vie au LLM (API Mistral), chaque message, qui sera exclusivement vocal, est interprété pour capter l'émotion grâce à une similarité cosinus entre le message généré et les descriptions de chaque émotion ou animation que Jorge peut adopter. La voix viendra de Piper TTS en local.

---

## Format JSON

### 1. Nouvelles du jour
**Server → Client**
```json
{
  "type": "info/new_news",
  "payload": [
    {
      "titre": "<titre>",
      "resume_actionnable": "<résumé de la news>",
      "score": 0
    },
    {
      "titre": "<titre>",
      "resume_actionnable": "<résumé de la news>",
      "score": 0
    },
    {
      "titre": "<titre>",
      "resume_actionnable": "<résumé de la news>",
      "score": 0
    },
    {
      "titre": "<titre>",
      "resume_actionnable": "<résumé de la news>",
      "score": 0
    }
  ]
}
```

### 2. Interaction avec Jorge
**Client → Server**
```json
{
  "type": "jorge/user_request",
  "payload": {
    "demande": "parle-moi plus de l'article sur Nvidia"
  }
}
```

**Arrivée de la réponse : Server → Client**
```json
{
  "type": "jorge/rep",
  "payload": {
    "emotion": "naturelle",
    "audio_base64": "<audio encodé en base64>"
  }
}
```
> Quand le front reçoit `jorge/rep`, il joue l'audio reçu via le WebSocket `/ws`.

### Liste des émotions

<img width="100%" alt="Émotions Jorge" src="https://github.com/user-attachments/assets/dccd4813-3d79-4afc-bf83-749affb319f2" />

### 3. Envoi des infos de bourse

Le serveur stocke une liste prédéfinie d'actions classées en "niveau 1". Si une entreprise mentionnée dans un article est jugée intéressante (niveau 2), elle est promue en niveau 1.

Suite à `info/need`, le message `bourse/info` contient un nombre variable d'éléments dans le payload, avec le nom de l'entreprise et sa variation journalière (ex: -1,61%).

Le premier message doit impérativement contenir 5 éléments pour l'interface. Le LLM a accès au Tool Use, il peut ensuite envoyer un `bourse/info` avec uniquement l'élément modifié pour actualiser l'interface.

**Server → Client**
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
