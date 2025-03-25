import feedparser
from bs4 import BeautifulSoup
from atproto import Client
import os
import sys

# Configurações
RSS_URL = "https://www.vaticannews.va/pt.rss.xml"

def get_latest_news():
    try:
        print("\n=== INICIANDO LEITURA DO RSS ===")
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            print(">> ERRO: Nenhuma notícia encontrada no feed RSS")
            return None, None, None

        latest = feed.entries[0]
        title = latest.title
        link = latest.link
        description = BeautifulSoup(latest.description, "html.parser").get_text()

        print(f">> Notícia mais recente: {title[:50]}...")
        return title, link, description

    except Exception as e:
        print(f">> ERRO AO LER RSS: {str(e)}")
        return None, None, None

def post_to_bluesky(title, link, description):
    try:
        # Configuração do cliente
        client = Client(base_url="https://bsky.social")
        
        print("\n=== TENTANDO AUTENTICAÇÃO ===")
        print(f"Usuário: {os.environ.get('BLUESKY_USERNAME', 'NÃO DEFINIDO')}")
        
        # Autenticação (sem timeout)
        client.login(
            os.environ['BLUESKY_USERNAME'],
            os.environ['BLUESKY_PASSWORD']
        )
        print(">> Autenticação bem-sucedida!")

        # Preparar e postar
        post_text = f"{title}\n\n{description}\n\nLeia mais: {link}"
        print(f"\n=== CONTEÚDO DO POST ===")
        print(post_text[:200] + "...")

        response = client.send_post(text=post_text)
        print("\n>> Post publicado com sucesso!")
        print(f"URI do post: {response.uri}")

    except Exception as e:
        print(f"\n>> ERRO CRÍTICO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not os.environ.get('BLUESKY_USERNAME') or not os.environ.get('BLUESKY_PASSWORD'):
        print("ERRO: Credenciais não definidas.")
        sys.exit(1)

    title, link, description = get_latest_news()
    
    if title and link:
        post_to_bluesky(title, link, description)
    else:
        print(">> Nenhum conteúdo válido para postar.")
        sys.exit(0)
