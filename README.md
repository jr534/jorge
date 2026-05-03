
<img width="2230" height="938" alt="image" src="https://github.com/user-attachments/assets/0f5768ff-a2af-4d72-ad24-7f232c49beeb" />


  <p align="right">
    <img src="https://img.shields.io/badge/-HTML-E34F26?style=flat-square&logo=html&logoColor=white"/>
    <img src="https://img.shields.io/badge/-CSS-1572B6?style=flat-square&logo=css&logoColor=white"/>
    <img src="https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=white"/>
    <img src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/-Apache-333?style=flat-square&logo=apache&logoColor=white"/>
    <img src="https://img.shields.io/badge/-sentence-transformers-333?style=flat-square&logo=sentence-transformers&logoColor=white"/>
    <img src="https://img.shields.io/badge/-scikit-learn-333?style=flat-square&logo=scikit-learn&logoColor=white"/>
    <img src="https://img.shields.io/badge/-yfinance-333?style=flat-square&logo=yfinance&logoColor=white"/>
    <img src="https://img.shields.io/badge/-json-333?style=flat-square&logo=json&logoColor=white"/>
    <img src="https://img.shields.io/badge/-websocket-333?style=flat-square&logo=websocket&logoColor=white"/>
    <img src="https://img.shields.io/badge/-asyncio-333?style=flat-square&logo=asyncio&logoColor=white"/>
    <img src="https://img.shields.io/badge/-httpx-333?style=flat-square&logo=httpx&logoColor=white"/>
    <img src="https://img.shields.io/badge/-Home%20Assistant-333?style=flat-square&logo=homeassistant&logoColor=white"/>
    <img src="https://img.shields.io/badge/-SSH-333?style=flat-square&logo=ssh&logoColor=white"/>
    <img src="https://img.shields.io/badge/-RAG-333?style=flat-square&logo=rag&logoColor=white"/>
    <img src="https://img.shields.io/badge/-Mistral%20API-333?style=flat-square&logo=mistralapi&logoColor=white"/>
    <img src="https://img.shields.io/badge/-cosine%20similarity-333?style=flat-square&logo=cosinesimilarity&logoColor=white"/>
    <img src="https://img.shields.io/badge/-TTS-333?style=flat-square&logo=tts&logoColor=white"/>
  </p>


# jorge
Le Projet Jorge est un panel intelligent qui sera installé sur une ancienne tablette Microsoft Surface dont le tactile est défectueux. Le projet consiste à avoir la tablette avec Jorge posée sur mon bureau, allumée 24h/24 avec le programme qui tourne.
La tablette sera sous Ubuntu avec l'écran éteint toute la journée. À 18h, si Home Assistant et mes capteurs détectent ma présence dans mon bureau, HA envoie à la Surface un ordre de réveil de l'écran via SSH, ainsi qu'un "start" au socket TCP qui s'allume.
Durant toute la journée, la Surface effectue du polling de flux Atom et RSS. Elle réalise un scoring de tous les articles "new tech", notamment par embedding et autres méthodes, afin de sortir les quatre news les plus pertinentes de la journée. Et me la affichés à 18h si je suis la . 
La partie IA consistera à intégrer un assistant à ce panel via une sorte de RAG. L'assistant aura accès aux quatre articles affichés à l'écran pour contextualiser ses réponses.
Également, pour donner plus de vie au LLM (provenant de l'API Mistral), il y aura une phase de gestion d'affichage. Chaque message du LLM, qui sera exclusivement vocal, sera interprété pour capter l'émotion grâce à une similarité cosinus entre le message généré et les descriptions de chaque émotion ou animation que Jorge peut adopter. la vois vindera de piper tts en local 

**Format Json :**
nouvelle new:
server → Client 

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





<br clear="both"/>

