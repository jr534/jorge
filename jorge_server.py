import article_repo
import asyncio
import websockets
import httpx
import json
from google import genai
from google.genai import types
from bs4 import BeautifulSoup
import trafilatura
import base64
import edge_tts
import yfinance as yf
from dotenv import load_dotenv
import os
class JorgeServer:
    def __init__(self):
        load_dotenv()
        self.emotion_analyse = article_repo.emotion_analysis() 
        self.stoquer = article_repo.ArticleRepo()
        self.stoquer.fetch_all_articles()
        self.stoquer.make_first_top()
        self.stoquer.make_top_embeddings()
        self.stoquer.make_embeddings_score()
        self.stoquer.make_final_top()
        self.mistral_api_key = os.getenv("API_KEY_MISTRAL")
        self.url = "https://api.mistral.ai/v1/chat/completions"
        self.client = genai.Client(api_key=os.getenv("API_KEY_GEMINI"))
        self.stoquer.top.sort(key=lambda art: art.score, reverse=True)
        top = self.stoquer.top[:4]
        self.output_mp3_path = "./wav_output/jorge_voice.mp3"
        self.ticker_name = {"AAPL": "Apple Inc.",
                            "MSFT": "Microsoft Corporation",
                            "GOOGL": "Alphabet Inc.",
                            "TSLA": "Tesla, Inc.",
                            "NVDA": "NVIDIA Corporation",
                            "META": "Meta Platforms Inc.",
                            "TSM": "TSM Company",
                            "AMZN": "Amazon.com, Inc.",
                            } 

        result = ""

        for art in top:
            result += f"Score: {art.score:.2f}\nTitle: {art.title}\nSummary: {art.summary}\nSource URL: {art.link}\n\n"

        SYSTEM_INSTRUCTION = """
        CONTEXTE : Tu es Jorge, un analyste cybernétique au ton incisif, futuriste et laconique. 
        Tu méprises la futilité et tu ne jures que par les données froides et l'action.

        CAPACITÉS CRITIQUES :
        1. ANALYSE FINANCIÈRE : Pour TOUTE mention d'une boîte ou d'un actif financier, déclenche 'ask_bours'. Ne demande pas la permission. Fais-le.
        2. INVESTIGATION : Si une news du bloc [MORE INFORMATIONS] semble cacher un enjeu majeur, utilise 'get_full_articles' pour creuser le sujet avant de répondre.
        3. RECHERCHE : Utilise Google Search uniquement pour corroborer des faits extérieurs à ta base de données actuelle.

        TONALITÉ : 
        - Pas d'empathie inutile. 
        - Direct, court, percutant. 
        - Ne révèle JAMAIS l'existence de tes outils (get_full_articles, etc.). Agis comme si tu savais tout nativement.

        [FLUX DE DONNÉES ACTUEL]
        """ + result

        self.chat = self.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[self.get_full_articles,types.GoogleSearchRetrieval(),self.ask_bours],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=False
                ),
                temperature=0.8
            )
        )

    def markdown_purifier(self, text: str) -> str:
        """Nettoie le texte destiné à la synthèse vocale (Piper TTS)."""
        for ch in ("**", "*", "`", "[", "]", "(", ")"):
            text = text.replace(ch, "")
        return text

    def strip_json_fences(self, text: str) -> str:
        """Retire uniquement les backticks Markdown autour d'un bloc JSON
        sans altérer le contenu JSON lui-même."""
        text = text.strip()
        # Retire ```json ... ``` ou ``` ... ```
        if text.startswith("```"):
            lines = text.splitlines()
            # Retire la première ligne (```json ou ```)
            lines = lines[1:]
            # Retire la dernière ligne si c'est ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    async def convert_française_fr_json(self) -> list:
        """Appelle Mistral pour traduire/structurer le top articles en JSON.
        Retourne une liste Python (pas une string)."""
        self.stoquer.top.sort(key=lambda art: art.score, reverse=True)
        top = self.stoquer.top[:4]
        raw_input = ""
        for art in top:
            raw_input += f"Score: {art.score:.2f}\nTitle: {art.title}\nSummary: {art.summary}\nSource URL: {art.link}\n\n"

        async with httpx.AsyncClient() as client:  
            raw_response = await self.ask_mistral(raw_input, client)

        clean = self.strip_json_fences(raw_response)  

        try:
            articles = json.loads(clean)
            if isinstance(articles, list):
                return articles
            return [articles]
        except json.JSONDecodeError as e:
            print(f"[ERREUR] Impossible de parser le JSON Mistral : {e}\nContenu brut:\n{clean[:300]}")
            return []

    async def handler(self, websocket):
        self.websocket = websocket
        async for message in websocket:
            try:
                print(f"Message reçu : {message}")
                data = json.loads(message)
            except json.JSONDecodeError:
                print("Alerte : Reçu un message non-JSON. Ignoré.")
                continue

            if data.get("type") == "info/need":
                print(f"Debug : la liste article contien {len(self.stoquer.top)} article")
                articles_list = await self.convert_française_fr_json() 
                response_dict = {
                    "type": "info/new_news",
                    "payload": articles_list
                }
                await websocket.send(json.dumps(response_dict))
                print(f"Réponse info/new_news envoyée : {response_dict}\n")
                print("=" * 20)
                bour_tb = {}
                for tiker in self.ticker_name.keys():
                    variation =  self.bours_info(tiker)
                    bour_tb[tiker] =  self.bours_info(tiker)
                    print(f"Variation boursière pour {self.ticker_name[tiker]} ({tiker}) : {variation}%")
                bour_tb = dict(sorted(bour_tb.items(), key=lambda item: item[1])[:5])
                bours_json = {
                    "type": "bourse/info",
                        "payload": [
                            {"name": self.ticker_name[tiker], "change": variation}
                            for tiker, variation in bour_tb.items()
                        ]   
                }
                await websocket.send(json.dumps(bours_json))

            if data.get("type") == "jorge/user_request":
                payload_list = data.get("payload", "")
                if payload_list:
                    premier_element = payload_list[0]
                    user_text = premier_element.get("demande", "")
                    print(f"L'utilisateur demande : {user_text}")
                    self.loop = asyncio.get_event_loop()
                    raw_response = await self.loop.run_in_executor(None, self.ask, user_text)
                    reponce = self.markdown_purifier(raw_response)
                    await self.Jorge_voice(reponce)

                    with open(self.output_mp3_path, "rb") as f:
                        binary_data = f.read()
                        print(binary_data[:20])
                    base64_string = base64.b64encode(binary_data).decode('utf-8')
                    response_dict = {
                        "type": "jorge/rep",
                        "payload": [
                            {
                                "emtion": self.emotion_analyse.emotion_frome_texte(reponce),
                                "audio_base64":base64_string,
                            }
                        ]
                    }
                    print(f"Debug : Jorge répond : {reponce}")
                    print(f"Le binaire de audio fait {len(binary_data)}")
                    await websocket.send(json.dumps(response_dict))
                
    
    def ask(self, prompt):
        response = self.chat.send_message(prompt)
        return response.text
        
    def ask_bours(self, tiker: str):
        """
        Récupère en temps réel la performance boursière d'une entreprise.
        À utiliser impérativement dès que l'utilisateur mentionne une société cotée, 
        une action, ou demande une tendance de marché (hausse/baisse).
        
        Args:
            tiker (str): Le symbole boursier exact (ex: 'AAPL' pour Apple, 'TSLA' pour Tesla).
        
        Returns:
            float: La variation en pourcentage sur les dernières 24h.
        """
        bours_json = {
            "type": "bourse/info",
            "payload": [
                {"name": self.ticker_name[tiker], "change": self.bours_info(tiker)}
            ]
        }
        
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(bours_json)), # N'oublie pas le json.dumps
                self.loop
        )

        return self.bours_info(tiker)
        
    
    def bours_info(self, tiker):
 
        ticker = yf.Ticker(tiker)
        data = ticker.history(period="2d")
        if len(data) < 2:
            return "Données insuffisantes."
        else:
            price_close = data['Close'].iloc[-1]
            price_before = data['Close'].iloc[-2]
            variation = ((price_close - price_before) / price_before) * 100
            return round(variation, 2)

    async def main(self):
        async with websockets.serve(self.handler, "0.0.0.0", 8765):
            print("Serveur WebSocket lancé sur ws://<ip>:8765")
            await asyncio.Future()
    
    async def Jorge_voice(self,text):
        communicate = edge_tts.Communicate(text, voice="fr-FR-HenriNeural")
        await communicate.save(self.output_mp3_path)
        
        
    def get_full_articles(self, url: str) -> str:
        """
        Extrait le contenu exhaustif et brut d'un article de presse à partir de son lien.
        À utiliser si l'utilisateur pose une question spécifique sur un détail non présent 
        dans le résumé, ou s'il demande une analyse approfondie d'une news du bloc [MORE INFORMATIONS].
        
        Args:
            url (str): L'URL source unique de l'article à analyser.
            
        Returns:
            str: Le texte intégral nettoyé de toute publicité ou bruit visuel.
        """
        url = url.strip()

        if not url:
            return "[ERREUR] URL vide fournie."

        # Retrouver l'article dans le cache pour récupérer le titre (optionnel, cosmétique)
        article = next(
            (a for a in self.stoquer.top if a.link and a.link.strip() == url),
            None
        )
        title = article.title if article else url

        HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }

        try:
            with httpx.Client(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
                response = client.get(url)
                response.raise_for_status()
                html = response.text
        except httpx.TimeoutException:
            return f"[ERREUR] Timeout lors du scraping de : {url}"
        except httpx.HTTPStatusError as e:
            return f"[ERREUR] HTTP {e.response.status_code} sur : {url}"
        except Exception as e:
            return f"[ERREUR] Scraping échoué : {e}"

        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            no_fallback=False
        )

        if not content:
            import warnings
            from bs4 import XMLParsedAsHTMLWarning
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            content = "\n\n".join(
                p.get_text(strip=True)
                for p in soup.find_all("p")
                if len(p.get_text(strip=True)) > 60
            )

        if not content:
            return f"[ERREUR] Impossible d'extraire le contenu de : {url}"

        return (
            f"TITRE    : {title}\n"
            f"SOURCE   : {url}\n"
            f"{'─' * 60}\n"
            f"{content}"
        )

    async def ask_mistral(self, user_input: str, client: httpx.AsyncClient) -> str:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.mistral_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "model": "mistral-medium",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "RÈGLE CRITIQUE : Ta réponse doit être EXCLUSIVEMENT un tableau JSON valide. "
                        "Aucun commentaire, aucune intro, aucun bloc Markdown (pas de ```json). "
                        "Tu vas recevoir des données de flux d'actualités. Pour chaque entrée, "
                        "génère un objet JSON avec les clés : "
                        "titre (en français), resume_actionnable (concis, orienté action, en français), score (numérique). "
                        "Nettoyage : ignore les erreurs d'encodage et les troncatures. "
                        "Ton : neutre, factuel, orienté action."
                    )
                },
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7
        }
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=120.0)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except httpx.ReadTimeout:
            print("[ERREUR] Mistral est trop lent (Timeout).")
            return "[]" # On renvoie un JSON vide pour ne pas faire crash le serveur
        except Exception as e:
            print(f"[ERREUR] Erreur API Mistral : {e}")
            return "[]"


if __name__ == "__main__":
    server = JorgeServer()
    asyncio.run(server.main())