import feedparser
from bs4 import BeautifulSoup
from atproto import Client
import os
import sys

# Configurações
RSS_URLS = [
    "https://www.vaticannews.va/pt.rss.xml",  # Feed principal
    # "https://siteficticio.xml",  # Feed fictício (descomente para adicionar)
]
MAX_POST_LENGTH = 300  # Limite do Bluesky
LINK_EMOJI = "🔗"      # Emoji para o link

def get_latest_news():
    """Obtém a última notícia dos feeds RSS, priorizando o primeiro com conteúdo"""
    try:
        print("\n=== INICIANDO LEITURA DOS FEEDS RSS ===")
        for url in RSS_URLS:
            print(f">> Verificando feed: {url}")
            feed = feedparser.parse(url)
            
            if feed.entries:
                latest = feed.entries[0]
                title = latest.title.strip()
                link = latest.link.strip()
                print(f">> Notícia encontrada: {title[:60]}...")
                return title, link
        
        print(">> AVISO: Nenhuma notícia encontrada em nenhum feed")
        return None, None

    except Exception as e:
        print(f">> ERRO CRÍTICO AO LER RSS: {str(e)}")
        return None, None

def prepare_post(title, link):
    """Formata o post garantindo o limite de caracteres"""
    # Versão 1: Título completo + link
    post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    if len(post_text) <= MAX_POST_LENGTH:
        return post_text
    
    # Versão 2: Título truncado se necessário
    max_title_length = MAX_POST_LENGTH - len(LINK_EMOJI) - len(link) - 4  # Espaços e quebras
    truncated_title = f"{title[:max_title_length]}..."
    return f"{truncated_title}\n\n{LINK_EMOJI} {link}"

def post_to_bluesky(title, link):
    """Publica no Bluesky com tratamento robusto de erros"""
    try:
        client = Client()
        print("\n=== TENTANDO AUTENTICAÇÃO ===")
        client.login(os.environ['BLUESKY_USERNAME'], os.environ['BLUESKY_PASSWORD'])
        print(">> Autenticação bem-sucedida!")

        post_text = prepare_post(title, link)
        print(f"\n=== CONTEÚDO PRONTO ({len(post_text)}/{MAX_POST_LENGTH} chars) ===")
        print(post_text)

        response = client.send_post(text=post_text)
        print("\n>> Post publicado com sucesso!")
        print(f"URL: bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}")

    except Exception as e:
        print(f"\n>> ERRO NA PUBLICAÇÃO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Validação das credenciais
    if not all(key in os.environ for key in ['BLUESKY_USERNAME', 'BLUESKY_PASSWORD']):
        print("ERRO: Credenciais não configuradas nos Secrets.")
        sys.exit(1)

    # Fluxo principal
    title, link = get_latest_news()
    
    if title and link:
        post_to_bluesky(title, link)
    else:
        print(">> Nenhum conteúdo válido para postar.")
        sys.exit(0)
