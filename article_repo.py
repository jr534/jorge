import feedparser
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch



# Initialiser le modèle de transformation de phrases
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


class emotion_analysis:
    def __init__(self):

        self.sonde_sarcasme = """
        Le sarcasme est une figure de style de la rhétorique consistant à exprimer une ironie mordante par l'usage de l'antiphrase. Ce procédé linguistique repose sur une divergence intentionnelle entre la signification littérale du message et l'intention communicative du locuteur, souvent marquée par une dimension critique ou dépréciative. Dans le cadre de l'analyse sémantique, il se définit comme une forme de communication indirecte où le contexte et l'inférence sont cruciaux pour décoder le mépris ou la dérision. C’est un outil de modulation de la polarité du langage, transformant un énoncé formellement positif en une assertion négative.
        """
        self.sonde_énervement = """L'énervement est un état d'agitation psychologique et de tension nerveuse caractérisé par une irritabilité accrue face à un stimulus perturbateur. Sur le plan comportemental, il se manifeste par une baisse du seuil de tolérance, entraînant des réactions d'exaspération, de colère ou d'hostilité latente. Ce phénomène de réactivité émotionnelle s'accompagne souvent de marqueurs physiologiques tels que l'augmentation du rythme cardiaque et de la tension musculaire. Dans une analyse de similarité sémantique, ce terme est étroitement lié aux concepts de frustration, d'impatience et de dysfonctionnement relationnel, représentant une rupture de l'équilibre homéostatique face à une contrainte environnementale ou sociale.
        """
        self.sonde_joie = """La joie est une émotion positive caractérisée par un sentiment de plaisir intense et de satisfaction profonde. Elle se manifeste par des expressions faciales telles que le sourire, ainsi que par des réactions physiologiques comme la libération d'endorphines. Sur le plan cognitif, la joie est associée à une perception optimiste de la réalité et à une augmentation de la motivation intrinsèque. Dans une analyse sémantique, elle est souvent corrélée à des concepts tels que le bonheur, l'euphorie et l'accomplissement personnel, constituant un état d'équilibre émotionnel favorable à la résilience psychologique et au bien-être général.
        """
        self.sonde_endormie = """L'endomorphie est une caractéristique morphologique définie par une prédominance de tissus adipeux, conférant à l'individu une silhouette arrondie et une tendance à stocker les graisses. Sur le plan physiologique, les endomorphes présentent souvent un métabolisme plus lent, ce qui peut favoriser la prise de poids et rendre la perte de masse grasse plus difficile. En termes d'analyse sémantique, ce terme est fréquemment associé à des concepts tels que la corpulence, l'obésité et les troubles métaboliques, constituant un facteur de risque pour diverses pathologies liées au surpoids.
        """

        
    def emotion_frome_texte(self, texte):
        # On encode le texte d'entrée
        emb_texte = model.encode([texte])[0]
        
        # On encode les sondes
        emb_sarcasme = model.encode([self.sonde_sarcasme])[0]
        emb_énervement = model.encode([self.sonde_énervement])[0]
        emb_joie = model.encode([self.sonde_joie])[0]
        emb_endormie = model.encode([self.sonde_endormie])[0]
        
        # On calcule la similarité cosinus avec chaque sonde
        sim_sarcasme = cosine_similarity([emb_texte], [emb_sarcasme])[0][0]
        sim_énervement = cosine_similarity([emb_texte], [emb_énervement])[0][0]
        sim_joie = cosine_similarity([emb_texte], [emb_joie])[0][0]
        sim_endormie = cosine_similarity([emb_texte], [emb_endormie])[0][0]
        
        if sim_sarcasme > max(sim_énervement, sim_joie, sim_endormie):
            return "sarcasme"
        elif sim_énervement > max(sim_sarcasme, sim_joie, sim_endormie):
            return "énervement"
        elif sim_joie > max(sim_sarcasme, sim_énervement, sim_endormie):
            return "joie"
        elif sim_endormie > max(sim_sarcasme, sim_énervement, sim_joie):
            return "endormie"
        else:
            return "naturelle"
    
class Article:
    def __init__(self, score, title, summary, source_url, link):
        self.source_url = source_url   # URL du feed RSS (source)
        self.link = link or source_url  # URL de l'article individuel
        self.score = score
        self.title = title
        self.summary = summary

class ArticleRepo:
    def __init__(self):
        self.first_top = [] # max 15
        self.articles = []
        self.top = [] # max 4
        self.first_top_embeddings = {}
        self.sonde_positive = """
        Annonces disruptives, IA multimodale, agents autonomes, intelligence embarquée. 
        Benchmarks de performance, inférence, vision par ordinateur, hardware révolutionnaire.
        """

        # SONDE B : LE BOUCLIER (Pour le filtrage négatif)
        self.sonde_negative = """
        Top 10, meilleurs outils, comparatif générique, publicité, pub, promotion.
        Business, levée de fonds, bourse, régulation, loi, AI Act, URSSAF, interview CEO.
        """
        self.url_scores = {
    # --- L'ELITE (Score 10) : Infos primaires, analyses de fond ---
    "https://arstechnica.com/feed/": 10,                 # Analyse tech ultra-profonde
    "https://feeds.feedburner.com/TechCrunch/": 10,       # Startups et business tech mondial
    "https://linuxfr.org/news.atom": 10,                  # Le bastion du Libre (Atom)
    "https://news.ycombinator.com/rss": 10,               # Hacker News (Le pouls de la Silicon Valley)
    
    # --- LES INCONTOURNABLES (Score 8-9) : Très réactifs ---
    "https://www.theverge.com/rss/index.xml": 9,           # Culture tech et hardware
    "https://www.numerama.com/feed/": 9,                  # Référence fr sur le futur du numérique
    "https://www.zdnet.fr/feeds/rss/actualites/": 8,      # Actu tech pro
    "https://www.wired.com/feed/rss": 8,                  # Longs formats et prospective
    
    # --- DEV & IA (Score 8-9) : Pour le codeur ---
    "https://www.infoq.com/feed": 9,                      # Architecture logicielle et patterns
    "https://dev.to/feed": 8,                             # Communauté dev (beaucoup de volume)
    "https://openai.com/blog/rss.xml": 9,                 # Directement à la source de l'IA
    "https://machinelearningmastery.com/feed/": 8,        # Deep learning et ML
    
    # --- CYBERSÉCURITÉ (Score 9) : Pour ne pas se faire hacker ---
    "https://feeds.feedburner.com/TheHackersNews": 9,     # Alertes mondiales
    "https://www.schneier.com/blog/index.rdf": 9,         # Bruce Schneier (La légende de la crypto)
    "https://krebsonsecurity.com/feed/": 9,               # Brian Krebs (Investigations cyber)
    
    # --- HARDWARE & MOBILITÉ (Score 7-8) ---
    "https://www.frandroid.com/feed": 8,                  # Hardware et Android
    "https://9to5google.com/feed/": 7,                    # Écosystème Google
    
    # --- INSOLITE & SCIENCE-TECH (Score 6-7) ---
    "https://spectrum.ieee.org/rss/blog/the-human-os/fulltext": 7, # Ingénierie de pointe
    "https://www.tomshardware.com/feeds/all": 7,          # Hardware PC
    "https://hackaday.com/blog/feed/": 8,                 # Projets DIY et bidouille de génie
}
    def fetch_articles_from_rss(self, url, score_de_base):
        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"Erreur sur le flux : {url}")
            return []
        
        liste_locale = []
        for entry in feed.entries:
            score_final = score_de_base

            date_parsed = entry.get('date_parsed')
            if date_parsed is None:
                continue  # On ignore les articles sans date

            today = datetime.now().date()
            if datetime.fromtimestamp(time.mktime(date_parsed)).date() == today:
                score_final = score_de_base + 1  # Bonus de fraîcheur

            nouvel_art = Article(
                score=score_final,
                title=entry.title,
                summary=entry.get('summary', 'Pas de résumé'),
                source_url=url,
                link=entry.get('link', url)  
            )
            liste_locale.append(nouvel_art)
        
        return liste_locale  # Retour après la boucle

    def fetch_all_articles(self):
            for url, score in self.url_scores.items():
                # fetch_articles_from_rss renvoie maintenant une LISTE d'objets
                nouveaux_articles = self.fetch_articles_from_rss(url, score)
                
                # On fusionne la petite liste dans la grande liste du repo
                # .extend() est plus efficace que .append() pour ajouter une liste à une autre
                self.articles.extend(nouveaux_articles)

    def make_first_top(self):
        self.top = self.articles
        
    def make_top_embeddings(self):
        # On prépare les textes à encoder (titre + résumé)
        textes = [art.title + " " + art.summary for art in self.top]
        
        # On génère les embeddings en une seule fois
        self.top_embeddings = model.encode(textes)
    def make_embeddings_score(self):
        # On encode les sondes
        emb_positive = model.encode([self.sonde_positive])[0]
        emb_negative = model.encode([self.sonde_negative])[0]
        
        # On calcule la similarité cosinus avec chaque article
        for i, art in enumerate(self.top):
            sim_pos = cosine_similarity([self.top_embeddings[i]], [emb_positive])[0][0]
            sim_neg = cosine_similarity([self.top_embeddings[i]], [emb_negative])[0][0]
            
            # On ajuste le score de l'article en fonction de ces similitudes
            art.score += sim_pos * 2  # Pondération positive
            art.score -= sim_neg * 50  # Pondération négative

    def make_final_top(self):
        # Après ajustement, on retrie la liste
        self.top.sort(key=lambda art: art.score, reverse=True)

                # On garde seulement les 4 premiers
        self.final_top = self.top[:4]
        
""""
stoquer = ArticleRepo()
stoquer.fetch_all_articles()
stoquer.make_first_top()
stoquer.make_top_embeddings()
stoquer.make_embeddings_score()
stoquer.make_final_top()


for i in range(len(stoquer.top)):
    print(f"Score: {stoquer.top[i].score} - Titre: {stoquer.top[i].title.encode('ascii', 'ignore').decode('ascii')}")
print(f"Nombre total d'articles récupérés : {len(stoquer.articles)}")

print("========================================")

print("Embeddings du top 15 :")
for i, emb in enumerate(stoquer.top_embeddings):
    print(f"Article {i+1} embedding (extrait) : {emb[:5]}...")  

print("========================================")
print("Scores après ajustement :")
for i in range(len(stoquer.final_top)):
    print(f"\nScore ajusté: {stoquer.final_top[i].score} - Titre: {stoquer.final_top[i].title} - résumé: {stoquer.final_top[i].summary}\n")
"""