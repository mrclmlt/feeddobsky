import feedparser
from bs4 import BeautifulSoup
from atproto import Client
import os
import sys

# Configurações
RSS_URL = "https://www.vaticannews.va/pt.rss.xml"
MAX_POST_LENGTH = 300  # Limite do Bluesky
LINK_EMOJI = "🔗"      # Emoji para o link

def get_latest_news():
    """Obtém a última notícia do feed RSS"""
    try:
        print("\n=== INICIANDO LEITURA DO RSS ===")
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            print(">> ERRO: Nenhuma notícia encontrada no feed RSS")
            return None, None

        latest = feed.entries[0]
        title = latest.title.strip()
        link = latest.link.strip()

        print(f">> Notícia mais recente: {title[:60]}...")
        return title, link

    except Exception as e:
        print(f">> ERRO AO LER RSS: {str(e)}")
        return None, None

def prepare_post(title, link):
    """Formata o post respeitando o limite de caracteres"""
    # Versão minimalista (prioriza título + link)
    basic_post = f"{title}\n\n{LINK_EMOJI} {link}"
    
    if len(basic_post) <= MAX_POST_LENGTH:
        return basic_post
    
    # Se ainda for longo, encurta o título
    remaining_space = MAX_POST_LENGTH - len(link) - len(LINK_EMOJI) - 3  # 3 = espaços e quebras
    shortened_title = f"{title[:remaining_space]}..."
    return f"{shortened_title}\n\n{LINK_EMOJI} {link}"

def post_to_bluesky(title, link):
    """Publica no Bluesky com tratamento de erros"""
    try:
        client = Client()
        print("\n=== TENTANDO AUTENTICAÇÃO ===")
        client.login(os.environ['BLUESKY_USERNAME'], os.environ['BLUESKY_PASSWORD'])
        print(">> Autenticação bem-sucedida!")

        post_text = prepare_post(title, link)
        print(f"\n=== CONTEÚDO DO POST ({len(post_text)}/{MAX_POST_LENGTH} chars) ===")
        print(post_text)

        response = client.send_post(text=post_text)
        print("\n>> Post publicado com sucesso!")
        print(f"URI: bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}")

    except Exception as e:
        print(f"\n>> ERRO CRÍTICO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Verifica credenciais
    if not all(k in os.environ for k in ['BLUESKY_USERNAME', 'BLUESKY_PASSWORD']):
        print("ERRO: Configure BLUESKY_USERNAME e BLUESKY_PASSWORD nos Secrets.")
        sys.exit(1)

    title, link = get_latest_news()
    
    if title and link:
        post_to_bluesky(title, link)
    else:
        print(">> Nada para postar.")
        sys.exit(0)
