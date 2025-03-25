import feedparser
from bs4 import BeautifulSoup  # Esta é a linha corrigida
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
                
                if not link.startswith(('http://', 'https://')):
                    link = f"https://{link}"
                
                print(f">> Notícia encontrada: {title[:60]}...")
                return title, link
        
        print(">> AVISO: Nenhuma notícia encontrada")
        return None, None

    except Exception as e:
        print(f">> ERRO AO LER RSS: {str(e)}")
        return None, None

def prepare_post(title, link):
    post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    if len(post_text) > MAX_POST_LENGTH:
        max_title_length = MAX_POST_LENGTH - len(LINK_EMOJI) - len(link) - 4
        title = f"{title[:max_title_length]}..."
        post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    print(f">> Tamanho do post: {len(post_text)}/{MAX_POST_LENGTH} caracteres")
    return post_text

def post_to_bluesky(title, link):
    try:
        client = Client()
        print("\n=== TENTANDO AUTENTICAÇÃO ===")
        client.login(os.environ['BLUESKY_USERNAME'], os.environ['BLUESKY_PASSWORD'])
        print(">> Autenticação bem-sucedida!")

        post_text = prepare_post(title, link)
        print(f"\n=== CONTEÚDO PRONTO ===\n{post_text}")

        response = client.send_post(text=post_text)
        print("\n>> Post publicado com sucesso!")
        print(f">> URL: bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}")

    except Exception as e:
        print(f"\n>> ERRO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not all(var in os.environ for var in ['BLUESKY_USERNAME', 'BLUESKY_PASSWORD']):
        print("ERRO: Configure os secrets no GitHub!")
        sys.exit(1)

    title, link = get_latest_news()
    
    if title and link:
        post_to_bluesky(title, link)
    else:
        print(">> Nenhum conteúdo válido para postar.")
        sys.exit(0)
