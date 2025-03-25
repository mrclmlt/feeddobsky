import feedparser
from bs4 import BeautifulSoup
from atproto import Client
import os
import sys

# Configurações
RSS_URLS = [
    "https://www.vaticannews.va/pt.rss.xml",
    # "https://siteficticio.xml",
]
MAX_POST_LENGTH = 300
LINK_EMOJI = "🔗"

def get_latest_news():
    try:
        print("\n=== INICIANDO LEITURA DOS FEEDS RSS ===")
        for url in RSS_URLS:
            print(f">> Verificando feed: {url}")
            feed = feedparser.parse(url)
            
            if feed.entries:
                latest = feed.entries[0]
                title = latest.title.strip()
                link = latest.link.strip()
                
                # Garantia de link clicável:
                if not link.startswith(('http://', 'https://')):
                    link = f"https://{link}"
                elif link.startswith('http://'):
                    link = link.replace('http://', 'https://')  # Force HTTPS
                
                print(f">> Notícia encontrada: {title[:60]}...")
                return title, link
        
        print(">> AVISO: Nenhuma notícia encontrada")
        return None, None

    except Exception as e:
        print(f">> ERRO AO LER RSS: {str(e)}")
        return None, None

def prepare_post(title, link):
    """Formatação que garante links clicáveis no Bluesky"""
    # Estrutura otimizada:
    # 1. Link SEMPRE em linha separada
    # 2. Prefixo com emoji
    # 3. Espaçamento consistente
    
    post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    # Fallback se ainda for longo
    if len(post_text) > MAX_POST_LENGTH:
        available_space = MAX_POST_LENGTH - len(LINK_EMOJI) - len(link) - 4  # 4 = espaços e \n
        title = f"{title[:available_space]}..."
        post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    print(f">> Tamanho do post: {len(post_text)}/{MAX_POST_LENGTH} chars")
    return post_text

def post_to_bluesky(title, link):
    try:
        client = Client()
        print("\n=== TENTANDO AUTENTICAÇÃO ===")
        client.login(os.environ['BLUESKY_USERNAME'], os.environ['BLUESKY_PASSWORD'])
        print(">> Autenticação OK!")

        post_text = prepare_post(title, link)
        print(f"\n=== POST FINAL ===\n{post_text}\n=== FIM DO POST ===")

        response = client.send_post(text=post_text)
        print("\n>> Post publicado com sucesso!")
        print(f">> Link clicável: bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}")
        print(f">> URL da notícia: {link}")  # Confira se o link está correto

    except Exception as e:
        print(f"\n>> ERRO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not all(var in os.environ for var in ['BLUESKY_USERNAME', 'BLUESKY_PASSWORD']):
        print("ERRO: Configure os secrets BLUESKY_USERNAME e BLUESKY_PASSWORD")
        sys.exit(1)

    title, link = get_latest_news()
    
    if title and link:
        post_to_bluesky(title, link)
    else:
        print(">> Nada para postar.")
        sys.exit(0)
